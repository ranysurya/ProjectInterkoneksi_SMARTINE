import sys
import json
import socket
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QDoubleSpinBox, QStatusBar, QMessageBox, QDialog,
                             QFormLayout, QLineEdit, QSpinBox, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, Qt, QTimer
from PyQt5.QtGui import QFont
from pyqtgraph import PlotWidget
import pyqtgraph as pg
from datetime import datetime, timedelta
import time

# InfluxDB Client (Pastikan sudah diinstal: pip install influxdb-client)
from influxdb_client import InfluxDBClient

# --- Dialog Konfigurasi TCP Server dan InfluxDB ---
class ConfigDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Konfigurasi Sistem")
        self.config = config.copy()
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # TCP Server Settings
        tcp_group = QGroupBox("TCP Server (Data Real-time)")
        tcp_layout = QFormLayout()
        self.tcp_host_input = QLineEdit(self.config['tcp_host'])
        tcp_layout.addRow("Host TCP:", self.tcp_host_input)
        self.tcp_port_input = QSpinBox()
        self.tcp_port_input.setRange(1024, 65535)
        self.tcp_port_input.setValue(self.config['tcp_port'])
        tcp_layout.addRow("Port TCP:", self.tcp_port_input)
        tcp_group.setLayout(tcp_layout)
        layout.addRow(tcp_group)

        # InfluxDB Settings
        influx_group = QGroupBox("InfluxDB Database (Data Historis)")
        influx_layout = QFormLayout()
        self.influx_url_input = QLineEdit(self.config['influx_url'])
        influx_layout.addRow("URL:", self.influx_url_input)
        self.influx_token_input = QLineEdit(self.config['influx_token'])
        self.influx_token_input.setEchoMode(QLineEdit.Password)
        influx_layout.addRow("Token:", self.influx_token_input)
        self.influx_org_input = QLineEdit(self.config['influx_org'])
        influx_layout.addRow("Organisasi:", self.influx_org_input)
        self.influx_bucket_input = QLineEdit(self.config['influx_bucket'])
        influx_layout.addRow("Bucket:", self.influx_bucket_input)
        influx_group.setLayout(influx_layout)
        layout.addRow(influx_group)

        save_button = QPushButton("Simpan Konfigurasi")
        save_button.setObjectName("save_config_btn")
        save_button.clicked.connect(self.save_config)
        layout.addRow(save_button)

        self.setLayout(layout)

    def save_config(self):
        self.config['tcp_host'] = self.tcp_host_input.text()
        self.config['tcp_port'] = self.tcp_port_input.value()
        self.config['influx_url'] = self.influx_url_input.text()
        self.config['influx_token'] = self.influx_token_input.text()
        self.config['influx_org'] = self.influx_org_input.text()
        self.config['influx_bucket'] = self.influx_bucket_input.text()
        self.accept()

# --- Worker Klien TCP ---
class TcpClientWorker(QObject):
    data_received = pyqtSignal(dict)
    connection_status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._running = False
        self._socket = None
        self._reconnect_delay = 3

    @pyqtSlot()
    def run(self):
        self._running = True
        while self._running:
            if self._connect():
                self._read_data()
            if self._running:
                time.sleep(self._reconnect_delay) 
        self._close_socket()
        self.connection_status_changed.emit("Monitoring Dihentikan.")

    def _connect(self):
        self._close_socket()
        self.connection_status_changed.emit("Mencoba koneksi...")
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(5)
            self._socket.connect((self.config['tcp_host'], self.config['tcp_port']))
            self._socket.settimeout(None)
            self.connection_status_changed.emit("Terhubung")
            print(f"Terhubung ke server TCP di {self.config['tcp_host']}:{self.config['tcp_port']}")
            return True
        except ConnectionRefusedError:
            self.connection_status_changed.emit("Tidak Terhubung (Ditolak)")
            self.error_occurred.emit(f"Koneksi Ditolak: Pastikan Rust TCP Server berjalan dan alamat/port benar.")
        except socket.timeout:
            self.connection_status_changed.emit("Tidak Terhubung (Timeout)")
            self.error_occurred.emit(f"Koneksi Timeout: Tidak dapat terhubung ke server Rust.")
        except Exception as e:
            self.connection_status_changed.emit("Tidak Terhubung (Error)")
            self.error_occurred.emit(f"Error Koneksi TCP: {str(e)}")
        
        self._close_socket()
        return False

    def _read_data(self):
        buffer = b""
        while self._running and self._socket:
            try:
                self._socket.settimeout(1.0) 
                chunk = self._socket.recv(4096)
                
                if not chunk: 
                    print("Server menutup koneksi.")
                    self.connection_status_changed.emit("Koneksi terputus")
                    break
                
                buffer += chunk
                
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    
                    if not line.strip(): 
                        continue
                        
                    try:
                        json_string = line.decode('utf-8').strip()
                        if json_string:
                            json_data = json.loads(json_string)
                            if all(k in json_data for k in ['timestamp', 'temperature_celsius', 'humidity_percent']):
                                self.data_received.emit(json_data)
                            else:
                                print(f"Data JSON tidak lengkap atau format salah: {json_string}")
                                self.error_occurred.emit(f"Data diterima tidak lengkap: '{json_string}'")
                        else:
                            print(f"Baris kosong atau hanya spasi diterima: '{line.decode('utf-8', errors='ignore')}'")

                    except json.JSONDecodeError as e:
                        print(f"JSON Decode Error: {e} | Data: {line.decode('utf-8', errors='ignore')}")
                        self.error_occurred.emit(f"Error parse data dari server: {str(e)}. Data: '{line.decode('utf-8', errors='ignore')}'")
                    except Exception as e:
                        print(f"Error pemrosesan data: {e}")
                        self.error_occurred.emit(f"Error tidak terduga saat memproses data: {str(e)}")

            except socket.timeout:
                pass 
            except socket.error as e: 
                print(f"Socket Error saat membaca: {e}")
                self.error_occurred.emit(f"Socket error saat membaca data: {str(e)}")
                self.connection_status_changed.emit("Koneksi terputus")
                break
            except Exception as e:
                print(f"Error tidak terduga saat membaca: {e}")
                self.error_occurred.emit(f"Error tidak terduga saat membaca data: {str(e)}")
                break

    @pyqtSlot()
    def stop(self):
        self._running = False
        self._close_socket()

    def _close_socket(self):
        if self._socket:
            try:
                self._socket.shutdown(socket.SHUT_RDWR) 
                self._socket.close()
            except OSError as e:
                if e.errno == 9: 
                    print(f"Warning: Socket already closed or invalid (Bad file descriptor): {e}")
                else:
                    print(f"Error closing TCP socket: {e}")
            except Exception as e:
                print(f"Error closing TCP socket: {e}")
            finally:
                self._socket = None

# --- InfluxDB Worker ---
class InfluxDBWorker(QObject):
    data_loaded = pyqtSignal(list) 
    status_update = pyqtSignal(str, str) 
    error_occurred = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.client = None

    def _init_influxdb_client(self):
        """Inisialisasi klien InfluxDB dan tes koneksi."""
        try:
            if self.client:
                self.client.close()
            
            self.client = InfluxDBClient(
                url=self.config['influx_url'],
                token=self.config['influx_token'],
                org=self.config['influx_org']
            )
            # Ping database untuk cek konektivitas
            if self.client.ping():
                self.status_update.emit("db", "🟢 InfluxDB: Terhubung")
                return True
            else:
                self.status_update.emit("db", "🔴 InfluxDB: Ping Gagal")
                self.error_occurred.emit("Gagal terhubung ke InfluxDB: Ping gagal.")
                return False
        except Exception as e:
            self.status_update.emit("db", "🔴 InfluxDB: Gagal Terhubung")
            self.error_occurred.emit(f"Gagal terhubung ke InfluxDB:\n{str(e)}")
            self.client = None 
            return False

    @pyqtSlot()
    def load_historical_data(self):
        """Memuat data historis dari InfluxDB."""
        if not self._init_influxdb_client():
            self.data_loaded.emit([]) 
            return

        query_api = self.client.query_api()
        query = f'''
        from(bucket: "{self.config['influx_bucket']}")
        |> range(start: -24h) 
        |> filter(fn: (r) => r._measurement == "environment_monitoring")
        |> filter(fn: (r) => r._field == "temperature_celsius" or r._field == "humidity_percent")
        |> pivot(rowKey:["_time", "sensor_id", "location", "process_stage"], columnKey: ["_field"], valueColumn: "_value")
        |> keep(columns: ["_time", "sensor_id", "location", "process_stage", "temperature_celsius", "humidity_percent"])
        |> sort(columns: ["_time"])
        '''
        
        records = []
        try:
            tables = query_api.query(query, org=self.config['influx_org'])
            for table in tables:
                for record in table.records:
                    records.append({
                        "time": record.get_time(), 
                        "sensor_id": record.values.get("sensor_id", "N/A"),
                        "location": record.values.get("location", "N/A"),
                        "process_stage": record.values.get("process_stage", "N/A"), # Usia Telur (Hari)
                        "temperature_celsius": record.values.get("temperature_celsius", float('nan')),
                        "humidity_percent": record.values.get("humidity_percent", float('nan')),
                    })
            self.status_update.emit("db", f"🟢 Database: Data berhasil dimuat ({len(records)} catatan)")
            self.data_loaded.emit(records)
        except Exception as e:
            self.status_update.emit("db", "🔴 Database: Gagal Memuat Data")
            self.error_occurred.emit(f"Error memuat data historis dari InfluxDB:\n{str(e)}")
            self.data_loaded.emit([]) 
        finally:
            if self.client:
                self.client.close() 

# --- Kelas Utama Aplikasi GUI ---
class TelurMonitoringApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Konfigurasi Default
        self.config = {
            'tcp_host': "127.0.0.1",
            'tcp_port': 7878,
            'min_temp': 24.0,       
            'max_temp': 30.0,       
            'min_humid': 50.0,      
            'max_humid': 70.0,      
            'influx_url': "http://localhost:8086",
            'influx_token': "hkyHqP236AVjN2JL84XYNJVPWCDXnC756c1Gxc2CO6n_nkG-dCTLB3Ik-c761g3YRqasOSGRZrOandYZhN8QrQ==", # Ganti dengan token Anda
            'influx_org': "Institute Teknologi Sepuluh Nopember",
            'influx_bucket': "telur_monitoring_db"
        }
        self.load_config_from_file()

        self.tcp_worker = None
        self.tcp_worker_thread = None
        self.influxdb_worker = None
        self.influxdb_worker_thread = None

        self.time_data = []
        self.temp_data = []
        self.humidity_data = []

        self.init_ui()

        self.init_influxdb_client_main_thread()


    def load_config_from_file(self, filename="config.json"):
        try:
            with open(filename, 'r') as f:
                loaded_config = json.load(f)
                for key, value in loaded_config.items():
                    if key in self.config:
                        self.config[key] = value
                print(f"Konfigurasi dimuat dari {filename}")
        except FileNotFoundError:
            print(f"File konfigurasi '{filename}' tidak ditemukan. Menggunakan konfigurasi default.")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error Konfigurasi", f"Gagal membaca file konfigurasi '{filename}'. Pastikan format JSON valid.\nDetail: {e}")
            print(f"Error membaca file konfigurasi '{filename}': {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error Konfigurasi", f"Error saat memuat konfigurasi dari file.\nDetail: {e}")
            print(f"Error saat memuat konfigurasi: {e}")

    def save_config_to_file(self, filename="config.json"):
        try:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"Konfigurasi disimpan ke {filename}")
        except Exception as e:
            print(f"Error saat menyimpan konfigurasi: {e}")
            QMessageBox.warning(self, "Simpan Konfigurasi", f"Gagal menyimpan konfigurasi ke file: {e}")

    def init_ui(self):
        # --- JUDUL JENDELA BARU ---
        self.setWindowTitle("Smartine : Smart Incubator Egg Instrument")
        self.setGeometry(100, 100, 1200, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # --- Tab Widget ---
        self.tab_widget = QTabWidget()
        self.dashboard_tab = QWidget()
        self.data_sensor_tab = QWidget()

        self.tab_widget.addTab(self.dashboard_tab, "DASHBOARD")
        # --- JUDUL TAB BARU ---
        self.tab_widget.addTab(self.data_sensor_tab, "DATA SENSOR INKUBATOR") 
        layout.addWidget(self.tab_widget)

        # --- DASHBOARD Tab Content ---
        self.setup_dashboard_tab()

        # --- DATA SENSOR Tab Content ---
        self.setup_data_sensor_tab()

        # Status bar
        self.statusBar().showMessage("Sistem siap. Pastikan Rust TCP Server berjalan.")


    def setup_dashboard_tab(self):
        dashboard_layout = QVBoxLayout(self.dashboard_tab)

        # --- Informasi Kelompok (TIDAK BERUBAH) ---
        group_info_group = QGroupBox("KELOMPOK 3")
        group_info_layout = QVBoxLayout()
        self.member_label = QLabel("Raffi Fitra Akbar (2042231018)\nRafi Muhammad Zhafir (2042231038)\nRany Surya Oktavia (2042231060)")
        self.member_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.member_label.setAlignment(Qt.AlignCenter) 
        group_info_layout.addWidget(self.member_label)
        group_info_group.setLayout(group_info_layout)
        dashboard_layout.addWidget(group_info_group)

        # --- Status Panel (TIDAK BERUBAH) ---
        status_group = QGroupBox("Status Sistem")
        status_layout = QHBoxLayout()
        self.tcp_status_label = QLabel("🔴 TCP Server: Tidak Terhubung")
        self.db_status_label = QLabel("🔴 InfluxDB: Tidak Terhubung")
        self.last_update_label = QLabel("Terakhir Update: -")
        self.tcp_status_label.setFont(QFont("Arial", 10))
        self.db_status_label.setFont(QFont("Arial", 10))
        self.last_update_label.setFont(QFont("Arial", 10))
        status_layout.addWidget(self.tcp_status_label)
        status_layout.addWidget(self.db_status_label)
        status_layout.addWidget(self.last_update_label)
        status_group.setLayout(status_layout)
        dashboard_layout.addWidget(status_group)

        # --- Control Panel (TIDAK BERUBAH) ---
        control_group = QGroupBox("Kontrol")
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶ Mulai Monitoring")
        self.start_btn.setObjectName("start_btn")
        self.start_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.start_btn.clicked.connect(self.start_monitoring)
        self.stop_btn = QPushButton("⏹ Berhenti")
        self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)
        self.config_btn = QPushButton("⚙ Konfigurasi")
        self.config_btn.setObjectName("config_btn")
        self.config_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.config_btn.clicked.connect(self.show_config_dialog)
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.config_btn)
        control_group.setLayout(control_layout)
        dashboard_layout.addWidget(control_group)

        # --- Reading Panel (TIDAK BERUBAH) ---
        reading_group = QGroupBox("Pembacaan Sensor Real-time")
        reading_layout = QHBoxLayout()
        self.temp_label = QLabel("🌡 Suhu: -- °C")
        self.temp_label.setObjectName("temp_label")
        self.humidity_label = QLabel("💧 Kelembaban: -- %")
        self.humidity_label.setObjectName("humidity_label")
        reading_layout.addWidget(self.temp_label, stretch=1)
        reading_layout.addWidget(self.humidity_label, stretch=1)
        reading_group.setLayout(reading_layout)
        dashboard_layout.addWidget(reading_group)

        # --- Threshold Panel (JUDUL BERUBAH) ---
        self.threshold_group = QGroupBox("Batas Optimal Inkubasi Telur") 
        threshold_layout = QHBoxLayout()
        self.min_temp_input = QDoubleSpinBox()
        self.min_temp_input.setRange(0, 50)
        self.min_temp_input.setValue(self.config['min_temp'])
        self.min_temp_input.setSuffix(" °C")
        self.min_temp_input.setSingleStep(0.1)
        self.max_temp_input = QDoubleSpinBox()
        self.max_temp_input.setRange(0, 50)
        self.max_temp_input.setValue(self.config['max_temp'])
        self.max_temp_input.setSuffix(" °C")
        self.max_temp_input.setSingleStep(0.1)

        self.min_humidity_input = QDoubleSpinBox()
        self.min_humidity_input.setRange(0, 100)
        self.min_humidity_input.setValue(self.config['min_humid'])
        self.min_humidity_input.setSuffix(" %")
        self.min_humidity_input.setSingleStep(0.1)
        self.max_humidity_input = QDoubleSpinBox()
        self.max_humidity_input.setRange(0, 100)
        self.max_humidity_input.setValue(self.config['max_humid'])
        self.max_humidity_input.setSuffix(" %")
        self.max_humidity_input.setSingleStep(0.1)

        threshold_layout.addWidget(QLabel("Suhu Min:"))
        threshold_layout.addWidget(self.min_temp_input)
        threshold_layout.addWidget(QLabel("Max:"))
        threshold_layout.addWidget(self.max_temp_input)
        threshold_layout.addSpacing(20)
        threshold_layout.addWidget(QLabel("Kelembaban Min:"))
        threshold_layout.addWidget(self.min_humidity_input)
        threshold_layout.addWidget(QLabel("Max:"))
        threshold_layout.addWidget(self.max_humidity_input)
        self.threshold_group.setLayout(threshold_layout)
        dashboard_layout.addWidget(self.threshold_group)

        # Graph Widget (TIDAK BERUBAH)
        self.graph_widget = PlotWidget()
        self.setup_graph()
        dashboard_layout.addWidget(self.graph_widget, stretch=1)

    def setup_data_sensor_tab(self):
        data_sensor_layout = QVBoxLayout(self.data_sensor_tab)

        # --- JUDUL TAB BARU ---
        tab_title_label = QLabel("DATA SENSOR INKUBATOR")
        tab_title_label.setFont(QFont("Arial", 16, QFont.Bold))
        tab_title_label.setAlignment(Qt.AlignCenter)
        data_sensor_layout.addWidget(tab_title_label)

        # Control Panel for Data Sensor tab (TIDAK BERUBAH)
        control_panel_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh Data")
        self.refresh_btn.setObjectName("refresh_btn")
        self.refresh_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.refresh_btn.clicked.connect(self.load_historical_data)
        
        control_panel_layout.addWidget(self.refresh_btn)
        control_panel_layout.addStretch(1)
        data_sensor_layout.addLayout(control_panel_layout)

        # Table Widget for historical data (PERUBAHAN KOLOM)
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(7) # Disesuaikan untuk 7 kolom
        self.data_table.setHorizontalHeaderLabels([
            "Waktu", 
            "Sensor ID", 
            "Lokasi Inkubator", 
            "Usia Telur (Hari)", 
            "Fase Inkubasi", 
            "Suhu (°C)", 
            "Kelembaban (%)"
        ])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)
        data_sensor_layout.addWidget(self.data_table)

    def setup_graph(self):
        self.graph_widget.setBackground('w')
        self.graph_widget.setLabel('left', 'Nilai', units='(°C / %)', color='#333', font='Arial')
        self.graph_widget.setLabel('bottom', 'Waktu', color='#333', font='Arial')
        self.graph_widget.addLegend()
        self.graph_widget.getAxis('bottom').setTickFont(QFont("Arial", 9))
        self.graph_widget.getAxis('left').setTickFont(QFont("Arial", 9))
        self.graph_widget.showGrid(x=True, y=True, alpha=0.5)
        pg.setConfigOptions(antialias=True)
        self.temp_plot = self.graph_widget.plot(
            [], [], name='Suhu (°C)', pen=pg.mkPen(color='#e74c3c', width=2),
            symbol='o', symbolSize=6, symbolBrush='#e74c3c'
        )
        self.humidity_plot = self.graph_widget.plot(
            [], [], name='Kelembaban (%)', pen=pg.mkPen(color='#3498db', width=2),
            symbol='o', symbolSize=6, symbolBrush='#3498db'
        )
        class TimeAxisItem(pg.AxisItem):
            def tickStrings(self, values, scale, spacing):
                return [datetime.fromtimestamp(float(value)).strftime('%H:%M:%S') for value in values]
        self.graph_widget.getPlotItem().setAxisItems({'bottom': TimeAxisItem(orientation='bottom')})

    def load_config_from_file(self, filename="config.json"):
        try:
            with open(filename, 'r') as f:
                loaded_config = json.load(f)
                for key, value in loaded_config.items():
                    if key in self.config:
                        self.config[key] = value
                print(f"Konfigurasi dimuat dari {filename}")
        except FileNotFoundError:
            print(f"File konfigurasi '{filename}' tidak ditemukan. Menggunakan konfigurasi default.")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error Konfigurasi", f"Gagal membaca file konfigurasi '{filename}'. Pastikan format JSON valid.\nDetail: {e}")
            print(f"Error membaca file konfigurasi '{filename}': {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error Konfigurasi", f"Error saat memuat konfigurasi dari file.\nDetail: {e}")
            print(f"Error saat memuat konfigurasi: {e}")

    def save_config_to_file(self, filename="config.json"):
        try:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"Konfigurasi disimpan ke {filename}")
        except Exception as e:
            print(f"Error saat menyimpan konfigurasi: {e}")
            QMessageBox.warning(self, "Simpan Konfigurasi", f"Gagal menyimpan konfigurasi ke file: {e}")

    @pyqtSlot()
    def start_monitoring(self):
        self.stop_monitoring() 

        self.tcp_worker_thread = QThread()
        self.tcp_worker = TcpClientWorker(self.config)
        self.tcp_worker.moveToThread(self.tcp_worker_thread)
        self.tcp_worker.data_received.connect(self.update_ui)
        self.tcp_worker.connection_status_changed.connect(self.update_tcp_status_label)
        self.tcp_worker.error_occurred.connect(self.handle_worker_error)
        self.tcp_worker_thread.started.connect(self.tcp_worker.run)
        self.tcp_worker_thread.finished.connect(self.tcp_worker.stop)
        self.tcp_worker_thread.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.statusBar().showMessage(f"Mencoba terhubung ke Rust TCP Server di {self.config['tcp_host']}:{self.config['tcp_port']}...")

    @pyqtSlot()
    def stop_monitoring(self):
        if self.tcp_worker_thread and self.tcp_worker_thread.isRunning():
            try:
                self.tcp_worker.data_received.disconnect(self.update_ui)
                self.tcp_worker.connection_status_changed.disconnect(self.update_tcp_status_label)
                self.tcp_worker.error_occurred.disconnect(self.handle_worker_error)
            except TypeError:
                pass
            self.tcp_worker.stop()
            self.tcp_worker_thread.quit()
            if not self.tcp_worker_thread.wait(5000): 
                print("Warning: TCP Worker thread did not terminate gracefully. Forcing termination.")
                self.tcp_worker_thread.terminate()
            self.tcp_worker_thread = None
            self.tcp_worker = None

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.statusBar().showMessage("Monitoring dihentikan.")
        self.tcp_status_label.setText("🔴 TCP Server: Tidak Terhubung")
        self.temp_label.setText("🌡 Suhu: -- °C")
        self.humidity_label.setText("💧 Kelembaban: -- %")
        self.last_update_label.setText("Terakhir Update: -")
        
        self.time_data.clear()
        self.temp_data.clear()
        self.humidity_data.clear()
        
        self.temp_plot.setData([], [])
        self.humidity_plot.setData([], [])

    @pyqtSlot(dict)
    def update_ui(self, data):
        self.temp_label.setText(f"🌡 Suhu: {data.get('temperature_celsius', '--'):.1f} °C")
        self.humidity_label.setText(f"💧 Kelembaban: {data.get('humidity_percent', '--'):.1f} %")

        timestamp_str = data.get('timestamp')
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            self.time_data.append(timestamp.timestamp())
            self.last_update_label.setText(f"Terakhir Update: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            self.time_data.append(time.time())
            self.last_update_label.setText(f"Terakhir Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        self.temp_data.append(data.get('temperature_celsius', 0.0))
        self.humidity_data.append(data.get('humidity_percent', 0.0))
        max_points = 60
        if len(self.time_data) > max_points:
            self.time_data = self.time_data[-max_points:]
            self.temp_data = self.temp_data[-max_points:]
            self.humidity_data = self.humidity_data[-max_points:]
        self.temp_plot.setData(self.time_data, self.temp_data)
        self.humidity_plot.setData(self.time_data, self.humidity_data)
        if self.time_data:
            end_time = self.time_data[-1]
            start_time = end_time - 600
            self.graph_widget.setXRange(start_time, end_time, padding=0)

        min_temp = self.min_temp_input.value()
        max_temp = self.max_temp_input.value()
        min_humid = self.min_humidity_input.value()
        max_humid = self.max_humidity_input.value()
        current_temp = data.get('temperature_celsius', float('nan'))
        current_humid = data.get('humidity_percent', float('nan'))

        temp_alert = False
        if not (current_temp == float('nan')): 
            if current_temp < min_temp or current_temp > max_temp: 
                temp_alert = True
        
        if temp_alert:
            self.temp_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #c0392b; background-color: #ffe0e0; border: 1px solid #c0392b; border-radius: 5px;")
            self.statusBar().showMessage(f"Peringatan: Suhu ({current_temp:.1f}°C) di luar batas optimal ({min_temp:.1f}-{max_temp:.1f}°C)!", 5000)
        else:
            self.temp_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #e74c3c;") 

        humid_alert = False
        if not (current_humid == float('nan')): 
            if current_humid < min_humid or current_humid > max_humid: 
                humid_alert = True
        
        if humid_alert:
            self.humidity_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2980b9; background-color: #e0f2ff; border: 1px solid #2980b9; border-radius: 5px;")
            if not temp_alert: 
                self.statusBar().showMessage(f"Peringatan: Kelembaban ({current_humid:.1f}%) di luar batas optimal ({min_humid:.1f}-{max_humid:.1f}%)!", 5000)
        else:
            self.humidity_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #3498db;") 

    @pyqtSlot(str)
    def update_tcp_status_label(self, status_message):
        self.tcp_status_label.setText(f"⚡️ TCP Server: {status_message}")
        if "Terhubung" in status_message:
            self.tcp_status_label.setStyleSheet("color: green;")
        elif "Tidak Terhubung" in status_message:
            self.tcp_status_label.setStyleSheet("color: red;")
        else:
            self.tcp_status_label.setStyleSheet("color: orange;")

    @pyqtSlot(str, str)
    def update_db_status_label(self, component, message=""):
        self.db_status_label.setText(message)
        if "Terhubung" in message and "Gagal" not in message:
            self.db_status_label.setStyleSheet("color: green;")
        elif "Gagal" in message or "Tidak Terhubung" in message:
            self.db_status_label.setStyleSheet("color: red;")
        else:
            self.db_status_label.setStyleSheet("color: black;")


    def show_config_dialog(self):
        current_config = self.config.copy()
        dialog = ConfigDialog(current_config, self)

        if dialog.exec_():
            self.config = dialog.config
            self.config['min_temp'] = self.min_temp_input.value()
            self.config['max_temp'] = self.max_temp_input.value()
            self.config['min_humid'] = self.min_humidity_input.value()
            self.config['max_humid'] = self.max_humidity_input.value()

            self.save_config_to_file()
            self.statusBar().showMessage("Konfigurasi disimpan. Mohon restart aplikasi untuk menerapkan perubahan penuh (terutama InfluxDB).")
            self.stop_monitoring()
            self.init_influxdb_client_main_thread()


    @pyqtSlot()
    def load_historical_data(self):
        if self.influxdb_worker_thread and self.influxdb_worker_thread.isRunning():
            self.statusBar().showMessage("Memuat data... Mohon tunggu.")
            return

        self.influxdb_worker_thread = QThread()
        self.influxdb_worker = InfluxDBWorker(self.config)
        self.influxdb_worker.moveToThread(self.influxdb_worker_thread)

        self.influxdb_worker.data_loaded.connect(self.update_data_table)
        self.influxdb_worker.status_update.connect(self.update_db_status_label)
        self.influxdb_worker.error_occurred.connect(self.handle_worker_error)

        self.influxdb_worker_thread.started.connect(self.influxdb_worker.load_historical_data)
        self.influxdb_worker_thread.start()
        self.statusBar().showMessage("Memuat data historis dari InfluxDB...")


    @pyqtSlot(list)
    def update_data_table(self, records):
        self.data_table.setRowCount(len(records))
        for row_idx, record in enumerate(reversed(records)): 
            time_str = record['time'].strftime('%Y-%m-%d %H:%M:%S') if record['time'] else "N/A"
            sensor_id = record.get('sensor_id', 'N/A')
            location = record.get('location', 'N/A') # Lokasi Inkubator
            egg_age_days = record.get('process_stage', 'N/A') # Usia Telur (Hari)
            temp = f"{record.get('temperature_celsius', float('nan')):.2f}" if isinstance(record.get('temperature_celsius'), (float, int)) else "N/A"
            humid = f"{record.get('humidity_percent', float('nan')):.2f}" if isinstance(record.get('humidity_percent'), (float, int)) else "N/A"

            # Tentukan Fase Inkubasi berdasarkan Usia Telur (Hari)
            incubation_phase = "N/A"
            if isinstance(egg_age_days, str) and egg_age_days.startswith("Hari ke-"):
                try:
                    actual_day = int(egg_age_days.split('-')[1])
                    if actual_day >= 1 and actual_day <= 18:
                        incubation_phase = "Inkubasi (dengan pembalikan rutin)"
                    elif actual_day >= 19 and actual_day <= 21:
                        incubation_phase = "Inkubasi (tanpa pembalikan, kelembaban tinggi)"
                    elif actual_day >= 21 and actual_day <= 22: # Hari 21 +- 1
                        incubation_phase = "Proses Penetasan Anak Ayam"
                    elif actual_day > 22 and actual_day <= 23:
                        incubation_phase = "Pengeringan Anak Ayam"
                    elif actual_day > 23:
                        incubation_phase = "Pemindahan Anak Ayam ke Brooder"
                    else:
                        incubation_phase = "Seleksi/Persiapan" # Default awal atau hari 0
                except (ValueError, IndexError):
                    incubation_phase = "Usia tidak valid"
            else:
                incubation_phase = "Usia tidak valid"


            self.data_table.setItem(row_idx, 0, QTableWidgetItem(time_str))
            self.data_table.setItem(row_idx, 1, QTableWidgetItem(sensor_id))
            self.data_table.setItem(row_idx, 2, QTableWidgetItem(location))
            self.data_table.setItem(row_idx, 3, QTableWidgetItem(egg_age_days)) # Usia Telur (Hari)
            self.data_table.setItem(row_idx, 4, QTableWidgetItem(incubation_phase)) # Fase Inkubasi
            self.data_table.setItem(row_idx, 5, QTableWidgetItem(temp))
            self.data_table.setItem(row_idx, 6, QTableWidgetItem(humid))
        
        self.data_table.resizeColumnsToContents()
        self.statusBar().showMessage(f"Data historis berhasil dimuat. Total {len(records)} catatan.")

    def init_influxdb_client_main_thread(self):
        try:
            temp_client = InfluxDBClient(
                url=self.config['influx_url'],
                token=self.config['influx_token'],

                org=self.config['influx_org']
            )
            if temp_client.ping():
                self.update_db_status_label("db", "🟢 InfluxDB: Terhubung (Siap)")
            else:
                self.update_db_status_label("db", "🔴 InfluxDB: Ping Gagal")
            temp_client.close()
        except Exception as e:
            self.update_db_status_label("db", f"🔴 InfluxDB: Gagal Inisialisasi ({str(e)})")


    def handle_worker_error(self, message):
        QMessageBox.critical(self, "Kesalahan Komunikasi", message)
        self.stop_monitoring() 

    def closeEvent(self, event):
        self.stop_monitoring()
        if self.influxdb_worker_thread and self.influxdb_worker_thread.isRunning():
            self.influxdb_worker_thread.quit()
            if not self.influxdb_worker_thread.wait(2000):
                print("Warning: InfluxDB worker thread did not terminate gracefully.")
                self.influxdb_worker_thread.terminate()
        self.save_config_to_file()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 10))

    app.setStyleSheet("""
        QMainWindow { background-color: #f8f8f8; }
        QGroupBox {
            font-weight: bold; border: 1px solid #d0d0d0; border-radius: 8px;
            margin-top: 15px; padding-top: 15px; padding-bottom: 5px;
            background-color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin; left: 10px; padding: 0 5px;
            color: #555; font-size: 11pt; font-weight: bold;
        }
        QLabel { color: #333; font-size: 10pt; }
        QLabel#temp_label, QLabel#humidity_label {
            padding: 10px; border: 1px solid #eee; border-radius: 5px;
            background-color: #f0f8ff;
        }
        QPushButton {
            border: none; border-radius: 7px; padding: 12px 20px;
            margin: 5px; font-weight: bold; color: white;
        }
        QPushButton#start_btn { background-color: #28a745; } QPushButton#start_btn:hover { background-color: #218838; } QPushButton#start_btn:pressed { background-color: #1e7e34; }
        QPushButton#stop_btn { background-color: #dc3545; } QPushButton#stop_btn:hover { background-color: #c82333; } QPushButton#stop_btn:pressed { background-color: #bd2130; }
        QPushButton#config_btn { background-color: #007bff; } QPushButton#config_btn:hover { background-color: #0056b3; } QPushButton#config_btn:pressed { background-color: #004085; }
        QPushButton#save_config_btn { background-color: #6c757d; } QPushButton#save_config_btn:hover { background-color: #5a6268; } QPushButton#save_config_btn:pressed { background-color: #495057; }
        QPushButton#refresh_btn { background-color: #f39c12; } QPushButton#refresh_btn:hover { background-color: #e67e22; } QPushButton#refresh_btn:pressed { background-color: #d35400; }

        QDoubleSpinBox, QSpinBox, QLineEdit {
            padding: 8px; border: 1px solid #ced4da; border-radius: 5px;
            background-color: #fff; color: #495057;
        }
        QStatusBar { background-color: #e9ecef; color: #495057; border-top: 1px solid #dee2e6; padding: 5px; }
        QMessageBox { background-color: #ffffff; }
        QTabWidget::pane { border: 1px solid #ccc; background-color: #fcfcfc; }
        QTabWidget::tab-bar { left: 5px; }
        QTabBar::tab {
            background: #eee; border: 1px solid #ccc; border-bottom-color: #eee;
            border-top-left-radius: 4px; border-top-right-radius: 4px;
            min-width: 8ex; padding: 8px;
        }
        QTabBar::tab:selected {
            background: #fff; border-color: #ccc; border-bottom-color: white;
        }
        QTableWidget {
            border: 1px solid #ccc;
            selection-background-color: #b0e0e6;
            selection-color: #333;
        }
        QHeaderView::section {
            background-color: #e0e0e0;
            padding: 5px;
            border: 1px solid #ccc;
            font-weight: bold;
        }
    """)

    window = TelurMonitoringApp()
    window.show()
    sys.exit(app.exec_())