// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20; // Gunakan versi Solidity yang kompatibel dengan Hardhat Anda (biasanya 0.8.20 atau yang mendekati)

contract SensorData {
    // Struktur untuk menyimpan satu entri data sensor
    struct SensorReading {
        uint256 timestamp;
        uint16 temperature; // Menggunakan uint16 untuk menghemat gas, asumsikan suhu antara 0-65535
        uint16 humidity;    // Menggunakan uint16 untuk menghemat gas, asumsikan kelembaban antara 0-100
        string sensorId;
        string location;
        string processStage;
    }

    // Array untuk menyimpan semua pembacaan sensor
    SensorReading[] public readings;

    // Event untuk memudahkan pemantauan data baru dari luar kontrak
    event NewSensorReading(
        uint256 indexed timestamp,
        uint16 temperature,
        uint16 humidity,
        string sensorId,
        string location,
        string processStage
    );

    constructor() {}

    // Fungsi untuk menambahkan data sensor baru
    // Parameter: timestamp (Unix), suhu (integer), kelembaban (integer), id sensor, lokasi, tahap proses
    function addSensorReading(
        uint256 _timestamp,
        uint16 _temperature,
        uint16 _humidity,
        string calldata _sensorId,
        string calldata _location,
        string calldata _processStage
    ) public {
        // Simpan data ke array
        readings.push(SensorReading(
            _timestamp,
            _temperature,
            _humidity,
            _sensorId,
            _location,
            _processStage
        ));

        // Emit event
        emit NewSensorReading(
            _timestamp,
            _temperature,
            _humidity,
            _sensorId,
            _location,
            _processStage
        );
    }

    // Fungsi untuk mendapatkan semua data pembacaan sensor (baca-saja, tidak memakan gas)
    function getAllReadings() public view returns (SensorReading[] memory) {
        return readings;
    }

    // Fungsi untuk mendapatkan jumlah total pembacaan sensor
    function getReadingsCount() public view returns (uint256) {
        return readings.length;
    }

    // Fungsi untuk mendapatkan pembacaan sensor berdasarkan indeks
    function getReadingByIndex(uint256 _index) public view returns (SensorReading memory) {
        require(_index < readings.length, "Index out of bounds");
        return readings[_index];
    }
}