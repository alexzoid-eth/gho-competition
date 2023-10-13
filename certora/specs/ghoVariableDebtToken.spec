import "./methods/GhoTokenHelperMethods.spec";
import "./methods/ScaledBalanceTokenBaseMethods.spec";
import "./methods/EIP712BaseMethods.spec";
import "./helpers/VersionedInitializable.spec";
import "./helpers/EIP712Base.spec";
import "./helpers/IncentivizedERC20.spec";

using GhoDiscountRateStrategy as _GhoDiscountRateStrategy;
using DummyERC20WithTimedBalanceOf as _DummyERC20WithTimedBalanceOf;
using DummyPool as _DummyPool;

///////////////// METHODS //////////////////////

methods{
    
    //
    // Current contract
    //

    // GhoVariableDebtTokenHarness
    function getUserCurrentIndex(address user) external returns (uint256) envfree;
    function getUserDiscountRate(address user) external returns (uint256) envfree;
    function getUserAccumulatedDebtInterest(address user) external returns (uint256) envfree;
    function scaledBalanceOfToBalanceOf(uint256 bal) internal returns (uint256);
    function getBalanceOfDiscountToken(address user) external returns (uint256);
    function rayMul(uint256 x, uint256 y) external returns (uint256) envfree;
    function rayDiv(uint256 x, uint256 y) external returns (uint256) envfree;
    // added
    function getRevisionHarness() external returns (uint256) envfree;
    function getPoolAddress() external returns (address) envfree;
    function calculateDomainSeparator() external returns (bytes32);
    function isPoolAdmin(address account) external returns (bool);
    function setName1() external envfree;
    function setName2() external envfree;

    // GhoVariableDebtToken
    function DEBT_TOKEN_REVISION() external returns (uint256) envfree;
    function initialize(address initializingPool, address underlyingAsset, address incentivesController,
        uint8 debtTokenDecimals, string calldata debtTokenName, string calldata debtTokenSymbol,
        bytes calldata params) external;
    function getRevision() internal returns (uint256);
    function balanceOf(address user) internal returns (uint256);
    function mint(address user, address onBehalfOf, uint256 amount, uint256 index) external returns (bool, uint256);
    function burn(address from, uint256 amount, uint256 index) external returns (uint256);
    function totalSupply() internal returns (uint256);
    function _EIP712BaseId() internal returns (string memory);
    function transfer(address, uint256) external returns (bool) envfree;
    function allowance(address, address) external returns (uint256) envfree;
    function approve(address, uint256) external returns (bool) envfree;
    function transferFrom(address, address, uint256) external returns (bool) envfree;
    function increaseAllowance(address, uint256) external returns (bool) envfree;
    function decreaseAllowance(address, uint256) external returns (bool) envfree;
    function UNDERLYING_ASSET_ADDRESS() external returns (address) envfree;
    function setAToken(address ghoAToken) external;
    function getAToken() external returns (address) envfree;
    function updateDiscountRateStrategy(address newDiscountRateStrategy) external;
    function getDiscountRateStrategy() external returns (address) envfree;
    function updateDiscountToken(address newDiscountToken) external;
    function getDiscountToken() external returns (address) envfree;
    function updateDiscountDistribution(address sender, address recipient, uint256 senderDiscountTokenBalance, 
        uint256 recipientDiscountTokenBalance, uint256 amount) external;
    function getDiscountPercent(address user) external returns (uint256) envfree;
    function getBalanceFromInterest(address user) external returns (uint256) envfree;
    function decreaseBalanceFromInterest(address user, uint256 amount) external;
    function rebalanceUserDiscountPercent(address user) external;
    function _mintScaled(address caller, address onBehalfOf, uint256 amount, uint256 index) internal returns (bool);
    function _burnScaled(address user, address target, uint256 amount, uint256 index) internal;
    function _accrueDebtOnAction(address user, uint256 previousScaledBalance, 
        uint256 discountPercent, uint256 index) internal returns (uint256, uint256);
    function _refreshDiscountPercent(address user, uint256 balance, uint256 discountTokenBalance, 
        uint256 previousDiscountPercent) internal;

    //
    // External calls
    //

    // DummyERC20WithTimedBalanceOf (linked to _discountToken) represent a random balance per block 
    function _DummyERC20WithTimedBalanceOf.balanceOf(address user) external returns (uint256) with (env e) 
        => balanceOfDiscountTokenAtTimestamp(user, e.block.timestamp) ;

    // DummyPool (linked to POOL), represent a random index per block
    function _DummyPool.getReserveNormalizedVariableDebt(address asset) external returns (uint256) with (env e) 
        => indexAtTimestamp(e.block.timestamp);

    // GhoDiscountRateStrategy
    function _GhoDiscountRateStrategy.calculateDiscountRate(uint256, uint256) external returns (uint256) envfree;

    // PoolAddressesProvider
    function _.getACLManager() external => CONSTANT;

    // ACLManager
    function _.isPoolAdmin(address) external => CONSTANT;

    // Possibility of run-time optimization
    function _.rayMul(uint256 a, uint256 b) internal => rayMulUint256(a, b) expect uint256 ALL;
    function _.rayDiv(uint256 a, uint256 b) internal => rayDivUint256(a, b) expect uint256 ALL;
}

///////////////// DEFINITIONS /////////////////////

definition UINT128_MAX() returns uint256 = 0xffffffffffffffffffffffffffffffff;
definition UINT256_MAX() returns uint256 = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;

definition MAX_DISCOUNT() returns uint256 = 10000; // equals to 100% discount, in points

definition RAY() returns uint256 =     1000000000000000000000000000; // 10^27
definition HALF_RAY() returns uint256 = 500000000000000000000000000; 

definition DISALLOWED_FUNCTIONS(method f) returns bool = 
    f.selector == sig:transfer(address, uint256).selector ||
    f.selector == sig:allowance(address, address).selector ||
    f.selector == sig:approve(address, uint256).selector ||
    f.selector == sig:transferFrom(address, address, uint256).selector ||
    f.selector == sig:increaseAllowance(address, uint256).selector ||
    f.selector == sig:decreaseAllowance(address, uint256).selector;

definition VIEW_FUNCTIONS(method f) returns bool = f.isView || f.isPure;

definition HARNESS_FUNCTIONS(method f) returns bool = 
    f.selector == sig:getUserCurrentIndex(address).selector
    || f.selector == sig:getUserDiscountRate(address).selector
    || f.selector == sig:getUserAccumulatedDebtInterest(address).selector
    || f.selector == sig:scaledBalanceOfToBalanceOf(uint256).selector
    || f.selector == sig:getBalanceOfDiscountToken(address).selector
    || f.selector == sig:rayMul(uint256, uint256).selector
    || f.selector == sig:rayDiv(uint256, uint256).selector
    || f.selector == sig:getRevisionHarness().selector
    || f.selector == sig:getPoolAddress().selector
    || f.selector == sig:calculateDomainSeparator().selector
    || f.selector == sig:isPoolAdmin(address).selector
    || f.selector == sig:setName1().selector
    || f.selector == sig:setName2().selector
    ;

definition EXCLUDED_FUNCTIONS(method f) returns bool = 
    DISALLOWED_FUNCTIONS(f) || HARNESS_FUNCTIONS(f) || VIEW_FUNCTIONS(f);

////////////////// FUNCTIONS //////////////////////

function setUp() {

    // TODO: Cannot make work dynamically linking, several rules are violated
    // Don't statically link variables that could be changed externally

    // "GhoVariableDebtTokenHarness:_discountToken=DummyERC20WithTimedBalanceOf"
    // require(ghostDiscountToken == _DummyERC20WithTimedBalanceOf);

    // "GhoVariableDebtTokenHarness:_discountRateStrategy=GhoDiscountRateStrategy"
    // require(ghostDiscountRateStrategy == _GhoDiscountRateStrategy);
}

//
// CVL implementation of rayMul
//

function rayMulCVL(uint256 a, uint256 b) returns mathint {
    return ((a * b + (RAY() / 2)) / RAY());
}

function rayDivCVL(uint256 a, uint256 b) returns mathint {
    return ((a * RAY() + (b / 2)) / b);
}

function rayMulUint256(uint256 a, uint256 b) returns uint256 {
    // to avoid overflow, a <= (type(uint256).max - HALF_RAY) / b
    require(b != 0 && a <= require_uint256((UINT256_MAX() - HALF_RAY()) / b));
    return require_uint256((a * b + (RAY() / 2)) / RAY());
}

function rayDivUint256(uint256 a, uint256 b) returns uint256 {
    // to avoid overflow, a <= (type(uint256).max - halfB) / RAYs
    require(b != 0 && a <= require_uint256((UINT256_MAX() - (b / 2)) / RAY()));
    return require_uint256((a * RAY() + (b / 2)) / b);
}

// Query index_ghost for the index value at the input timestamp
function indexAtTimestamp(uint256 timestamp) returns uint256 {
    // require(index_ghost[timestamp] >= RAY());
    return index_ghost[timestamp];
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

ghost mapping(address => mapping (uint256 => uint256)) discount_ghost;

ghost mapping(uint256 => uint256) index_ghost {
    axiom forall uint256 timestamp. (index_ghost[timestamp] >= RAY() 
        && index_ghost[timestamp] <= UINT128_MAX());
}

//
// Ghost copy of `_ghoAToken`
//

ghost address ghostGhoAToken {
    init_state axiom ghostGhoAToken == 0;
}

hook Sload address val currentContract._ghoAToken STORAGE {
    require(ghostGhoAToken == val);
}

hook Sstore currentContract._ghoAToken address val STORAGE {
    ghostGhoAToken = val;
}

//
// Ghost copy of `_discountToken`
//

ghost address ghostDiscountToken {
    init_state axiom ghostDiscountToken == 0;
}

hook Sload address val currentContract._discountToken STORAGE {
    require(ghostDiscountToken == val);
}

hook Sstore currentContract._discountToken address val STORAGE {
    ghostDiscountToken = val;
}

//
// Ghost copy of `_discountRateStrategy`
//

ghost address ghostDiscountRateStrategy {
    init_state axiom ghostDiscountRateStrategy == 0;
}

hook Sload address val currentContract._discountRateStrategy STORAGE {
    require(ghostDiscountRateStrategy == val);
}

hook Sstore currentContract._discountRateStrategy address val STORAGE {
    ghostDiscountRateStrategy = val;
}

//
// Ghost copy of `mapping(address => GhoUserState.accumulatedDebtInterest)`
//

ghost mapping (address => uint128) ghostAccumulatedDebtInterest {
    init_state axiom forall address i. ghostAccumulatedDebtInterest[i] == 0;
}

hook Sload uint128 val currentContract._ghoUserState[KEY address i].(offset 0) STORAGE {
    require(ghostAccumulatedDebtInterest[i] == val);
}

hook Sstore currentContract._ghoUserState[KEY address i].(offset 0) uint128 val STORAGE {
    ghostAccumulatedDebtInterest[i] = val;
}

//
// Ghost copy of `mapping(address => GhoUserState.discountPercent)`
//

ghost mapping (address => uint16) ghostDiscountPercent {
    init_state axiom forall address i. ghostDiscountPercent[i] == 0;
}

hook Sload uint16 val currentContract._ghoUserState[KEY address i].(offset 16) STORAGE {
    require(ghostDiscountPercent[i] == val);
}

hook Sstore currentContract._ghoUserState[KEY address i].(offset 16) uint16 val STORAGE {
    ghostDiscountPercent[i] = val;
}

//
// Ghost copy of `mapping(address => mapping(address => uint256)) _borrowAllowances`
//

ghost mapping(address => mapping(address => uint256)) ghostBorrowAllowances {
    init_state axiom forall address key. forall address val. ghostBorrowAllowances[key][val] == 0;
}

hook Sstore currentContract._borrowAllowances[KEY address key][KEY address val] uint256 amount STORAGE {
    ghostBorrowAllowances[key][val] = amount;
}

hook Sload uint256 amount currentContract._borrowAllowances[KEY address key][KEY address val] STORAGE {
    require(ghostBorrowAllowances[key][val] == amount);
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
// Ghost copy of `mapping(address => UserState.balance)`
//

ghost mapping (address => uint128) ghostUserStateBalance {
    init_state axiom forall address i. ghostUserStateBalance[i] == 0;
}

hook Sload uint128 val currentContract._userState[KEY address i].(offset 0) STORAGE {
    require(ghostUserStateBalance[i] == val);
}

hook Sstore currentContract._userState[KEY address i].(offset 0) uint128 val (uint128 oldVal) STORAGE {
    ghostUserStateBalance[i] = val;
}

//
// Ghost copy of `mapping(address => UserState.additionalData)`
//

ghost mapping (address => uint256) ghostUserStateAdditionalData {
    init_state axiom forall address user. forall uint256 timestamp. (ghostUserStateAdditionalData[user] >= RAY() 
        && ghostUserStateAdditionalData[user] <= index_ghost[timestamp]);
}

hook Sload uint128 val currentContract._userState[KEY address i].(offset 16) STORAGE {
    require(require_uint128(ghostUserStateAdditionalData[i]) == val);
}

hook Sstore currentContract._userState[KEY address i].(offset 16) uint128 val STORAGE {
    ghostUserStateAdditionalData[i] = val;
}

///////////////// PROPERTIES //////////////////////

// At any point in time, the user's discount rate isn't larger than 100%
invariant discountCantExceed100Percent(address user)
    // changed from `getUserDiscountRate(user)` to `ghostDiscountPercent[user]`
    ghostDiscountPercent[user] <= assert_uint16(MAX_DISCOUNT()) filtered { f -> !EXCLUDED_FUNCTIONS(f) } { // added
        preserved updateDiscountDistribution(address sender,address recipient,uint256 senderDiscountTokenBalance,uint256 recipientDiscountTokenBalance,uint256 amount) with (env e) {
            require(indexAtTimestamp(e.block.timestamp) >= RAY());
        }
    }

// Ensuring that the defined disallowed functions revert in any case (from VariableDebtToken.spec)
rule disallowedFunctionalities(method f, env e, calldataarg args) filtered { f -> DISALLOWED_FUNCTIONS(f) } {
    f@withrevert(e, args);
    assert(lastReverted);
}

// Proves that the user's balance of debt token (as reported by GhoVariableDebtToken::balanceOf) 
//  can't increase by calling any external non-mint function.
rule nonMintFunctionCantIncreaseBalance(method f) 
    filtered { f-> f.selector != sig:mint(address, address, uint256, uint256).selector 
        && !EXCLUDED_FUNCTIONS(f) } { // Added

    address user;
    uint256 ts1;
    uint256 ts2;
    require(ts2 >= ts1);
    // Forcing the index to be fixed (otherwise the rule times out). For non-fixed index replace `==` with `>=`
    require((indexAtTimestamp(ts1) >= RAY()) && 
            (indexAtTimestamp(ts2) == indexAtTimestamp(ts1)));
    require(getUserCurrentIndex(user) == indexAtTimestamp(ts1));
    requireInvariant discountCantExceed100Percent(user);

    env e = envAtTimestamp(ts2);
    uint256 balanceBeforeOp = balanceOf(e, user);
    calldataarg args;
    f(e,args);

    mathint balanceAfterOp = balanceOf(e, user);
    mathint allowedDiff = indexAtTimestamp(ts2) / RAY();

    // assert(balanceAfterOp != balanceBeforeOp + allowedDiff + 1);
    assert(balanceAfterOp <= balanceBeforeOp + allowedDiff);
}

// Proves that a call to a non-mint operation won't increase the user's balance of the actual 
//  debt tokens (i.e. it's scaled balance)
rule nonMintFunctionCantIncreaseScaledBalance(method f) 
    filtered { f-> f.selector != sig:mint(address, address, uint256, uint256).selector 
        && !EXCLUDED_FUNCTIONS(f) } {

    address user;
    uint256 ts1;
    uint256 ts2;
    require(ts2 >= ts1);
    require((indexAtTimestamp(ts1) >= RAY()) && 
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
rule debtTokenIsNotTransferable(method f) filtered { f-> !EXCLUDED_FUNCTIONS(f) } { // added
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
rule onlyCertainFunctionsCanModifyScaledBalance(method f) filtered { f-> !EXCLUDED_FUNCTIONS(f) } { // added
    address user;
    uint256 ts1;
    uint256 ts2;
    require(ts2 >= ts1);
    require((indexAtTimestamp(ts1) >= RAY()) && (indexAtTimestamp(ts2) >= indexAtTimestamp(ts1)));

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
rule userAccumulatedDebtInterestWontDecrease(method f) filtered { f-> !EXCLUDED_FUNCTIONS(f) } { // added
    address user;
    uint256 ts1;
    uint256 ts2;
    require(ts2 >= ts1);
    require((indexAtTimestamp(ts1) >= RAY()) && (indexAtTimestamp(ts2) >= indexAtTimestamp(ts1)));

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
rule userCantNullifyItsDebt(method f) filtered { f-> !EXCLUDED_FUNCTIONS(f) } { // added

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
rule integrityOfMint_updateDiscountRate() {

    address user1;
    address user2;
    env e;
    uint256 amount;
    uint256 index = indexAtTimestamp(e.block.timestamp);

    mint(e, user1, user2, amount, index);
    
    uint256 debtBalance = balanceOf(e, user2);
    uint256 discountBalance = getBalanceOfDiscountToken(e, user2);
    uint256 discountRate = getUserDiscountRate(user2);
    assert(_GhoDiscountRateStrategy.calculateDiscountRate(debtBalance, discountBalance) == discountRate);
}

// Proves the after calling mint, the user's state is updated with the recent index value
rule integrityOfMint_updateIndex() {
    address user1;
    address user2;
    env e;
    uint256 amount;
    uint256 index;
    
    mint(e, user1, user2, amount, index);

    assert(getUserCurrentIndex(user2) == index);
}

// Proves that on a fixed index calling mint(user, amount) will increase the user's scaled balance by amount. 
rule integrityOfMint_updateScaledBalance_fixedIndex() {
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
    mint(e, user1, user1, amount, indexAtTimestamp(e.block.timestamp));
    uint256 finBalanceAfterMint = balanceOf(e, user1);

    assert(finBalanceAfterMint != finBalanceBeforeMint);
}

// Checking atoken alone (from VariableDebtToken.spec)
rule integrityMint_atoken(address a, uint256 x) {
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
rule integrityOfBurn_updateDiscountRate() {

    address user;
    env e;
    uint256 amount;
    uint256 index = indexAtTimestamp(e.block.timestamp);
    
    burn(e, user, amount, index);
    
    uint256 debtBalance = balanceOf(e, user);
    uint256 discountBalance = getBalanceOfDiscountToken(e, user);
    uint256 discountRate = getUserDiscountRate(user);

    assert(_GhoDiscountRateStrategy.calculateDiscountRate(debtBalance, discountBalance) == discountRate);
}

// Proves the after calling burn, the user's state is updated with the recent index value
rule integrityOfBurn_updateIndex() {
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
rule integrityOfBurn_fullRepay_concrete() {

    env e;
    address user;
    uint256 currentDebt = balanceOf(e, user);
    uint256 index = indexAtTimestamp(e.block.timestamp);

    // handle timeouts
    require(getUserCurrentIndex(user) == RAY());
    require(to_mathint(index) == 2*RAY());
    require(to_mathint(scaledBalanceOf(user)) == 4*RAY());
    
    burn(e, user, currentDebt, index);

    uint256 scaled = scaledBalanceOf(user);
    assert(scaled == 0);
}

// Proves that burn can't effect other user's scaled balance
rule integrityOfBurn_userIsolation() {
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

// Proves the after calling updateDiscountDistribution, the user's state is updated with the recent index value
rule integrityOfUpdateDiscountDistribution_updateIndex() {

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
rule integrityOfUpdateDiscountDistribution_userIsolation() {
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
rule integrityOfRebalanceUserDiscountPercent_updateDiscountRate() {

    address user;
    env e;

    rebalanceUserDiscountPercent(e, user);
    
    assert(_GhoDiscountRateStrategy.calculateDiscountRate(balanceOf(e, user), getBalanceOfDiscountToken(e, user)) 
        == getUserDiscountRate(user));
}

// Proves that after calling rebalanceUserDiscountPercent, the user's state is updated with the recent index value
rule integrityOfRebalanceUserDiscountPercent_updateIndex() {
    
    address user;
    env e;

    rebalanceUserDiscountPercent(e, user);

    uint256 index = indexAtTimestamp(e.block.timestamp);
    assert(getUserCurrentIndex(user) == index);
}

// Proves that rebalanceUserDiscountPercent can't effect other user's scaled balance
rule integrityOfRebalanceUserDiscountPercent_userIsolation() {
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
rule integrityOfBalanceOf_fullDiscount(env e1, env e2, address user) {
    require(getUserDiscountRate(user) == MAX_DISCOUNT()); //100%
    assert(balanceOf(e1, user) == balanceOf(e2, user));
}

// Proves that a user's balance, with no discount, is equal to rayMul(scaledBalance, current index)
rule integrityOfBalanceOf_noDiscount() {

    address user;
    require(getUserDiscountRate(user) == 0);
    env e;
    uint256 scaledBalance = scaledBalanceOf(user);
    uint256 currentIndex = indexAtTimestamp(e.block.timestamp);
    mathint expectedBalance = rayMulCVL(scaledBalance, currentIndex);

    assert(to_mathint(balanceOf(e, user)) == expectedBalance);
}

// Proves the a user with zero scaled balance has a zero balance
rule integrityOfBalanceOf_zeroScaledBalance() {
    address user;
    env e;
    uint256 scaledBalance = scaledBalanceOf(user);
    require(scaledBalance == 0);

    assert(balanceOf(e, user) == 0);
}

// Proves the balance will be zero when burn whole dept
rule burnAllDebtReturnsZeroDebt(address user) {

    env e;
    uint256 _variableDebt = balanceOf(e, user);
    
    burn(e, user, _variableDebt, indexAtTimestamp(e.block.timestamp));
    
    uint256 variableDebt_ = balanceOf(e, user);
    assert(variableDebt_ == 0);
}

///////////////// ADDED PROPERTIES //////////////////////

// User_index >= RAY() and user_index <= current_index
invariant userIndexSetup(env eInv, address user) ghostUserStateAdditionalData[user] >= RAY()
    && ghostUserStateAdditionalData[user] <= index_ghost[eInv.block.timestamp]
    filtered { f -> !EXCLUDED_FUNCTIONS(f) } {
        preserved with (env eFunc) {
            // Use the same timestamp in env and invariantEnv
            require(eInv.block.timestamp == eFunc.block.timestamp);
        }
    }

// [1] Initialize could be executed once (from VersionedInitializable.spec)
use rule initializeCouldBeExecutedOnce;

// [2] Could be initialized with specific pool address only
rule initializedWithSpecificPoolAddressOnly(
    env e, 
    address initializingPool, 
    address underlyingAsset, 
    address incentivesController,
    uint8 debtTokenDecimals, 
    string debtTokenName, 
    string debtTokenSymbol,
    bytes params
    ) {
    
    initialize(e, initializingPool, underlyingAsset, incentivesController, 
        debtTokenDecimals, debtTokenName, debtTokenSymbol, params);
    bool reverted = lastReverted;

    assert(initializingPool != getPoolAddress() => reverted);
}

// [3-5] Initialize set initial params correctly
rule initializeSetInitialParamsCorrectly(
    env e, 
    address initializingPool, 
    address underlyingAsset, 
    address incentivesController,
    uint8 debtTokenDecimals, 
    string debtTokenName, 
    string debtTokenSymbol,
    bytes params
) {
    require(debtTokenName.length < 16);
    require(debtTokenSymbol.length < 16);

    initialize(e, initializingPool, underlyingAsset, incentivesController, 
        debtTokenDecimals, debtTokenName, debtTokenSymbol, params);

    string n = name(e);
    string s = symbol();
    uint256 ni;
    require(ni < n.length && ni < debtTokenName.length);
    uint256 si;
    require(si < s.length && si < debtTokenSymbol.length);

    assert(
        underlyingAsset == UNDERLYING_ASSET_ADDRESS()
        && incentivesController == getIncentivesController()
        && debtTokenDecimals == decimals()
        && debtTokenName.length == n.length
        && debtTokenSymbol.length == s.length
        && DOMAIN_SEPARATOR(e) == calculateDomainSeparator(e)
    );
}

// [6] Domain separator depends on token name (from EIP712Base.spec)
use rule domainSeparatorDepensOnName;

// Viewers integrity
rule viewersIntegrity(env e, address user) {
    assert(
        getRevisionHarness() == DEBT_TOKEN_REVISION()
        && UNDERLYING_ASSET_ADDRESS() == ghostUnderlyingAsset
        && getAToken() == ghostGhoAToken
        && getDiscountRateStrategy() == ghostDiscountRateStrategy
        && getDiscountToken() == ghostDiscountToken
        && assert_uint16(getDiscountPercent(user)) == ghostDiscountPercent[user]
        && assert_uint128(getBalanceFromInterest(user)) == ghostAccumulatedDebtInterest[user]
        && decimals() == ghostDecimals
        && getIncentivesController() == ghostIncentivesController
    );
}


