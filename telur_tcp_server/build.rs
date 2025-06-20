// telur_tcp_server/build.rs

use std::path::{Path, PathBuf};
use std::process::Command;
use std::env;
use std::fs;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Tentukan path ke direktori Hardhat Anda
    let hardhat_dir = PathBuf::from("../hardhat_sensor_contract").canonicalize()?;

    // Pastikan Hardhat compile dijalankan untuk menghasilkan ABI terbaru
    println!("cargo:rerun-if-changed={}/contracts/SensorData.sol", hardhat_dir.display());
    
    let status = Command::new("npx")
        .current_dir(&hardhat_dir)
        .arg("hardhat")
        .arg("compile")
        .status()?;

    if !status.success() {
        eprintln!("Hardhat compilation failed with status: {}", status);
        // Panic agar build gagal jika kompilasi Hardhat gagal
        return Err("Hardhat compilation failed".into());
    }
    println!("Hardhat compilation successful.");

    // Path ke file ABI yang digenerate oleh Hardhat
    let abi_path = Path::new(&hardhat_dir)
        .join("artifacts")
        .join("contracts")
        .join("SensorData.sol")
        .join("SensorData.json");

    // Pastikan ABI file ada
    if !abi_path.exists() {
        return Err(format!("ABI file not found at: {:?}. Did you run `npx hardhat compile` in your hardhat_sensor_contract directory?", abi_path).into());
    }

    // Baca ABI dari file
    let abi_content = fs::read_to_string(&abi_path)?;
    let abi_json: serde_json::Value = serde_json::from_str(&abi_content)?;

    // Extract 'abi' field from the JSON
    let contract_abi = abi_json["abi"].to_string(); // Ini akan menjadi string dari array ABI JSON

    // Dapatkan direktori output untuk file yang dihasilkan Cargo
    let out_dir = PathBuf::from(env::var("OUT_DIR")?);
    let dest_path = out_dir.join("sensor_data_contract.rs");

    // Gunakan ethers::contract::Abigen untuk menghasilkan bindings
    // Perhatikan bahwa kita memberikan ABI sebagai string, bukan path ke file.
    let bindings = ethers::contract::Abigen::new("SensorDataContract", &contract_abi)?
        .add_derive("serde::Serialize")? // <-- Tambahkan '?' di sini
        .add_derive("serde::Deserialize")? // <-- Dan di sini
        .generate()?;

    // Tulis bindings ke file
    bindings.write_to_file(&dest_path)?;

    println!("cargo:rustc-link-search=native={}", out_dir.display());
    println!("cargo:rerun-if-changed=build.rs");
    println!("cargo:rerun-if-changed={}", abi_path.display()); // Penting: Agar build.rs jalan lagi jika ABI berubah

    Ok(())
}