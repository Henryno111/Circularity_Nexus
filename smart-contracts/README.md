# 🌍 Circularity Nexus Smart Contracts

## *"Tokenize Trash. Earn Wealth. Heal the Planet."* - Smart Contract Layer

[![Solidity](https://img.shields.io/badge/Solidity-0.8.24-blue.svg)](https://soliditylang.org)
[![Hardhat](https://img.shields.io/badge/Hardhat-Latest-yellow.svg)](https://hardhat.org)
[![Hedera](https://img.shields.io/badge/Hedera-Testnet%20%7C%20Mainnet-purple.svg)](https://hedera.com)
[![OpenZeppelin](https://img.shields.io/badge/OpenZeppelin-5.0.1-green.svg)](https://openzeppelin.com)

> **Revolutionary Smart Contracts** for waste tokenization, DeFi staking, and carbon credit conversion on Hedera Hashgraph. Transform waste into tradeable assets with enterprise-grade security and sustainability features.

---

## 🚀 **Smart Contract Architecture**

### **Core Contracts**

#### 🗑️ **WasteTokens.sol** - Material-Specific Tokenization
- **50+ Waste Types**: PET, Aluminum, Glass, E-waste, Organic, etc.
- **Quality Grading**: EXCELLENT → GOOD → FAIR → POOR → UNUSABLE
- **AI Verification**: Integration with Groq AI validation system
- **Dynamic Pricing**: Market-based token multipliers
- **Anti-Fraud**: Cross-verification with IoT sensor data

#### 💰 **RecycleVault.sol** - DeFi Staking Platform
- **Corporate ESG Pools**: Partner-funded reward vaults
- **Multi-Token Support**: Stake any waste token type
- **Flexible Rewards**: USDC, HBAR, or custom token rewards
- **Yield Farming**: 5-25% APY based on waste demand
- **Lock Periods**: Configurable minimum staking times

#### 🌱 **CarbonConverter.sol** - Carbon Credit Engine
- **Automatic Conversion**: Waste tokens → Carbon credits
- **Chainlink Oracles**: Real-time carbon pricing
- **Methodology Support**: VCS, Gold Standard, ACR compliance
- **Verification Tiers**: Automated + Manual verification
- **Impact Tracking**: Real CO2 reduction calculations

---

## 📁 **Project Structure**

```
smart-contracts/
├── 📄 contracts/                    # Solidity smart contracts
│   ├── WasteTokens.sol             # Core waste tokenization
│   ├── RecycleVault.sol            # DeFi staking vaults
│   └── CarbonConverter.sol         # Carbon credit conversion
├── 🧪 test/                        # Comprehensive test suite
│   ├── WasteTokens.test.js         # WasteTokens contract tests
│   ├── RecycleVault.test.js        # DeFi vault tests
│   └── CarbonConverter.test.js     # Carbon conversion tests
├── 🚀 scripts/                     # Deployment & utility scripts
│   ├── deploy.js                   # Full deployment script
│   ├── verify.js                   # Contract verification
│   └── utils/                      # Helper utilities
├── 📊 deployments/                 # Deployment records
│   ├── hedera-testnet_latest.json  # Latest testnet deployment
│   └── hedera-mainnet_latest.json  # Latest mainnet deployment
├── ⚙️ hardhat.config.js            # Hardhat configuration
├── 📦 package.json                 # Dependencies & scripts
└── 📚 README.md                    # This file
```

---

## 🛠️ **Quick Start**

### **Prerequisites**
```bash
# System Requirements
Node.js 18+
npm or yarn
Git

# Hedera Account (for deployment)
Hedera Testnet Account ID & Private Key
HBAR balance for gas fees
```

### **1. Installation**
```bash
# Clone the repository
git clone https://github.com/circularitynexus/core.git
cd core/smart-contracts

# Install dependencies
npm install

# Copy environment template
cp .env.example .env
```

### **2. Environment Setup**
```bash
# Edit .env file with your Hedera credentials
nano .env
```

**Required Environment Variables:**
```bash
# Hedera Testnet
HEDERA_TESTNET_PRIVATE_KEY=your_private_key_here
HEDERA_TESTNET_ACCOUNT_ID=0.0.YOUR_ACCOUNT_ID

# Hedera Mainnet (for production)
HEDERA_MAINNET_PRIVATE_KEY=your_mainnet_private_key
HEDERA_MAINNET_ACCOUNT_ID=0.0.YOUR_MAINNET_ACCOUNT_ID

# Optional: HashScan API Key (for verification)
HASHSCAN_API_KEY=your_api_key_here
```

### **3. Compile Contracts**
```bash
# Compile all contracts
npm run compile

# Check contract sizes
npx hardhat size-contracts
```

### **4. Run Tests**
```bash
# Run comprehensive test suite
npm test

# Run with gas reporting
REPORT_GAS=true npm test

# Run with coverage
npm run coverage
```

---

## 🚀 **Deployment**

### **Testnet Deployment**
```bash
# Deploy to Hedera Testnet
npm run deploy:testnet

# Verify contracts on HashScan
npm run verify
```

### **Mainnet Deployment**
```bash
# Deploy to Hedera Mainnet (production)
npm run deploy:mainnet

# Verify contracts
npm run verify
```

### **Deployment Output**
After successful deployment, you'll receive:
```
🎉 Deployment Summary
====================
📍 Network: hedera-testnet
👤 Deployer: 0x1234...5678
📅 Timestamp: 2024-12-14T10:30:00.000Z

📋 Contract Addresses:
   WasteTokens:     0xABC123...DEF456
   CarbonConverter: 0x789ABC...123DEF
   RecycleVault:    0x456DEF...789ABC

🔗 HashScan Links:
   WasteTokens:     https://hashscan.io/testnet/address/0xABC123...DEF456
   CarbonConverter: https://hashscan.io/testnet/address/0x789ABC...123DEF
   RecycleVault:    https://hashscan.io/testnet/address/0x456DEF...789ABC
```

---

## 🧪 **Testing**

### **Comprehensive Test Coverage**
```bash
# Run all tests
npm test

# Run specific contract tests
npx hardhat test test/WasteTokens.test.js
npx hardhat test test/RecycleVault.test.js
npx hardhat test test/CarbonConverter.test.js

# Run with detailed output
npx hardhat test --verbose
```

### **Test Categories**
- ✅ **Unit Tests**: Individual contract functionality
- ✅ **Integration Tests**: Inter-contract interactions
- ✅ **Security Tests**: Access controls, reentrancy protection
- ✅ **Economic Tests**: Token economics, reward calculations
- ✅ **Edge Cases**: Boundary conditions, error handling

### **Coverage Report**
```bash
npm run coverage
```
Target: **90%+ code coverage** across all contracts

---

## 📊 **Contract Features**

### **🗑️ WasteTokens Contract**

#### **Waste Types & Multipliers**
| Waste Type | Multiplier | Example Use Case |
|------------|------------|------------------|
| **PET Plastic** | 1.2x | Plastic bottles, containers |
| **Aluminum** | 1.5x | Cans, foil (high recycling value) |
| **Glass** | 0.8x | Bottles, jars |
| **Cardboard** | 0.6x | Packaging, boxes |
| **Paper** | 0.5x | Newspapers, documents |
| **Steel** | 1.0x | Cans, metal objects |
| **E-waste** | 2.0x | Electronics (highest multiplier) |
| **Organic** | 0.3x | Compostable materials |

#### **Quality Grades**
| Quality | Multiplier | Description |
|---------|------------|-------------|
| **EXCELLENT** | 1.0x | Perfect condition, high recycling value |
| **GOOD** | 0.8x | Minor imperfections, good recyclability |
| **FAIR** | 0.6x | Moderate damage, still recyclable |
| **POOR** | 0.4x | Significant wear, limited recyclability |
| **UNUSABLE** | 0x | Cannot be recycled, no tokens minted |

### **💰 RecycleVault Contract**

#### **Staking Features**
- **Multi-Pool Support**: Different pools for different waste types
- **Corporate Partnerships**: ESG-funded reward pools
- **Flexible Lock Periods**: 1 day to 1 year options
- **Dynamic APY**: 5-25% based on demand and partner funding
- **Auto-Compounding**: Optional reward reinvestment

#### **Pool Configuration**
```solidity
// Example pool creation
createPool(
    wasteTokenAddress,    // Staking token
    usdcAddress,         // Reward token
    0.1 ether,           // 0.1 USDC per second reward rate
    86400,               // 1 day minimum staking
    10000 ether,         // 10,000 token max per user
    "Unilever ESG Pool"  // Partner name
);
```

### **🌱 CarbonConverter Contract**

#### **Carbon Conversion Factors**
| Waste Type | CO₂ Saved (kg/kg) | Impact |
|------------|-------------------|---------|
| **PET** | 1.5 | Reduces plastic production emissions |
| **Aluminum** | 8.0 | Massive energy savings vs. new production |
| **Glass** | 0.5 | Moderate energy savings |
| **Cardboard** | 1.2 | Prevents deforestation |
| **Paper** | 1.0 | Saves trees and processing energy |
| **Steel** | 2.0 | High energy recycling savings |
| **E-waste** | 5.0 | Prevents toxic material mining |
| **Organic** | 0.3 | Composting vs. landfill methane |

---

## 🔒 **Security Features**

### **Access Controls**
- **Ownable**: Admin functions restricted to contract owner
- **Role-Based**: Multiple admin roles for different functions
- **Multi-Sig**: Recommended for production deployments

### **Security Measures**
- **ReentrancyGuard**: Prevents reentrancy attacks
- **Pausable**: Emergency stop functionality
- **SafeERC20**: Safe token transfer operations
- **Input Validation**: Comprehensive parameter checking
- **Rate Limiting**: Prevent spam and abuse

### **Audit Readiness**
- **Comprehensive Tests**: 90%+ code coverage
- **Static Analysis**: Solhint + Slither compatible
- **Gas Optimization**: Efficient contract design
- **Upgrade Safety**: Proxy-safe implementation patterns

---

## 🌐 **Network Configuration**

### **Hedera Networks**
| Network | Chain ID | JSON-RPC URL | Purpose |
|---------|----------|--------------|---------|
| **Testnet** | 296 | `https://testnet.hashio.io/api` | Development & testing |
| **Previewnet** | 297 | `https://previewnet.hashio.io/api` | Pre-production testing |
| **Mainnet** | 295 | `https://mainnet.hashio.io/api` | Production deployment |

### **Gas & Fees**
- **Gas Limit**: 3,000,000 per transaction
- **Gas Price**: 2 gwei (fixed on Hedera)
- **Deployment Cost**: ~0.1 HBAR per contract
- **Transaction Cost**: ~$0.0001 per operation

---

## 🔗 **Integration Guide**

### **Frontend Integration**
```javascript
// Import contract ABI and addresses
import { WasteTokensABI, WASTE_TOKENS_ADDRESS } from './contracts';
import { ethers } from 'ethers';

// Connect to contract
const provider = new ethers.JsonRpcProvider('https://testnet.hashio.io/api');
const contract = new ethers.Contract(WASTE_TOKENS_ADDRESS, WasteTokensABI, provider);

// Submit waste for tokenization
const submitWaste = async (wasteType, quality, weight, ipfsHash, location) => {
  const tx = await contract.submitWaste(wasteType, quality, weight, ipfsHash, location);
  return await tx.wait();
};

// Get user statistics
const getUserStats = async (userAddress) => {
  return await contract.getUserStats(userAddress);
};
```

### **Backend Integration**
```javascript
// Using Hedera SDK for native integration
const { Client, AccountId, PrivateKey, ContractExecuteTransaction } = require("@hashgraph/sdk");

const client = Client.forTestnet();
client.setOperator(accountId, privateKey);

// Execute contract function
const contractExecution = new ContractExecuteTransaction()
  .setContractId(contractId)
  .setGas(100000)
  .setFunction("submitWaste", parameters);

const response = await contractExecution.execute(client);
```

---

## 📈 **Economics & Tokenomics**

### **Token Economics**
- **Base Rate**: 1 gram waste = 1,000 tokens (with multipliers)
- **Total Supply**: Unlimited (minted based on verified waste)
- **Burn Mechanism**: Failed verification burns tokens
- **Fee Structure**: 1-5% platform fees on rewards

### **Reward Distribution**
```
Corporate ESG Pool Funding:
├── 90% → User Rewards
├── 5%  → Platform Operations
└── 5%  → Carbon Offset Fund
```

### **Carbon Credit Pricing**
- **Market Rate**: $10-50 per ton CO₂ (via Chainlink oracles)
- **Conversion**: Automatic waste → carbon credits
- **Verification**: Required for credits >1000 tokens
- **Retirement**: Permanent burn for carbon offsetting

---

## 🚀 **Roadmap**

### **Phase 1: Core Contracts** ✅
- [x] WasteTokens implementation
- [x] RecycleVault staking
- [x] CarbonConverter mechanism
- [x] Comprehensive testing
- [x] Hedera testnet deployment

### **Phase 2: Advanced Features** 🚧
- [ ] NFT certificates for large recyclers
- [ ] Governance token (CIRC) implementation
- [ ] Cross-chain bridge support
- [ ] Advanced oracle integrations

### **Phase 3: Enterprise Features** 📋
- [ ] Multi-signature treasury
- [ ] Regulatory compliance modules
- [ ] Enterprise dashboard contracts
- [ ] Supply chain tracking

### **Phase 4: Global Scale** 🌍
- [ ] Multi-region deployment
- [ ] Government partnership contracts
- [ ] International carbon credit standards
- [ ] Global impact measurement

---

## 🤝 **Contributing**

### **Development Setup**
```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/circularity-nexus.git
cd circularity-nexus/smart-contracts

# Install dependencies
npm install

# Create your feature branch
git checkout -b feature/amazing-feature

# Make your changes and test
npm test

# Submit a pull request
```

### **Contribution Guidelines**
- **Code Quality**: Follow Solidity best practices
- **Testing**: Maintain 90%+ test coverage
- **Documentation**: Update README and code comments
- **Security**: No hardcoded keys or unsafe operations
- **Gas Optimization**: Efficient contract designs

---

## 📞 **Support & Community**

### **Get Help**
- 📚 **Documentation**: [docs.circularitynexus.io](https://docs.circularitynexus.io)
- 💬 **Discord**: [Join our developer community](https://discord.gg/circularitynexus)
- 🐛 **Issues**: [GitHub Issues](https://github.com/circularitynexus/core/issues)
- 📧 **Email**: contracts@circularitynexus.io

### **Security**
Found a security issue? Please report responsibly:
- 📧 **Email**: security@circularitynexus.io
- 🔒 **PGP**: [Public Key](https://circularitynexus.io/pgp)
- ⏰ **Response**: < 24 hours

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

<div align="center">

## 🌍 **Building the Future of Waste Management**

*Every smart contract deployed is a step toward a circular economy.*  
*Every token minted represents real environmental impact.*  
*Every developer who contributes helps heal our planet.*

**[Deploy Contracts](./scripts/deploy.js) | [Run Tests](./test/) | [View Docs](https://docs.circularitynexus.io)**

---

**Made with 💚 by the Circularity Nexus Team**  
*Tokenize Trash. Earn Wealth. Heal the Planet.*

</div>