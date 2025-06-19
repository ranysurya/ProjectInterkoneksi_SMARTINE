# 🐣 Smartine : _Smart Incubator Egg Instrument_ Sistem Monitoring Suhu dan Kelembaban untuk Inkubator Telur Berbasis IoT dan Visualisasi _Realtime_


## 📘 Deskripsi Proyek
**Smartine adalah** sistem monitoring suhu 🌡️ dan kelembapan 💧 pada mesin penetas telur ayam yang dapat dipantau secara real-time 📲. Dirancang untuk membantu peternak rumahan, **alat ini menjaga kestabilan inkubasi** agar proses penetasan lebih **efisien** **dan akurat**. **Dengan sensor digital (SHT), pencatatan data otomatis, dan tampilan visual yang informatif, peternak dapat meningkatkan tingkat keberhasilan menetas dan mempercepat waktu panen.** Inovasi ini juga mendorong adopsi teknologi di sektor peternakan 💼 serta membuka peluang kolaborasi bagi mahasiswa dan pengembang 🎓 dalam menghadirkan solusi berbasis data dan teknologi terkini 📡. Dari sisi bisnis, sistem ini memberikan solusi yang ekonomis namun berdampak besar. Peternak dapat meningkatkan jumlah telur yang berhasil menetas 🐣, mempercepat siklus panen, dan meningkatkan daya saing di pasar lokal maupun nasional.

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

## ⚙️ Fitur Utama
- ✅ Monitoring Suhu & Kelembaban Real-Time 🌡️💧
- ✅ Penyimpanan Data Historis 🕒
- ✅ Visualisasi Data 📊
- ✅ Blockchain-based Data Logging, untuk Menjamin keaslian & keamanan data inkubasi


---

## 🛠️ Implementasi dan Kode Program
**- Rust Modbust Client**
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
  
**- TCP Server**
  
---

## 🚀 Cara Menggunak

## 📚 Tutorial Setup Program 

---

## 📚 Tutorial Setup Program 
 
---

## 🖼️ Dokumentasi dan Demo

📹 Tonton video demo: 

📷 Lihat dokumentasi foto di folder


---

## 📌 Saran untuk Pengembangan Selanjutnya
- Integrasi Kecerdasan Buatan (AI) untuk Prediksi dan Optimasi Penetasan 🤖
- Fitur Prediksi Waktu Tetas Otomatis ⏳
- Integrasi Kamera Mini untuk Pemantauan Visual 📷
- Fitur Marketplace Internal 🛒

---

## 🌱 Lisensi
SMARTINE_TEKINS23_ITS

---

> 🚀 “Tetas Lebih Cerdas, Panen Lebih Cepat!, Smartine: Awal Cerdas untuk Anak Ayam Berkualitas.”  
> — Tim Smartine

