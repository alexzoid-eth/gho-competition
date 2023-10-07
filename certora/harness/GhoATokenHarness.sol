pragma solidity ^0.8.0;

import {GhoAToken} from '../../src/contracts/facilitators/aave/tokens/GhoAToken.sol';
import {IPool} from '@aave/core-v3/contracts/interfaces/IPool.sol';
import {IACLManager} from '@aave/core-v3/contracts/interfaces/IACLManager.sol';

contract GhoATokenHarness is GhoAToken {
  constructor(IPool pool) GhoAToken(pool) {}

  //
  // Added functions
  //

  function getPoolAddress() external view returns (address) {
    return address(POOL);
  }

  function calculateDomainSeparator() external view returns (bytes32) {
    return _calculateDomainSeparator();
  }

  function isPoolAdmin(address account) external view returns (bool) {
    IACLManager aclManager = IACLManager(_addressesProvider.getACLManager());
    return aclManager.isPoolAdmin(account);
  }

  function setAnotherName() external {
    string memory anotherName = 'anotherName';
    _setName(anotherName);
  }
}
