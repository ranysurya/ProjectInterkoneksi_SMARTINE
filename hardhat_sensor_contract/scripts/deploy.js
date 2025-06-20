const hre = require("hardhat");
const fs = require('fs');
const path = require('path');

async function main() {
  const deployerPrivateKey = process.env.DEPLOYER_PRIVATE_KEY;
  if (!deployerPrivateKey) {
      throw new Error("DEPLOYER_PRIVATE_KEY environment variable is not set. Please run via 'start_dev_env.js' wrapper script.");
  }
  
  const deployer = new hre.ethers.Wallet(deployerPrivateKey, hre.ethers.provider);

  console.log("Deploying contracts with the account:", deployer.address);
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", balance.toString());

  console.log("Private Key of deployer (from script):", deployerPrivateKey); // Verifikasi
  
  const SensorData = await hre.ethers.getContractFactory("SensorData");
  const sensorData = await SensorData.deploy();
  await sensorData.waitForDeployment();

  const contractAddress = await sensorData.getAddress();
  console.log(`SensorData contract deployed to: ${contractAddress}`);

  const outputDir = path.join(__dirname, '..', 'contract_info');
  if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir);
  }

  // --- PERBAIKAN DI SINI ---
  // Baca konten ABI artifact yang asli dari folder artifacts Hardhat
  const artifactPath = path.join(__dirname, '..', 'artifacts', 'contracts', 'SensorData.sol', 'SensorData.json');
  const artifactContent = fs.readFileSync(artifactPath, 'utf8');
  const artifactJSON = JSON.parse(artifactContent);
  const contractABI = artifactJSON.abi; // Dapatkan ABI dari artifact

  const contractInfo = {
      address: contractAddress,
      privateKey: deployerPrivateKey,
      abi: contractABI, // <-- Sekarang ABI juga disimpan di sini
  };
  fs.writeFileSync(
      path.join(outputDir, 'SensorData.json'),
      JSON.stringify(contractInfo, null, 2)
  );

  console.log(`Contract info (address, private key, and ABI) saved to ${path.join(outputDir, 'SensorData.json')}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});