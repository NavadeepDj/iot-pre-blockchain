// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script} from "forge-std/Script.sol";
import {DataRegistry} from "../src/Counter.sol";

contract DeployDataRegistry is Script {
    function run() public returns (DataRegistry registry) {
        vm.startBroadcast();
        registry = new DataRegistry();
        vm.stopBroadcast();
    }
}
