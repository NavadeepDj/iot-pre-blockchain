// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract DataRegistry {

    struct DataRecord {
        address owner;
        string ipfsCid;
        bytes32 dataHash;
        uint256 timestamp;
    }

    mapping(bytes32 => DataRecord) public records;

    event DataRecorded(bytes32 indexed recordId, string ipfsCid, bytes32 dataHash, address indexed owner);

    function recordData(bytes32 recordId, string memory ipfsCid, bytes32 dataHash) external {
        require(records[recordId].timestamp == 0, "Record exists");

        records[recordId] = DataRecord({
            owner: msg.sender,
            ipfsCid: ipfsCid,
            dataHash: dataHash,
            timestamp: block.timestamp
        });

        emit DataRecorded(recordId, ipfsCid, dataHash, msg.sender);
    }
}
