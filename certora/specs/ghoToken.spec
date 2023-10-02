import "./ghoTokenHelperMethods.spec";

///////////////// METHODS //////////////////////

methods{
    // GhoToken
    function mint(address account, uint256 amount) external;
    function burn(uint256 amount) external;
    function addFacilitator(address facilitatorAddress, string memory facilitatorLabel, 
        uint128 bucketCapacity) external;
    function removeFacilitator(address facilitatorAddress) external;
    function setFacilitatorBucketCapacity(address facilitator, uint128 newCapacity) external;
    function getFacilitator(address facilitator) external returns (IGhoToken.Facilitator) envfree;
    function getFacilitatorBucket(address facilitator) external returns (uint256, uint256) envfree;
    function getFacilitatorsList() external returns (address[]) envfree;

    // ERC20
    function approve(address spender, uint256 amount) internal returns (bool);
    function transfer(address to, uint256 amount) internal returns (bool);
    function transferFrom(address from, address to, uint256 amount) internal returns (bool);
    function permit(address owner, address spender, uint256 value, uint256 deadline, uint8 v, 
        bytes32 r, bytes32 s) internal;
    function DOMAIN_SEPARATOR() internal returns (bytes32);
    function computeDomainSeparator() internal returns (bytes32);
    function _mint(address to, uint256 amount) internal;
    function _burn(address from, uint256 amount) internal;
    function totalSupply() external returns uint256 envfree;
    function balanceOf(address) external returns (uint256) envfree;
    function nonces(address) external returns (uint256) envfree;
}

///////////////// DEFINITIONS /////////////////////

// Returns, whether a value is in the set.
definition inFacilitatorsList(bytes32 value) returns bool = (ghostIndexes[value] != 0);

////////////////// FUNCTIONS //////////////////////

function toBytes32(address value) returns bytes32 {
    return GhoTokenHelper.toBytes32(value);
}

///////////////// GHOSTS & HOOKS //////////////////

/**
* Ghost copy of `mapping(address => Facilitator) _facilitators`
*  .offset 0 - bucketCapacity
*  .offset 16 - bucketLevels
*  .offset 32 - label
*/

ghost mapping (address => uint128) ghostBucketCapacity {
    init_state axiom forall address i. ghostBucketCapacity[i] == 0;
}

ghost mapping (address => uint128) ghostBucketLevels {
    init_state axiom forall address i. ghostBucketLevels[i] == 0;
}

ghost mapping (address => bool) ghostInFacilitatorsMapping  {
    init_state axiom forall address i. ghostInFacilitatorsMapping[i] == false;
}

ghost mathint ghostSumAllLevel {
    init_state axiom ghostSumAllLevel == 0;
}

hook Sload uint128 capacity _facilitators[KEY address a].(offset 0) STORAGE {
    require(ghostBucketCapacity[a] == capacity);
}

hook Sstore _facilitators[KEY address a].(offset 0) uint128 capacity STORAGE {
    ghostBucketCapacity[a] = capacity;
}

hook Sload uint128 level _facilitators[KEY address a].(offset 16) STORAGE {
    require(ghostBucketLevels[a] == level);
}

hook Sstore _facilitators[KEY address a].(offset 16) uint128 level (uint128 oldLevel) STORAGE {
    ghostBucketLevels[a] = level;
    ghostSumAllLevel = ghostSumAllLevel + level - oldLevel;
}

hook Sload uint256 stringLength _facilitators[KEY address a].(offset 32) STORAGE {
    if (stringLength > 0) {
        require(ghostInFacilitatorsMapping[a] == true);
    } else {
        require(ghostInFacilitatorsMapping[a] == false);
    }
}

hook Sstore _facilitators[KEY address a].(offset 32) uint256 stringLength STORAGE {
    if (stringLength > 0) {
        ghostInFacilitatorsMapping[a] = true;
    } else {
        ghostInFacilitatorsMapping[a] = false;
    }
}

/**
* Ghost copy of `EnumerableSet.AddressSet _facilitatorsList`
*/

ghost uint256 ghostFacilitatorsListLength {
    // assumption: it's infeasible to grow the list to these many elements.
    axiom ghostFacilitatorsListLength < max_uint64;
}

ghost mapping(mathint => bytes32) ghostValues {
    init_state axiom forall mathint x. ghostValues[x] == to_bytes32(0);
}

ghost mapping(bytes32 => uint256) ghostIndexes {
    init_state axiom forall bytes32 x. ghostIndexes[x] == 0;
}

hook Sload uint256 length currentContract._facilitatorsList.(offset 0) STORAGE {
    require(ghostFacilitatorsListLength == length);
}

hook Sstore currentContract._facilitatorsList.(offset 0) uint256 newLength STORAGE {
    ghostFacilitatorsListLength = newLength;
}

hook Sload bytes32 val currentContract._facilitatorsList._inner._values[INDEX uint256 i] STORAGE {
    require(ghostValues[i] == val);
}

hook Sstore currentContract._facilitatorsList._inner._values[INDEX uint256 i] bytes32 val STORAGE {
    ghostValues[i] = val;
}

hook Sload uint256 i currentContract._facilitatorsList._inner._indexes[KEY bytes32 val] STORAGE {
    require(ghostIndexes[val] == i);
}

hook Sstore currentContract._facilitatorsList._inner._indexes[KEY bytes32 val] uint256 i STORAGE {
    ghostIndexes[val] = i;
}

/**
* Sum of all balances
*/

ghost mapping (address => uint256) ghostBalanceOfMapping {
    init_state axiom forall address i. ghostBalanceOfMapping[i] == 0;
}

ghost mathint sumAllBalance {
    init_state axiom sumAllBalance == 0;
}

hook Sload uint256 balance balanceOf[KEY address a] STORAGE {
    require(ghostBalanceOfMapping[a] == balance);
    require(to_mathint(balance) <= sumAllBalance);
} 

hook Sstore balanceOf[KEY address a] uint256 balance (uint256 old_balance) STORAGE {
    ghostBalanceOfMapping[a] = balance;
   sumAllBalance = sumAllBalance + balance - old_balance;
}

///////////////// ASSUME INVARIANTS ////////////////

// AddressSet internal coherency
invariant facilitatorsListSetup()
    (forall uint256 i. i < ghostFacilitatorsListLength => to_mathint(ghostIndexes[ghostValues[i]]) == i + 1)
    && (forall bytes32 val. ghostIndexes[val] == 0 
        || (
            ghostValues[ghostIndexes[val] - 1] == val 
            && ghostIndexes[val] >= 1 && ghostIndexes[val] <= ghostFacilitatorsListLength
        )
    );

// GhoToken mapping-AddressSet coherency
invariant addrInSetIfInMap(address facilitator)
    ghostInFacilitatorsMapping[facilitator] <=> inFacilitatorsList(toBytes32(facilitator)) {
        preserved {
            requireInvariant facilitatorsListSetup();
        }
    }

// Validity of a facilitator struct
invariant validFacilitatorLabel(address facilitator) 
    ghostInFacilitatorsMapping[facilitator] <=> GhoTokenHelper.getFacilitatorsLabelLen(facilitator) > 0 {
        preserved {
            requireInvariant facilitatorsListSetup();
            requireInvariant addrInSetIfInMap(facilitator);
        }
    }

function assumeInvariants(address facilitator) {
    requireInvariant facilitatorsListSetup();
    requireInvariant addrInSetIfInMap(facilitator);
    requireInvariant validFacilitatorLabel(facilitator);
}

///////////////// PROPERTIES //////////////////////

// Sum of balances is totalSupply()
invariant sumAllBalanceEqTotalSupply() 
    sumAllBalance == to_mathint(totalSupply());

// User's balance not greater than totalSupply()
invariant balanceOfLeqTotalSupply(address user) 
    balanceOf(user) <= totalSupply() {
        preserved {
            requireInvariant sumAllBalanceEqTotalSupply();
        }
    }

// Sum of bucket levels is equals to totalSupply()
invariant totalSupplyEqGhostSumAllLevel() 
    ghostSumAllLevel == to_mathint(totalSupply()) {
        preserved burn(uint256 amount) with (env e){
            requireInvariant balanceOfLeqTotalSupply(e.msg.sender);
        }
    }

// The sum of bucket level is equal to the sum of GhoToken balances
invariant sumAllLevelEqSumAllBalance() 
    ghostSumAllLevel == sumAllBalance {
        preserved {
            requireInvariant sumAllBalanceEqTotalSupply();
        }
    }

// A facilitator with a positive bucket capacity exists in the _facilitators mapping
invariant validCapacity(address facilitator)
    ((GhoTokenHelper.getFacilitatorBucketCapacity(facilitator) > 0) 
        => ghostInFacilitatorsMapping[facilitator]);

// A facilitator with a positive bucket level exists in the _facilitators mapping
invariant validLevel(address facilitator) 
    ((GhoTokenHelper.getFacilitatorBucketLevel(facilitator) > 0) 
        => ghostInFacilitatorsMapping[facilitator]) {
        preserved{
            requireInvariant validCapacity(facilitator);
        }
    }

// Bucket level <= bucket capacity unless setFacilitatorBucketCapacity() lowered it
rule levelLeqCapacity(address facilitator, method f) filtered { f -> !f.isView } {
    env e;
    calldataarg arg;

    assumeInvariants(facilitator);
    requireInvariant validCapacity(facilitator);
    require(GhoTokenHelper.getFacilitatorBucketLevel(facilitator) 
        <= GhoTokenHelper.getFacilitatorBucketCapacity(facilitator)); 
    
    f(e, arg);

    assert((f.selector != sig:setFacilitatorBucketCapacity(address,uint128).selector)
        => (GhoTokenHelper.getFacilitatorBucketLevel(facilitator) 
            <= GhoTokenHelper.getFacilitatorBucketCapacity(facilitator))
    );
}

/**
* If Bucket level < bucket capacity then the first invocation of mint() succeeds after burn
*   unless setFacilitatorBucketCapacity() lowered bucket capacity or removeFacilitator() was called
*/
rule mintAfterBurn(method f) filtered { f -> !f.isView } {
    env e;
    calldataarg arg;
    uint256 amount_burn;
    uint256 amount_mint;
    address account;

    assumeInvariants(e.msg.sender);
    require(GhoTokenHelper.getFacilitatorBucketLevel(e.msg.sender) 
        <= GhoTokenHelper.getFacilitatorBucketCapacity(e.msg.sender));
    require(amount_mint > 0);
    requireInvariant balanceOfLeqTotalSupply(e.msg.sender);
    requireInvariant validCapacity(e.msg.sender);

    burn(e, amount_burn);
    f(e, arg);
    mint@withrevert(e, account, amount_mint);

    assert(((amount_mint <= amount_burn)
            && f.selector != sig:mint(address,uint256).selector
            && f.selector != sig:setFacilitatorBucketCapacity(address,uint128).selector
            && f.selector != sig:removeFacilitator(address).selector
            ) => !lastReverted), "mint failed";
}

/**
* Burn after mint succeeds. BorrowLogic::executeRepa() executes the following code before 
* invocation of handleRepayment() 
*/
rule burnAfterMint(method f) filtered { f -> !f.isView } {
    env e;
    uint256 amount;
    address account;

    requireInvariant balanceOfLeqTotalSupply(e.msg.sender);
    
    mint(e, account, amount);
    transferFrom(e, account, e.msg.sender, amount);
    burn@withrevert(e, amount);

    assert(!lastReverted, "burn failed");
}

// BucketLevel remains unchanged after mint() followed by burn()
rule levelUnchangedAfterMintFollowedByBurn() {
    env e;
    calldataarg arg;
    uint256 amount;
    address account;

    uint256 levelBefore = GhoTokenHelper.getFacilitatorBucketLevel(e.msg.sender);

    mint(e, account, amount);
    burn(e, amount);
    
    uint256 levelAfter = GhoTokenHelper.getFacilitatorBucketLevel(e.msg.sender);
    
    assert(levelBefore == levelAfter);
}

rule levelAfterMint() {
    env e;
    calldataarg arg;
    uint256 amount;
    address account;

    uint256 levelBefore = GhoTokenHelper.getFacilitatorBucketLevel(e.msg.sender);

    mint(e, account, amount);

    uint256 levelAfter = GhoTokenHelper.getFacilitatorBucketLevel(e.msg.sender);

    assert(levelBefore + amount == to_mathint(levelAfter));

}

rule levelAfterBurn() {
    env e;
    calldataarg arg;
    uint256 amount;

    uint256 levelBefore = GhoTokenHelper.getFacilitatorBucketLevel(e.msg.sender);

    burn(e, amount);
    
    uint256 levelAfter = GhoTokenHelper.getFacilitatorBucketLevel(e.msg.sender);
    
    assert(to_mathint(levelBefore) == levelAfter + amount);
}

// Facilitator is valid after successful call to setFacilitatorBucketCapacity()
rule facilitatorInListAfterSetFacilitatorBucketCapacity() {
    env e;
    address facilitator;
    uint128 newCapacity;

    assumeInvariants(facilitator);

    setFacilitatorBucketCapacity(e, facilitator, newCapacity);
    
    assert(inFacilitatorsList(toBytes32(facilitator)));
}

/**
* GhoTokenHelper.getFacilitatorBucketCapacity() called after setFacilitatorBucketCapacity() 
* return the assign bucket capacity 
*/
rule getFacilitatorBucketCapacity_after_setFacilitatorBucketCapacity() {
    env e;
    address facilitator;
    uint128 newCapacity;

    setFacilitatorBucketCapacity(e, facilitator, newCapacity);

    assert(GhoTokenHelper.getFacilitatorBucketCapacity(facilitator) == require_uint256(newCapacity));
}

// Facilitator is valid after successful call to addFacilitator()
rule facilitatorInListAfterAddFacilitator() {
    env e;
    address facilitator;
    string label;
    uint128 capacity;

    assumeInvariants(facilitator);

    addFacilitator(e, facilitator, label, capacity);

    assert(inFacilitatorsList(toBytes32(facilitator)));
}

// Facilitator is valid after successful call to mint() or burn()
rule facilitatorInListAfterMintAndBurn(method f) {
    env e;
    calldataarg args;

    requireInvariant validCapacity(e.msg.sender);
    requireInvariant validLevel(e.msg.sender);
    assumeInvariants(e.msg.sender);

    f(e,args);

    assert(((f.selector == sig:mint(address,uint256).selector) || (f.selector == sig:burn(uint256).selector)) 
        => inFacilitatorsList(toBytes32(e.msg.sender))
    );
}

// Facilitator address is removed from list  (GhoToken._facilitatorsList._values) after calling removeFacilitator()
rule addressNotInListAfterRemoveFacilitator(address facilitator) {
    env e;

    assumeInvariants(facilitator);
    
    bool before = inFacilitatorsList(toBytes32(facilitator));
    removeFacilitator(e, facilitator);
    
    assert(before && !inFacilitatorsList(toBytes32(facilitator)));
}

rule balanceAfterMint() {
    env e;
    address user;
    uint256 initBalance = balanceOf(user);
    uint256 initSupply = totalSupply();
    uint256 amount;

    requireInvariant sumAllBalanceEqTotalSupply();

    mint(e, user, amount);
    
    uint256 finBalance = balanceOf(user);
    uint256 finSupply = totalSupply();
    
    assert(initBalance + amount == to_mathint(finBalance));
    assert(initSupply + amount == to_mathint(finSupply));
}

rule balanceAfterBurn() {
    env e;
    requireInvariant balanceOfLeqTotalSupply(e.msg.sender);

    uint256 initBalance = balanceOf(e.msg.sender);
    uint256 initSupply = totalSupply();
    uint256 amount;
    burn(e, amount);
    uint256 finBalance = balanceOf(e.msg.sender);
    uint256 finSupply = totalSupply();
    
    assert(to_mathint(initBalance) == finBalance + amount);
    assert(to_mathint(initSupply) == finSupply + amount);
}

// Proves that you can't mint more than the facilitator's remaining capacity
rule mintLimitedByFacilitatorRemainingCapacity() {
    env e;
    uint256 amount;

    mathint diff = GhoTokenHelper.getFacilitatorBucketCapacity(e.msg.sender) 
        - GhoTokenHelper.getFacilitatorBucketLevel(e.msg.sender);
    require(to_mathint(amount) > diff);
    
    address user;
    mint@withrevert(e, user, amount);
    
    assert(lastReverted);
}

// Proves that you can't burn more than the facilitator's current level
rule burnLimitedByFacilitatorLevel() {
    env e;

    require(GhoTokenHelper.getFacilitatorBucketCapacity(e.msg.sender) 
        > GhoTokenHelper.getFacilitatorBucketLevel(e.msg.sender));

    uint256 amount;
    require(amount > GhoTokenHelper.getFacilitatorBucketLevel(e.msg.sender));
    burn@withrevert(e, amount);
    
    assert(lastReverted);
}
