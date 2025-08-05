const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");

describe("WasteTokens", function () {
  // Waste types enum
  const WasteType = {
    PET: 0,
    ALUMINUM: 1,
    GLASS: 2,
    CARDBOARD: 3,
    PAPER: 4,
    STEEL: 5,
    EWASTE: 6,
    ORGANIC: 7
  };
  
  // Quality enum
  const Quality = {
    EXCELLENT: 0,
    GOOD: 1,
    FAIR: 2,
    POOR: 3,
    UNUSABLE: 4
  };
  
  async function deployWasteTokensFixture() {
    const [owner, user1, user2] = await ethers.getSigners();
    
    const WasteTokens = await ethers.getContractFactory("WasteTokens");
    const wasteTokens = await WasteTokens.deploy(
      "Circularity Waste Token",
      "CWT",
      owner.address
    );
    
    return { wasteTokens, owner, user1, user2 };
  }
  
  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      const { wasteTokens, owner } = await loadFixture(deployWasteTokensFixture);
      expect(await wasteTokens.owner()).to.equal(owner.address);
    });
    
    it("Should set the correct token name and symbol", async function () {
      const { wasteTokens } = await loadFixture(deployWasteTokensFixture);
      expect(await wasteTokens.name()).to.equal("Circularity Waste Token");
      expect(await wasteTokens.symbol()).to.equal("CWT");
    });
    
    it("Should initialize waste type multipliers correctly", async function () {
      const { wasteTokens } = await loadFixture(deployWasteTokensFixture);
      
      expect(await wasteTokens.wasteTypeMultipliers(WasteType.PET)).to.equal(12000);
      expect(await wasteTokens.wasteTypeMultipliers(WasteType.ALUMINUM)).to.equal(15000);
      expect(await wasteTokens.wasteTypeMultipliers(WasteType.EWASTE)).to.equal(20000);
    });
    
    it("Should initialize quality multipliers correctly", async function () {
      const { wasteTokens } = await loadFixture(deployWasteTokensFixture);
      
      expect(await wasteTokens.qualityMultipliers(Quality.EXCELLENT)).to.equal(10000);
      expect(await wasteTokens.qualityMultipliers(Quality.GOOD)).to.equal(8000);
      expect(await wasteTokens.qualityMultipliers(Quality.UNUSABLE)).to.equal(0);
    });
  });
  
  describe("Waste Submission", function () {
    it("Should submit waste and mint tokens correctly", async function () {
      const { wasteTokens, user1 } = await loadFixture(deployWasteTokensFixture);
      
      const weight = 1000; // 1000 grams
      const wasteType = WasteType.PET;
      const quality = Quality.EXCELLENT;
      const ipfsHash = "QmTestHash123";
      const location = "40.7128,-74.0060"; // NYC coordinates
      
      await expect(
        wasteTokens.connect(user1).submitWaste(
          wasteType,
          quality,
          weight,
          ipfsHash,
          location
        )
      ).to.emit(wasteTokens, "WasteSubmitted")
        .and.to.emit(wasteTokens, "TokensMinted");
      
      // Check if tokens were minted
      const expectedTokens = await wasteTokens.calculateTokens(wasteType, quality, weight);
      expect(await wasteTokens.balanceOf(user1.address)).to.equal(expectedTokens);
    });
    
    it("Should not mint tokens for UNUSABLE quality", async function () {
      const { wasteTokens, user1 } = await loadFixture(deployWasteTokensFixture);
      
      await wasteTokens.connect(user1).submitWaste(
        WasteType.PET,
        Quality.UNUSABLE,
        1000,
        "QmTestHash",
        "40.7128,-74.0060"
      );
      
      expect(await wasteTokens.balanceOf(user1.address)).to.equal(0);
    });
    
    it("Should revert with zero weight", async function () {
      const { wasteTokens, user1 } = await loadFixture(deployWasteTokensFixture);
      
      await expect(
        wasteTokens.connect(user1).submitWaste(
          WasteType.PET,
          Quality.EXCELLENT,
          0, // Zero weight
          "QmTestHash",
          "40.7128,-74.0060"
        )
      ).to.be.revertedWith("Weight must be greater than 0");
    });
    
    it("Should revert with empty IPFS hash", async function () {
      const { wasteTokens, user1 } = await loadFixture(deployWasteTokensFixture);
      
      await expect(
        wasteTokens.connect(user1).submitWaste(
          WasteType.PET,
          Quality.EXCELLENT,
          1000,
          "", // Empty IPFS hash
          "40.7128,-74.0060"
        )
      ).to.be.revertedWith("IPFS hash required");
    });
  });
  
  describe("Token Calculation", function () {
    it("Should calculate tokens correctly for different waste types", async function () {
      const { wasteTokens } = await loadFixture(deployWasteTokensFixture);
      
      const weight = 1000; // 1000 grams
      const quality = Quality.EXCELLENT;
      
      // PET: 1.2x multiplier
      const petTokens = await wasteTokens.calculateTokens(WasteType.PET, quality, weight);
      const expectedPetTokens = ethers.parseEther("1200000"); // 1000 * 1000 * 1.2 * 1.0
      expect(petTokens).to.equal(expectedPetTokens);
      
      // Aluminum: 1.5x multiplier
      const aluminumTokens = await wasteTokens.calculateTokens(WasteType.ALUMINUM, quality, weight);
      const expectedAluminumTokens = ethers.parseEther("1500000"); // 1000 * 1000 * 1.5 * 1.0
      expect(aluminumTokens).to.equal(expectedAluminumTokens);
      
      // E-waste: 2.0x multiplier
      const ewasteTokens = await wasteTokens.calculateTokens(WasteType.EWASTE, quality, weight);
      const expectedEwasteTokens = ethers.parseEther("2000000"); // 1000 * 1000 * 2.0 * 1.0
      expect(ewasteTokens).to.equal(expectedEwasteTokens);
    });
    
    it("Should calculate tokens correctly for different qualities", async function () {
      const { wasteTokens } = await loadFixture(deployWasteTokensFixture);
      
      const weight = 1000;
      const wasteType = WasteType.PET; // 1.2x multiplier
      
      // Excellent: 1.0x quality multiplier
      const excellentTokens = await wasteTokens.calculateTokens(wasteType, Quality.EXCELLENT, weight);
      const expectedExcellent = ethers.parseEther("1200000"); // 1000 * 1000 * 1.2 * 1.0
      expect(excellentTokens).to.equal(expectedExcellent);
      
      // Good: 0.8x quality multiplier
      const goodTokens = await wasteTokens.calculateTokens(wasteType, Quality.GOOD, weight);
      const expectedGood = ethers.parseEther("960000"); // 1000 * 1000 * 1.2 * 0.8
      expect(goodTokens).to.equal(expectedGood);
      
      // Unusable: 0x quality multiplier
      const unusableTokens = await wasteTokens.calculateTokens(wasteType, Quality.UNUSABLE, weight);
      expect(unusableTokens).to.equal(0);
    });
  });
  
  describe("Verification", function () {
    it("Should allow owner to verify waste submissions", async function () {
      const { wasteTokens, owner, user1 } = await loadFixture(deployWasteTokensFixture);
      
      // Submit waste
      await wasteTokens.connect(user1).submitWaste(
        WasteType.PET,
        Quality.EXCELLENT,
        1000,
        "QmTestHash",
        "40.7128,-74.0060"
      );
      
      const submissionId = 0;
      
      // Verify submission
      await expect(
        wasteTokens.connect(owner).verifyWaste(submissionId, true)
      ).to.emit(wasteTokens, "WasteVerified")
        .withArgs(submissionId, true);
      
      const submission = await wasteTokens.wasteSubmissions(submissionId);
      expect(submission.verified).to.be.true;
    });
    
    it("Should burn tokens if verification fails", async function () {
      const { wasteTokens, owner, user1 } = await loadFixture(deployWasteTokensFixture);
      
      // Submit waste
      await wasteTokens.connect(user1).submitWaste(
        WasteType.PET,
        Quality.EXCELLENT,
        1000,
        "QmTestHash",
        "40.7128,-74.0060"
      );
      
      const initialBalance = await wasteTokens.balanceOf(user1.address);
      expect(initialBalance).to.be.gt(0);
      
      const submissionId = 0;
      
      // Fail verification
      await wasteTokens.connect(owner).verifyWaste(submissionId, false);
      
      // Tokens should be burned
      expect(await wasteTokens.balanceOf(user1.address)).to.equal(0);
    });
    
    it("Should not allow non-owner to verify", async function () {
      const { wasteTokens, user1, user2 } = await loadFixture(deployWasteTokensFixture);
      
      // Submit waste
      await wasteTokens.connect(user1).submitWaste(
        WasteType.PET,
        Quality.EXCELLENT,
        1000,
        "QmTestHash",
        "40.7128,-74.0060"
      );
      
      const submissionId = 0;
      
      // Try to verify as non-owner
      await expect(
        wasteTokens.connect(user2).verifyWaste(submissionId, true)
      ).to.be.revertedWithCustomError(wasteTokens, "OwnableUnauthorizedAccount");
    });
  });
  
  describe("Statistics", function () {
    it("Should track user statistics correctly", async function () {
      const { wasteTokens, user1 } = await loadFixture(deployWasteTokensFixture);
      
      // Submit multiple waste items
      await wasteTokens.connect(user1).submitWaste(
        WasteType.PET,
        Quality.EXCELLENT,
        1000,
        "QmTestHash1",
        "40.7128,-74.0060"
      );
      
      await wasteTokens.connect(user1).submitWaste(
        WasteType.ALUMINUM,
        Quality.GOOD,
        500,
        "QmTestHash2",
        "40.7128,-74.0060"
      );
      
      const [totalSubmissions, totalTokensEarned, currentBalance] = 
        await wasteTokens.getUserStats(user1.address);
      
      expect(totalSubmissions).to.equal(2);
      expect(totalTokensEarned).to.be.gt(0);
      expect(currentBalance).to.equal(totalTokensEarned); // No transfers yet
    });
    
    it("Should track platform statistics correctly", async function () {
      const { wasteTokens, user1, user2 } = await loadFixture(deployWasteTokensFixture);
      
      // Submit waste from multiple users
      await wasteTokens.connect(user1).submitWaste(
        WasteType.PET,
        Quality.EXCELLENT,
        1000,
        "QmTestHash1",
        "40.7128,-74.0060"
      );
      
      await wasteTokens.connect(user2).submitWaste(
        WasteType.ALUMINUM,
        Quality.GOOD,
        500,
        "QmTestHash2",
        "40.7128,-74.0060"
      );
      
      const [totalProcessed, totalSubs, totalSupply] = 
        await wasteTokens.getPlatformStats();
      
      expect(totalProcessed).to.equal(1500); // 1000 + 500 grams
      expect(totalSubs).to.equal(2);
      expect(totalSupply).to.be.gt(0);
    });
  });
  
  describe("Admin Functions", function () {
    it("Should allow owner to update waste type multipliers", async function () {
      const { wasteTokens, owner } = await loadFixture(deployWasteTokensFixture);
      
      const newMultiplier = 25000; // 2.5x
      
      await expect(
        wasteTokens.connect(owner).updateWasteTypeMultiplier(WasteType.PET, newMultiplier)
      ).to.emit(wasteTokens, "MultiplierUpdated")
        .withArgs(WasteType.PET, newMultiplier);
      
      expect(await wasteTokens.wasteTypeMultipliers(WasteType.PET)).to.equal(newMultiplier);
    });
    
    it("Should allow owner to update quality multipliers", async function () {
      const { wasteTokens, owner } = await loadFixture(deployWasteTokensFixture);
      
      const newMultiplier = 9000; // 0.9x
      
      await expect(
        wasteTokens.connect(owner).updateQualityMultiplier(Quality.GOOD, newMultiplier)
      ).to.emit(wasteTokens, "QualityMultiplierUpdated")
        .withArgs(Quality.GOOD, newMultiplier);
      
      expect(await wasteTokens.qualityMultipliers(Quality.GOOD)).to.equal(newMultiplier);
    });
    
    it("Should not allow setting multipliers too high", async function () {
      const { wasteTokens, owner } = await loadFixture(deployWasteTokensFixture);
      
      await expect(
        wasteTokens.connect(owner).updateWasteTypeMultiplier(WasteType.PET, 60000) // 6x
      ).to.be.revertedWith("Multiplier too high");
      
      await expect(
        wasteTokens.connect(owner).updateQualityMultiplier(Quality.EXCELLENT, 15000) // 1.5x
      ).to.be.revertedWith("Multiplier too high");
    });
  });
  
  describe("Pausable", function () {
    it("Should allow owner to pause and unpause", async function () {
      const { wasteTokens, owner } = await loadFixture(deployWasteTokensFixture);
      
      // Pause contract
      await wasteTokens.connect(owner).pause();
      expect(await wasteTokens.paused()).to.be.true;
      
      // Unpause contract
      await wasteTokens.connect(owner).unpause();
      expect(await wasteTokens.paused()).to.be.false;
    });
    
    it("Should prevent waste submission when paused", async function () {
      const { wasteTokens, owner, user1 } = await loadFixture(deployWasteTokensFixture);
      
      // Pause contract
      await wasteTokens.connect(owner).pause();
      
      // Try to submit waste
      await expect(
        wasteTokens.connect(user1).submitWaste(
          WasteType.PET,
          Quality.EXCELLENT,
          1000,
          "QmTestHash",
          "40.7128,-74.0060"
        )
      ).to.be.revertedWithCustomError(wasteTokens, "EnforcedPause");
    });
  });
});