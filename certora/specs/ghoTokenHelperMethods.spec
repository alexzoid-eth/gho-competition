using GhoTokenHelper as GhoTokenHelper;

methods{
    function GhoTokenHelper.getFacilitatorBucketCapacity(address facilitator) external returns (uint256) envfree;
    function GhoTokenHelper.getFacilitatorBucketLevel(address facilitator) external returns (uint256) envfree;
    function GhoTokenHelper.getFacilitatorsListLen() external returns (uint256) envfree;
    function GhoTokenHelper.getFacilitatorsLabelLen(address facilitator) external returns (uint256) envfree;
    function GhoTokenHelper.toBytes32(address value) external returns (bytes32) envfree;
}