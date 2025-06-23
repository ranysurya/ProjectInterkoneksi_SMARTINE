# 🐣 Smartine : _Smart Incubator Egg Instrument_ Sistem Monitoring Suhu dan Kelembaban untuk Inkubator Telur Berbasis IoT dan Visualisasi _Realtime_


## 📘 Deskripsi Proyek
**Smartine adalah** sistem monitoring suhu dan kelembapan pada mesin penetas telur ayam yang dapat dipantau secara real-time. Dirancang untuk membantu peternak rumahan, **alat ini menjaga kestabilan inkubasi** agar proses penetasan lebih **efisien** **dan akurat**. **Dengan sensor digital (SHT), pencatatan data otomatis, dan tampilan visual yang informatif, peternak dapat meningkatkan tingkat keberhasilan menetas dan mempercepat waktu panen.** Inovasi ini juga mendorong adopsi teknologi di sektor peternakan serta membuka peluang kolaborasi bagi mahasiswa dan pengembang dalam menghadirkan solusi berbasis data dan teknologi terkini. Dari sisi bisnis, sistem ini memberikan solusi yang ekonomis namun berdampak besar. Peternak dapat meningkatkan jumlah telur yang berhasil menetas, mempercepat siklus panen, dan meningkatkan daya saing di pasar lokal maupun nasional.

---

## 🎓 Mata Kuliah
- **[Interkoneksi Sistem Instrumentasi]** – Program Studi Teknik Instrumentasi
- Dosen Pengampu: [Ahmad Radhy, S.Si., M.Si]

---
## 👨‍💻 Anggota Kelompok
| Nama | NIM | 
|------|-----|
| [Raffi Fitra Akbar] | [2042231018] | 
| [Rafi Muhammad Zhafir] | [2042231038] | 
| [Rany Surya Oktavia] | [2042231060] | 

---

## 📚 State Of The Art
| Topik, Penulis, dan Tahun | Teknologi yang Digunakan | Hasil|
|------|-----|-----|
| Sistem Monitoring Suhu Pada Inkubator Penetas Telur Berbasis IoT. Yunus et al. (2024) | Sensor DHT11, NodeMCU ESP8266, platform Blynk |Sistem efektif dalam meningkatkan kualitas penetasan telur dan efisiensi pemantauan |
| Monitoring Inkubator Telur Menggunakan Protokol ESP-MESH. Asyam & Purwoto (2024)| ESP32 & ESP8266, sensor SHTC3, protokol ESP-MESH, platform Thinger.io |Akurasi tinggi (error suhu 0,79%, kelembapan 7,69%), sistem efisien untuk banyak inkubator|
| Sistem Monitoring Suhu dan Kelembaban Berbasis IoT pada Ruang Data Center. Kusumah et al. (2023) | Sensor DHT11, NodeMCU ESP8266, OLED I2C, MQTT, dashboard web |Error suhu 1,7%, kelembapan 2,1%, sistem stabil dan efisien |

---

## ⚙️ Fitur Utama
- ✅ Monitoring Suhu & Kelembaban Real-Time 
- ✅ Penyimpanan Data Historis 
- ✅ Visualisasi Data 
- ✅ Blockchain-based Data Logging, untuk Menjamin keaslian & keamanan data inkubasi


---

## ⚙️ Tutorial Run Program
1.	Langkah pertama adalah menjalankan layanan berbasis Node.js. 
2.	Buka terminal atau command prompt, lalu arahkan direktori kerja ke folder project Node menggunakan perintah cd Dokuments/ISI. ![image](https://github.com/user-attachments/assets/c0c5cabd-0944-40d8-bf00-b3c86ac254ac)
3.	Setelah itu, jalankan program dengan perintah node index.js atau gunakan node start_dev_env jika script sudah didefinisikan dalam file package.json.                     ![image](https://github.com/user-attachments/assets/5dd11cdb-2ce3-4f7f-ba15-90a08b1190ab)
4.	Jika sudah maka akan tertulis Hardhat node dan deploy selesai. Biarkan terminal ini terbuka untu Hardhat node
5.	Selanjutnya, jalankan program TCP server yang ditulis menggunakan bahasa pemrograman Rust. 
6.	Buka terminal baru agar proses sebelumnya tetap berjalan
7.	Kemudian arahkan direktori ke folder proyek TCP server, cd telur_tcp_server/ ![image](https://github.com/user-attachments/assets/7ad6b1b2-a6f2-4ac2-9199-99fa91553d8d)
8.	Setelah berada di direktori yang benar, jalankan program dengan perintah cargo run. Program ini akan memulai server TCP untuk menerima dan mengelola koneksi dari client.
9.	Setelah TCP server berjalan, lanjutkan dengan menjalankan program Modbus yang juga dibuat dengan Rust. ![image](https://github.com/user-attachments/assets/4401ec7b-808b-448c-8e00-9ac21c816903)
10.	Buka terminal baru kembali, lalu pindah ke folder project Modbus dengan perintah cd modbus_client/. Jalankan program ini menggunakan perintah cargo run, yang akan menginisialisasi komunikasi protokol Modbus.
11.	Berikutnya, jalankan antarmuka pengguna (GUI) yang dikembangkan menggunakan Python dan framework Qt. 
12.	Buka terminal baru, arahkan direktori kerja ke folder GUI, cd Qt/. ![image](https://github.com/user-attachments/assets/10db9954-a794-4ef9-851d-a2ca0d7ff42f)
13.	Sebelum menjalankan program, aktifkan virtual environment dengan perintah source venv_coffe/bin/activate, yang akan mengatur lingkungan Python agar sesuai dengan dependensi yang telah disiapkan. 
14.	Lakukan install influx db client dengan sourse pip install influxdb-client ![image](https://github.com/user-attachments/assets/1647459e-880b-45c5-a7ef-a1f36741b66a)
15.	Sebelum melakukan perintah ke python, tulis source pip install PyQt5 untuk menginstall 
16.	Setelah environment aktif, jalankan file utama GUI dengan perintah python3 main.py. sebelum itu install pyqtgraph ![image](https://github.com/user-attachments/assets/bdaac3ef-9203-4f4b-b813-2a4c966dfd3f)
17.	Terakhir, jalankan tampilan web (frontend) berbasis Node.js
18.	Buka terminal baru lagi, lalu pindah ke direktori project web frontend menggunakan perintah cd sensor_dapp_frontend/ ![image](https://github.com/user-attachments/assets/a077faa1-2d3f-4635-8cdf-cd169a3373f2)
19.	Setelah itu, aktifkan mode pengembangan dengan perintah node npm run dev yang akan memulai server lokal dan menampilkan antarmuka web yang terhubung dengan backend dan sistem lainnya.
20.	Dari local host yang tertera, buka firefox dan search laman http://localhost:5173/
21.	Maka akan tertampil sebagai berikut ![image](https://github.com/user-attachments/assets/5dbffc6a-e368-4a6b-823c-99f5bf9c0108)
22.	Jika ingin menghubungkan ke metamask, klik pada extension di dalam firefox lalu klik pada Metamask untuk menghubungkan blockchain
23.	Setelah itu klik pada tampilan kiri, Lalu klik ‘add a custom network’ 
24.	Lalu sesuaikan dengan localhost dan klik save
25.	kemudian klik panah ke bawah di sebelah account, lalu klik ‘add account or hardware wallet, lalu klik private keys, Kemudian isikan Private Keys dan klik import.
26.	Kemudian klik ‘muat data sensor’ pada halaman Web3, kemudian akan muncul tampilan dari extension metamask. Kemudian klik connect maka tampilan dari Web3 akan menampilkan tabel dari data yang telah dikirimkan ke TCP Server

---

## 🛠️ Implementasi dan Kode Program
**- Rust Modbust Client**
async fn send_to_server(
    sensor_id: &str,
    location: &str,
    process_stage: &str,
    temperature: f32,
    humidity: f32,
    timestamp: chrono::DateTime<Local>,
) -> Result<(), Box<dyn Error>> {
    let mut stream = TcpStream::connect("127.0.0.1:7878").await?;
    
    let payload = json!({
        "timestamp": timestamp.to_rfc3339_opts(SecondsFormat::Secs, true),
        "sensor_id": sensor_id,
        "location": location,
        "process_stage": process_stage,
        "temperature_celsius": temperature,
        "humidity_percent": humidity
    });

    let json_str = payload.to_string();
    println!("Sending JSON: {}", json_str);
    
    stream.write_all(json_str.as_bytes()).await?;
    let mut buf = [0; 1024];
    let n = stream.read(&mut buf).await?;
    println!("Server response: {}", std::str::from_utf8(&buf[..n])?);
    
    Ok(())
}

  
**- Rust TCP Server**
  #[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let influx_url = "http://localhost:8086";
    let influx_org = "Institute Teknologi Sepuluh Nopember";
    let influx_token = "hkyHqP236AVjN2JL84XYNJVPWCDXnC756c1Gxc2CO6n_nkG-dCTLB3Ik-c761g3YRqasOSGRZrOandYZhN8QrQ==";
    let influx_bucket = "coffe_monitoring_db";

    let client = Client::new(influx_url, influx_org, influx_token);

    match client.health().await {
        Ok(health) => println!("InfluxDB connection healthy: {:?}", health),
        Err(e) => {
            eprintln!("Failed to connect to InfluxDB: {}", e);
            return Err(e.into());
        }
    }

    let listener = TcpListener::bind("127.0.0.1:7878").await?;
    println!("Server running on 127.0.0.1:7878");

    loop {
        let (mut socket, _) = listener.accept().await?;
        let client = client.clone();
        let bucket = influx_bucket.to_string();
        
        tokio::spawn(async move {
            let mut buf = [0; 1024];
            
            match socket.read(&mut buf).await {
                Ok(n) if n == 0 => return,
                Ok(n) => {
                    let data = match std::str::from_utf8(&buf[..n]) {
                        Ok(d) => d,
                        Err(e) => {
                            eprintln!("Error parsing data: {}", e);
                            let _ = socket.write_all(b"ERROR: Invalid UTF-8 data").await;
                            return;
                        }
                    };
                    
                    println!("Received raw data: {}", data);
                    
                    match serde_json::from_str::<SensorData>(data) {
                        Ok(sensor_data) => {
                            // Parsing timestamp dan menyusun DataPoint
                            let timestamp = match DateTime::parse_from_rfc3339(&sensor_data.timestamp) {
                                Ok(dt) => dt.with_timezone(&Utc),
                                Err(e) => {
                                    eprintln!("Invalid timestamp format: {}", e);
                                    let _ = socket.write_all(b"ERROR: Invalid timestamp format").await;
                                    return;
                                }
                            };

                            let timestamp_ns = timestamp.timestamp_nanos_opt().unwrap_or(0);

                            let point = DataPoint::builder("environment_monitoring")
                                .tag("sensor_id", &sensor_data.sensor_id)
                                .tag("location", &sensor_data.location)
                                .tag("process_stage", &sensor_data.process_stage)
                                .field("temperature_celsius", sensor_data.temperature_celsius)
                                .field("humidity_percent", sensor_data.humidity_percent)
                                .timestamp(timestamp_ns)
                                .build()
                                .unwrap();

                            match client.write(&bucket, stream::iter(vec![point])).await {
                                Ok(_) => {
                                    println!("Data successfully written to InfluxDB");
                                    let _ = socket.write_all(b"OK").await;
                                },
                                Err(e) => {
                                    eprintln!("Failed to write to InfluxDB: {}", e);
                                    let _ = socket.write_all(
                                        format!("ERROR: Database write failed - {}", e).as_bytes()
                                    ).await;
                                }
                            }
                        }
                        Err(e) => {
                            eprintln!("Error parsing JSON: {}", e);
                            let _ = socket.write_all(
                                format!("ERROR: Invalid JSON - {}", e).as_bytes()
                            ).await;
                        }
                    }
                }
                Err(e) => eprintln!("Error reading socket: {}", e),
            }
        });
    }
}

---

## 📚 Analisa Hasil Pengujian
 ![image](https://github.com/user-attachments/assets/498bc7ef-a226-4001-aea5-644eccb75d73)
![image](https://github.com/user-attachments/assets/6c94d5af-c500-4c18-bc37-be5584ea7a33)
Gambar tersebut menyajikan dokumentasi hasil pembacaan suhu dan kelembaban selama proses inkubasi yang berlangsung. Data tersebut ditampilkan dalam bentuk hasil penyimpanan di database time-series InfluxDB dan tampilan real-time dashboard pada platform visualisasi Grafana. Pada InfluxDB menunjukkan bahwa data berhasil direkam secara berkala dengan struktur timestamp, field value, dan tag yang merepresentasikan parameter suhu dan kelembaban dari sensor. Sementara itu, pada dashboard Grafana terlihat grafik dinamis yang merekam perubahan nilai suhu dan kelembaban sepanjang waktu, memungkinkan pengguna untuk melakukan pemantauan secara langsung.
Berdasarkan analisis terhadap grafik dan data yang ditampilkan, nilai suhu selama proses inkubasi umumnya berada pada rentang 25–29 °C, sedangkan kelembaban berkisar antara 55–68%. Hal ini menunjukkan bahwa kedua parameter tersebut berada dalam rentang optimal yang direkomendasikan, yaitu 24–30 °C untuk suhu dan 50–70% untuk kelembaban. Kondisi ini dianggap stabil dan sesuai untuk mendukung proses inkubasi, sehingga peluang keberhasilan penetasan telur atau pertumbuhan biologis dalam ruang inkubasi dapat dikatakan tinggi.
![image](https://github.com/user-attachments/assets/fdc2ca8f-93c5-4b0e-ab68-5478283dd8d1)
![image](https://github.com/user-attachments/assets/47fe8f9c-11c2-4975-a372-849d837722cf)

---
##  Kesimpulan
1.	Proyek ini berhasil merancang dan mengimplementasikan sistem pemantauan suhu dan kelembaban berbasis Internet of Things (IoT) menggunakan sensor SHT20 dan protokol Modbus RTU yang diolah oleh Modbus client berbasis Rust. Data yang dibaca dikirimkan melalui TCP server dan disimpan dalam InfluxDB, lalu divisualisasikan secara real-time melalui dashboard Grafana dan antarmuka Qt.
2.	Arsitektur sistem berhasil mengintegrasikan berbagai komponen secara modular dan berlapis, mulai dari sensor, pemrosesan data, penyimpanan basis data, hingga visualisasi pada platform web dan GUI Python. Penggunaan Rust memberikan efisiensi dan keandalan tinggi dalam komunikasi data TCP dan proses parsing JSON.
3.	Berdasarkan hasil pengujian, suhu selama proses inkubasi berkisar antara 25–29 °C dan kelembaban 55–68%, yang keduanya berada dalam rentang optimal yang direkomendasikan untuk proses inkubasi telur (suhu 24–30 °C dan kelembaban 50–70%). Hal ini menunjukkan bahwa sistem mampu menjalankan fungsinya secara akurat dan konsisten dalam mendukung proses biologis.
4.	Dashboard Grafana dan GUI Python Qt mampu menyajikan grafik waktu nyata yang memudahkan pengguna dalam memantau tren suhu dan kelembaban secara historis maupun saat ini, sekaligus memungkinkan interaksi berbasis Web3 melalui integrasi dengan Metamask.

---
## 🖼️ Dokumentasi 

📹 PPT : https://its.id/m/PPTProjectISISmartine_Kelompok3  

📷 Laporan : https://its.id/m/LaporanAkhirProjectInterkoneksi_Kelompok3 


---

## 📌 Saran untuk Pengembangan Selanjutnya
- Integrasi Kecerdasan Buatan (AI) untuk Prediksi dan Optimasi Penetasan 
- Fitur Prediksi Waktu Tetas Otomatis 
- Integrasi Kamera Mini untuk Pemantauan Visual 
- Fitur Marketplace Internal 

---

## 🔖 Lisensi
SMARTINE_TEKINS23_ITS

---

> 🐥 “Tetas Lebih Cerdas, Panen Lebih Cepat!, Smartine: Awal Cerdas untuk Anak Ayam Berkualitas.”  
> Tim Smartine

