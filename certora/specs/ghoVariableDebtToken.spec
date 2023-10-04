using GhoDiscountRateStrategy as discStrategy;
using DummyERC20WithTimedBalanceOf as discountToken;
using DummyPool as pool;

///////////////// METHODS //////////////////////

methods{
    
    // PoolAddressesProvider
    function _.getACLManager() external => CONSTANT;

    // ACLManager
    function _.isPoolAdmin(address) external => CONSTANT;

    // DummyERC20WithTimedBalanceOf.sol (linked to _discountToken)
    // represent a random balance per block 
    function discountToken.balanceOf(address user) external returns (uint256) with (env e) => balanceOfDiscountTokenAtTimestamp(user, e.block.timestamp) ;

    // DummyPool.sol (linked to POOL)
    // represent a random index per block
    function pool.getReserveNormalizedVariableDebt(address asset) external returns (uint256) with (env e) => indexAtTimestamp(e.block.timestamp);

    // GhoVariableDebtTokenHarness.sol
    function discStrategy.calculateDiscountRate(uint256, uint256) external returns (uint256) envfree;

    // GhoVariableDebtTokenHarness.sol
    function getUserCurrentIndex(address) external returns (uint256) envfree;
    function getUserDiscountRate(address) external returns (uint256) envfree;
    function getUserAccumulatedDebtInterest(address) external returns (uint256) envfree;
    function getBalanceOfDiscountToken(address) external returns (uint256);

    // GhoVariableDebtToken.sol
    function totalSupply() external returns(uint256) envfree;
    function balanceOf(address) external returns (uint256);
    function mint(address, address, uint256, uint256) external returns (bool, uint256);
    function burn(address ,uint256 ,uint256) external returns (uint256);
    function scaledBalanceOf(address) external returns (uint256) envfree;
    function getBalanceFromInterest(address) external returns (uint256) envfree;
    function rebalanceUserDiscountPercent(address) external;
    function updateDiscountDistribution(address ,address ,uint256 ,uint256 ,uint256) external;
}

///////////////// DEFINITIONS /////////////////////

// equals to 100% discount, in points
definition MAX_DISCOUNT() returns uint256 = 10000; 
definition ray() returns uint256 = 1000000000000000000000000000; // 10^27
definition disAllowedFunctions(method f) returns bool = 
            f.selector == sig:transfer(address, uint256).selector ||
            f.selector == sig:allowance(address, address).selector ||
            f.selector == sig:approve(address, uint256).selector ||
            f.selector == sig:transferFrom(address, address, uint256).selector ||
            f.selector == sig:increaseAllowance(address, uint256).selector ||
            f.selector == sig:decreaseAllowance(address, uint256).selector;

////////////////// FUNCTIONS //////////////////////

//
// CVL implementation of rayMul
//

function rayMulCVL(uint256 a, uint256 b) returns mathint {
    return ((a * b + (ray() / 2)) / ray());
}

function rayDivCVL(uint256 a, uint256 b) returns mathint {
    return ((a * ray() + (b / 2)) / b);
}

// Query index_ghost for the index value at the input timestamp
function indexAtTimestamp(uint256 timestamp) returns uint256 {
    require index_ghost[timestamp] >= ray();
    return index_ghost[timestamp];
    // return 1001684385021630839436707910;//index_ghost[timestamp];
}

// Query discount_ghost for the [user]'s balance of discount token at [timestamp]
function balanceOfDiscountTokenAtTimestamp(address user, uint256 timestamp) returns uint256 {
    return discount_ghost[user][timestamp];
}

// Returns an env instance with [ts] as the block timestamp
function envAtTimestamp(uint256 ts) returns env {
    env e;
    require(e.block.timestamp == ts);
    return e;
}

///////////////// GHOSTS & HOOKS //////////////////

//todo: check balanceof after mint (stable index), burn after balanceof

ghost mapping(address => mapping (uint256 => uint256)) discount_ghost;
ghost mapping(uint256 => uint256) index_ghost;

///////////////// PROPERTIES //////////////////////

// At any point in time, the user's discount rate isn't larger than 100%
invariant discountCantExceed100Percent(address user)
    getUserDiscountRate(user) <= MAX_DISCOUNT()
    {
        preserved updateDiscountDistribution(address sender,address recipient,uint256 senderDiscountTokenBalance,uint256 recipientDiscountTokenBalance,uint256 amount) with (env e) {
            require(indexAtTimestamp(e.block.timestamp) >= ray());
        }
    }

// Ensuring that the defined disallowed functions revert in any case (from VariableDebtToken.spec)
rule disallowedFunctionalities(method f) filtered { f -> disAllowedFunctions(f) } {
    env e; 
    calldataarg args;
    f@withrevert(e, args);
    assert lastReverted;
}

// Proves that the user's balance of debt token (as reported by GhoVariableDebtToken::balanceOf) 
//  can't increase by calling any external non-mint function.
rule nonMintFunctionCantIncreaseBalance(method f) 
    filtered { f-> f.selector != sig:mint(address, address, uint256, uint256).selector } {
    address user;
    uint256 ts1;
    uint256 ts2;
    require(ts2 >= ts1);
    // Forcing the index to be fixed (otherwise the rule times out). For non-fixed index replace `==` with `>=`
    require((indexAtTimestamp(ts1) >= ray()) && 
            (indexAtTimestamp(ts2) == indexAtTimestamp(ts1)));
    require(getUserCurrentIndex(user) == indexAtTimestamp(ts1));
    requireInvariant discountCantExceed100Percent(user);

    env e = envAtTimestamp(ts2);
    uint256 balanceBeforeOp = balanceOf(e, user);
    calldataarg args;
    f(e,args);

    mathint balanceAfterOp = balanceOf(e, user);
    mathint allowedDiff = indexAtTimestamp(ts2) / ray();

    // assert(balanceAfterOp != balanceBeforeOp + allowedDiff + 1);
    assert(balanceAfterOp <= balanceBeforeOp + allowedDiff);
}

// Proves that a call to a non-mint operation won't increase the user's balance of the actual 
//  debt tokens (i.e. it's scaled balance)
rule nonMintFunctionCantIncreaseScaledBalance(method f) 
    filtered { f-> f.selector != sig:mint(address, address, uint256, uint256).selector } {
    address user;
    uint256 ts1;
    uint256 ts2;
    require(ts2 >= ts1);
    require((indexAtTimestamp(ts1) >= ray()) && 
            (indexAtTimestamp(ts2) >= indexAtTimestamp(ts1)));

    require(getUserCurrentIndex(user) == indexAtTimestamp(ts1));
    requireInvariant discountCantExceed100Percent(user);
    uint256 balanceBeforeOp = scaledBalanceOf(user);

    env e = envAtTimestamp(ts2);
    calldataarg args;
    f(e,args);
    uint256 balanceAfterOp = scaledBalanceOf(user);

    assert(balanceAfterOp <= balanceBeforeOp);
}

// Proves that debt tokens aren't transferable
rule debtTokenIsNotTransferable(method f) {
    address user1;
    address user2;
    require(user1 != user2);
    uint256 scaledBalanceBefore1 = scaledBalanceOf(user1);
    uint256 scaledBalanceBefore2 = scaledBalanceOf(user2);

    env e;
    calldataarg args;
    f(e,args);
    uint256 scaledBalanceAfter1 = scaledBalanceOf(user1);
    uint256 scaledBalanceAfter2 = scaledBalanceOf(user2);

    assert(scaledBalanceBefore1 + scaledBalanceBefore2 == scaledBalanceAfter1 + scaledBalanceAfter2 
        => (scaledBalanceBefore1 == scaledBalanceAfter1 && scaledBalanceBefore2 == scaledBalanceAfter2)
    );
}

// Proves that only burn/mint/rebalanceUserDiscountPercent/updateDiscountDistribution 
//  can modify user's scaled balance
rule onlyCertainFunctionsCanModifyScaledBalance(method f) {
    address user;
    uint256 ts1;
    uint256 ts2;
    require(ts2 >= ts1);
    require((indexAtTimestamp(ts1) >= ray()) && (indexAtTimestamp(ts2) >= indexAtTimestamp(ts1)));

    require(getUserCurrentIndex(user) == indexAtTimestamp(ts1));
    requireInvariant discountCantExceed100Percent(user);
    uint256 balanceBeforeOp = scaledBalanceOf(user);

    env e = envAtTimestamp(ts2);
    calldataarg args;
    f(e,args);

    uint256 balanceAfterOp = scaledBalanceOf(user);
    assert(balanceAfterOp != balanceBeforeOp => (
        (f.selector == sig:mint(address ,address ,uint256 ,uint256).selector) ||
        (f.selector == sig:burn(address ,uint256 ,uint256).selector) ||
        (f.selector == sig:updateDiscountDistribution(address ,address ,uint256 ,uint256 ,uint256).selector) ||
        (f.selector == sig:rebalanceUserDiscountPercent(address).selector)
    ));
}

// Proves that only a call to decreaseBalanceFromInterest will decrease the user's 
//  accumulated interest listing.
rule userAccumulatedDebtInterestWontDecrease(method f) {
    address user;
    uint256 ts1;
    uint256 ts2;
    require(ts2 >= ts1);
    require((indexAtTimestamp(ts1) >= ray()) && (indexAtTimestamp(ts2) >= indexAtTimestamp(ts1)));

    require(getUserCurrentIndex(user) == indexAtTimestamp(ts1));
    requireInvariant discountCantExceed100Percent(user);
    uint256 initAccumulatedInterest = getUserAccumulatedDebtInterest(user);
    
    env e2 = envAtTimestamp(ts2);
    calldataarg args;
    f(e2,args);
    
    uint256 finAccumulatedInterest = getUserAccumulatedDebtInterest(user);
    assert(initAccumulatedInterest > finAccumulatedInterest => f.selector 
        == sig:decreaseBalanceFromInterest(address, uint256).selector);
}

// Proves that a user can't nullify its debt without calling burn
rule userCantNullifyItsDebt(method f) {
    address user;
    env e;
    env e2;
    require(getUserCurrentIndex(user) == indexAtTimestamp(e.block.timestamp));
    requireInvariant discountCantExceed100Percent(user);
    uint256 balanceBeforeOp = balanceOf(e, user);
    
    calldataarg args;
    require e2.block.timestamp == e.block.timestamp;
    f(e2,args);
    
    uint256 balanceAfterOp = balanceOf(e, user);
    assert((balanceBeforeOp > 0 && balanceAfterOp == 0) 
        => (f.selector == sig:burn(address, uint256, uint256).selector));
}

//
// Integrity of mint()
//

// Proves that after calling mint, the user's discount rate is up to date
rule integrityOfMintUpdateDiscountRate() {
    address user1;
    address user2;
    env e;
    uint256 amount;
    uint256 index = indexAtTimestamp(e.block.timestamp);

    mint(e, user1, user2, amount, index);
    
    uint256 debtBalance = balanceOf(e, user2);
    uint256 discountBalance = getBalanceOfDiscountToken(e, user2);
    uint256 discountRate = getUserDiscountRate(user2);
    assert(discStrategy.calculateDiscountRate(debtBalance, discountBalance) == discountRate);
}

// Proves the after calling mint, the user's state is updated with the recent index value
rule integrityOfMintUpdateIndex() {
    address user1;
    address user2;
    env e;
    uint256 amount;
    uint256 index;
    
    mint(e, user1, user2, amount, index);

    assert(getUserCurrentIndex(user2) == index);
}

// Proves that on a fixed index calling mint(user, amount) will increase the user's scaled balance 
//  by amount. 
rule integrityOfMintUpdateScaledBalanceFixedIndex() {
    address user;
    env e;
    uint256 balanceBefore = balanceOf(e, user);
    uint256 scaledBalanceBefore = scaledBalanceOf(user);
    address caller;
    uint256 amount;
    uint256 index = indexAtTimestamp(e.block.timestamp);
    require(getUserCurrentIndex(user) == index);

    mint(e, caller, user, amount, index);

    uint256 balanceAfter = balanceOf(e, user);
    mathint scaledBalanceAfter = scaledBalanceOf(user);
    mathint scaledAmount = rayDivCVL(amount, index);

    assert(scaledBalanceAfter == scaledBalanceBefore + scaledAmount);
}

// Proves that mint can't effect other user's scaled balance
rule integrityOfMint_userIsolation() {
    address otherUser;
    uint256 scaledBalanceBefore = scaledBalanceOf(otherUser);
    env e;
    uint256 amount;
    uint256 index;
    address targetUser;
    address caller;

    mint(e, caller, targetUser, amount, index);
    
    uint256 scaledBalanceAfter = scaledBalanceOf(otherUser);
    assert(scaledBalanceAfter != scaledBalanceBefore => otherUser == targetUser);
}

// Proves that when calling mint, the user's balance (as reported by GhoVariableDebtToken::balanceOf) 
//  will increase if the call is made on bahalf of the user.
rule onlyMintForUserCanIncreaseUsersBalance() {
    address user1;
    env e;
    require(getUserCurrentIndex(user1) == indexAtTimestamp(e.block.timestamp));
    
    uint256 finBalanceBeforeMint = balanceOf(e, user1);
    uint256 amount;
    mint(e,user1, user1, amount, indexAtTimestamp(e.block.timestamp));
    uint256 finBalanceAfterMint = balanceOf(e, user1);

    assert(finBalanceAfterMint != finBalanceBeforeMint);
}

// Checking atoken alone (from VariableDebtToken.spec)
rule integrityMintAtoken(address a, uint256 x) {
    env e;
    address delegatedUser;
    uint256 index = indexAtTimestamp(e.block.timestamp);
    uint256 underlyingBalanceBefore = balanceOf(e, a);
    uint256 atokenBalanceBefore = scaledBalanceOf(a);
    uint256 totalATokenSupplyBefore = scaledTotalSupply(e);
    mint(e, delegatedUser, a, x, index);
    
    uint256 underlyingBalanceAfter = balanceOf(e, a);
    uint256 atokenBalanceAfter = scaledBalanceOf(a);
    uint256 totalATokenSupplyAfter = scaledTotalSupply(e);

    assert(atokenBalanceAfter - atokenBalanceBefore 
        == totalATokenSupplyAfter - totalATokenSupplyBefore);
    //assert totalATokenSupplyAfter > totalATokenSupplyBefore;
    //assert bounded_error_eq(underlyingBalanceAfter, underlyingBalanceBefore+x, 1, index);
    // assert balanceAfter == balancebefore+x;
}

//
// Integrity of burn()
//

// Proves that after calling burn, the user's discount rate is up to date
rule integrityOfBurnUpdateDiscountRate() {
    address user;
    env e;
    uint256 amount;
    uint256 index = indexAtTimestamp(e.block.timestamp);
    
    burn(e, user, amount, index);
    
    uint256 debtBalance = balanceOf(e, user);
    uint256 discountBalance = getBalanceOfDiscountToken(e, user);
    uint256 discountRate = getUserDiscountRate(user);

    assert(discStrategy.calculateDiscountRate(debtBalance, discountBalance) == discountRate);
}

// Proves the after calling burn, the user's state is updated with the recent index value
rule integrityOfBurnUpdateIndex() {
    address user;
    env e;
    uint256 amount;
    uint256 index;
    
    burn(e, user, amount, index);

    assert(getUserCurrentIndex(user) == index);
}

// Proves that calling burn with 0 amount doesn't change the user's balance (from VariableDebtToken.spec)
rule burnZeroDoesntChangeBalance(address u, uint256 index) {
    env e;
    uint256 balanceBefore = balanceOf(e, u);
    
    burn@withrevert(e, u, 0, index);

    uint256 balanceAfter = balanceOf(e, u);
    assert balanceBefore == balanceAfter;
}

// Proves a concrete case of repaying the full debt that ends with a zero balance
rule integrityOfBurnFullRepayConcrete() {
    env e;
    address user;
    uint256 currentDebt = balanceOf(e, user);
    uint256 index = indexAtTimestamp(e.block.timestamp);

    // handle timeouts
    require(getUserCurrentIndex(user) == ray());
    require(to_mathint(index) == 2*ray());
    require(to_mathint(scaledBalanceOf(user)) == 4*ray());
    
    burn(e, user, currentDebt, index);

    uint256 scaled = scaledBalanceOf(user);
    assert(scaled == 0);
}

// Proves that burn can't effect other user's scaled balance
rule integrityOfBurnUserIsolation() {
    address otherUser;
    uint256 scaledBalanceBefore = scaledBalanceOf(otherUser);
    env e;
    uint256 amount;
    uint256 index;
    address targetUser;
    
    burn(e,targetUser, amount, index);

    uint256 scaledBalanceAfter = scaledBalanceOf(otherUser);
    assert(scaledBalanceAfter != scaledBalanceBefore => otherUser == targetUser);
}

//
// integrity of updateDiscountDistribution()
// 

// Proves the after calling updateDiscountDistribution, the user's state is updated with the 
//  recent index value
rule integrityOfUpdateDiscountDistributionUpdateIndex() {
    address sender;
    address recipient;
    uint256 senderDiscountTokenBalance;
    uint256 recipientDiscountTokenBalance;
    env e;
    uint256 amount;
    uint256 index = indexAtTimestamp(e.block.timestamp);
    
    updateDiscountDistribution(e, sender, recipient, senderDiscountTokenBalance, 
        recipientDiscountTokenBalance, amount);
    
    assert(scaledBalanceOf(sender) > 0 => getUserCurrentIndex(sender) == index);
    assert(scaledBalanceOf(recipient) > 0 => getUserCurrentIndex(recipient) == index);
}

// Proves that updateDiscountDistribution can't effect other user's scaled balance
rule integrityOfUpdateDiscountDistributionUserIsolation() {
    address otherUser;
    uint256 scaledBalanceBefore = scaledBalanceOf(otherUser);

    env e;
    uint256 amount;
    uint256 senderDiscountTokenBalance;
    uint256 recipientDiscountTokenBalance;
    address sender;
    address recipient;
    updateDiscountDistribution(e, sender, recipient, senderDiscountTokenBalance, 
        recipientDiscountTokenBalance, amount);
    
    uint256 scaledBalanceAfter = scaledBalanceOf(otherUser);
    assert(scaledBalanceAfter != scaledBalanceBefore => 
        (otherUser == sender || otherUser == recipient)
    );
}

//
// Integrity of rebalanceUserDiscountPercent()
//

// Proves that after calling rebalanceUserDiscountPercent, the user's discount rate is up to date
rule integrityOfRebalanceUserDiscountPercentUpdateDiscountRate() {
    address user;
    env e;

    rebalanceUserDiscountPercent(e, user);
    
    assert(discStrategy.calculateDiscountRate(balanceOf(e, user), getBalanceOfDiscountToken(e, user)) 
        == getUserDiscountRate(user));
}

// Proves that after calling rebalanceUserDiscountPercent, the user's state is updated with the 
//  recent index value
rule integrityOfRebalanceUserDiscountPercentUpdateIndex() {
    address user;
    env e;
    
    rebalanceUserDiscountPercent(e, user);

    uint256 index = indexAtTimestamp(e.block.timestamp);
    assert(getUserCurrentIndex(user) == index);
}

// Proves that rebalanceUserDiscountPercent can't effect other user's scaled balance
rule integrityOfRebalanceUserDiscountPercentUserIsolation() {
    address otherUser;
    uint256 scaledBalanceBefore = scaledBalanceOf(otherUser);
    env e;
    address targetUser;

    rebalanceUserDiscountPercent(e, targetUser);
    
    uint256 scaledBalanceAfter = scaledBalanceOf(otherUser);
    assert(scaledBalanceAfter != scaledBalanceBefore => otherUser == targetUser);
}

//
// Integrity of balanceOf()
//

// Proves that a user with 100% discounts has a fixed balance over time
rule integrityOfBalanceOfFullDiscount() {
    address user;
    uint256 fullDiscountRate = 10000; //100%
    require(getUserDiscountRate(user) == fullDiscountRate);
    env e1;
    env e2;
    uint256 index1 = indexAtTimestamp(e1.block.timestamp);
    uint256 index2 = indexAtTimestamp(e2.block.timestamp);

    assert(balanceOf(e1, user) == balanceOf(e2, user));
}

// Proves that a user's balance, with no discount, is equal to rayMul(scaledBalance, current index)
rule integrityOfBalanceOfNoDiscount() {
    address user;
    require(getUserDiscountRate(user) == 0);
    env e;
    uint256 scaledBalance = scaledBalanceOf(user);
    uint256 currentIndex = indexAtTimestamp(e.block.timestamp);
    mathint expectedBalance = rayMulCVL(scaledBalance, currentIndex);

    assert(to_mathint(balanceOf(e, user)) == expectedBalance);
}

// Proves the a user with zero scaled balance has a zero balance
rule integrityOfBalanceOfZeroScaledBalance() {
    address user;
    env e;
    uint256 scaledBalance = scaledBalanceOf(user);
    require(scaledBalance == 0);

    assert(balanceOf(e, user) == 0);
}

rule burnAllDebtReturnsZeroDebt(address user) {
    env e;
    uint256 _variableDebt = balanceOf(e, user);
    
    burn(e, user, _variableDebt, indexAtTimestamp(e.block.timestamp));
    
    uint256 variableDebt_ = balanceOf(e, user);
    assert(variableDebt_ == 0);
}
