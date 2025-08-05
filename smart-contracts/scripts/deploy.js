const { ethers } = require("hardhat");
const { writeFileSync, existsSync, mkdirSync } = require("fs");
const path = require("path");

async function main() {
  console.log("🚀 Starting Circularity Nexus Smart Contract Deployment");
  console.log("======================================================");
  
  // Get network info
  const network = await ethers.provider.getNetwork();
  console.log(`📡 Network: ${network.name} (Chain ID: ${network.chainId})`);
  
  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log(`👤 Deployer: ${deployer.address}`);
  console.log(`💰 Balance: ${ethers.formatEther(await ethers.provider.getBalance(deployer.address))} ETH`);
  
  console.log("\n🔧 Deploying contracts...\n");
  
  // Deployment configuration
  const config = {
    wasteToken: {
      name: "Circularity Waste Token",
      symbol: "CWT",
      initialOwner: deployer.address
    },
    carbonToken: {
      name: "Circularity Carbon Credits",
      symbol: "CCC",
      wasteToken: "", // Will be set after WasteTokens deployment
      carbonPriceFeed: "0x0000000000000000000000000000000000000000", // Placeholder - update with real Chainlink feed
      feeCollector: deployer.address,
      initialOwner: deployer.address
    },
    recycleVault: {
      initialOwner: deployer.address,
      feeCollector: deployer.address
    }
  };
  
  // Store deployment addresses
  const deployments = {};
  
  try {
    // 1. Deploy WasteTokens contract
    console.log("1️⃣ Deploying WasteTokens...");
    const WasteTokens = await ethers.getContractFactory("WasteTokens");
    const wasteTokens = await WasteTokens.deploy(
      config.wasteToken.name,
      config.wasteToken.symbol,
      config.wasteToken.initialOwner
    );
    await wasteTokens.waitForDeployment();
    
    const wasteTokensAddress = await wasteTokens.getAddress();
    deployments.WasteTokens = wasteTokensAddress;
    
    console.log(`   ✅ WasteTokens deployed to: ${wasteTokensAddress}`);
    console.log(`   🧾 Transaction hash: ${wasteTokens.deploymentTransaction().hash}`);
    
    // Update config with deployed address
    config.carbonToken.wasteToken = wasteTokensAddress;
    
    // 2. Deploy CarbonConverter contract
    console.log("\n2️⃣ Deploying CarbonConverter...");
    const CarbonConverter = await ethers.getContractFactory("CarbonConverter");
    const carbonConverter = await CarbonConverter.deploy(
      config.carbonToken.name,
      config.carbonToken.symbol,
      config.carbonToken.initialOwner,
      config.carbonToken.wasteToken,
      config.carbonToken.carbonPriceFeed,
      config.carbonToken.feeCollector
    );
    await carbonConverter.waitForDeployment();
    
    const carbonConverterAddress = await carbonConverter.getAddress();
    deployments.CarbonConverter = carbonConverterAddress;
    
    console.log(`   ✅ CarbonConverter deployed to: ${carbonConverterAddress}`);
    console.log(`   🧾 Transaction hash: ${carbonConverter.deploymentTransaction().hash}`);
    
    // 3. Deploy RecycleVault contract
    console.log("\n3️⃣ Deploying RecycleVault...");
    const RecycleVault = await ethers.getContractFactory("RecycleVault");
    const recycleVault = await RecycleVault.deploy(
      config.recycleVault.initialOwner,
      config.recycleVault.feeCollector
    );
    await recycleVault.waitForDeployment();
    
    const recycleVaultAddress = await recycleVault.getAddress();
    deployments.RecycleVault = recycleVaultAddress;
    
    console.log(`   ✅ RecycleVault deployed to: ${recycleVaultAddress}`);
    console.log(`   🧾 Transaction hash: ${recycleVault.deploymentTransaction().hash}`);
    
    console.log("\n🔧 Setting up contract permissions...\n");
    
    // 4. Setup permissions and initial configuration
    
    // Authorize CarbonConverter to interact with WasteTokens if needed
    // (This depends on your specific integration requirements)
    
    // Set up initial staking pool in RecycleVault (example)
    console.log("4️⃣ Creating initial staking pool...");
    
    // Example: Create a PET token staking pool
    // You might want to deploy a mock USDC token for testnet
    const createPoolTx = await recycleVault.createPool(
      wasteTokensAddress,  // Staking token (waste tokens)
      wasteTokensAddress,  // Reward token (using waste tokens as placeholder)
      ethers.parseEther("0.1"), // 0.1 tokens per second reward rate
      86400, // 1 day minimum staking period
      ethers.parseEther("10000"), // 10,000 token max staking
      "Circularity Nexus Foundation Pool"
    );
    await createPoolTx.wait();
    
    console.log(`   ✅ Initial staking pool created`);
    console.log(`   🧾 Transaction hash: ${createPoolTx.hash}`);
    
    // 5. Save deployment information
    console.log("\n💾 Saving deployment information...");
    
    const deploymentInfo = {
      network: network.name,
      chainId: network.chainId.toString(),
      deployer: deployer.address,
      timestamp: new Date().toISOString(),
      gasUsed: {
        // You can add gas usage tracking here if needed
      },
      contracts: {
        WasteTokens: {
          address: wasteTokensAddress,
          constructorArgs: [
            config.wasteToken.name,
            config.wasteToken.symbol,
            config.wasteToken.initialOwner
          ]
        },
        CarbonConverter: {
          address: carbonConverterAddress,
          constructorArgs: [
            config.carbonToken.name,
            config.carbonToken.symbol,
            config.carbonToken.initialOwner,
            config.carbonToken.wasteToken,
            config.carbonToken.carbonPriceFeed,
            config.carbonToken.feeCollector
          ]
        },
        RecycleVault: {
          address: recycleVaultAddress,
          constructorArgs: [
            config.recycleVault.initialOwner,
            config.recycleVault.feeCollector
          ]
        }
      }
    };
    
    // Create deployments directory if it doesn't exist
    const deploymentsDir = path.join(__dirname, "..", "deployments");
    if (!existsSync(deploymentsDir)) {
      mkdirSync(deploymentsDir, { recursive: true });
    }
    
    // Save to file
    const filename = `${network.name}_${Date.now()}.json`;
    const filepath = path.join(deploymentsDir, filename);
    writeFileSync(filepath, JSON.stringify(deploymentInfo, null, 2));
    
    // Also save as latest
    const latestFilepath = path.join(deploymentsDir, `${network.name}_latest.json`);
    writeFileSync(latestFilepath, JSON.stringify(deploymentInfo, null, 2));
    
    console.log(`   ✅ Deployment info saved to: ${filepath}`);
    
    // 6. Display summary
    console.log("\n🎉 Deployment Summary");
    console.log("====================");
    console.log(`📍 Network: ${network.name}`);
    console.log(`👤 Deployer: ${deployer.address}`);
    console.log(`📅 Timestamp: ${deploymentInfo.timestamp}`);
    console.log("\n📋 Contract Addresses:");
    console.log(`   WasteTokens:     ${wasteTokensAddress}`);
    console.log(`   CarbonConverter: ${carbonConverterAddress}`);
    console.log(`   RecycleVault:    ${recycleVaultAddress}`);
    
    console.log("\n🔗 Next Steps:");
    console.log("1. Verify contracts on HashScan:");
    console.log(`   npx hardhat verify --network ${network.name} ${wasteTokensAddress} "${config.wasteToken.name}" "${config.wasteToken.symbol}" "${config.wasteToken.initialOwner}"`);
    console.log(`   npx hardhat verify --network ${network.name} ${carbonConverterAddress} "${config.carbonToken.name}" "${config.carbonToken.symbol}" "${config.carbonToken.initialOwner}" "${config.carbonToken.wasteToken}" "${config.carbonToken.carbonPriceFeed}" "${config.carbonToken.feeCollector}"`);
    console.log(`   npx hardhat verify --network ${network.name} ${recycleVaultAddress} "${config.recycleVault.initialOwner}" "${config.recycleVault.feeCollector}"`);
    
    console.log("\n2. Update frontend configuration with contract addresses");
    console.log("3. Test contract interactions");
    console.log("4. Set up Chainlink price feeds for production");
    
    console.log("\n✨ Deployment completed successfully!");
    
  } catch (error) {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  }
}

// Handle errors
main().catch((error) => {
  console.error("❌ Script failed:", error);
  process.exitCode = 1;
});