import React, { useState, useEffect, useCallback } from 'react';
import { ethers } from 'ethers';
import './App.css';

// Import untuk Chart
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// Register komponen Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// --- BARIS INI TELAH DIHAPUS SEPENUHNYA ---
// import SensorDataJSON from './SensorData.json'; 

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [account, setAccount] = useState(null);
  const [contract, setContract] = useState(null); 
  const [provider, setProvider] = useState(null);
  const [sensorReadings, setSensorReadings] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // --- State untuk informasi kontrak yang dimuat secara dinamis ---
  const [contractInfo, setContractInfo] = useState(null); // Akan menyimpan {address, abi}
  const [wsProvider, setWsProvider] = useState(null);
  const [eventContract, setEventContract] = useState(null);

  // --- State untuk Data Grafik ---
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Suhu (°C)',
        data: [],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        yAxisID: 'y',
      },
      {
        label: 'Kelembaban (%)',
        data: [],
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
        yAxisID: 'y1',
      },
    ],
  });

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false, 
    interaction: {
      mode: 'index',
      intersect: false,
    },
    stacked: false,
    plugins: {
      title: {
        display: true,
        text: 'Tren Suhu dan Kelembaban Inkubator',
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Waktu',
        },
      },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
            display: true,
            text: 'Suhu (°C)',
        },
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
            display: true,
            text: 'Kelembaban (%)',
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  // useEffect pertama: Memuat SensorData.json dari folder public/
  useEffect(() => {
    const loadContractInfo = async () => {
      try {
        console.log("Attempting to load SensorData.json from public/ folder...");
        const response = await fetch('/SensorData.json'); 
        if (!response.ok) {
          throw new Error(`Failed to fetch /SensorData.json: ${response.statusText} (Status: ${response.status})`);
        }
        const data = await response.json();
        if (!data.address || !data.abi) {
          throw new Error("SensorData.json is missing 'address' or 'abi' properties.");
        }
        setContractInfo(data);
        console.log("Contract info loaded successfully:", data);

        // Setelah info kontrak dimuat, coba koneksi MetaMask secara otomatis
        if (window.ethereum && window.ethereum.selectedAddress) {
          console.log("MetaMask detected and already selected an address. Attempting auto-connect.");
          connectWallet();
        } else {
          setError("Connect your MetaMask wallet to begin.");
          setLoading(false);
        }
      } catch (err) {
        console.error("Error loading contract info JSON:", err);
        setError(`Failed to load contract details: ${err.message}. Make sure 'SensorData.json' is in the 'public/' folder and contains 'address' and 'abi'.`);
        setLoading(false);
      }
    };

    loadContractInfo();
  }, []); // [] agar hanya berjalan sekali saat komponen mount

  // connectWallet: Sekarang tergantung pada contractInfo
  const connectWallet = useCallback(async () => {
    setError(null);
    setLoading(true);

    if (!window.ethereum) {
      setError("MetaMask is not installed. Please install it to use this DApp.");
      console.error("MetaMask is not installed!");
      setLoading(false);
      return;
    }

    if (!contractInfo) { // Pastikan contractInfo sudah dimuat
      setError("Contract information is still loading. Please wait or refresh.");
      setLoading(false);
      return;
    }

    try {
      console.log("Attempting to connect to MetaMask...");
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
      console.log("MetaMask requestAccounts response:", accounts);

      if (!accounts || accounts.length === 0) {
        setError("No accounts provided by MetaMask. Connection failed or user denied.");
        setIsConnected(false);
        setAccount(null);
        setLoading(false);
        return;
      }

      const connectedAccount = accounts[0];
      setAccount(connectedAccount);
      setIsConnected(true);

      const ethProvider = new ethers.BrowserProvider(window.ethereum);
      setProvider(ethProvider);
      console.log("Ethers BrowserProvider initialized.");

      const ethSigner = await ethProvider.getSigner();
      console.log("Ethers Signer obtained:", await ethSigner.getAddress());

      // --- PERBAIKAN: Gunakan contractInfo.address dan contractInfo.abi ---
      const sensorContract = new ethers.Contract(contractInfo.address, contractInfo.abi, ethSigner);
      setContract(sensorContract);

      console.log("MetaMask Connected:", connectedAccount);
      console.log("Contract Initialized:", contractInfo.address);

    } catch (err) {
      console.error("Error connecting to MetaMask or initializing main contract:", err);
      setError(`Failed to connect: ${err.message || err.code || err}. Is Hardhat node running? Is MetaMask configured for Hardhat Local?`);
      setIsConnected(false);
      setAccount(null);
      setContract(null);
      setProvider(null);
    } finally {
      setLoading(false);
    }
  }, [contractInfo]); // contractInfo adalah dependency

  // Fungsi untuk memuat data historis dari kontrak
  const loadHistoricalData = useCallback(async () => {
    if (!contract) {
      console.warn("Contract not initialized yet, cannot load historical data.");
      setError("Contract is not initialized. Please connect MetaMask first.");
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const readings = await contract.getAllReadings();
      console.log("Raw historical data from blockchain:", readings);

      const formattedReadings = readings.map(reading => ({
        timestamp: new Date(Number(reading.timestamp) * 1000).toLocaleString(),
        temperature: Number(reading.temperature),
        humidity: Number(reading.humidity),
        sensorId: reading.sensorId,
        location: reading.location, 
        eggAgeDays: reading.processStage, // Ini akan menjadi "Usia Telur (Hari)"
      })).reverse();

      setSensorReadings(formattedReadings);
      console.log("Historical data loaded and formatted:", formattedReadings.length, "readings.");

      // Perbarui Data Grafik saat data historis dimuat
      const labels = formattedReadings.map(r => new Date(r.timestamp).toLocaleTimeString());
      const temperatures = formattedReadings.map(r => r.temperature);
      const humidities = formattedReadings.map(r => r.humidity);

      setChartData(prevData => ({
        ...prevData,
        labels: labels.reverse(), 
        datasets: [
          { ...prevData.datasets[0], data: temperatures.reverse() },
          { ...prevData.datasets[1], data: humidities.reverse() },
        ],
      }));

    } 
    catch (err) {
      console.error("Error loading historical data:", err);
      setError("Failed to load historical data from blockchain. " + (err.message || err.code));
    } finally {
      setLoading(false);
    }
  }, [contract]);

  // useEffect untuk mendengarkan event MetaMask accountsChanged/chainChanged
  useEffect(() => {
    if (window.ethereum) {
        if (window.ethereum.selectedAddress) {
            console.log("MetaMask detected and already selected an address. Attempting auto-connect.");
            connectWallet();
        } else {
            setError("Connect your MetaMask wallet to begin.");
            setLoading(false);
        }

        const handleAccountsChanged = (accounts) => {
            console.log("MetaMask accounts changed:", accounts);
            if (accounts.length === 0) {
                setIsConnected(false);
                setAccount(null);
                setContract(null);
                setProvider(null);
                setSensorReadings([]);
                setError("MetaMask disconnected.");
            } else {
                connectWallet();
            }
        };

        const handleChainChanged = (chainId) => {
            console.log("MetaMask chain changed to:", chainId);
            window.location.reload(); 
        };

        window.ethereum.on('accountsChanged', handleAccountsChanged);
        window.ethereum.on('chainChanged', handleChainChanged);

        return () => {
            if (window.ethereum.removeListener) {
                window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
                window.ethereum.removeListener('chainChanged', handleChainChanged);
            }
        };
    } else {
        setError("MetaMask is not installed. Please install it to use this DApp.");
        setLoading(false);
    }
  }, [connectWallet]);

  // useEffect KHUSUS untuk Event Listening (real-time)
  useEffect(() => {
    let cleanupFunc = () => {};

    if (contractInfo) { // Pastikan contractInfo sudah dimuat
        try {
            const wsUrl = "ws://127.0.0.1:8545"; 
            const newWsProvider = new ethers.WebSocketProvider(wsUrl);
            setWsProvider(newWsProvider); 

            // Gunakan contractInfo.address dan contractInfo.abi
            const newEventContract = new ethers.Contract(contractInfo.address, contractInfo.abi, newWsProvider);
            setEventContract(newEventContract);

            console.log("WebSocketProvider initialized:", wsUrl);
            console.log("Event Contract initialized with WebSocketProvider.");

            const handleNewSensorReading = (timestamp, temperature, humidity, sensorId, location, processStage, event) => {
                console.log("Event NewSensorReading received:", { timestamp, temperature, humidity, sensorId, location, processStage, event });
                const newReading = {
                    timestamp: new Date(Number(timestamp) * 1000).toLocaleString(),
                    temperature: Number(temperature),
                    humidity: Number(humidity),
                    sensorId: sensorId,
                    location: location,
                    eggAgeDays: processStage,
                };
                setSensorReadings(prevReadings => [newReading, ...prevReadings]); 
                console.log("New sensor reading added to state:", newReading);

                // Perbarui Data Grafik secara real-time
                setChartData(prevData => {
                    const newLabels = [...prevData.labels, new Date(newReading.timestamp).toLocaleTimeString()];
                    const newTemperatures = [...prevData.datasets[0].data, newReading.temperature];
                    const newHumidities = [...prevData.datasets[1].data, newReading.humidity];

                    const maxDataPoints = 20; 
                    if (newLabels.length > maxDataPoints) {
                        return {
                            ...prevData,
                            labels: newLabels.slice(-maxDataPoints),
                            datasets: [
                                { ...prevData.datasets[0], data: newTemperatures.slice(-maxDataPoints) },
                                { ...prevData.datasets[1], data: newHumidities.slice(-maxDataPoints) },
                            ],
                        };
                    }

                    return {
                        ...prevData,
                        labels: newLabels,
                        datasets: [
                            { ...prevData.datasets[0], data: newTemperatures },
                            { ...prevData.datasets[1], data: newHumidities },
                        ],
                    };
                });
            };

            newEventContract.on('NewSensorReading', handleNewSensorReading);
            console.log("Listening for NewSensorReading events via WebSocketProvider...");

            cleanupFunc = () => {
                newEventContract.off('NewSensorReading', handleNewSensorReading);
                console.log("Stopped listening for NewSensorReading events.");
                if (newWsProvider) {
                    newWsProvider.destroy();
                    console.log("WebSocketProvider destroyed.");
                }
            };

        } catch (wsErr) {
            console.error("Error initializing WebSocketProvider or Event Contract for real-time updates:", wsErr);
            setError(`Failed to set up real-time events: ${wsErr.message}. Data will update on refresh.`);
        }
    }

    return cleanupFunc;
  }, [contractInfo]);

  // Panggil loadHistoricalData setelah contract utama diinisialisasi
  useEffect(() => {
    if (contract) {
      loadHistoricalData();
    }
  }, [contract, loadHistoricalData]);

  if (loading || !contractInfo) {
    return (
      <div className="App">
        <header className="App-header">
          <h1>Smartine : Smart Incubator Egg Instrument</h1>
          <p>{loading ? "Memuat..." : "Menunggu informasi kontrak..."}</p>
          <p>Harap tunggu dan pastikan MetaMask sudah terinstal serta Hardhat node berjalan.</p>
        </header>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Smartine : Smart Incubator Egg Instrument</h1>
        <p className="status">
          Status: {isConnected ? <span className="connected">🟢 Terhubung</span> : <span className="disconnected">🔴 Terputus</span>}
          {account && typeof account === 'string' && ` | Akun: ${account.substring(0, 6)}...${account.substring(account.length - 4)}`}
        </p>
        {error && <p className="error-message">{error}</p>}
        {!isConnected && (
          <button onClick={connectWallet} className="connect-button">
            Hubungkan ke MetaMask
          </button>
        )}
        {isConnected && (
          <button onClick={loadHistoricalData} className="refresh-button">
            Refresh Data Historis
          </button>
        )}
      </header>

      <main>
        <div className="data-container">
          <div className="table-wrapper">
            <h2>Data Real-time & Historis (dari Blockchain)</h2>
            <table>
              <thead>
                <tr>
                  <th>Waktu</th>
                  <th>Sensor ID</th>
                  <th>Lokasi Inkubator</th>
                  <th>Usia Telur (Hari)</th>
                  <th>Fase Inkubasi</th>
                  <th>Suhu (°C)</th>
                  <th>Kelembaban (%)</th>
                </tr>
              </thead>
              <tbody>
                {sensorReadings.length === 0 ? (
                  <tr>
                    <td colSpan="7">Tidak ada data sensor yang ditemukan di blockchain. Pastikan Rust TCP Server berjalan dan mengirim transaksi.</td>
                  </tr>
                ) : (
                  sensorReadings.map((reading, index) => {
                    let incubationPhase = "Seleksi/Persiapan"; 

                    const ageMatch = reading.eggAgeDays.match(/Hari ke-(\d+)/);
                    const actualDay = ageMatch ? parseInt(ageMatch[1], 10) : 0; 
                    
                    if (actualDay >= 1 && actualDay <= 18) {
                        incubationPhase = "Inkubasi (dengan pembalikan rutin)";
                    }
                    if (actualDay >= 19 && actualDay <= 21) {
                        incubationPhase = "Inkubasi (tanpa pembalikan, kelembaban tinggi)";
                    }
                    if (actualDay >= 21 && actualDay <= 22) { 
                        incubationPhase = "Proses Penetasan Anak Ayam";
                    }
                    if (actualDay > 22 && actualDay <= 23) {
                        incubationPhase = "Pengeringan Anak Ayam";
                    }
                    if (actualDay > 23) {
                        incubationPhase = "Pemindahan Anak Ayam ke Brooder";
                    }
                    
                    return (
                      <tr key={index}>
                        <td>{reading.timestamp}</td>
                        <td>{reading.sensorId}</td>
                        <td>{reading.location}</td>
                        <td>{reading.eggAgeDays}</td>
                        <td>{incubationPhase}</td>
                        <td>{reading.temperature.toFixed(1)}</td>
                        <td>{reading.humidity.toFixed(1)}</td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          <div className="chart-wrapper">
            <h2>Tren Suhu dan Kelembaban</h2>
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;