
# 🔧 Sensor Monitoring SHT20 & Blockchain Logger

Proyek ini adalah sistem pencatatan dan monitoring data sensor suhu & kelembapan **SHT20** menggunakan protokol **Modbus RTU** yang dikembangkan dengan **Rust**, disimpan ke **InfluxDB**, divisualisasikan lewat **Grafana**, dan **dikirim ke blockchain** (Ganache) menggunakan **Python + Web3 + Solidity**.

## 🧩 Arsitektur Sistem

```

\[SHT20 Sensor]
│
▼ (Modbus RTU)
\[Sensor Client - Rust]
│
├──> \[InfluxDB] ──> \[Grafana]
└──> \[TCP Server]
│
▼
\[Blockchain Logger - Python + Web3]
│
▼
\[Ganache / Ethereum Local Node]

````

## 📦 Fitur Utama

### ✅ Rust Sensor Client
- Membaca data dari SHT20 via **Modbus RTU**.
- Menyimpan data ke **InfluxDB**.
- Menyediakan **TCP server async** agar data dapat dibaca client lain secara real-time.

### ✅ Python Blockchain Logger
- Mengambil data dari TCP server atau langsung dari sensor.
- Mengirim data ke **Smart Contract Solidity** di jaringan Ethereum lokal (Ganache).
- Menyediakan script untuk deploy dan interact dengan kontrak.

### ✅ Visualisasi
- Dashboard **Grafana** untuk memantau suhu & kelembapan secara historis.
- Data terdesentralisasi di blockchain sebagai log permanen.

---

## 🛠️ Cara Menjalankan

### 1. Setup InfluxDB & Grafana
```bash
# Ubuntu
sudo apt install influxdb grafana
sudo systemctl start influxdb grafana-server
````

Buat database `sensor_data` di InfluxDB:

```bash
influx
> CREATE DATABASE sensor_data
> exit
```

Akses Grafana via `http://localhost:3000`, login default: `admin / admin`.

---

### 2. Jalankan Rust Sensor Client

```bash
cd Server/
cargo run
```

Konfigurasi port serial & InfluxDB ada di dalam kode.

---

### 3. Deploy Smart Contract (Solidity)

```bash
cd blockchain/
npx hardhat compile
npx hardhat node         # Menjalankan Ganache lokal
npx hardhat run scripts/deploy.js --network localhost
```

---

### 4. Kirim Data ke Blockchain (Python)

```bash
cd blockchain/logger/
python3 main.py
```

Pastikan file `.env` berisi:

```env
PRIVATE_KEY=0x...
CONTRACT_ADDRESS=0x...
WEB3_PROVIDER=http://127.0.0.1:8545
```

---

## 🔍 Dependensi

### Rust

* `tokio`
* `tokio-modbus`
* `tokio-serial`
* `influxdb`

### Python

* `web3`
* `python-dotenv`

### Solidity Tools

* Hardhat
* Ganache

## 📊 Dashboard Grafana

Grafana menggunakan InfluxDB sebagai sumber data. Panel menampilkan:

* Suhu & kelembapan real-time
* Tren historis dengan query `SELECT * FROM temperature WHERE ...`
