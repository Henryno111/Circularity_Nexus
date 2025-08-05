// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";

/**
 * @title RecycleVault
 * @dev DeFi staking vault for waste tokens with corporate ESG partner funding
 * Enables users to stake waste tokens and earn USDC rewards from corporate partners
 */
contract RecycleVault is Ownable, Pausable, ReentrancyGuard {
    using SafeERC20 for IERC20;
    using Math for uint256;
    
    // Staking pool structure
    struct StakingPool {
        IERC20 stakingToken;        // Waste token to stake
        IERC20 rewardToken;         // Reward token (typically USDC)
        uint256 totalStaked;        // Total tokens staked in pool
        uint256 rewardRate;         // Reward rate per second (scaled by 1e18)
        uint256 lastUpdateTime;     // Last time rewards were calculated
        uint256 rewardPerTokenStored; // Accumulated reward per token
        uint256 minStakingPeriod;   // Minimum staking period in seconds
        uint256 maxStakingAmount;   // Maximum amount per user
        bool active;                // Pool active status
        string partnerName;         // Corporate partner name
    }
    
    // User staking information
    struct UserStake {
        uint256 amount;             // Amount staked
        uint256 rewardPerTokenPaid; // Reward per token paid
        uint256 rewards;            // Pending rewards
        uint256 stakeTime;          // Time when staked
        uint256 lastClaimTime;      // Last reward claim time
    }
    
    // Pool ID counter
    uint256 public nextPoolId;
    
    // Pool mappings
    mapping(uint256 => StakingPool) public stakingPools;
    mapping(uint256 => mapping(address => UserStake)) public userStakes;
    
    // Platform statistics
    uint256 public totalValueLocked;        // Total USD value locked
    uint256 public totalRewardsDistributed; // Total rewards distributed
    mapping(address => uint256) public userTotalStaked;   // User total staked across all pools
    mapping(address => uint256) public userTotalRewards;  // User total rewards earned
    
    // Platform fees
    uint256 public platformFeeRate = 500; // 5% (basis points)
    address public feeCollector;
    
    // Corporate partner management
    mapping(address => bool) public authorizedPartners;
    mapping(uint256 => address) public poolPartners; // Pool ID -> Partner address
    
    // Events
    event PoolCreated(
        uint256 indexed poolId,
        address indexed stakingToken,
        address indexed rewardToken,
        uint256 rewardRate,
        string partnerName
    );
    
    event Staked(
        uint256 indexed poolId,
        address indexed user,
        uint256 amount,
        uint256 timestamp
    );
    
    event Unstaked(
        uint256 indexed poolId,
        address indexed user,
        uint256 amount,
        uint256 reward
    );
    
    event RewardsClaimed(
        uint256 indexed poolId,
        address indexed user,
        uint256 reward
    );
    
    event PoolUpdated(uint256 indexed poolId, uint256 newRewardRate);
    event PartnerAuthorized(address indexed partner, bool authorized);
    event PlatformFeeUpdated(uint256 newFeeRate);
    
    constructor(address initialOwner, address _feeCollector) Ownable(initialOwner) {
        feeCollector = _feeCollector;
    }
    
    modifier updateReward(uint256 poolId, address account) {
        StakingPool storage pool = stakingPools[poolId];
        pool.rewardPerTokenStored = rewardPerToken(poolId);
        pool.lastUpdateTime = lastTimeRewardApplicable(poolId);
        
        if (account != address(0)) {
            UserStake storage userStake = userStakes[poolId][account];
            userStake.rewards = earned(poolId, account);
            userStake.rewardPerTokenPaid = pool.rewardPerTokenStored;
        }
        _;
    }
    
    modifier onlyAuthorizedPartner() {
        require(authorizedPartners[msg.sender] || msg.sender == owner(), "Not authorized partner");
        _;
    }
    
    /**
     * @dev Create a new staking pool (only authorized partners or owner)
     */
    function createPool(
        address _stakingToken,
        address _rewardToken,
        uint256 _rewardRate,
        uint256 _minStakingPeriod,
        uint256 _maxStakingAmount,
        string memory _partnerName
    ) external onlyAuthorizedPartner returns (uint256 poolId) {
        require(_stakingToken != address(0), "Invalid staking token");
        require(_rewardToken != address(0), "Invalid reward token");
        require(_rewardRate > 0, "Reward rate must be > 0");
        
        poolId = nextPoolId++;
        
        stakingPools[poolId] = StakingPool({
            stakingToken: IERC20(_stakingToken),
            rewardToken: IERC20(_rewardToken),
            totalStaked: 0,
            rewardRate: _rewardRate,
            lastUpdateTime: block.timestamp,
            rewardPerTokenStored: 0,
            minStakingPeriod: _minStakingPeriod,
            maxStakingAmount: _maxStakingAmount,
            active: true,
            partnerName: _partnerName
        });
        
        poolPartners[poolId] = msg.sender;
        
        emit PoolCreated(poolId, _stakingToken, _rewardToken, _rewardRate, _partnerName);
        
        return poolId;
    }
    
    /**
     * @dev Stake tokens in a pool
     */
    function stake(uint256 poolId, uint256 amount) 
        external 
        whenNotPaused 
        nonReentrant 
        updateReward(poolId, msg.sender) 
    {
        require(amount > 0, "Cannot stake 0");
        require(poolId < nextPoolId, "Invalid pool ID");
        
        StakingPool storage pool = stakingPools[poolId];
        require(pool.active, "Pool not active");
        
        UserStake storage userStake = userStakes[poolId][msg.sender];
        
        // Check maximum staking limit
        if (pool.maxStakingAmount > 0) {
            require(
                userStake.amount + amount <= pool.maxStakingAmount,
                "Exceeds max staking amount"
            );
        }
        
        // Transfer tokens from user to contract
        pool.stakingToken.safeTransferFrom(msg.sender, address(this), amount);
        
        // Update user stake
        userStake.amount += amount;
        userStake.stakeTime = block.timestamp;
        
        // Update pool total
        pool.totalStaked += amount;
        
        // Update platform statistics
        userTotalStaked[msg.sender] += amount;
        // Note: totalValueLocked would need oracle for USD conversion
        
        emit Staked(poolId, msg.sender, amount, block.timestamp);
    }
    
    /**
     * @dev Unstake tokens from a pool
     */
    function unstake(uint256 poolId, uint256 amount) 
        external 
        nonReentrant 
        updateReward(poolId, msg.sender) 
    {
        require(amount > 0, "Cannot unstake 0");
        require(poolId < nextPoolId, "Invalid pool ID");
        
        UserStake storage userStake = userStakes[poolId][msg.sender];
        require(userStake.amount >= amount, "Insufficient staked amount");
        
        StakingPool storage pool = stakingPools[poolId];
        
        // Check minimum staking period
        require(
            block.timestamp >= userStake.stakeTime + pool.minStakingPeriod,
            "Minimum staking period not met"
        );
        
        // Calculate and claim rewards
        uint256 reward = userStake.rewards;
        if (reward > 0) {
            userStake.rewards = 0;
            userStake.lastClaimTime = block.timestamp;
            
            // Calculate platform fee
            uint256 fee = (reward * platformFeeRate) / 10000;
            uint256 userReward = reward - fee;
            
            // Transfer rewards
            pool.rewardToken.safeTransfer(msg.sender, userReward);
            if (fee > 0) {
                pool.rewardToken.safeTransfer(feeCollector, fee);
            }
            
            // Update statistics
            userTotalRewards[msg.sender] += userReward;
            totalRewardsDistributed += userReward;
        }
        
        // Update user stake
        userStake.amount -= amount;
        
        // Update pool total
        pool.totalStaked -= amount;
        
        // Update platform statistics
        userTotalStaked[msg.sender] -= amount;
        
        // Transfer staked tokens back to user
        pool.stakingToken.safeTransfer(msg.sender, amount);
        
        emit Unstaked(poolId, msg.sender, amount, reward);
    }
    
    /**
     * @dev Claim rewards without unstaking
     */
    function claimRewards(uint256 poolId) 
        external 
        nonReentrant 
        updateReward(poolId, msg.sender) 
    {
        require(poolId < nextPoolId, "Invalid pool ID");
        
        UserStake storage userStake = userStakes[poolId][msg.sender];
        uint256 reward = userStake.rewards;
        require(reward > 0, "No rewards to claim");
        
        userStake.rewards = 0;
        userStake.lastClaimTime = block.timestamp;
        
        StakingPool storage pool = stakingPools[poolId];
        
        // Calculate platform fee
        uint256 fee = (reward * platformFeeRate) / 10000;
        uint256 userReward = reward - fee;
        
        // Transfer rewards
        pool.rewardToken.safeTransfer(msg.sender, userReward);
        if (fee > 0) {
            pool.rewardToken.safeTransfer(feeCollector, fee);
        }
        
        // Update statistics
        userTotalRewards[msg.sender] += userReward;
        totalRewardsDistributed += userReward;
        
        emit RewardsClaimed(poolId, msg.sender, userReward);
    }
    
    /**
     * @dev Fund pool with reward tokens (called by partners)
     */
    function fundPool(uint256 poolId, uint256 amount) external {
        require(poolId < nextPoolId, "Invalid pool ID");
        
        StakingPool storage pool = stakingPools[poolId];
        require(
            msg.sender == poolPartners[poolId] || msg.sender == owner(),
            "Not pool partner"
        );
        
        pool.rewardToken.safeTransferFrom(msg.sender, address(this), amount);
    }
    
    /**
     * @dev Update pool reward rate (only pool partner or owner)
     */
    function updateRewardRate(uint256 poolId, uint256 newRewardRate) 
        external 
        updateReward(poolId, address(0)) 
    {
        require(poolId < nextPoolId, "Invalid pool ID");
        require(
            msg.sender == poolPartners[poolId] || msg.sender == owner(),
            "Not pool partner"
        );
        
        stakingPools[poolId].rewardRate = newRewardRate;
        emit PoolUpdated(poolId, newRewardRate);
    }
    
    /**
     * @dev Calculate reward per token
     */
    function rewardPerToken(uint256 poolId) public view returns (uint256) {
        StakingPool storage pool = stakingPools[poolId];
        
        if (pool.totalStaked == 0) {
            return pool.rewardPerTokenStored;
        }
        
        return pool.rewardPerTokenStored + 
            (((lastTimeRewardApplicable(poolId) - pool.lastUpdateTime) * 
              pool.rewardRate * 1e18) / pool.totalStaked);
    }
    
    /**
     * @dev Calculate earned rewards for a user
     */
    function earned(uint256 poolId, address account) public view returns (uint256) {
        UserStake storage userStake = userStakes[poolId][account];
        
        return ((userStake.amount * 
                (rewardPerToken(poolId) - userStake.rewardPerTokenPaid)) / 1e18) + 
                userStake.rewards;
    }
    
    /**
     * @dev Get last time reward is applicable
     */
    function lastTimeRewardApplicable(uint256 poolId) public view returns (uint256) {
        return block.timestamp;
    }
    
    /**
     * @dev Get pool information
     */
    function getPoolInfo(uint256 poolId) external view returns (
        address stakingToken,
        address rewardToken,
        uint256 totalStaked,
        uint256 rewardRate,
        bool active,
        string memory partnerName
    ) {
        StakingPool storage pool = stakingPools[poolId];
        return (
            address(pool.stakingToken),
            address(pool.rewardToken),
            pool.totalStaked,
            pool.rewardRate,
            pool.active,
            pool.partnerName
        );
    }
    
    /**
     * @dev Get user stake information
     */
    function getUserStakeInfo(uint256 poolId, address user) external view returns (
        uint256 stakedAmount,
        uint256 earnedRewards,
        uint256 stakeTime,
        uint256 lastClaimTime
    ) {
        UserStake storage userStake = userStakes[poolId][user];
        return (
            userStake.amount,
            earned(poolId, user),
            userStake.stakeTime,
            userStake.lastClaimTime
        );
    }
    
    /**
     * @dev Authorize/deauthorize corporate partner (only owner)
     */
    function setPartnerAuthorization(address partner, bool authorized) external onlyOwner {
        authorizedPartners[partner] = authorized;
        emit PartnerAuthorized(partner, authorized);
    }
    
    /**
     * @dev Update platform fee rate (only owner)
     */
    function setPlatformFeeRate(uint256 newFeeRate) external onlyOwner {
        require(newFeeRate <= 1000, "Fee rate too high"); // Max 10%
        platformFeeRate = newFeeRate;
        emit PlatformFeeUpdated(newFeeRate);
    }
    
    /**
     * @dev Update fee collector address (only owner)
     */
    function setFeeCollector(address newFeeCollector) external onlyOwner {
        require(newFeeCollector != address(0), "Invalid address");
        feeCollector = newFeeCollector;
    }
    
    /**
     * @dev Toggle pool active status (only pool partner or owner)
     */
    function togglePoolStatus(uint256 poolId) external {
        require(poolId < nextPoolId, "Invalid pool ID");
        require(
            msg.sender == poolPartners[poolId] || msg.sender == owner(),
            "Not pool partner"
        );
        
        stakingPools[poolId].active = !stakingPools[poolId].active;
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