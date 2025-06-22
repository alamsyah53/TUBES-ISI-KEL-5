async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contract with account:", deployer.address);

  const SensorStorage = await ethers.getContractFactory("SensorStorage");
  const contract = await SensorStorage.deploy();  // <- deploy di sini
  await contract.waitForDeployment();             // <- yang benar sekarang (Hardhat v2.20+)

  console.log("✅ Contract deployed at:", await contract.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

