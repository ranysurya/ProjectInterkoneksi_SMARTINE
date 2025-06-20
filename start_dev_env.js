const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Pastikan jalur ke direktori Hardhat Anda benar
const HARDHAT_DIR = path.resolve(__dirname, 'hardhat_sensor_contract'); 
// Path ke file info kontrak yang akan disimpan oleh deploy.js
const CONTRACT_INFO_PATH = path.join(HARDHAT_DIR, 'contract_info', 'SensorData.json');

// Fungsi untuk menjalankan skrip deployment Hardhat
async function runDeployScript(privateKey) {
    console.log("\n--- Menjalankan skrip deployment Hardhat ---");
    // Jalankan npx hardhat run scripts/deploy.js
    const deployProcess = spawn('npx', ['hardhat', 'run', 'scripts/deploy.js', '--network', 'localhost'], {
        cwd: HARDHAT_DIR,
        stdio: 'inherit', // Biarkan output deploy script langsung ke konsol induk
        env: { ...process.env, DEPLOYER_PRIVATE_KEY: privateKey } // Teruskan private key melalui variabel lingkungan
    });

    return new Promise((resolve, reject) => {
        deployProcess.on('close', (code) => {
            if (code === 0) {
                console.log("--- Skrip deployment selesai dengan sukses ---");
                resolve();
            } else {
                console.error(`--- Skrip deployment gagal dengan kode ${code} ---`);
                reject(new Error("Deployment gagal."));
            }
        });
    });
}

// Fungsi utama untuk memulai Hardhat node dan deployment
async function startHardhatAndDeploy() {
    console.log("--- Memulai Hardhat node ---");
    // Memulai npx hardhat node sebagai child process
    const hardhatNode = spawn('npx', ['hardhat', 'node'], {
        cwd: HARDHAT_DIR,
        stdio: ['ignore', 'pipe', 'inherit'] // ignore stdin, pipe stdout to capture, inherit stderr
    });

    let privateKey = null;
    let buffer = '';

    // Menangkap output stdout dari Hardhat node untuk mencari private key
    hardhatNode.stdout.on('data', (data) => {
        const chunk = data.toString();
        buffer += chunk;
        
        // Pola regex untuk mencari Private Key
        const pkMatch = buffer.match(/Private Key:\s*(0x[a-fA-F0-9]{64})/);

        if (pkMatch && !privateKey) { // Jika private key ditemukan dan belum diambil
            privateKey = pkMatch[1];
            console.log(`\n--- Private key ditemukan: ${privateKey} ---`);
            
            // Hapus listener data dari stdout Hardhat setelah private key ditemukan
            // Ini untuk mencegah script deploy berjalan berkali-kali jika ada data lain
            // hardhatNode.stdout.removeAllListeners('data'); 
            
            // Sekarang jalankan skrip deployment
            runDeployScript(privateKey)
                .then(() => {
                    console.log("\n--- Hardhat node dan deployment selesai. Biarkan terminal ini terbuka untuk Hardhat node. ---");
                })
                .catch(err => {
                    console.error("Error selama deployment:", err);
                    hardhatNode.kill(); // Matikan Hardhat node jika deployment gagal
                    process.exit(1);
                });
        }
        // Selalu teruskan output Hardhat node ke konsol induk agar pengguna bisa melihat
        process.stdout.write(chunk);
    });

    // Tangani penutupan Hardhat node secara tidak terduga
    hardhatNode.on('close', (code) => {
        if (code !== 0) {
            console.error(`Hardhat node keluar dengan kode ${code}`);
            process.exit(1);
        }
    });

    // Tangani sinyal Ctrl+C (SIGINT) untuk mematikan Hardhat node dengan graceful
    process.on('SIGINT', () => {
        console.log("\n--- Mematikan Hardhat node... ---");
        hardhatNode.kill();
        process.exit(0);
    });
}

// Pastikan direktori contract_info ada sebelum memulai
if (!fs.existsSync(path.join(HARDHAT_DIR, 'contract_info'))) {
    fs.mkdirSync(path.join(HARDHAT_DIR, 'contract_info'));
}

// Jalankan fungsi utama
startHardhatAndDeploy().catch(console.error);