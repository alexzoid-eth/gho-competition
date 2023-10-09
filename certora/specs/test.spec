hook Sload bytes32 val currentContract._domainSeparator STORAGE {
}

hook Sstore currentContract._domainSeparator bytes32 val STORAGE {
}

rule sanityCheck(env e, method f, calldataarg args) {
    f@withrevert(e, args);
    assert(true);
}