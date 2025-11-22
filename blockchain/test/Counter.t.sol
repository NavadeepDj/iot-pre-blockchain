// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test} from "forge-std/Test.sol";
import {DataRegistry} from "../src/Counter.sol";

contract DataRegistryTest is Test {
    DataRegistry internal registry;
    string internal constant CID = "QmExampleCID";
    bytes32 internal constant DATA_HASH =
        bytes32(uint256(0x1234));
    string internal constant SENSOR_ID = "sensor-1";
    address internal constant RECIPIENT = address(0xBEEF);

    function setUp() public {
        registry = new DataRegistry();
    }

    function testRegisterData() public {
        bytes32 recordId = registry.registerData(CID, DATA_HASH, SENSOR_ID);

        DataRegistry.DataRecord memory record = registry.getRecord(recordId);
        assertEq(record.cid, CID);
        assertEq(record.dataHash, DATA_HASH);
        assertEq(record.sensorId, SENSOR_ID);
        assertEq(record.owner, address(this));
        assertTrue(record.createdAt > 0);
    }

    function testCannotRegisterSameCidTwice() public {
        registry.registerData(CID, DATA_HASH, SENSOR_ID);

        vm.expectRevert(
            abi.encodeWithSelector(
                DataRegistry.DataAlreadyRegistered.selector,
                keccak256(bytes(CID))
            )
        );
        registry.registerData(CID, DATA_HASH, SENSOR_ID);
    }

    function testGrantAccess() public {
        bytes32 recordId = registry.registerData(CID, DATA_HASH, SENSOR_ID);
        string memory uri = "ipfs://kfrags";

        registry.grantAccess(recordId, RECIPIENT, uri);
        assertTrue(registry.hasAccess(recordId, RECIPIENT));

        DataRegistry.Grant memory grantData = registry.getGrant(recordId, RECIPIENT);
        assertTrue(grantData.exists);
        assertEq(grantData.kfragURI, uri);
        assertTrue(grantData.grantedAt > 0);
    }

    function testOnlyOwnerCanGrant() public {
        bytes32 recordId = registry.registerData(CID, DATA_HASH, SENSOR_ID);

        vm.prank(address(0xCAFE));
        vm.expectRevert(
            abi.encodeWithSelector(
                DataRegistry.NotRecordOwner.selector,
                recordId,
                address(0xCAFE)
            )
        );
        registry.grantAccess(recordId, RECIPIENT, "uri");
    }

    function testRevokeAccess() public {
        bytes32 recordId = registry.registerData(CID, DATA_HASH, SENSOR_ID);
        registry.grantAccess(recordId, RECIPIENT, "uri");
        assertTrue(registry.hasAccess(recordId, RECIPIENT));

        registry.revokeAccess(recordId, RECIPIENT);
        assertFalse(registry.hasAccess(recordId, RECIPIENT));
    }
}
