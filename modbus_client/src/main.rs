use chrono::{Local, SecondsFormat, Duration as ChronoDuration};
use tokio_modbus::{client::rtu, prelude::*};
use tokio_serial::SerialStream;
use tokio::{
    net::TcpStream,
    time::{sleep, Duration},
    io::AsyncWriteExt,
};
use serde_json::json;
use std::error::Error;
use once_cell::sync::OnceCell;
use chrono::DateTime;

// --- Import Baru untuk File I/O ---
use std::fs;
use std::io::{self, Read, Write}; // Mengimpor Read dan Write untuk operasi file

// Definisi path untuk file yang akan menyimpan tanggal mulai inkubasi
const START_DATE_FILE: &str = "incubation_start_date.txt";

// Variabel statis untuk menyimpan waktu mulai inkubasi (akan dimuat/diinisialisasi sekali)
static INCUBATION_START_TIME: OnceCell<DateTime<Local>> = OnceCell::new();

// --- Fungsi Baru: Membaca tanggal mulai dari file ---
fn read_start_date() -> Result<DateTime<Local>, Box<dyn Error>> {
    let mut file = fs::File::open(START_DATE_FILE)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    
    // Parse tanggal dari string RFC3339 yang disimpan
    let dt = DateTime::parse_from_rfc3339(&contents.trim())?
        .with_timezone(&Local); // Pastikan dikonversi ke zona waktu lokal
    Ok(dt)
}

// --- Fungsi Baru: Menulis tanggal mulai ke file ---
fn write_start_date(start_time: &DateTime<Local>) -> Result<(), Box<dyn Error>> {
    let mut file = fs::File::create(START_DATE_FILE)?;
    file.write_all(start_time.to_rfc3339().as_bytes())?;
    Ok(())
}

// Fungsi untuk membaca data dari sensor SHT20 melalui Modbus RTU (TIDAK BERUBAH)
async fn sht20(slave: u8) -> Result<Vec<u16>, Box<dyn Error>> {
    let port = tokio_serial::new("/dev/ttyUSB0", 9600) 
        .parity(tokio_serial::Parity::None)
        .stop_bits(tokio_serial::StopBits::One)
        .data_bits(tokio_serial::DataBits::Eight)
        .timeout(Duration::from_secs(1));
    
    let port = SerialStream::open(&port)?;
    let slave = Slave(slave);
    
    let response = {
        let mut ctx = rtu::attach_slave(port, slave);
        ctx.read_input_registers(1, 2).await? 
    };

    Ok(response)
}

// Fungsi untuk mengirim data sensor ke Rust TCP Server (TIDAK BERUBAH)
async fn send_to_server(
    sensor_id: &str,
    location: &str,
    process_stage: &str, // Ini akan jadi Usia Telur (Hari)
    temperature: f32,
    humidity: f32,
    timestamp: chrono::DateTime<Local>,
) -> Result<(), Box<dyn Error>> {
    let server_address = "127.0.0.1:7877"; 
    let mut stream = TcpStream::connect(server_address).await?;
    
    let payload = json!({
        "timestamp": timestamp.to_rfc3339_opts(SecondsFormat::Secs, true),
        "sensor_id": sensor_id,
        "location": location,
        "process_stage": process_stage, // Menggunakan ini untuk Usia Telur
        "temperature_celsius": temperature,  
        "humidity_percent": humidity        
    });

    let mut json_str = payload.to_string();
    json_str.push('\n'); 

    println!("Sending JSON to {}: {}", server_address, json_str.trim());
    
    stream.write_all(json_str.as_bytes()).await?;
    
    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let sensor_id_base = "SHT20-Smartine";
    let location_name = "Inkubator 1"; 
    let current_sensor_id = sensor_id_base.to_string(); 

    INCUBATION_START_TIME.get_or_init(|| {
        match read_start_date() {
            Ok(dt) => {
                println!("Inkubasi dimulai (dari file): {}", dt.format("%Y-%m-%d %H:%M:%S"));
                dt
            },
            Err(e) => {
                eprintln!("Gagal membaca tanggal mulai inkubasi dari file ({}). Menetapkan waktu saat ini sebagai awal: {}", START_DATE_FILE, e);
                let new_start_time = Local::now();
                if let Err(write_err) = write_start_date(&new_start_time) {
                    eprintln!("Gagal menyimpan tanggal mulai inkubasi ke file: {}", write_err);
                } else {
                    println!("Inkubasi dimulai (baru): {}", new_start_time.format("%Y-%m-%d %H:%M:%S"));
                }
                new_start_time
            }
        }
    });
    let start_time = INCUBATION_START_TIME.get().unwrap(); 

    loop {
        let timestamp = Local::now();
        
        let elapsed_duration: ChronoDuration = timestamp.signed_duration_since(*start_time);
        let current_egg_age_days = elapsed_duration.num_days();

        let display_egg_age = if current_egg_age_days >= 0 { 
            current_egg_age_days + 1 
        } else { 
            1 
        };
        
        let process_stage_str = format!("Hari ke-{}", display_egg_age);

        match sht20(1).await {
            Ok(response) if response.len() == 2 => {
                let temp = response[0] as f32 / 10.0; 
                let rh = response[1] as f32 / 10.0;   
                
                println!("[{}] {} - {}: Temp={:.1}°C, RH={:.1}%", 
                    timestamp.format("%Y-%m-%d %H:%M:%S"),
                    location_name,      
                    process_stage_str,  
                    temp,
                    rh);
                
                if let Err(e) = send_to_server(
                    &current_sensor_id, 
                    &location_name,     
                    &process_stage_str, 
                    temp, 
                    rh,
                    timestamp
                ).await {
                    eprintln!("Failed to send data to TCP Server: {}", e);
                }
            }
            Ok(invalid) => eprintln!("Invalid sensor response length: {:?}", invalid),
            Err(e) => eprintln!("Sensor read error: {}", e),
        }
        
        sleep(Duration::from_secs(10)).await;
    }
}