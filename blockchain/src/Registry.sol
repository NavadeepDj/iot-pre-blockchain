// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

contract Registry {
    struct Record {
        string cid;
        bytes32 dataHash;
        string sensorId;
        address owner;
        uint256 createdAt;
    }

    struct Grant {
        string cid;
        address recipient;
        string recipientPublicKey;
        string kfragUri;
        string reencryptedCid;
        bool processed;
        uint256 createdAt;
    }

    // Mappings
    mapping(bytes32 => Record) public records; // recordId => Record
    mapping(bytes32 => Grant) public grants;   // grantId => Grant

    // Events
    event DataRegistered(bytes32 indexed recordId, string cid, address indexed owner);
    event AccessGranted(bytes32 indexed grantId, string cid, address indexed recipient);
    event AccessProcessed(bytes32 indexed grantId, string reencryptedCid);

    // Modifiers
    modifier onlyOwner(bytes32 _recordId) {
        require(records[_recordId].owner == msg.sender, "Not the data owner");
        _;
    }

    modifier onlyRecipient(bytes32 _grantId) {
        require(grants[_grantId].recipient == msg.sender, "Not the recipient");
        _;
    }

    // Functions

    function registerData(string memory _cid, bytes32 _dataHash, string memory _sensorId) public {
        bytes32 recordId = keccak256(abi.encodePacked(_cid));
        require(records[recordId].createdAt == 0, "Record already exists");

        records[recordId] = Record({
            cid: _cid,
            dataHash: _dataHash,
            sensorId: _sensorId,
            owner: msg.sender,
            createdAt: block.timestamp
        });

        emit DataRegistered(recordId, _cid, msg.sender);
    }

    function grantAccess(
        string memory _cid,
        address _recipient,
        string memory _recipientPublicKey,
        string memory _kfragUri
    ) public {
        bytes32 recordId = keccak256(abi.encodePacked(_cid));
        require(records[recordId].createdAt != 0, "Record does not exist");
        require(records[recordId].owner == msg.sender, "Not the data owner");

        bytes32 grantId = keccak256(abi.encodePacked(_cid, _recipient));
        
        grants[grantId] = Grant({
            cid: _cid,
            recipient: _recipient,
            recipientPublicKey: _recipientPublicKey,
            kfragUri: _kfragUri,
            reencryptedCid: "",
            processed: false,
            createdAt: block.timestamp
        });

        emit AccessGranted(grantId, _cid, _recipient);
    }

    function completeAccess(string memory _cid, address _recipient, string memory _reencryptedCid) public {
        // Anyone can complete access? Ideally only the proxy. 
        // For now, we can leave it open or restrict if we had a registered proxy.
        // But to keep it simple and decentralized, maybe we verify the caller?
        // Actually, the proxy is an off-chain worker. It doesn't necessarily have a specific address 
        // unless we register it. Let's allow anyone to submit the result for now, 
        // or maybe restrict to the recipient? No, the recipient doesn't do the re-encryption.
        // The proxy does. The proxy needs to pay gas.
        
        bytes32 grantId = keccak256(abi.encodePacked(_cid, _recipient));
        require(grants[grantId].createdAt != 0, "Grant does not exist");
        require(!grants[grantId].processed, "Already processed");

        grants[grantId].reencryptedCid = _reencryptedCid;
        grants[grantId].processed = true;

        emit AccessProcessed(grantId, _reencryptedCid);
    }

    // Read helpers
    function getRecord(bytes32 _recordId) public view returns (Record memory) {
        return records[_recordId];
    }

    function getGrant(bytes32 _grantId) public view returns (Grant memory) {
        return grants[_grantId];
    }
}
