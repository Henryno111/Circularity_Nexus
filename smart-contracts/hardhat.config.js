require("@nomicfoundation/hardhat-toolbox");
require("@nomicfoundation/hardhat-verify");
require("hardhat-contract-sizer");
require("hardhat-gas-reporter");
require("solidity-coverage");
require("dotenv").config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      },
      viaIR: true
    }
  },
  
  networks: {
    // Hedera Testnet
    "hedera-testnet": {
      url: "https://testnet.hashio.io/api",
      accounts: process.env.HEDERA_TESTNET_PRIVATE_KEY ? [process.env.HEDERA_TESTNET_PRIVATE_KEY] : [],
      chainId: 296,
      gas: 1000000,
      gasPrice: 2000000000, // 2 gwei
      timeout: 20000
    },
    
    // Hedera Previewnet
    "hedera-previewnet": {
      url: "https://previewnet.hashio.io/api",
      accounts: process.env.HEDERA_PREVIEWNET_PRIVATE_KEY ? [process.env.HEDERA_PREVIEWNET_PRIVATE_KEY] : [],
      chainId: 297,
      gas: 1000000,
      gasPrice: 2000000000,
      timeout: 20000
    },
    
    // Hedera Mainnet
    "hedera-mainnet": {
      url: "https://mainnet.hashio.io/api",
      accounts: process.env.HEDERA_MAINNET_PRIVATE_KEY ? [process.env.HEDERA_MAINNET_PRIVATE_KEY] : [],
      chainId: 295,
      gas: 1000000,
      gasPrice: 2000000000,
      timeout: 20000
    },
    
    // Local development
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337
    }
  },
  
  // Etherscan verification (for HashScan)
  etherscan: {
    apiKey: {
      "hedera-testnet": process.env.HASHSCAN_API_KEY || "dummy",
      "hedera-previewnet": process.env.HASHSCAN_API_KEY || "dummy",
      "hedera-mainnet": process.env.HASHSCAN_API_KEY || "dummy"
    },
    customChains: [
      {
        network: "hedera-testnet",
        chainId: 296,
        urls: {
          apiURL: "https://server-verify.hashscan.io",
          browserURL: "https://hashscan.io/testnet"
        }
      },
      {
        network: "hedera-previewnet", 
        chainId: 297,
        urls: {
          apiURL: "https://server-verify.hashscan.io",
          browserURL: "https://hashscan.io/previewnet"
        }
      },
      {
        network: "hedera-mainnet",
        chainId: 295,
        urls: {
          apiURL: "https://server-verify.hashscan.io",
          browserURL: "https://hashscan.io/mainnet"
        }
      }
    ]
  },
  
  // Gas reporting
  gasReporter: {
    enabled: process.env.REPORT_GAS !== undefined,
    currency: "USD",
    gasPrice: 2
  },
  
  // Contract size reporting
  contractSizer: {
    alphaSort: true,
    disambiguatePaths: false,
    runOnCompile: true,
    strict: true
  },
  
  // Code coverage
  coverage: {
    statements: 95,
    branches: 90,
    functions: 95,
    lines: 95
  },
  
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  },
  
  mocha: {
    timeout: 40000
  }
};