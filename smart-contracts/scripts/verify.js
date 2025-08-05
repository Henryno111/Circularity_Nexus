const { readFileSync } = require("fs");
const path = require("path");
const { run } = require("hardhat");

async function main() {
  console.log("🔍 Starting Contract Verification on HashScan");
  console.log("============================================");
  
  // Get network info
  const network = await ethers.provider.getNetwork();
  console.log(`📡 Network: ${network.name} (Chain ID: ${network.chainId})`);
  
  try {
    // Load deployment info
    const deploymentFile = path.join(__dirname, "..", "deployments", `${network.name}_latest.json`);
    
    if (!require("fs").existsSync(deploymentFile)) {
      console.error(`❌ Deployment file not found: ${deploymentFile}`);
      console.log("Please run deployment first: npm run deploy:testnet");
      process.exit(1);
    }
    
    const deploymentInfo = JSON.parse(readFileSync(deploymentFile, "utf8"));
    console.log(`📁 Loaded deployment from: ${deploymentFile}`);
    
    const contracts = deploymentInfo.contracts;
    
    // 1. Verify WasteTokens
    console.log("\n1️⃣ Verifying WasteTokens contract...");
    try {
      await run("verify:verify", {
        address: contracts.WasteTokens.address,
        constructorArguments: contracts.WasteTokens.constructorArgs,
      });
      console.log(`   ✅ WasteTokens verified: ${contracts.WasteTokens.address}`);
    } catch (error) {
      if (error.message.includes("Already Verified")) {
        console.log(`   ✅ WasteTokens already verified: ${contracts.WasteTokens.address}`);
      } else {
        console.error(`   ❌ WasteTokens verification failed:`, error.message);
      }
    }
    
    // 2. Verify CarbonConverter
    console.log("\n2️⃣ Verifying CarbonConverter contract...");
    try {
      await run("verify:verify", {
        address: contracts.CarbonConverter.address,
        constructorArguments: contracts.CarbonConverter.constructorArgs,
      });
      console.log(`   ✅ CarbonConverter verified: ${contracts.CarbonConverter.address}`);
    } catch (error) {
      if (error.message.includes("Already Verified")) {
        console.log(`   ✅ CarbonConverter already verified: ${contracts.CarbonConverter.address}`);
      } else {
        console.error(`   ❌ CarbonConverter verification failed:`, error.message);
      }
    }
    
    // 3. Verify RecycleVault
    console.log("\n3️⃣ Verifying RecycleVault contract...");
    try {
      await run("verify:verify", {
        address: contracts.RecycleVault.address,
        constructorArguments: contracts.RecycleVault.constructorArgs,
      });
      console.log(`   ✅ RecycleVault verified: ${contracts.RecycleVault.address}`);
    } catch (error) {
      if (error.message.includes("Already Verified")) {
        console.log(`   ✅ RecycleVault already verified: ${contracts.RecycleVault.address}`);
      } else {
        console.error(`   ❌ RecycleVault verification failed:`, error.message);
      }
    }
    
    // 4. Display HashScan links
    console.log("\n🔗 HashScan Links:");
    console.log("=================");
    
    const hashscanBaseUrl = getHashScanUrl(network.name);
    
    console.log(`WasteTokens:     ${hashscanBaseUrl}/address/${contracts.WasteTokens.address}`);
    console.log(`CarbonConverter: ${hashscanBaseUrl}/address/${contracts.CarbonConverter.address}`);
    console.log(`RecycleVault:    ${hashscanBaseUrl}/address/${contracts.RecycleVault.address}`);
    
    console.log("\n✨ Verification completed successfully!");
    
  } catch (error) {
    console.error("❌ Verification failed:", error);
    process.exit(1);
  }
}

function getHashScanUrl(networkName) {
  switch (networkName.toLowerCase()) {
    case 'hedera-testnet':
    case 'testnet':
      return 'https://hashscan.io/testnet';
    case 'hedera-previewnet':
    case 'previewnet':
      return 'https://hashscan.io/previewnet';
    case 'hedera-mainnet':
    case 'mainnet':
      return 'https://hashscan.io/mainnet';
    default:
      return 'https://hashscan.io/testnet';
  }
}

// Handle errors
main().catch((error) => {
  console.error("❌ Verification script failed:", error);
  process.exitCode = 1;
});