// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title WasteTokens
 * @dev Material-specific waste tokenization contract for Circularity Nexus
 * Supports multiple waste types with quality grading and metadata
 */
contract WasteTokens is ERC20, ERC20Burnable, Ownable, Pausable, ReentrancyGuard {
    
    // Waste material types
    enum WasteType {
        PET,        // Plastic bottles
        ALUMINUM,   // Aluminum cans
        GLASS,      // Glass bottles
        CARDBOARD,  // Cardboard
        PAPER,      // Paper
        STEEL,      // Steel cans
        EWASTE,     // Electronic waste
        ORGANIC     // Organic waste
    }
    
    // Quality grades for waste
    enum Quality {
        EXCELLENT,  // 100% token value
        GOOD,       // 80% token value
        FAIR,       // 60% token value
        POOR,       // 40% token value
        UNUSABLE    // 0% token value
    }
    
    // Waste submission structure
    struct WasteSubmission {
        address submitter;
        WasteType wasteType;
        Quality quality;
        uint256 weight;        // Weight in grams
        uint256 tokensMinted;  // Tokens minted for this submission
        string ipfsHash;       // IPFS hash of waste image
        uint256 timestamp;
        bool verified;         // AI verification status
        string location;       // GPS coordinates
    }
    
    // Token multipliers for different waste types (basis points, 10000 = 1.0x)
    mapping(WasteType => uint256) public wasteTypeMultipliers;
    
    // Quality multipliers (basis points, 10000 = 1.0x)
    mapping(Quality => uint256) public qualityMultipliers;
    
    // Waste submissions tracking
    mapping(uint256 => WasteSubmission) public wasteSubmissions;
    uint256 public nextSubmissionId;
    
    // User statistics
    mapping(address => uint256) public userTotalSubmissions;
    mapping(address => uint256) public userTotalTokensEarned;
    mapping(address => mapping(WasteType => uint256)) public userWasteTypeTokens;
    
    // Platform statistics
    uint256 public totalWasteProcessed; // Total weight in grams
    uint256 public totalSubmissions;
    mapping(WasteType => uint256) public wasteTypeStats;
    
    // Base token rate: 1 gram = 1000 tokens (with 18 decimals)
    uint256 public constant BASE_RATE = 1000 * 1e18;
    
    // Events
    event WasteSubmitted(
        uint256 indexed submissionId,
        address indexed submitter,
        WasteType wasteType,
        Quality quality,
        uint256 weight,
        uint256 tokensMinted
    );
    
    event WasteVerified(uint256 indexed submissionId, bool verified);
    event TokensMinted(address indexed user, uint256 amount, WasteType wasteType);
    event MultiplierUpdated(WasteType wasteType, uint256 multiplier);
    event QualityMultiplierUpdated(Quality quality, uint256 multiplier);
    
    constructor(
        string memory name,
        string memory symbol,
        address initialOwner
    ) ERC20(name, symbol) Ownable(initialOwner) {
        // Initialize waste type multipliers (basis points)
        wasteTypeMultipliers[WasteType.PET] = 12000;      // 1.2x - High demand
        wasteTypeMultipliers[WasteType.ALUMINUM] = 15000;  // 1.5x - Very high value
        wasteTypeMultipliers[WasteType.GLASS] = 8000;      // 0.8x - Lower value
        wasteTypeMultipliers[WasteType.CARDBOARD] = 6000;  // 0.6x - Common
        wasteTypeMultipliers[WasteType.PAPER] = 5000;      // 0.5x - Very common
        wasteTypeMultipliers[WasteType.STEEL] = 10000;     // 1.0x - Standard
        wasteTypeMultipliers[WasteType.EWASTE] = 20000;    // 2.0x - Highest value
        wasteTypeMultipliers[WasteType.ORGANIC] = 3000;    // 0.3x - Composting
        
        // Initialize quality multipliers (basis points)
        qualityMultipliers[Quality.EXCELLENT] = 10000;  // 1.0x
        qualityMultipliers[Quality.GOOD] = 8000;        // 0.8x
        qualityMultipliers[Quality.FAIR] = 6000;        // 0.6x
        qualityMultipliers[Quality.POOR] = 4000;        // 0.4x
        qualityMultipliers[Quality.UNUSABLE] = 0;       // 0x
    }
    
    /**
     * @dev Submit waste for tokenization
     * @param wasteType Type of waste material
     * @param quality Quality grade of the waste
     * @param weight Weight of waste in grams
     * @param ipfsHash IPFS hash of waste image
     * @param location GPS coordinates of submission
     */
    function submitWaste(
        WasteType wasteType,
        Quality quality,
        uint256 weight,
        string memory ipfsHash,
        string memory location
    ) external whenNotPaused nonReentrant returns (uint256 submissionId) {
        require(weight > 0, "Weight must be greater than 0");
        require(bytes(ipfsHash).length > 0, "IPFS hash required");
        
        submissionId = nextSubmissionId++;
        
        // Calculate tokens to mint based on waste type and quality
        uint256 tokensToMint = calculateTokens(wasteType, quality, weight);
        
        // Create waste submission record
        wasteSubmissions[submissionId] = WasteSubmission({
            submitter: msg.sender,
            wasteType: wasteType,
            quality: quality,
            weight: weight,
            tokensMinted: tokensToMint,
            ipfsHash: ipfsHash,
            timestamp: block.timestamp,
            verified: false,
            location: location
        });
        
        // Update statistics
        userTotalSubmissions[msg.sender]++;
        totalSubmissions++;
        
        // Mint tokens if quality is not UNUSABLE
        if (quality != Quality.UNUSABLE && tokensToMint > 0) {
            _mint(msg.sender, tokensToMint);
            
            // Update user statistics
            userTotalTokensEarned[msg.sender] += tokensToMint;
            userWasteTypeTokens[msg.sender][wasteType] += tokensToMint;
            
            // Update platform statistics
            totalWasteProcessed += weight;
            wasteTypeStats[wasteType] += weight;
            
            emit TokensMinted(msg.sender, tokensToMint, wasteType);
        }
        
        emit WasteSubmitted(
            submissionId,
            msg.sender,
            wasteType,
            quality,
            weight,
            tokensToMint
        );
        
        return submissionId;
    }
    
    /**
     * @dev Verify waste submission (called by AI verification system)
     * @param submissionId ID of the submission to verify
     * @param verified Verification result
     */
    function verifyWaste(uint256 submissionId, bool verified) external onlyOwner {
        require(submissionId < nextSubmissionId, "Invalid submission ID");
        
        WasteSubmission storage submission = wasteSubmissions[submissionId];
        require(!submission.verified, "Already verified");
        
        submission.verified = verified;
        
        // If verification fails, burn the minted tokens
        if (!verified && submission.tokensMinted > 0) {
            _burn(submission.submitter, submission.tokensMinted);
            
            // Update statistics
            userTotalTokensEarned[submission.submitter] -= submission.tokensMinted;
            userWasteTypeTokens[submission.submitter][submission.wasteType] -= submission.tokensMinted;
            totalWasteProcessed -= submission.weight;
            wasteTypeStats[submission.wasteType] -= submission.weight;
        }
        
        emit WasteVerified(submissionId, verified);
    }
    
    /**
     * @dev Calculate tokens for waste submission
     * @param wasteType Type of waste material
     * @param quality Quality grade
     * @param weight Weight in grams
     * @return tokensToMint Number of tokens to mint
     */
    function calculateTokens(
        WasteType wasteType,
        Quality quality,
        uint256 weight
    ) public view returns (uint256 tokensToMint) {
        if (quality == Quality.UNUSABLE) {
            return 0;
        }
        
        // Base tokens = weight * BASE_RATE
        uint256 baseTokens = weight * BASE_RATE;
        
        // Apply waste type multiplier
        uint256 wasteMultiplier = wasteTypeMultipliers[wasteType];
        uint256 tokensAfterType = (baseTokens * wasteMultiplier) / 10000;
        
        // Apply quality multiplier
        uint256 qualityMultiplier = qualityMultipliers[quality];
        tokensToMint = (tokensAfterType * qualityMultiplier) / 10000;
        
        return tokensToMint;
    }
    
    /**
     * @dev Update waste type multiplier (only owner)
     */
    function updateWasteTypeMultiplier(WasteType wasteType, uint256 multiplier) external onlyOwner {
        require(multiplier <= 50000, "Multiplier too high"); // Max 5x
        wasteTypeMultipliers[wasteType] = multiplier;
        emit MultiplierUpdated(wasteType, multiplier);
    }
    
    /**
     * @dev Update quality multiplier (only owner)
     */
    function updateQualityMultiplier(Quality quality, uint256 multiplier) external onlyOwner {
        require(multiplier <= 10000, "Multiplier too high"); // Max 1x
        qualityMultipliers[quality] = multiplier;
        emit QualityMultiplierUpdated(quality, multiplier);
    }
    
    /**
     * @dev Get user statistics
     */
    function getUserStats(address user) external view returns (
        uint256 totalSubmissions,
        uint256 totalTokensEarned,
        uint256 currentBalance
    ) {
        return (
            userTotalSubmissions[user],
            userTotalTokensEarned[user],
            balanceOf(user)
        );
    }
    
    /**
     * @dev Get platform statistics
     */
    function getPlatformStats() external view returns (
        uint256 totalProcessed,
        uint256 totalSubs,
        uint256 totalSupply
    ) {
        return (
            totalWasteProcessed,
            totalSubmissions,
            totalSupply()
        );
    }
    
    /**
     * @dev Pause contract (emergency stop)
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause contract
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Override required by Solidity
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override whenNotPaused {
        super._beforeTokenTransfer(from, to, amount);
    }
}