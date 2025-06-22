// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SensorStorage {
    event DataStored(
        uint256 timestamp,
        string sensorId,
        string location,
        string stage,
        int256 temperature,
        int256 humidity
    );

    function storeData(
        uint256 timestamp,
        string memory sensorId,
        string memory location,
        string memory stage,
        int256 temperature,
        int256 humidity
    ) public {
        emit DataStored(timestamp, sensorId, location, stage, temperature, humidity);
    }
}
