// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

/**
 * @title CarbonConverter
 * @dev Converts waste tokens to carbon credit tokens based on environmental impact
 * Uses Chainlink oracles for carbon pricing and emission factors
 */
contract CarbonConverter is ERC20, Ownable, Pausable, ReentrancyGuard {
    using SafeERC20 for IERC20;
    
    // Carbon conversion factors (kg CO2 saved per kg of waste recycled)
    // Values scaled by 1e18 for precision
    mapping(uint8 => uint256) public carbonFactors;
    
    // Waste token contract
    IERC20 public wasteToken;
    
    // Chainlink price feeds
    AggregatorV3Interface public carbonPriceFeed;
    
    // Conversion statistics
    struct ConversionRecord {
        address user;
        uint256 wasteAmount;        // Amount of waste tokens converted
        uint8 wasteType;           // Type of waste (enum from WasteTokens)
        uint256 carbonCredits;     // Carbon credits minted
        uint256 timestamp;
        string methodology;        // Carbon methodology used
        bool verified;            // External verification status
    }
    
    // Conversion tracking
    mapping(uint256 => ConversionRecord) public conversions;
    uint256 public nextConversionId;
    
    // User statistics
    mapping(address => uint256) public userTotalConversions;
    mapping(address => uint256) public userTotalCarbonCredits;
    
    // Platform statistics
    uint256 public totalWasteConverted;
    uint256 public totalCarbonCreditsIssued;
    mapping(uint8 => uint256) public wasteTypeConversions;
    
    // Conversion settings
    uint256 public conversionFee = 100; // 1% fee in basis points
    address public feeCollector;
    uint256 public minimumConversion = 1e18; // Minimum 1 waste token
    
    // Carbon credit validation
    mapping(address => bool) public authorizedVerifiers;
    uint256 public verificationRequiredThreshold = 1000e18; // 1000 carbon credits
    
    // Seasonal adjustment factors (for different carbon market conditions)
    uint256 public seasonalAdjustment = 10000; // 100% (basis points)
    
    // Events
    event WasteConverted(
        uint256 indexed conversionId,
        address indexed user,
        uint256 wasteAmount,
        uint8 wasteType,
        uint256 carbonCredits
    );
    
    event ConversionVerified(uint256 indexed conversionId, bool verified);
    event CarbonFactorUpdated(uint8 wasteType, uint256 factor);
    event VerifierAuthorized(address indexed verifier, bool authorized);
    event ConversionFeeUpdated(uint256 newFee);
    
    // Waste types (should match WasteTokens.sol)
    enum WasteType {
        PET,        // 0
        ALUMINUM,   // 1
        GLASS,      // 2
        CARDBOARD,  // 3
        PAPER,      // 4
        STEEL,      // 5
        EWASTE,     // 6
        ORGANIC     // 7
    }
    
    constructor(
        string memory name,
        string memory symbol,
        address initialOwner,
        address _wasteToken,
        address _carbonPriceFeed,
        address _feeCollector
    ) ERC20(name, symbol) Ownable(initialOwner) {
        wasteToken = IERC20(_wasteToken);
        carbonPriceFeed = AggregatorV3Interface(_carbonPriceFeed);
        feeCollector = _feeCollector;
        
        // Initialize carbon factors (kg CO2 saved per kg waste, scaled by 1e18)
        // Based on EPA and IPCC emission factors
        carbonFactors[uint8(WasteType.PET)] = 1500e15;       // 1.5 kg CO2/kg
        carbonFactors[uint8(WasteType.ALUMINUM)] = 8000e15;   // 8.0 kg CO2/kg (high energy savings)
        carbonFactors[uint8(WasteType.GLASS)] = 500e15;       // 0.5 kg CO2/kg
        carbonFactors[uint8(WasteType.CARDBOARD)] = 1200e15;  // 1.2 kg CO2/kg
        carbonFactors[uint8(WasteType.PAPER)] = 1000e15;      // 1.0 kg CO2/kg
        carbonFactors[uint8(WasteType.STEEL)] = 2000e15;      // 2.0 kg CO2/kg
        carbonFactors[uint8(WasteType.EWASTE)] = 5000e15;     // 5.0 kg CO2/kg (high impact)
        carbonFactors[uint8(WasteType.ORGANIC)] = 300e15;     // 0.3 kg CO2/kg (composting)
    }
    
    /**
     * @dev Convert waste tokens to carbon credits
     * @param wasteAmount Amount of waste tokens to convert
     * @param wasteType Type of waste being converted
     * @param methodology Carbon methodology reference (e.g., "VCS-001")
     */
    function convertToCarbonCredits(
        uint256 wasteAmount,
        uint8 wasteType,
        string memory methodology
    ) external whenNotPaused nonReentrant returns (uint256 conversionId) {
        require(wasteAmount >= minimumConversion, "Amount below minimum");
        require(wasteType < 8, "Invalid waste type");
        require(bytes(methodology).length > 0, "Methodology required");
        
        // Transfer waste tokens from user
        wasteToken.safeTransferFrom(msg.sender, address(this), wasteAmount);
        
        // Calculate carbon credits to mint
        uint256 carbonCredits = calculateCarbonCredits(wasteAmount, wasteType);
        require(carbonCredits > 0, "No carbon credits to mint");
        
        // Apply conversion fee
        uint256 fee = (carbonCredits * conversionFee) / 10000;
        uint256 userCredits = carbonCredits - fee;
        
        // Create conversion record
        conversionId = nextConversionId++;
        conversions[conversionId] = ConversionRecord({
            user: msg.sender,
            wasteAmount: wasteAmount,
            wasteType: wasteType,
            carbonCredits: userCredits,
            timestamp: block.timestamp,
            methodology: methodology,
            verified: carbonCredits < verificationRequiredThreshold // Auto-verify small amounts
        });
        
        // Mint carbon credits
        if (conversions[conversionId].verified) {
            _mint(msg.sender, userCredits);
            
            if (fee > 0) {
                _mint(feeCollector, fee);
            }
        }
        
        // Update statistics
        userTotalConversions[msg.sender]++;
        userTotalCarbonCredits[msg.sender] += userCredits;
        totalWasteConverted += wasteAmount;
        totalCarbonCreditsIssued += userCredits;
        wasteTypeConversions[wasteType] += wasteAmount;
        
        emit WasteConverted(conversionId, msg.sender, wasteAmount, wasteType, userCredits);
        
        return conversionId;
    }
    
    /**
     * @dev Calculate carbon credits for waste conversion
     * @param wasteAmount Amount of waste tokens (1 token = 1 gram)
     * @param wasteType Type of waste
     * @return carbonCredits Amount of carbon credits to mint
     */
    function calculateCarbonCredits(
        uint256 wasteAmount,
        uint8 wasteType
    ) public view returns (uint256 carbonCredits) {
        require(wasteType < 8, "Invalid waste type");
        
        // Convert waste tokens to grams (assuming 1 token = 1 gram with 18 decimals)
        uint256 wasteKg = wasteAmount / 1e18; // Convert to kg
        
        // Get carbon factor for this waste type
        uint256 carbonFactor = carbonFactors[wasteType];
        
        // Calculate base carbon credits (kg CO2 * carbon factor)
        uint256 baseCarbonCredits = (wasteKg * carbonFactor) / 1e18;
        
        // Apply seasonal adjustment
        carbonCredits = (baseCarbonCredits * seasonalAdjustment) / 10000;
        
        // Scale to token decimals (18 decimals)
        carbonCredits = carbonCredits * 1e18;
        
        return carbonCredits;
    }
    
    /**
     * @dev Verify a conversion (called by authorized verifiers)
     * @param conversionId ID of conversion to verify
     * @param verified Verification result
     */
    function verifyConversion(uint256 conversionId, bool verified) 
        external 
        onlyAuthorizedVerifier 
    {
        require(conversionId < nextConversionId, "Invalid conversion ID");
        
        ConversionRecord storage conversion = conversions[conversionId];
        require(!conversion.verified, "Already verified");
        require(conversion.carbonCredits >= verificationRequiredThreshold, "Below verification threshold");
        
        conversion.verified = verified;
        
        if (verified) {
            // Mint the carbon credits
            _mint(conversion.user, conversion.carbonCredits);
            
            // Mint fee to collector
            uint256 fee = (conversion.carbonCredits * conversionFee) / (10000 - conversionFee);
            if (fee > 0) {
                _mint(feeCollector, fee);
            }
        } else {
            // Return waste tokens if verification fails
            wasteToken.safeTransfer(conversion.user, conversion.wasteAmount);
            
            // Update statistics (reverse)
            userTotalCarbonCredits[conversion.user] -= conversion.carbonCredits;
            totalCarbonCreditsIssued -= conversion.carbonCredits;
        }
        
        emit ConversionVerified(conversionId, verified);
    }
    
    /**
     * @dev Batch convert multiple waste types
     * @param wasteAmounts Array of waste amounts
     * @param wasteTypes Array of waste types
     * @param methodology Carbon methodology reference
     */
    function batchConvert(
        uint256[] memory wasteAmounts,
        uint8[] memory wasteTypes,
        string memory methodology
    ) external whenNotPaused nonReentrant returns (uint256[] memory conversionIds) {
        require(wasteAmounts.length == wasteTypes.length, "Array length mismatch");
        require(wasteAmounts.length <= 10, "Too many conversions"); // Prevent gas limit issues
        
        conversionIds = new uint256[](wasteAmounts.length);
        
        for (uint256 i = 0; i < wasteAmounts.length; i++) {
            conversionIds[i] = convertToCarbonCredits(
                wasteAmounts[i],
                wasteTypes[i],
                methodology
            );
        }
        
        return conversionIds;
    }
    
    /**
     * @dev Get current carbon price from Chainlink oracle
     */
    function getCarbonPrice() public view returns (int256) {
        (, int256 price, , , ) = carbonPriceFeed.latestRoundData();
        return price;
    }
    
    /**
     * @dev Get conversion information
     */
    function getConversionInfo(uint256 conversionId) external view returns (
        address user,
        uint256 wasteAmount,
        uint8 wasteType,
        uint256 carbonCredits,
        uint256 timestamp,
        string memory methodology,
        bool verified
    ) {
        ConversionRecord storage conversion = conversions[conversionId];
        return (
            conversion.user,
            conversion.wasteAmount,
            conversion.wasteType,
            conversion.carbonCredits,
            conversion.timestamp,
            conversion.methodology,
            conversion.verified
        );
    }
    
    /**
     * @dev Get user conversion statistics
     */
    function getUserStats(address user) external view returns (
        uint256 totalConversions,
        uint256 totalCredits,
        uint256 currentBalance
    ) {
        return (
            userTotalConversions[user],
            userTotalCarbonCredits[user],
            balanceOf(user)
        );
    }
    
    /**
     * @dev Update carbon factor for waste type (only owner)
     */
    function updateCarbonFactor(uint8 wasteType, uint256 factor) external onlyOwner {
        require(wasteType < 8, "Invalid waste type");
        require(factor > 0, "Factor must be > 0");
        require(factor <= 20000e15, "Factor too high"); // Max 20 kg CO2/kg
        
        carbonFactors[wasteType] = factor;
        emit CarbonFactorUpdated(wasteType, factor);
    }
    
    /**
     * @dev Authorize/deauthorize verifier (only owner)
     */
    function setVerifierAuthorization(address verifier, bool authorized) external onlyOwner {
        authorizedVerifiers[verifier] = authorized;
        emit VerifierAuthorized(verifier, authorized);
    }
    
    /**
     * @dev Update conversion fee (only owner)
     */
    function setConversionFee(uint256 newFee) external onlyOwner {
        require(newFee <= 1000, "Fee too high"); // Max 10%
        conversionFee = newFee;
        emit ConversionFeeUpdated(newFee);
    }
    
    /**
     * @dev Update seasonal adjustment (only owner)
     */
    function setSeasonalAdjustment(uint256 adjustment) external onlyOwner {
        require(adjustment >= 5000 && adjustment <= 20000, "Invalid adjustment"); // 50%-200%
        seasonalAdjustment = adjustment;
    }
    
    /**
     * @dev Update verification threshold (only owner)
     */
    function setVerificationThreshold(uint256 threshold) external onlyOwner {
        verificationRequiredThreshold = threshold;
    }
    
    /**
     * @dev Update minimum conversion amount (only owner)
     */
    function setMinimumConversion(uint256 minimum) external onlyOwner {
        minimumConversion = minimum;
    }
    
    /**
     * @dev Retire carbon credits (burn tokens to offset emissions)
     * @param amount Amount of carbon credits to retire
     * @param reason Reason for retirement (e.g., "Corporate offset Q4 2024")
     */
    function retireCredits(uint256 amount, string memory reason) external {
        require(amount > 0, "Amount must be > 0");
        require(bytes(reason).length > 0, "Reason required");
        
        _burn(msg.sender, amount);
        
        // Could emit retirement event or certificate here
        // emit CarbonCreditsRetired(msg.sender, amount, reason, block.timestamp);
    }
    
    modifier onlyAuthorizedVerifier() {
        require(authorizedVerifiers[msg.sender] || msg.sender == owner(), "Not authorized verifier");
        _;
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
     * @dev Emergency withdraw (only owner, when paused)
     */
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner whenPaused {
        IERC20(token).safeTransfer(owner(), amount);
    }
}