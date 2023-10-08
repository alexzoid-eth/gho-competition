import "./methods/ghoTokenHelperMethods.spec";

using GhoTokenHarness as _GhoTokenHarness;
using GhoVariableDebtTokenHarness as _GhoVariableDebtTokenHarness;
using DummyERC20A as _DummyERC20A;

///////////////// METHODS //////////////////////

methods{

    //
    // Current contract
    //

    // GhoATokenHarness
    function getPoolAddress() external returns (address) envfree;
    function calculateDomainSeparator() external returns (bytes32);
    function isPoolAdmin(address account) external returns (bool);
    function setAnotherName() external envfree;

    // GhoAToken
    function initialize(address initializingPool, address treasury, address underlyingAsset, 
        address incentivesController, uint8 aTokenDecimals, string calldata aTokenName, 
        string calldata aTokenSymbol, bytes calldata params) external;
    function mint(address caller, address onBehalfOf, uint256 amount, uint256 index) external returns (bool); // Always reverts
    function burn(address from, address receiverOfUnderlying, uint256 amount, uint256 index) external; // Always reverts
    function mintToTreasury(uint256 amount, uint256 index) external; // Always reverts
    function transferOnLiquidation(address from, address to, uint256 value) external; // Always reverts
    function balanceOf(address) external returns (uint256) envfree;
    function totalSupply() external returns (uint256) envfree;
    function RESERVE_TREASURY_ADDRESS() external returns (address) envfree;
    function UNDERLYING_ASSET_ADDRESS() external returns (address) envfree;
    function transferUnderlyingTo(address target, uint256 amount) external;
    function handleRepayment(address user, address onBehalfOf, uint256 amount) external; 
    function distributeFeesToTreasury() external;
    function permit(address owner, address spender, uint256 value, uint256 deadline, uint8 v, 
        bytes32 r, bytes32 s) external; // Always reverts
    function _transfer(address from, address to, uint128 amount) internal;
    function DOMAIN_SEPARATOR() internal returns (bytes32);
    function _EIP712BaseId() internal returns (string memory);
    function rescueTokens(address token, address to, uint256 amount) external;
    function setVariableDebtToken(address ghoVariableDebtToken) external;
    function getVariableDebtToken() external returns (address) envfree;
    function updateGhoTreasury(address newGhoTreasury) external;
    function getGhoTreasury() external returns (address) envfree;

    // ScaledBalanceTokenBase
    function scaledBalanceOf(address) external returns (uint256) envfree;
    function getScaledUserBalanceAndSupply(address user) external returns (uint256, uint256) envfree;
    function scaledTotalSupply() internal returns (uint256);
    function getPreviousIndex(address user) external returns (uint256) envfree;

    // IncentivizedERC20
    function name() internal returns (string memory);
    function symbol() external returns (string memory) envfree;
    function decimals() external returns (uint8) envfree;
    // function totalSupply() internal returns (uint256); // overridden in GhoAToken
    // function balanceOf(address account) internal returns (uint256); // overridden in GhoAToken
    function getIncentivesController() external returns (address) envfree;
    function setIncentivesController(address controller) external;
    function transfer(address recipient, uint256 amount) external returns (bool); // Always reverts
    function allowance(address owner, address spender) external returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool); // Always reverts
    function increaseAllowance(address spender, uint256 addedValue) external returns (bool);
    function decreaseAllowance(address spender, uint256 subtractedValue) external returns (bool);
    // function _transfer(address sender, address recipient, uint128 amount) virtual; // overridden in GhoAToken
    function _setName(string memory newName) internal;
    function _setSymbol(string memory newSymbol) internal;
    function _setDecimals(uint8 newDecimals) internal;

    // EIP712Base
    // function DOMAIN_SEPARATOR() internal returns (bytes32); // overridden in GhoAToken
    // function nonces(address owner) internal returns (uint256); // overridden in GhoAToken
    function _calculateDomainSeparator() internal returns (bytes32);

    //
    // External calls
    //

    // _DummyERC20A, GhoToken
    function _.balanceOf(address) external => DISPATCHER(true);

    // GhoToken
    function _.transfer(address to, uint256 amount) external => DISPATCHER(true);
    function _.mint(address account, uint256 amount) external => DISPATCHER(true);
    function _.burn(uint256 amount) external => DISPATCHER(true);
    function _.totalSupply() external => DISPATCHER(true);

    // GhoTokenVariableDebtToken
    function _.getBalanceFromInterest(address user) external => DISPATCHER(true);
    function _.decreaseBalanceFromInterest(address user, uint256 amount) external => DISPATCHER(true);

    // IERC20(token)
    function _.safeTransfer(address, uint256) external => DISPATCHER(true);

    // Pool
    function _.ADDRESSES_PROVIDER() external => addressesProviderSummarize() expect address ALL;

    // PoolAddressesProvider
    function _.getACLManager() external => CONSTANT;

    // ACLManager
    function _.isPoolAdmin(address) external => CONSTANT;
}

///////////////// DEFINITIONS /////////////////////

definition ADDRESSES_PROVIDER_ADDRESS() returns address = 111;
definition POOL_ADDRESS() returns address = 222;
definition NAME_SYMBOL_STR() returns string = "GHO_ATOKEN_IMPL";

definition VIEW_FUNCTIONS(method f) returns bool = f.isView || f.isPure;

definition ALWAYS_REVERT_FUNCTIONS(method f) returns bool = 
    f.selector == sig:mint(address, address, uint256, uint256).selector
    || f.selector == sig:burn(address, address, uint256, uint256).selector
    || f.selector == sig:mintToTreasury(uint256, uint256).selector
    || f.selector == sig:transferOnLiquidation(address, address, uint256).selector
    || f.selector == sig:transfer(address, uint256).selector
    || f.selector == sig:transferFrom(address, address, uint256).selector
    || f.selector == sig:permit(address, address, uint256, uint256, uint8, bytes32, bytes32).selector
    ;

definition INITIALIZE_FUNCTION(method f) returns bool = 
    f.selector == sig:initialize(address, address, address, address, uint8, string, string, bytes).selector;

definition HANDLE_REPAYMENT_FUNCTION(method f) returns bool = 
    f.selector == sig:handleRepayment(address, address, uint256).selector;

definition DISTRIBUTE_FEES_TO_TREASUTY_FUNCTION(method f) returns bool = 
    f.selector == sig:distributeFeesToTreasury().selector;

definition BURN_USE_FUNCTION(method f) returns bool = 
    f.selector == sig:transferUnderlyingTo(address, uint256).selector;

definition MINT_USE_FUNCTION(method f) returns bool = 
    f.selector == sig:handleRepayment(address, address, uint256).selector;

definition BURN_MINT_USE_FUNCTIONS(method f) returns bool = 
    BURN_USE_FUNCTION(f) || MINT_USE_FUNCTION(f);


////////////////// FUNCTIONS //////////////////////

function addressesProviderSummarize() returns address {
    ghostAddressesProvider = ADDRESSES_PROVIDER_ADDRESS();
    return ADDRESSES_PROVIDER_ADDRESS();
}

function setUp() {
    require(_GhoTokenHarness == ghostUnderlyingAsset);
    require(_GhoVariableDebtTokenHarness == ghostGhoVariableDebtToken);

    require(ghostGhoTreasury != _GhoTokenHarness);
    require(ghostGhoTreasury != _GhoVariableDebtTokenHarness);
    require(ghostGhoTreasury != currentContract);
}

///////////////// GHOSTS & HOOKS //////////////////

//
// Ghost copy of `POOL`
//

ghost address ghostPool {
    init_state axiom ghostPool == 0;
}

//
// Ghost copy of `_addressesProvider`
//

ghost address ghostAddressesProvider {
    init_state axiom ghostAddressesProvider == 0;
}

//
// VersionedInitializable initial values
//

ghost bool ghostInitializing {
    init_state axiom ghostInitializing == false;
}

hook Sload bool val currentContract.initializing STORAGE {
    require(val == ghostInitializing);
}

hook Sstore currentContract.initializing bool val STORAGE {
    ghostInitializing = val;
}

ghost uint256 ghostLastInitializedRevision {
    init_state axiom ghostLastInitializedRevision == 0;
}

hook Sload uint256 val currentContract.lastInitializedRevision STORAGE {
    require(val == ghostLastInitializedRevision);
}

hook Sstore currentContract.lastInitializedRevision uint256 val STORAGE {
    ghostLastInitializedRevision = val;
}

//
// Ghost copy of `_treasury`
//

ghost address ghostTreasury {
    init_state axiom ghostTreasury == 0;
}

hook Sload address val currentContract._treasury STORAGE {
    require(ghostTreasury == val);
}

hook Sstore currentContract._treasury address val STORAGE {
    ghostTreasury = val;
}

//
// Ghost copy of `_underlyingAsset`
//

ghost address ghostUnderlyingAsset {
    init_state axiom ghostUnderlyingAsset == 0;
}

hook Sload address val currentContract._underlyingAsset STORAGE {
    require(ghostUnderlyingAsset == val);
}

hook Sstore currentContract._underlyingAsset address val STORAGE {
    ghostUnderlyingAsset = val;
}

//
// Ghost copy of `_ghoVariableDebtToken`
//

ghost address ghostGhoVariableDebtToken {
    init_state axiom ghostGhoVariableDebtToken == 0;
}

hook Sload address val currentContract._ghoVariableDebtToken STORAGE {
    require(ghostGhoVariableDebtToken == val);
}

hook Sstore currentContract._ghoVariableDebtToken address val STORAGE {
    ghostGhoVariableDebtToken = val;
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

//
// Ghost copy of `_incentivesController`
//

ghost address ghostIncentivesController {
    init_state axiom ghostIncentivesController == 0;
}

hook Sload address val currentContract._incentivesController STORAGE {
    require(ghostIncentivesController == val);
}

hook Sstore currentContract._incentivesController address val STORAGE {
    ghostIncentivesController = val;
}

//
// Ghost copy of `_domainSeparator`
//
// TODO: uncommenting this block leads to unexpected errors in Prover
// uncommented: https://prover.certora.com/output/52567/3fce257bd5bd447db7f25eb12b961f05/?anonymousKey=001f36a371acf2f144e09f729eee9da2ac9878e4
// commented: https://prover.certora.com/output/52567/1e25deaa8cd148bc88fcb323adeef0db/?anonymousKey=38ada586409811a6877cbfc14a8d5f7f3251bbaf
/*
ghost bytes32 ghostDomainSeparator {
    init_state axiom ghostDomainSeparator == to_bytes32(0);
}

hook Sload bytes32 val currentContract._domainSeparator STORAGE {
    require(ghostDomainSeparator == val);
}

hook Sstore currentContract._domainSeparator bytes32 val STORAGE {
    ghostDomainSeparator = val;
}
*/

//
// Ghost copy of `ERC20.name`
//

ghost uint256 ghostNameLength {
    init_state axiom ghostNameLength == 0;
}

hook Sload uint256 val currentContract._name.(offset 0) STORAGE {
    require(ghostNameLength == val);
}

hook Sstore currentContract._name.(offset 0) uint256 val STORAGE {
    ghostNameLength = val;
}

//
// Ghost copy of `ERC20.symbol`
//

ghost uint256 ghostSymbolLength {
    init_state axiom ghostSymbolLength == 0;
}

hook Sload uint256 val currentContract._symbol.(offset 0) STORAGE {
    require(ghostSymbolLength == val);
}

hook Sstore currentContract._symbol.(offset 0) uint256 val STORAGE {
    ghostSymbolLength = val;
}

//
// Ghost copy of `ERC20.decimals`
//

ghost uint8 ghostDecimals {
    init_state axiom ghostDecimals == 0;
}

hook Sload uint8 val currentContract._decimals STORAGE {
    require(ghostDecimals == val);
}

hook Sstore currentContract._decimals uint8 val STORAGE {
    ghostDecimals = val;
}


///////////////// PROPERTIES //////////////////////

// Proves that ghoAToken::mint always reverts
rule noMint(env e, calldataarg args) {
    mint@withrevert(e, args);
    assert(lastReverted);
}

// Proves that ghoAToken::burn always reverts
rule noBurn(env e, calldataarg args) {
    burn@withrevert(e, args);
    assert(lastReverted);
}

// Proves that ghoAToken::transfer always reverts
rule noTransfer(env e, calldataarg args) {
    transfer@withrevert(e, args);
    assert(lastReverted);
}

// Proves that calling ghoAToken::transferUnderlyingTo will revert if the amount exceeds the excess 
//  capacity. A user can’t borrow more than the facilitator’s remaining capacity.
rule transferUnderlyingToCantExceedCapacity() {

    // Added
    setUp();

    address target;
    uint256 amount;
    env e;
    mathint facilitatorLevel = _GhoTokenHelper.getFacilitatorBucketLevel(currentContract);
    mathint facilitatorCapacity = _GhoTokenHelper.getFacilitatorBucketCapacity(currentContract);
    
    transferUnderlyingTo@withrevert(e, target, amount);
    
    assert(to_mathint(amount) > (facilitatorCapacity - facilitatorLevel) => lastReverted);
}

// Proves that the total supply of GhoAToken is always zero
rule totalSupplyAlwaysZero() {
    assert(totalSupply() == 0);
} 

// Proves that any user's balance of GhoAToken is always zero
rule userBalanceAlwaysZero(address user) {
    assert(balanceOf(user) == 0);
}

// BucketLevel decreases after transferUnderlyingTo() followed by handleRepayment(). repayment 
//  funds are, partially or fully, transferred to the treasury
rule integrityTransferUnderlyingToWithHandleRepayment() {

    // Added
    setUp();

    env e;
    calldataarg arg;
    uint256 amount;
    address target;
    address user;
    address onBehalfOf;

    uint256 levelBefore = _GhoTokenHelper.getFacilitatorBucketLevel(currentContract);
    transferUnderlyingTo(e, target, amount);
    handleRepayment(e, user, onBehalfOf, amount);
    uint256 levelAfter = _GhoTokenHelper.getFacilitatorBucketLevel(currentContract);

    assert(levelBefore <= levelAfter);
}

///////////////// ADDED PROPERTIES //////////////////////

// TODO: Sanity fail, the only way to test constructor. Skip it?
// Prove that POOL, _addressesProvider, 
//  ERC20 setup correctly in constructor
/*
invariant initialSetupInConstructor() 
    ghostNameLength > 0 && ghostSymbolLength > 0 
    // TODO: add ghostPool set check
    // TODO: seems that addressesProviderSummarize() is not executed
    // && ghostAddressesProvider == ADDRESSES_PROVIDER_ADDRESS() {
{
    preserved {
        require(false);
    }
}
*/

// [2] Initialize could be executed once
rule initializeCouldBeExecutedOnce(env e1, calldataarg args1, env e2, calldataarg args2) {

    require(ghostLastInitializedRevision == 0);
    require(ghostInitializing == false);

    initialize@withrevert(e1, args1);
    bool firstCallReverted = lastReverted;

    initialize@withrevert(e2, args2);
    bool secondCallReverted = lastReverted;

    assert(!firstCallReverted => secondCallReverted);
}

// [3] Could be initialized with specific pool address only
rule initializedWithSpecificPoolAddressOnly(
    env e, 
    address initializingPool, 
    address treasury, 
    address underlyingAsset, 
    address incentivesController, 
    uint8 aTokenDecimals, 
    string aTokenName, 
    string aTokenSymbol, 
    bytes params
    ) {
    
    initialize@withrevert(e, initializingPool, treasury, underlyingAsset, incentivesController, 
        aTokenDecimals, aTokenName, aTokenSymbol, params);
    bool reverted = lastReverted;

    assert(initializingPool != getPoolAddress() => reverted);
}

// [4] Initialize set initial params correctly
rule initializeSetInitialParamsCorrectly(
    env e, 
    address initializingPool, 
    address treasury, 
    address underlyingAsset, 
    address incentivesController, 
    uint8 aTokenDecimals, 
    string aTokenName, 
    string aTokenSymbol, 
    bytes params
) {
    initialize(e, initializingPool, treasury, underlyingAsset, incentivesController, 
        aTokenDecimals, aTokenName, aTokenSymbol, params);

    assert(
        treasury == RESERVE_TREASURY_ADDRESS()
        && underlyingAsset == UNDERLYING_ASSET_ADDRESS()
        && incentivesController == getIncentivesController()
        && aTokenDecimals == decimals()
        && DOMAIN_SEPARATOR(e) == calculateDomainSeparator(e)
        // TODO: check with --hashing_length_bound --optimistic_hashing for keccak256 support
        // && _GhoTokenHelper.compareStrings(aTokenName, name(e))
        // && _GhoTokenHelper.compareStrings(aTokenSymbol, symbol())
    );
}

// [5] Specific functions always reverts
rule specificFunctionsAlwaysRevert(env e, method f, calldataarg args) 
    filtered { f -> ALWAYS_REVERT_FUNCTIONS(f) } {

    f@withrevert(e, args);
    
    assert(lastReverted);
}

// Viewers integrity
rule viewersIntegrity(env e) {
    assert(
        RESERVE_TREASURY_ADDRESS() == ghostTreasury
        && UNDERLYING_ASSET_ADDRESS() == ghostUnderlyingAsset
        && getVariableDebtToken() == ghostGhoVariableDebtToken
        && getGhoTreasury() == ghostGhoTreasury
        // TODO: check with --hashing_length_bound --optimistic_hashing for keccak256 support
        // && DOMAIN_SEPARATOR(e) == ghostDomainSeparator
        // && _GhoTokenHelper.compareStrings(NAME_SYMBOL_STR(), name(e))
        // && _GhoTokenHelper.compareStrings(NAME_SYMBOL_STR(), symbol())
        && decimals() == ghostDecimals
        && getIncentivesController() == ghostIncentivesController
        // TODO: prove scaledBalanceOf, getScaledUserBalanceAndSupply, scaledTotalSupply, getPreviousIndex
    );
}

// [7] Only Pool admin could set Treasury, VariableDebtToken, IncentivesController (expect in `initialize()`)
rule onlyPoolAdminCouldUpdateCriticalAddresses(env e, method f, calldataarg args) 
    filtered { f -> !VIEW_FUNCTIONS(f) && !INITIALIZE_FUNCTION(f) } {

    address ghoTreasuryBefore = ghostGhoTreasury; 
    address ghoVariableDebtTokenBefore = ghostGhoVariableDebtToken;
    address incentivesControllerBefore = ghostIncentivesController;

    f@withrevert(e, args);
    bool reverted = lastReverted;

    bool ghoTreasuryChanged = ghoTreasuryBefore != ghostGhoTreasury; 
    bool ghoVariableDebtTokenChanged = ghoVariableDebtTokenBefore != ghostGhoVariableDebtToken;
    bool incentivesControllerChanged = incentivesControllerBefore != ghostIncentivesController;

    assert((!reverted && (ghoTreasuryChanged || ghoVariableDebtTokenChanged || incentivesControllerChanged)) 
        => isPoolAdmin(e, e.msg.sender)
    );
}

// [8] VariableDebtToken could be set once
rule variableDebtTokenSetOnlyOnce(env e, method f, calldataarg args) 
    filtered { f -> !VIEW_FUNCTIONS(f) && !INITIALIZE_FUNCTION(f) } {

    require(ghostGhoVariableDebtToken != 0);
    address before = ghostGhoVariableDebtToken;

    f@withrevert(e, args);

    assert(!lastReverted => before == ghostGhoVariableDebtToken);
}

// [6] VariableDebtToken could not be set to zero
rule variableDebtTokenNotSetToZero(env e, address ghoVariableDebtToken) {

    setVariableDebtToken(e, ghoVariableDebtToken);

    assert(ghostGhoVariableDebtToken != 0);
}

// [9] Treasury could not be set to zero (expect in `initialize()`)
rule treasuryNotSetToZero(env e, method f, calldataarg args) 
    filtered { f -> !VIEW_FUNCTIONS(f) && !INITIALIZE_FUNCTION(f) } {

    address before = ghostGhoTreasury; 

    f@withrevert(e, args);

    assert((!lastReverted && before != ghostGhoTreasury) => ghostGhoTreasury != 0);
}

// [10] Stuck tokens could be rescued only by pool admin
rule onlyPoolAdminCouldTransferOutTokens(env e, method f, calldataarg args) 
    filtered { f -> !VIEW_FUNCTIONS(f) } {

    setUp();

    uint256 balanceBefore = _DummyERC20A.balanceOf(e, currentContract);
    require(balanceBefore != 0);

    f@withrevert(e, args);
    bool reverted = lastReverted;

    uint256 balanceAfter = _DummyERC20A.balanceOf(e, currentContract);

    assert(!reverted && balanceBefore > balanceAfter => isPoolAdmin(e, e.msg.sender));
}

// [11] Possibility of rescue stuck tokens 
rule possibilityOfRescueStuckToken(env e, address token, address to, uint256 amount) {

    setUp();

    require(token == _DummyERC20A);
    require(amount != 0);

    uint256 currentBalanceBefore = _DummyERC20A.balanceOf(e, currentContract);
    require(currentBalanceBefore != 0);

    uint256 toBalanceBefore = _DummyERC20A.balanceOf(e, to);
    require(toBalanceBefore == 0);

    rescueTokens(e, token, to, amount);

    uint256 currentBalanceAfter = _DummyERC20A.balanceOf(e, currentContract);
    uint256 toBalanceAfter = _DummyERC20A.balanceOf(e, to);

    satisfy(toBalanceAfter == amount);
}

// [12,14] GHO tokens should be sent to ghoTresaury only. Pool admin could not rug pool GHO tokens 
//  via rescue mechanism. handleRepayment(), which changes balance of current contract via burn() is filtered
rule ghoTokensCouldBeTransferredOutToGhoTresauryOnly(env e, method f, calldataarg args) 
    filtered { f -> !HANDLE_REPAYMENT_FUNCTION(f) && !VIEW_FUNCTIONS(f) } {
    
    setUp();    

    // Current contract has some GHO
    uint256 currentBalanceBefore = _GhoTokenHarness.balanceOf(e, currentContract);
    require(currentBalanceBefore != 0);

    // Balance cannot overflow because the sum of all user sbalances can't exceed the max uint256 value
    uint256 ghoTotalSupply = _GhoTokenHarness.totalSupply(e);
    require(currentBalanceBefore <= ghoTotalSupply);

    // GHO treasury is empty
    uint256 tresauryBalanceBefore = _GhoTokenHarness.balanceOf(e, ghostGhoTreasury);
    require(tresauryBalanceBefore == 0);

    f@withrevert(e, args);
    bool reverted = lastReverted;

    uint256 currentBalanceAfter = _GhoTokenHarness.balanceOf(e, currentContract);
    uint256 transferOutAmount = currentBalanceBefore > currentBalanceAfter  
        ? assert_uint256(currentBalanceBefore - currentBalanceAfter)
        : 0;

    uint256 tresauryBalanceAfter = _GhoTokenHarness.balanceOf(e, ghostGhoTreasury);

    // The whole amount of current contract's balance should be transferred
    assert(!reverted && transferOutAmount != 0 => tresauryBalanceAfter == currentBalanceBefore);
}

// [13,15] Possibility of anyone to withdraw GHO tokens to the GHO Tresaury 
rule possibilityOfTransferOutGhoTokensToTresaury(env e) {

    setUp();    

    // User without any privilege
    address user;
    require(user == e.msg.sender
        && user != currentContract
        && user != ghostGhoTreasury
        && user != _GhoTokenHarness
        && user != getPoolAddress()
        && !isPoolAdmin(e, user)
    );

    // Current contract and treasury have some GHO tokens
    uint256 currentBalanceBefore = _GhoTokenHarness.balanceOf(e, currentContract);
    uint256 userBalance = _GhoTokenHarness.balanceOf(e, user);
    uint256 tresauryBalanceBefore = _GhoTokenHarness.balanceOf(e, ghostGhoTreasury);
    require(currentBalanceBefore != 0 
        && currentBalanceBefore != userBalance 
        && currentBalanceBefore != tresauryBalanceBefore
    );

    // Balance cannot overflow because the sum of all user sbalances can't exceed the max uint256 value
    uint256 ghoTotalSupply = _GhoTokenHarness.totalSupply(e);
    require(require_uint256(currentBalanceBefore + tresauryBalanceBefore) <= ghoTotalSupply);

    distributeFeesToTreasury(e);

    uint256 currentBalanceAfter = _GhoTokenHarness.balanceOf(e, currentContract);
    uint256 transferOutAmount = currentBalanceBefore > currentBalanceAfter  
        ? assert_uint256(currentBalanceBefore - currentBalanceAfter)
        : 0;
    uint256 tresauryBalanceAfter = _GhoTokenHarness.balanceOf(e, ghostGhoTreasury);

    // Any user can withdraw all tokens as a fee to the tresaury
    satisfy(currentBalanceAfter == 0 
        && tresauryBalanceAfter == require_uint256(tresauryBalanceBefore + transferOutAmount)
    );
}

// TODO: violated (keccak256 support needed)
// [16] Domain separator depends on token name
/*
rule domainSeparatorDepensOnName(env e) {

    bytes32 separator1 = calculateDomainSeparator(e);

    setAnotherName();
    bytes32 separator2 = calculateDomainSeparator(e);

    assert(separator1 != separator2);
}
*/

// [17] Only Pool could initialize a communication with GhoToken contract (distributeFeesToTreasury() is an exception)

ghost bool ghoTokenCalled;
hook CALL(uint g, address addr, uint value, uint argsOffset, uint argsLength, uint retOffset, uint retLength) uint rc {
    ghoTokenCalled = addr == ghostUnderlyingAsset ? true : ghoTokenCalled;
}

rule onlyPoolCanInitializeCommunicationWithGHOToken(env e, method f, calldataarg args) 
    filtered { f -> !DISTRIBUTE_FEES_TO_TREASUTY_FUNCTION(f) && !VIEW_FUNCTIONS(f) } {

    require(ghoTokenCalled == false);

    f@withrevert(e, args);
    
    assert(!lastReverted && ghoTokenCalled => e.msg.sender == getPoolAddress());
}

// [18,19] Possibility of change current contract's bucketLevel with mint and burn
rule possibilityOfBurnMintChangeBucketLevel(env e, method f, calldataarg args) 
    filtered { f -> BURN_MINT_USE_FUNCTIONS(f) } {

    require(e.msg.sender == getPoolAddress());

    uint256 bucketLevelBefore = _GhoTokenHelper.getFacilitatorBucketLevel(e, currentContract);
    require(bucketLevelBefore != 0);

    uint256 bucketCapacityBefore = _GhoTokenHelper.getFacilitatorBucketCapacity(e, currentContract);
    require(bucketCapacityBefore > bucketLevelBefore);

    f(e, args);
    
    uint256 bucketLevelAfter = _GhoTokenHelper.getFacilitatorBucketLevel(e, currentContract);

    satisfy(bucketLevelAfter != bucketLevelBefore);
}

// [20] Only bucketLevel of current contract could be changed
rule noAnotherUserBucketLevelCouldBeChanged(env e, method f, calldataarg args, address anotherUser) 
    filtered { f -> !VIEW_FUNCTIONS(f) } {

    require(anotherUser != currentContract);

    uint256 bucketLevelBefore = _GhoTokenHelper.getFacilitatorBucketLevel(e, anotherUser);

    f@withrevert(e, args);
    bool reverted = lastReverted;

    uint256 bucketLevelBeforeAfter = _GhoTokenHelper.getFacilitatorBucketLevel(e, anotherUser);

    assert(!reverted => bucketLevelBefore == bucketLevelBeforeAfter);
}

// TODO: bug21 bot caught
// [1, 21-26] handleRepayment() should burn anything more than balance from interest
rule handleRepaymentBurnAnythingMoreBalanceFromInterest(
    env e, address user, address onBehalfOf, uint256 amount
    ) {
    
    setUp();

    uint256 bucketLevelBefore = _GhoTokenHelper.getFacilitatorBucketLevel(e, currentContract);
    require(bucketLevelBefore != 0);

    uint256 bucketCapacityBefore = _GhoTokenHelper.getFacilitatorBucketCapacity(e, currentContract);
    require(bucketCapacityBefore > bucketLevelBefore);

    uint256 balanceFromInterestBefore = _GhoVariableDebtTokenHarness.getUserAccumulatedDebtInterest(e, onBehalfOf);

    handleRepayment(e, user, onBehalfOf, amount);

    uint256 bucketLevelAfter = _GhoTokenHelper.getFacilitatorBucketLevel(e, currentContract);
    uint256 balanceFromInterestAfter = _GhoVariableDebtTokenHarness.getUserAccumulatedDebtInterest(e, onBehalfOf);

    assert(amount > balanceFromInterestBefore 
        ? assert_uint256(bucketLevelBefore - bucketLevelAfter) == assert_uint256(amount - balanceFromInterestBefore)
            && balanceFromInterestAfter == 0
        : bucketLevelBefore == bucketLevelAfter 
            && balanceFromInterestAfter == assert_uint256(balanceFromInterestBefore - amount)
    );
}

// Possibility should not revert
rule functionsNotRevert(env e, method f, calldataarg args) 
    filtered { f -> !ALWAYS_REVERT_FUNCTIONS(f) } {

    f@withrevert(e, args);
    
    satisfy(!lastReverted);
}
