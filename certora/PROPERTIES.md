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
- `facilitatorInListAfterAddFacilitator`
  - Facilitator is valid after successful call to `addFacilitator()`

## Setup

- `facilitatorsList_setInvariant`
  - `EnumerableSet.AddressSet` internal coherency
- `addr_in_set_iff_in_map`
  - `Facilitator.label` <=> `EnumerableSet.AddressSet` (`_indexes[value]`) coherency
- `valid_facilitatorLabel`
  - `Facilitator.label` <=> `ghoToken.getFacilitator(facilitator).label` coherency
