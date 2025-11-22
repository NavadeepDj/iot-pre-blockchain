// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title DataRegistry
 * @notice Stores metadata for encrypted IoT data and manages access grants.
 *
 *  - Each record is referenced by a `recordId` = keccak256(cid)
 *  - Owners can register data (CID, hash, sensorId)
 *  - Owners can grant / revoke access for recipients, attaching an off-chain URI
 *    that points to the re-encryption material (kfrags)
 */
contract DataRegistry {
    struct DataRecord {
        string cid;
        bytes32 dataHash;
        string sensorId;
        address owner;
        uint64 createdAt;
    }

    struct Grant {
        bool exists;
        string kfragURI;
        uint64 grantedAt;
    }

    mapping(bytes32 => DataRecord) private records;
    mapping(bytes32 => mapping(address => Grant)) private grants;

    event DataRegistered(
        bytes32 indexed recordId,
        string cid,
        bytes32 dataHash,
        string sensorId,
        address indexed owner
    );

    event AccessGranted(
        bytes32 indexed recordId,
        address indexed owner,
        address indexed recipient,
        string kfragURI
    );

    event AccessRevoked(
        bytes32 indexed recordId,
        address indexed owner,
        address indexed recipient
    );

    error DataAlreadyRegistered(bytes32 recordId);
    error DataNotFound(bytes32 recordId);
    error NotRecordOwner(bytes32 recordId, address caller);
    error InvalidRecipient();
    error GrantNotFound(bytes32 recordId, address recipient);

    /**
     * @notice Register a new piece of encrypted data.
     * @param cid IPFS CID of the encrypted blob.
     * @param dataHash SHA-256 hash of the encrypted blob (bytes32).
     * @param sensorId Identifier for the sensor that produced the data.
     */
    function registerData(
        string calldata cid,
        bytes32 dataHash,
        string calldata sensorId
    ) external returns (bytes32 recordId) {
        recordId = keccak256(bytes(cid));

        if (records[recordId].owner != address(0)) {
            revert DataAlreadyRegistered(recordId);
        }

        records[recordId] = DataRecord({
            cid: cid,
            dataHash: dataHash,
            sensorId: sensorId,
            owner: msg.sender,
            createdAt: uint64(block.timestamp)
        });

        emit DataRegistered(recordId, cid, dataHash, sensorId, msg.sender);
    }

    /**
     * @notice Grant access to a recipient by attaching an off-chain URI that points
     *         to the re-encryption key (kfrag) material.
     */
    function grantAccess(
        bytes32 recordId,
        address recipient,
        string calldata kfragURI
    ) external {
        DataRecord storage record = records[recordId];
        if (record.owner == address(0)) revert DataNotFound(recordId);
        if (record.owner != msg.sender) revert NotRecordOwner(recordId, msg.sender);
        if (recipient == address(0)) revert InvalidRecipient();

        grants[recordId][recipient] = Grant({
            exists: true,
            kfragURI: kfragURI,
            grantedAt: uint64(block.timestamp)
        });

        emit AccessGranted(recordId, msg.sender, recipient, kfragURI);
    }

    /**
     * @notice Revoke a previously granted access.
     */
    function revokeAccess(bytes32 recordId, address recipient) external {
        DataRecord storage record = records[recordId];
        if (record.owner == address(0)) revert DataNotFound(recordId);
        if (record.owner != msg.sender) revert NotRecordOwner(recordId, msg.sender);

        if (grants[recordId][recipient].exists) {
            delete grants[recordId][recipient];
            emit AccessRevoked(recordId, msg.sender, recipient);
        }
    }

    /**
     * @notice Fetch metadata for a record.
     */
    function getRecord(bytes32 recordId) external view returns (DataRecord memory) {
        DataRecord memory record = records[recordId];
        if (record.owner == address(0)) revert DataNotFound(recordId);
        return record;
    }

    /**
     * @notice Fetch the grant data for a recipient.
     */
    function getGrant(
        bytes32 recordId,
        address recipient
    ) external view returns (Grant memory) {
        Grant memory grantData = grants[recordId][recipient];
        if (!grantData.exists) revert GrantNotFound(recordId, recipient);
        return grantData;
    }

    /**
     * @notice Check if a recipient currently has access to a record.
     */
    function hasAccess(bytes32 recordId, address recipient) external view returns (bool) {
        return grants[recordId][recipient].exists;
    }
}
