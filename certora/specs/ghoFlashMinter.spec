using GhoToken as _GhoToken;
using GhoAToken as _GhoAToken;
using MockFlashBorrower as _MockFlashBorrower;

///////////////// METHODS //////////////////////

methods{

    //
    // Current contract
    //

    // GhoFlashMinterHarness

    // GhoFlashMinter
    function flashLoan(address receiver, address token, uint256 amount, bytes data) external returns (bool);
    function distributeFeesToTreasury() external;
    function updateFee(uint256 newFee) external;
    function updateGhoTreasury(address newGhoTreasury) external;
    function maxFlashLoan(address token) external returns (uint256);
    function flashFee(address token, uint256 amount) external returns (uint256);
    function getFee() external returns (uint256) envfree;
    function getGhoTreasury() external returns (address) envfree; 
    function _flashFee(uint256 amount) internal returns (uint256);
    function _updateFee(uint256 newFee) internal;
    function _updateGhoTreasury(address newGhoTreasury) internal;

    //
    // External calls
    //

    // GhoToken
    function _GhoToken.allowance(address, address) external returns (uint256) envfree;
    function _GhoToken.totalSupply() external returns (uint256) envfree;
    function _GhoToken.balanceOf(address) external returns (uint256) envfree;
    // ERC20
    function _.mint(address, uint256)  external => DISPATCHER(true);
    function _.burn(uint256) external => DISPATCHER(true);
    function _.transfer(address, uint256) external => DISPATCHER(true);
    function _.transferFrom(address, address, uint256) external => DISPATCHER(true);
    function _.balanceOf(address) external => DISPATCHER(true);
    function _.getFacilitatorBucket(address) external => DISPATCHER(true);

    // GhoAToken
    function _GhoAToken.getGhoTreasury() external returns (address) envfree;

    // MockFlashBorrower
    function _MockFlashBorrower.onFlashLoan(address initiator, address token, uint256 amount, uint256 fee,
        bytes data) external returns (bytes32);
    function _MockFlashBorrower.action() external returns (MockFlashBorrower.Action) envfree;
    function _MockFlashBorrower._transferTo() external returns (address) envfree;
    // IERC3156FlashBorrower 
    function _.onFlashLoan(address initiator, address token, uint256 amount, uint256 fee,
        bytes data) external with (env e) 
            => onFlashLoanCVL(e, initiator, token, amount, fee, data) expect (bytes32) ALL;

    // IPoolAddressesProvider
    function _.getACLManager() external => NONDET;

    // ACL_MANAGER
    function _.isPoolAdmin(address user) external => retrievePoolAdminFromGhost(user) expect bool ALL;
    function _.isFlashBorrower(address user) external => retrieveFlashBorrowerFromGhost(user) expect bool ALL;
    
    // IGhoVariableDebtToken
    function _.decreaseBalanceFromInterest(address, uint256) external => NONDET;
    function _.getBalanceFromInterest(address) external => NONDET;
}

///////////////// DEFINITIONS /////////////////////

////////////////// FUNCTIONS //////////////////////

// a set of assumptions needed for rules that call flashloan
function flashLoanReqs(env e){
    require e.msg.sender != currentContract;
    require _GhoToken.allowance(currentContract, e.msg.sender) == 0;
}

// an assumption that demands the sum of balances of 3 given users is no more than the total supply
function ghoBalanceOfTwoUsersLETotalSupply(address user1, address user2, address user3){
    require _GhoToken.balanceOf(user1) + _GhoToken.balanceOf(user2) + _GhoToken.balanceOf(user3) <= to_mathint(_GhoToken.totalSupply());
}

function onFlashLoanCVL(env e, address initiator, address token, uint amount, uint fee, bytes data) returns bytes32 {
    return _MockFlashBorrower.onFlashLoan(e, initiator, token, amount, fee, data);
}

///////////////// GHOSTS & HOOKS //////////////////

//
// ACL_MANAGER.isPoolAdmin() and ACL_MANAGER.isFlashBorrower() summarisation
// 

// keeps track of users with pool admin permissions in order to return a consistent value per user
ghost mapping(address => bool) poolAdmin_ghost;

// keeps track of users with flash borrower permissions in order to return a consistent value per user
ghost mapping(address => bool) flashBorrower_ghost;

function retrievePoolAdminFromGhost(address user) returns bool{
    return poolAdmin_ghost[user];
}

function retrieveFlashBorrowerFromGhost(address user) returns bool{
    return flashBorrower_ghost[user];
}

//
// Ghost copy of `_fee`
//

ghost uint256 ghostFee {
    init_state axiom ghostFee == 0;
}

hook Sload uint256 val currentContract._fee STORAGE {
    require(ghostFee == val);
}

hook Sstore currentContract._fee uint256 val STORAGE {
    ghostFee = val;
}

//
// Ghost copy of `_ghoTreasury`
//

ghost address ghostGhoTreasury {
    init_state axiom ghostGhoTreasury == 0;
}

hook Sload address val currentContract._ghoTreasury STORAGE {
    require(ghostGhoTreasury == val);
}

hook Sstore currentContract._ghoTreasury address val STORAGE {
    ghostGhoTreasury = val;
}

///////////////// PROPERTIES //////////////////////

// The GHO balance of the flash minter should grow when calling any function, excluding distributeFees
rule balanceOfFlashMinterGrows(method f, env e, calldataarg args) 
    filtered { f -> f.selector != sig:distributeFeesToTreasury().selector } {
    
    // No overflow of gho is possible
    ghoBalanceOfTwoUsersLETotalSupply(currentContract, e.msg.sender, _GhoAToken);
    flashLoanReqs(e);
    // excluding calls to distribute fees
    mathint action = assert_uint256(_MockFlashBorrower.action());
    require action != 1; 

    uint256 _facilitatorBalance = _GhoToken.balanceOf(currentContract);

    f(e, args);

    uint256 facilitatorBalance_ = _GhoToken.balanceOf(currentContract);

    assert(facilitatorBalance_ >= _facilitatorBalance);
}

// Checks the integrity of updateGhoTreasury - after update the given address is set
rule integrityOfTreasurySet(address token){
    env e;
    updateGhoTreasury(e, token);

    address treasury_ = getGhoTreasury(e);

    assert(treasury_ == token);
}

// Checks the integrity of updateFee - after update the given value is set
rule integrityOfFeeSet(uint256 new_fee){
    env e;
    updateFee(e, new_fee);
    uint256 fee_ = getFee(e);

    assert(fee_ == new_fee);
}

// Checks that the available liquidity, retrieved by maxFlashLoan, stays the same after any action
rule availableLiquidityDoesntChange(method f, address token){
    env e; calldataarg args;
    uint256 _liquidity = maxFlashLoan(e, token);

    f(e, args);

    uint256 liquidity_ = maxFlashLoan(e, token);

    assert(liquidity_ == _liquidity);
}

// Checks the integrity of distributeFees:
//  1. As long as the treasury contract itself isn't acting as a flashloan minter, the flashloan 
//      facilitator's GHO balance should be empty after distribution
//  2. The change in balances of the receiver (treasury) and the sender (flash minter) is the 
//      same. i.e. no money is being generated out of thin air
rule integrityOfDistributeFeesToTreasury(){
    env e;
    address treasury = getGhoTreasury(e);
    uint256 _facilitatorBalance = _GhoToken.balanceOf(currentContract);
    uint256 _treasuryBalance = _GhoToken.balanceOf(treasury);

    // No overflow of gho is possible
    ghoBalanceOfTwoUsersLETotalSupply(currentContract, treasury, _GhoAToken);
    distributeFeesToTreasury(e);

    uint256 facilitatorBalance_ = _GhoToken.balanceOf(currentContract);
    uint256 treasuryBalance_ = _GhoToken.balanceOf(treasury);

    assert(treasury != currentContract => facilitatorBalance_ == 0);
    assert(treasuryBalance_ - _treasuryBalance == _facilitatorBalance - facilitatorBalance_);
}

// Checks that the fee amount reported by flashFee is the the same as the actual fee that is taken by flashloaning
rule feeSimulationEqualsActualFee(address receiver, address token, uint256 amount, bytes data){
    env e;
    mathint feeSimulationResult = flashFee(e, token, amount);
    uint256 _facilitatorBalance = _GhoToken.balanceOf(currentContract);
    
    flashLoanReqs(e);
    require _GhoAToken.getGhoTreasury() != currentContract;
    // No overflow of gho is possible
    ghoBalanceOfTwoUsersLETotalSupply(currentContract, e.msg.sender, _GhoAToken);
    // Excluding call to distributeFeesToTreasury & calling another flashloan (which will generate another fee in recursion)
    mathint borrower_action = assert_uint256(_MockFlashBorrower.action());
    require borrower_action != 1 && borrower_action != 0;
    // Because we calculate the actual fee by balance difference of the minter, we assume no extra money is being sent to the minter.
    require _MockFlashBorrower._transferTo() != currentContract;
    
    flashLoan(e, receiver, token, amount, data);

    uint256 facilitatorBalance_ = _GhoToken.balanceOf(currentContract);

    mathint actualFee = facilitatorBalance_ - _facilitatorBalance;

    assert(feeSimulationResult == actualFee);
}

///////////////// ADDED PROPERTIES //////////////////////

// Possibility should not revert
rule functionsNotRevert(env e, method f, calldataarg args) {
    
    f@withrevert(e, args); 
    
    satisfy(!lastReverted);
}
