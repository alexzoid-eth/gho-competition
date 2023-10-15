# GhoFlashMinter

## High-Level

- `availableLiquidityDoesntChange`
  - Checks that the available liquidity, retrieved by maxFlashLoan, stays the same after any action
- `integrityOfDistributeFeesToTreasury`
  - Checks the integrity of distributeFees

## Valid States

- `functionsNotRevert`
  - Possibility should not revert

## State Transitions

## Variable Transitions

## Unit Tests

- `integrityOfTreasurySet`
  - Checks the integrity of updateGhoTreasury - after update the given address is set
- `integrityOfFeeSet`
  - Checks the integrity of updateFee - after update the given value is set

# GhoVariableDebtToken

## High-Level

- `debtTokenIsNotTransferable`
  - Proves that debt tokens aren't transferable
- `integrityOfMint_userIsolation`
  - Proves that mint can't effect other user's scaled balance
- `integrityOfBurn_userIsolation`
  - Proves that burn can't effect other user's scaled balance
- `integrityOfUpdateDiscountDistribution_userIsolation`
  - Proves that updateDiscountDistribution can't effect other user's scaled balance
- `integrityOfRebalanceUserDiscountPercent_userIsolation`
  - Proves that rebalanceUserDiscountPercent can't effect other user's scaled balance

## Valid States

- `discountCantExceed100Percent`
  - At any point in time, the user's discount rate isn't larger than 100%
- `integrityOfBalanceOf_fullDiscount`
  - Proves that a user with 100% discounts has a fixed balance over time
- `integrityOfBalanceOf_noDiscount`
  - Proves that a user's balance, with no discount, is equal to rayMul(scaledBalance, current index)
- `integrityOfBalanceOf_zeroScaledBalance`
  - Proves the a user with zero scaled balance has a zero balance

## State Transitions

- `nonMintFunctionCantIncreaseBalance`
  - Proves that the user's balance of debt token can't increase by calling any external non-mint function.
- `nonMintFunctionCantIncreaseScaledBalance`
  - Proves that a call to a non-mint operation won't increase the user's balance of the actual debt tokens (i.e. it's scaled balance)
- `onlyCertainFunctionsCanModifyScaledBalance`
  - Proves that only burn/mint/rebalanceUserDiscountPercent/updateDiscountDistribution can modify user's scaled balance
- `userAccumulatedDebtInterestWontDecrease`
  - Proves that only a call to decreaseBalanceFromInterest will decrease the user's accumulated interest listing
- `userCantNullifyItsDebt`
  - Proves that a user can't nullify its debt without calling burn
- `onlyMintForUserCanIncreaseUsersBalance`
  - Proves that when calling mint, the user's balance will increase if the call is made on bahalf of the user
- `integrityOfBurn_fullRepay_concrete`
  - Proves a concrete case of repaying the full debt that ends with a zero balance

## Variable Transitions

- `integrityOfMint_updateIndex`
  - Proves the after calling mint, the user's state is updated with the recent index value
- `integrityOfBurn_updateIndex`
  - Proves the after calling burn, the user's state is updated with the recent index value
- `integrityOfMint_updateDiscountRate`
  - Proves that after calling mint, the user's discount rate is up to date
- `integrityOfBurn_updateDiscountRate`
  - Proves that after calling burn, the user's discount rate is up to date

## Unit Tests

- `disallowedFunctionalities`
  - Ensuring that the defined disallowed functions revert in any case (from VariableDebtToken.spec)
- `integrityOfMint_updateScaledBalance_fixedIndex`
  - Proves that on a fixed index calling mint(user, amount) will increase the user's scaled balance by amount
- `integrityMint_atoken`
  - Checking atoken alone (from VariableDebtToken.spec)
- `burnZeroDoesntChangeBalance`
  - Proves that calling burn with 0 amount doesn't change the user's balance (from VariableDebtToken.spec)
- `integrityOfUpdateDiscountDistribution_updateIndex`
  - Proves the after calling updateDiscountDistribution, the user's state is updated with the recent index value
- `integrityOfRebalanceUserDiscountPercent_updateDiscountRate`
  - Proves that after calling rebalanceUserDiscountPercent, the user's discount rate is up to date
- `integrityOfRebalanceUserDiscountPercent_updateIndex`
  - Proves that after calling rebalanceUserDiscountPercent, the user's state is updated with the recent index value
- `burnAllDebtReturnsZeroDebt`
  - Proves the balance will be zero when burn whole dept

# GhoAToken

## High-Level

- `transferUnderlyingToCantExceedCapacity`
  - Proves that calling ghoAToken::transferUnderlyingTo will revert if the amount exceeds the excess capacity
- `integrityTransferUnderlyingToWithHandleRepayment`
  - BucketLevel decreases after transferUnderlyingTo() followed by handleRepayment()

## Valid States

- `totalSupplyAlwaysZero`
  - Proves that the total supply of GhoAToken is always zero
- `userBalanceAlwaysZero`
  - Proves that any user's balance of GhoAToken is always zero

## State Transitions

## Variable Transitions

## Unit Tests

- `noMint`
  - Proves that ghoAToken::mint always reverts
- `noBurn`
  - Proves that ghoAToken::burn always reverts
- `noTransfer`
  - Proves that ghoAToken::transfer always reverts

# GhoToken

## High-Level

- `facilitatorInListAfterMintAndBurn`
  - [5] Facilitator is valid after successful call to `mint()` or `burn()`
- `mintLimitedByFacilitatorRemainingCapacity`
  - Proves that you can't mint more than the facilitator's remaining capacity
- `burnLimitedByFacilitatorLevel`
  - Proves that you can't burn more than the facilitator's current level

## Valid States

- `sumAllBalance_eq_totalSupply`
  - Sum of balances is `totalSupply()`
- `inv_balanceOf_leq_totalSupply`
  - User's balance not greater than `totalSupply()`
- `total_supply_eq_sumAllLevel`
  - Sum of bucket levels is equals to `totalSupply()`
- `sumAllLevel_eq_sumAllBalance`
  - The sum of bucket level is equal to the sum of GhoToken balances
- `inv_valid_capacity`
  - A facilitator with a positive bucket capacity exists in the `_facilitators` mapping
- `inv_valid_level`
  - A facilitator with a positive bucket level exists in the `_facilitators` mapping
- `level_leq_capacity`
  - Bucket level <= bucket capacity unless `setFacilitatorBucketCapacity()` lowered it

## State Transitions

- `mint_after_burn`
  - If Bucket level < bucket capacity then the first invocation of `mint()` succeeds after `burn()`
- `burn_after_mint`
  - Burn after mint succeeds
- `level_unchanged_after_mint_followed_by_burn`
  - BucketLevel remains unchanged after `mint()` followed by `burn()`
- `level_after_mint`
  - BucketLevel changed correctly after `mint()`
- `level_after_burn`
  - BucketLevel changed correctly after `burn()`
- `address_not_in_list_after_removeFacilitator`
  - Facilitator address is removed from list (GhoToken.\_facilitatorsList.\_values) after calling `removeFacilitator`
- `balance_after_mint`
  - Balance changed correctly after `mint()`
- `balance_after_burn`
  - Balance changed correctly after `burn()`

## Variable Transitions

## Unit Tests

- `facilitator_in_list_after_setFacilitatorBucketCapacity`
  - Facilitator is valid after successful call to setFacilitatorBucketCapacity()
- `getFacilitatorBucketCapacity_after_setFacilitatorBucketCapacity`
  - GhoTokenHelper.getFacilitatorBucketCapacity() called after setFacilitatorBucketCapacity() return the assign bucket capacity
- `facilitator_in_list_after_addFacilitator`
  - Facilitator is valid after successful call to `addFacilitator()`

## Setup

- `facilitatorsList_setInvariant`
  - `EnumerableSet.AddressSet` internal coherency
- `addr_in_set_iff_in_map`
  - `Facilitator.label` <=> `EnumerableSet.AddressSet` (`_indexes[value]`) coherency
- `valid_facilitatorLabel`
  - `Facilitator.label` <=> `ghoToken.getFacilitator(facilitator).label` coherency
