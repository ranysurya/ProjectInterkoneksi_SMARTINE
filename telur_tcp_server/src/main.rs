// src/main.rs (Untuk Rust TCP Server Anda)
use tokio::net::{TcpListener, TcpStream};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::sync::broadcast; 
use tokio::sync::broadcast::error::RecvError;
use serde::{Deserialize, Serialize};
use serde_json;
use std::sync::{Arc, Mutex};
use std::time::Duration;
use chrono::{Utc, DateTime, Local};
use influxdb2::Client;
use influxdb2::models::DataPoint;
use futures::stream;

// --- Impor untuk Web3 ---
use ethers::{
    providers::{Http, Provider},
    signers::{LocalWallet, Signer},
    types::{Address, U256},
    middleware::SignerMiddleware,
};
use std::str::FromStr;
use dotenv::dotenv;
use hex;

// --- Tambahkan ini untuk membaca file JSON
use std::fs;
use std::path::PathBuf;

// --- Impor Kontrak yang Digenerate oleh build.rs ---
#[allow(warnings)]
mod sensor_data_contract {
    include!(concat!(env!("OUT_DIR"), "/sensor_data_contract.rs"));
}
use sensor_data_contract::SensorDataContract;


// Struktur data yang sama seperti payload JSON
#[derive(Debug, Clone, Serialize, Deserialize)]
struct SensorData {
    timestamp: String,
    sensor_id: String,
    location: String,
    process_stage: String,
    temperature_celsius: f64,
    humidity_percent: f64,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenv().ok(); // Muat variabel lingkungan, misal HARDHAT_PROVIDER_URL

    // --- Konfigurasi Hardhat Blockchain (BACA DARI FILE JSON) ---
    let hardhat_provider_url = std::env::var("HARDHAT_PROVIDER_URL")
        .unwrap_or_else(|_| "http://127.0.0.1:8545".to_string());
    
    // Tentukan jalur ke file SensorData.json yang dihasilkan Hardhat
    // Asumsi hardhat_sensor_contract berada di satu level di atas telur_tcp_server
    let contract_info_path = PathBuf::from("../hardhat_sensor_contract/contract_info/SensorData.json");

    // Baca file JSON yang berisi alamat kontrak dan private key
    let contract_info_content = fs::read_to_string(&contract_info_path)
        .expect(&format!("Failed to read contract_info.json at {:?}. Did you run `npx hardhat run scripts/deploy.js` in hardhat_sensor_contract directory?", contract_info_path));
    let contract_info: serde_json::Value = serde_json::from_str(&contract_info_content)?;

    // Ekstrak alamat kontrak dan private key dari JSON
    let contract_address_str = contract_info["address"].as_str()
        .expect("Contract address not found in JSON").to_string();
    let private_key_str = contract_info["privateKey"].as_str()
        .expect("Private key not found in JSON").to_string();


    // Inisialisasi Provider (koneksi ke node Hardhat)
    let provider = Provider::<Http>::try_from(hardhat_provider_url.clone())?;
    let provider_arc = Arc::new(provider);

    // Inisialisasi Signer (akun pengirim transaksi)
    let private_key_bytes: Vec<u8> = hex::decode(private_key_str.strip_prefix("0x").unwrap_or(&private_key_str))?;
    let wallet = LocalWallet::from_bytes(&private_key_bytes)?.with_chain_id(31337_u64); // 31337 adalah Chain ID default Hardhat
    let wallet_address = wallet.address();
    let wallet_arc = Arc::new(wallet);
    println!("Wallet address: {:?}", wallet_address);

    // Inisialisasi Kontrak Smart Contract
    let contract_address = Address::from_str(&contract_address_str)?;
    
    // Inisialisasi client dengan provider dan signer
    let client = Arc::new(SignerMiddleware::new(provider_arc.clone(), (*wallet_arc).clone()));

    // Sekarang inisialisasi kontrak dengan client yang sudah memiliki signer
    let contract = SensorDataContract::new(contract_address, client.clone());
    println!("Smart Contract address: {:?}", contract_address);


    // --- Konfigurasi InfluxDB ---
    let influx_url = "http://localhost:8086";
    let influx_org = "Institute Teknologi Sepuluh Nopember";
    let influx_token = "hkyHqP236AVjN2JL84XYNJVPWCDXnC756c1Gxc2CO6n_nkG-dCTLB3Ik-c761g3YRqasOSGRZrOandYZhN8QrQ=="; // Ganti dengan token Anda
    let influx_bucket = "telur_monitoring_db";

    let influx_client = Arc::new(Client::new(influx_url, influx_org, influx_token));

    match influx_client.health().await {
        Ok(health) => println!("InfluxDB connection healthy: {:?}", health),
        Err(e) => {
            eprintln!("Failed to connect to InfluxDB: {}", e);
        }
    }

    // --- Definisi Alamat Listener ---
    let gui_client_listen_addr = "127.0.0.1:7878";
    let modbus_input_addr = "127.0.0.1:7877";

    let gui_listener = TcpListener::bind(gui_client_listen_addr).await?;
    println!("Server (untuk klien GUI Qt) mendengarkan di {}", gui_client_listen_addr);

    let modbus_input_listener = TcpListener::bind(modbus_input_addr).await?;
    println!("Server (untuk Rust Modbus Client) mendengarkan di {}", modbus_input_addr);

    // --- State Bersama: Data Sensor Terbaru & Broadcast Channel ---
    let latest_sensor_data_arc: Arc<Mutex<Option<SensorData>>> = Arc::new(Mutex::new(None));
    let (tx_data_broadcast, _rx_data_broadcast) = broadcast::channel::<SensorData>(16);

    // --- TASK: MENERIMA DATA DARI RUST MODBUS CLIENT (INCOMING DATA) ---
    let tx_modbus_clone = tx_data_broadcast.clone();
    let latest_data_modbus_clone = latest_sensor_data_arc.clone();
    let influx_client_modbus_clone = influx_client.clone();
    let influx_bucket_modbus_clone = influx_bucket.to_string();

    let contract_clone_for_tx = contract.clone();


    tokio::spawn(async move {
        println!("Task penerima data dari Modbus Client siap.");
        loop {
            let (mut stream, _) = match modbus_input_listener.accept().await {
                Ok(s) => s,
                Err(e) => {
                    eprintln!("Error menerima koneksi Modbus Client: {}", e);
                    tokio::time::sleep(Duration::from_secs(5)).await;
                    continue;
                }
            };
            println!("Koneksi baru dari Rust Modbus Client diterima.");

            let mut buffer = Vec::new();
            
            loop {
                let bytes_read = match stream.read_buf(&mut buffer).await {
                    Ok(0) => {
                        println!("Rust Modbus Client menutup koneksi.");
                        break;
                    },
                    Ok(n) => n,
                    Err(e) => {
                        eprintln!("Error membaca dari Rust Modbus Client: {}", e);
                        break;
                    }
                };
                
                if bytes_read == 0 && buffer.is_empty() {
                    tokio::time::sleep(Duration::from_millis(100)).await;
                    continue;
                }

                let mut cursor = 0;
                while let Some(newline_pos) = buffer[cursor..].iter().position(|&b| b == b'\n') {
                    let line_end = cursor + newline_pos;
                    let line = &buffer[cursor..line_end];
                    
                    if line.is_empty() {
                        cursor = line_end + 1;
                        continue;
                    }

                    match serde_json::from_slice::<SensorData>(line) {
                        Ok(sensor_data) => {
                            println!("Data diterima dari Modbus: {:?}", sensor_data);
                            
                            // --- PENULISAN KE INFLUXDB ---
                            let timestamp_influx = match DateTime::parse_from_rfc3339(&sensor_data.timestamp) {
                                Ok(dt) => dt.with_timezone(&Utc),
                                Err(e) => {
                                    eprintln!("Invalid timestamp format for InfluxDB: {}", e);
                                    cursor = line_end + 1;
                                    continue;
                                }
                            };

                            let timestamp_ns = timestamp_influx.timestamp_nanos_opt().unwrap_or_else(|| {
                                eprintln!("Warning: InfluxDB timestamp conversion failed, using 0 as fallback");
                                0
                            });

                            let point = DataPoint::builder("environment_monitoring")
                                .tag("sensor_id", &sensor_data.sensor_id)
                                .tag("location", &sensor_data.location)
                                .tag("process_stage", &sensor_data.process_stage)
                                .field("temperature_celsius", sensor_data.temperature_celsius)
                                .field("humidity_percent", sensor_data.humidity_percent)
                                .timestamp(timestamp_ns)
                                .build()
                                .expect("Failed to build DataPoint");
                            
                            let client_clone = influx_client_modbus_clone.clone();
                            let bucket_clone = influx_bucket_modbus_clone.clone();
                            tokio::spawn(async move {
                                match client_clone.write(&bucket_clone, stream::iter(vec![point])).await {
                                    Ok(_) => { /* println!("Data successfully written to InfluxDB"); */ },
                                    Err(e) => {
                                        eprintln!("Failed to write to InfluxDB: {}", e);
                                    }
                                }
                            });
                            // --- END INFLUXDB WRITE ---

                            // --- PENULISAN KE BLOCKCHAIN (HARDHAT) ---
                            let contract_for_tx = contract_clone_for_tx.clone();
                            let current_sensor_data = sensor_data.clone();

                            tokio::spawn(async move {
                                let timestamp_unix: U256;
                                if let Ok(dt) = DateTime::parse_from_rfc3339(&current_sensor_data.timestamp) {
                                    timestamp_unix = U256::from(dt.timestamp());
                                } else {
                                    eprintln!("Invalid timestamp for blockchain, using current time.");
                                    timestamp_unix = U256::from(Local::now().timestamp());
                                }

                                let temp_u16 = current_sensor_data.temperature_celsius as u16;
                                let humid_u16 = current_sensor_data.humidity_percent as u16;

                                println!("Sending to blockchain: T={}, H={}, S_ID={}, Loc={}, Stage={}",
                                    temp_u16, humid_u16, &current_sensor_data.sensor_id, &current_sensor_data.location, &current_sensor_data.process_stage);

                                match contract_for_tx.add_sensor_reading(
                                    timestamp_unix,
                                    temp_u16,
                                    humid_u16,
                                    current_sensor_data.sensor_id,
                                    current_sensor_data.location,
                                    current_sensor_data.process_stage,
                                ).send().await {
                                    Ok(tx_receipt) => {
                                        println!("Transaction sent to blockchain. Tx Hash: {:?}", tx_receipt.tx_hash());
                                        match tx_receipt.await {
                                            Ok(Some(receipt)) => println!("Transaction mined. Receipt: {:?}", receipt.transaction_hash),
                                            Ok(None) => eprintln!("Transaction not found in receipt (might still be pending or failed)."),
                                            Err(e) => eprintln!("Error waiting for transaction receipt: {}", e),
                                        }
                                    },
                                    Err(e) => {
                                        eprintln!("Failed to send transaction to blockchain: {}", e);
                                    }
                                }
                            });

                            // --- END BLOCKCHAIN WRITE ---

                            *latest_data_modbus_clone.lock().unwrap() = Some(sensor_data.clone());
                            if let Err(e) = tx_modbus_clone.send(sensor_data) {
                                eprintln!("Error mengirim data ke broadcast channel: {}", e);
                            }
                        },
                        Err(e) => {
                            eprintln!("Error parsing JSON dari Modbus Client: {} | Data: {:?}", e, String::from_utf8_lossy(line));
                        }
                    }
                    cursor = line_end + 1;
                }
                if cursor > 0 {
                    buffer.drain(0..cursor);
                }

                tokio::time::sleep(Duration::from_millis(10)).await;
            }
        }
    });

    // --- LOOP UTAMA: MENERIMA KONEKSI DARI KLIEN GUI QT ---
    loop {
        let (socket, _) = gui_listener.accept().await?;
        println!("Koneksi klien GUI Qt baru diterima.");

        let tx_for_client = tx_data_broadcast.clone();
        let latest_data_client_clone = latest_sensor_data_arc.clone();

        tokio::spawn(async move {
            handle_gui_client(socket, tx_for_client, latest_data_client_clone).await;
        });
    }
}

// --- FUNGSI: MENANGANI KONEKSI KLIEN GUI QT ---
async fn handle_gui_client(
    mut stream: TcpStream,
    tx_broadcast: broadcast::Sender<SensorData>,
    latest_sensor_data_arc: Arc<Mutex<Option<SensorData>>>,
) {
    let mut rx_client = tx_broadcast.subscribe();

    let initial_data_clone = {
        let latest_data_guard = latest_sensor_data_arc.lock().unwrap();
        latest_data_guard.clone()
    };

    if let Some(data) = initial_data_clone {
        let json_payload = serde_json::to_string(&data).expect("Failed to serialize sensor data");
        if let Err(e) = stream.write_all(format!("{}\n", json_payload).as_bytes()).await {
            eprintln!("Error mengirim data awal ke klien GUI Qt: {}", e);
            return;
        }
    }

    loop {
        tokio::select! {
            result = rx_client.recv() => {
                match result {
                    Ok(data) => {
                        let json_payload = serde_json::to_string(&data).expect("Failed to serialize sensor data");
                        if let Err(e) = stream.write_all(format!("{}\n", json_payload).as_bytes()).await {
                            eprintln!("Error mengirim data ke klien GUI Qt: {}", e);
                            break;
                        }
                    },
                    Err(RecvError::Lagged(skipped)) => {
                        eprintln!("Broadcast receiver lagged, skipped {} messages. Klien mungkin tidak mendapatkan data terbaru.", skipped);
                        let latest_data_after_lagged = {
                            let guard = latest_sensor_data_arc.lock().unwrap();
                            guard.clone()
                        };
                        if let Some(data) = latest_data_after_lagged {
                             let json_payload = serde_json::to_string(&data).expect("Failed to serialize sensor data");
                             if let Err(e) = stream.write_all(format!("{}\n", json_payload).as_bytes()).await {
                                 eprintln!("Error mengirim data setelah lagged: {}", e);
                                 break;
                             }
                        }
                    },
                    Err(RecvError::Closed) => {
                        println!("Broadcast channel ditutup, klien GUI Qt akan putus koneksi.");
                        break;
                    },
                }
            },
            _ = stream.readable() => {
                let mut buf = vec![0; 1];
                match stream.peek(&mut buf).await {
                    Ok(0) => {
                        println!("Klien GUI Qt menutup koneksi.");
                        break;
                    }
                    Ok(_) => {
                        let _ = stream.read_exact(&mut buf).await;
                    }
                    Err(e) => {
                        eprintln!("Error saat memantau stream klien GUI Qt: {}", e);
                        break;
                    }
                }
            }
        }
    }
    println!("Koneksi klien GUI Qt berakhir.");
}