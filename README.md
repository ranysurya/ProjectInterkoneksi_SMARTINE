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
## Latar Belakang
    Saat ini sektor peternakan menjadi sektor yang cukup penting untuk memenuhi kebutuhan pangan masyarakat Indonesia, karena produk peternak merupakan sumber protein hewani. Permintaan terhadap produk peternakan khususnya daging ayam terus meningkat setiap tahunnya. Oleh karena itu para peternak juga membutuhkan sebuah teknologi untuk menghasilkan bibit yang berkualitas dari telur yang dipanen. Jika sebelumnya para peternak melakukan proses panen telur secara manual atau konvensional dengan jarak panen sekitar 21 sampai 30 hari masa panen untuk satu induk ayam. Hal ini akan menjadi permasalahan bagi para peternak ayam yang hanya memiliki induk siap panen yang sedikit. 
Selain itu kondisi lingkungan yang kurang optimal juga akan mempengaruhi proses penetasan telur. Untuk mengatasi permasalahan ini telah diteliti suatu alat berupa mesin penetas telur untuk meningkatkan produktifitas dan daya telur yang cukup besar sehingga penetasan menjadi lebih efisien dan banyak. Keberhasilan pada mesin penetas ini dipengaruhi beberapa faktor diantaranya yaitu suhu yang ideal sekitar 38°-39° Celcius (Nisa & Andreansyah, 2024). Apabila telur ayam menetas di hari ke 20-21, maka telur menetas pada waktu yang sesuai dengan suhu yang stabil. Namun apabila telur menetas pada hari ke 18-19 berarti suhu yang digunakan terlalu tinggi dan akan menyebabkan kematian bagi anak ayam. Faktor lain yang mempengaruhi adalah kelembapan, untuk menetaskan telur kelembapan yang harus diperhatikan yaitu sekitar 35%-60% (Nisa & Andreansyah, 2024). 
    Dengan mesin ini kelembapan dan suhu akan tetap stabil karena para peternak dapat melakukan monitoring dan mendapatkan informasi mengenai perkembangan dan kondisi saat proses penetasan sehingga mampu mengurangi terjadinya kematian pada anak ayam. Hal ini terjadi karena mesin ini sudah dilengkapi dengan teknologi berbasis Internet of Things. Internet of Things (IoT) adalah sistem komputerisasi yang dapat terhubung atau berkomunikasi dengan mesin elektronik serta dapat melakukan pertukaran data melalui jaringan internet sehingga dapat mempermudah pekerjaan manusia(Venty et al., 2020). Dengan menggunakan konsep Internet of Things (IoT) akan sangat memudahkan para peternak karena para peternak dapat melakukan pemantauan secara real-time melalui sensor yang terhubung ke jaringan mengenai kondisi di dalam inkubator seperti suhu, kelembapan dan rotasi telur dimanapun dan kapanpun.
    Dengan menggunakan konsep IOT sistem monitoring suhu dan pencahayaan akan lebih mudah dan tidak perlu memonitor langsung ke kandang, tinggal kita koneksikan alat dan memonitor nya langsung melalui aplikasi berbasis mobile, memonitoring lebih efektif dan membantu peningkatan masa panen dan menekan tingkat quantity dari telur hasil bibit unggul induk ayam yang menetas. Dalam penulisan ini penulis tertarik membuat sistem monitoring suhu dan pencahayaan pada inkubator melalui aplikasi, sehingga membantu peternak dalam memonitoring ruang inkubator memalui gadget tanpa harus memonitor langsung ke kandang dan meningkatkan masa panen. Diharapkan dengan adanya inovasi ini dapat meningkatkan quantity pada penetasan telur ayam serta mempercepat waktu panen telur ayam

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


## 📚 Pengujian 
**- Hasil Pembacaan Suhu dan Kelembapan selama proses Inkubasi**
**- Hasil penyimpanan di InfluxDB.**
**- Visualisasi data Real-time dashboard di Grafana.**


---

## 📚 Analisa Hasil Pengujian
 
---

## 🖼️ Dokumentasi dan Demo

📹 Tonton video demo: 

📷 Lihat dokumentasi foto di folder


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

