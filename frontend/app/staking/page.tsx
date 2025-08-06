'use client';

import { useState, useEffect } from 'react';
import { 
  Lock, 
  Unlock, 
  TrendingUp, 
  Coins, 
  Calendar,
  DollarSign,
  Leaf,
  Building2,
  Users,
  ArrowRight,
  Loader2,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

interface Vault {
  id: string;
  name: string;
  description: string;
  tokenType: string;
  apy: number;
  totalStaked: number;
  maxCapacity: number;
  minStake: number;
  lockPeriod: number;
  partner: string;
  partnerLogo: string;
  riskLevel: 'low' | 'medium' | 'high';
  rewards: string[];
}

interface StakingPosition {
  id: string;
  vaultId: string;
  vaultName: string;
  stakedAmount: number;
  earnedRewards: number;
  startDate: string;
  endDate: string;
  status: 'active' | 'locked' | 'completed';
  apy: number;
}

export default function Staking() {
  const [vaults, setVaults] = useState<Vault[]>([]);
  const [positions, setPositions] = useState<StakingPosition[]>([]);
  const [selectedVault, setSelectedVault] = useState<Vault | null>(null);
  const [stakeAmount, setStakeAmount] = useState('');
  const [isStaking, setIsStaking] = useState(false);
  const [isUnstaking, setIsUnstaking] = useState(false);
  const [activeTab, setActiveTab] = useState<'vaults' | 'positions'>('vaults');

  useEffect(() => {
    fetchVaults();
    fetchPositions();
  }, []);

  const fetchVaults = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/v1/defi/vaults');
      // const data = await response.json();
      
      const mockVaults: Vault[] = [
        {
          id: '1',
          name: 'Unilever ESG Vault',
          description: 'Stake PET tokens and earn rewards from Unilever\'s sustainability initiatives',
          tokenType: 'PET',
          apy: 12.5,
          totalStaked: 150000,
          maxCapacity: 500000,
          minStake: 100,
          lockPeriod: 30,
          partner: 'Unilever',
          partnerLogo: '/unilever-logo.png',
          riskLevel: 'low',
          rewards: ['USDC rewards', 'Carbon credits', 'ESG certificates']
        },
        {
          id: '2',
          name: 'Coca-Cola Circular Fund',
          description: 'Aluminum recycling vault with premium yields from Coca-Cola\'s circular economy program',
          tokenType: 'ALUMINUM',
          apy: 18.2,
          totalStaked: 89000,
          maxCapacity: 300000,
          minStake: 50,
          lockPeriod: 60,
          partner: 'Coca-Cola',
          partnerLogo: '/coca-cola-logo.png',
          riskLevel: 'medium',
          rewards: ['USDC rewards', 'Coca-Cola tokens', 'Sustainability NFTs']
        },
        {
          id: '3',
          name: 'Tesla Green Metals Pool',
          description: 'High-yield vault for electronic waste tokens with Tesla\'s green manufacturing program',
          tokenType: 'EWASTE',
          apy: 25.8,
          totalStaked: 75000,
          maxCapacity: 200000,
          minStake: 200,
          lockPeriod: 90,
          partner: 'Tesla',
          partnerLogo: '/tesla-logo.png',
          riskLevel: 'high',
          rewards: ['USDC rewards', 'Tesla tokens', 'Carbon offsets', 'Green certificates']
        }
      ];
      
      setVaults(mockVaults);
    } catch (error) {
      console.error('Error fetching vaults:', error);
    }
  };

  const fetchPositions = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/v1/defi/positions');
      // const data = await response.json();
      
      const mockPositions: StakingPosition[] = [
        {
          id: '1',
          vaultId: '1',
          vaultName: 'Unilever ESG Vault',
          stakedAmount: 500,
          earnedRewards: 25.50,
          startDate: '2024-01-01T00:00:00Z',
          endDate: '2024-02-01T00:00:00Z',
          status: 'active',
          apy: 12.5
        },
        {
          id: '2',
          vaultId: '2',
          vaultName: 'Coca-Cola Circular Fund',
          stakedAmount: 300,
          earnedRewards: 18.75,
          startDate: '2024-01-10T00:00:00Z',
          endDate: '2024-03-10T00:00:00Z',
          status: 'locked',
          apy: 18.2
        }
      ];
      
      setPositions(mockPositions);
    } catch (error) {
      console.error('Error fetching positions:', error);
    }
  };

  const handleStake = async () => {
    if (!selectedVault || !stakeAmount) return;

    setIsStaking(true);
    
    try {
      // TODO: Replace with actual smart contract call
      // const response = await fetch('/api/v1/defi/stake', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({
      //     vaultId: selectedVault.id,
      //     amount: parseFloat(stakeAmount)
      //   })
      // });
      
      // Mock staking
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const newPosition: StakingPosition = {
        id: Date.now().toString(),
        vaultId: selectedVault.id,
        vaultName: selectedVault.name,
        stakedAmount: parseFloat(stakeAmount),
        earnedRewards: 0,
        startDate: new Date().toISOString(),
        endDate: new Date(Date.now() + selectedVault.lockPeriod * 24 * 60 * 60 * 1000).toISOString(),
        status: 'active',
        apy: selectedVault.apy
      };
      
      setPositions(prev => [newPosition, ...prev]);
      setSelectedVault(null);
      setStakeAmount('');
    } catch (error) {
      console.error('Error staking:', error);
    } finally {
      setIsStaking(false);
    }
  };

  const handleUnstake = async (positionId: string) => {
    setIsUnstaking(true);
    
    try {
      // TODO: Replace with actual smart contract call
      // const response = await fetch(`/api/v1/defi/unstake/${positionId}`, {
      //   method: 'POST'
      // });
      
      // Mock unstaking
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setPositions(prev => prev.filter(p => p.id !== positionId));
    } catch (error) {
      console.error('Error unstaking:', error);
    } finally {
      setIsUnstaking(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-800/50 dark:text-green-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800/50 dark:text-yellow-300';
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-800/50 dark:text-red-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800/50 dark:text-gray-300';
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-emerald-950">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 xl:px-16 2xl:px-24 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white mb-2">
            DeFi Staking Vaults
          </h1>
          <p className="text-gray-600 dark:text-emerald-200">
            Stake your waste tokens and earn yield from corporate ESG partners
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 dark:bg-emerald-800 p-1 rounded-xl mb-8">
          <button
            onClick={() => setActiveTab('vaults')}
            className={`flex-1 py-3 px-6 rounded-lg font-medium transition-all ${
              activeTab === 'vaults'
                ? 'bg-white dark:bg-emerald-700 text-emerald-600 dark:text-emerald-300 shadow-sm'
                : 'text-gray-600 dark:text-emerald-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Available Vaults
          </button>
          <button
            onClick={() => setActiveTab('positions')}
            className={`flex-1 py-3 px-6 rounded-lg font-medium transition-all ${
              activeTab === 'positions'
                ? 'bg-white dark:bg-emerald-700 text-emerald-600 dark:text-emerald-300 shadow-sm'
                : 'text-gray-600 dark:text-emerald-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            My Positions
          </button>
        </div>

        {activeTab === 'vaults' ? (
          /* Available Vaults */
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {vaults.map((vault) => (
              <div key={vault.id} className="bg-white dark:bg-emerald-900 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-emerald-800 hover:shadow-xl transition-all duration-300">
                {/* Vault Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-700 rounded-full flex items-center justify-center mr-3">
                      <Building2 className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">{vault.name}</h3>
                      <p className="text-sm text-gray-600 dark:text-emerald-300">{vault.partner}</p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRiskColor(vault.riskLevel)}`}>
                    {vault.riskLevel.toUpperCase()}
                  </span>
                </div>

                {/* Vault Details */}
                <p className="text-gray-600 dark:text-emerald-300 text-sm mb-4">
                  {vault.description}
                </p>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="text-center p-3 bg-emerald-50 dark:bg-emerald-800/50 rounded-lg">
                    <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                      {vault.apy}%
                    </div>
                    <div className="text-xs text-gray-600 dark:text-emerald-300">APY</div>
                  </div>
                  <div className="text-center p-3 bg-emerald-50 dark:bg-emerald-800/50 rounded-lg">
                    <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                      {vault.lockPeriod}d
                    </div>
                    <div className="text-xs text-gray-600 dark:text-emerald-300">Lock Period</div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 dark:text-emerald-300 mb-2">
                    <span>Capacity</span>
                    <span>{((vault.totalStaked / vault.maxCapacity) * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-emerald-800 rounded-full h-2">
                    <div
                      className="bg-emerald-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(vault.totalStaked / vault.maxCapacity) * 100}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-gray-500 dark:text-emerald-400 mt-1">
                    ${vault.totalStaked.toLocaleString()} / ${vault.maxCapacity.toLocaleString()}
                  </div>
                </div>

                {/* Rewards */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Rewards</h4>
                  <div className="space-y-1">
                    {vault.rewards.map((reward, index) => (
                      <div key={index} className="flex items-center text-xs text-gray-600 dark:text-emerald-300">
                        <CheckCircle className="w-3 h-3 mr-2 text-emerald-500" />
                        {reward}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Stake Button */}
                <button
                  onClick={() => setSelectedVault(vault)}
                  className="w-full flex items-center justify-center px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
                >
                  <Lock className="w-5 h-5 mr-2" />
                  Stake Tokens
                </button>
              </div>
            ))}
          </div>
        ) : (
          /* My Positions */
          <div className="space-y-6">
            {positions.length === 0 ? (
              <div className="text-center py-12">
                <Lock className="w-16 h-16 text-gray-400 dark:text-emerald-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  No Active Positions
                </h3>
                <p className="text-gray-600 dark:text-emerald-300 mb-6">
                  Start staking your waste tokens to earn rewards from corporate partners
                </p>
                <button
                  onClick={() => setActiveTab('vaults')}
                  className="flex items-center px-6 py-3 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl transition-colors"
                >
                  <ArrowRight className="w-5 h-5 mr-2" />
                  Browse Vaults
                </button>
              </div>
            ) : (
              positions.map((position) => (
                <div key={position.id} className="bg-white dark:bg-emerald-900 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-emerald-800">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{position.vaultName}</h3>
                      <p className="text-sm text-gray-600 dark:text-emerald-300">
                        Started {new Date(position.startDate).toLocaleDateString()}
                      </p>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                      position.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-800/50 dark:text-green-300' :
                      position.status === 'locked' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800/50 dark:text-yellow-300' :
                      'bg-blue-100 text-blue-800 dark:bg-blue-800/50 dark:text-blue-300'
                    }`}>
                      {position.status.toUpperCase()}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="text-center p-4 bg-emerald-50 dark:bg-emerald-800/50 rounded-lg">
                      <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                        ${position.stakedAmount.toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-emerald-300">Staked Amount</div>
                    </div>
                    <div className="text-center p-4 bg-emerald-50 dark:bg-emerald-800/50 rounded-lg">
                      <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                        ${position.earnedRewards.toFixed(2)}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-emerald-300">Earned Rewards</div>
                    </div>
                    <div className="text-center p-4 bg-emerald-50 dark:bg-emerald-800/50 rounded-lg">
                      <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                        {position.apy}%
                      </div>
                      <div className="text-sm text-gray-600 dark:text-emerald-300">APY</div>
                    </div>
                    <div className="text-center p-4 bg-emerald-50 dark:bg-emerald-800/50 rounded-lg">
                      <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                        {new Date(position.endDate).toLocaleDateString()}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-emerald-300">End Date</div>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    {position.status === 'active' && (
                      <button
                        onClick={() => handleUnstake(position.id)}
                        disabled={isUnstaking}
                        className="flex-1 flex items-center justify-center px-6 py-3 bg-red-500 hover:bg-red-600 disabled:opacity-50 text-white rounded-xl transition-all duration-300"
                      >
                        {isUnstaking ? (
                          <>
                            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                            Unstaking...
                          </>
                        ) : (
                          <>
                            <Unlock className="w-5 h-5 mr-2" />
                            Unstake
                          </>
                        )}
                      </button>
                    )}
                    <button className="flex-1 flex items-center justify-center px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-xl transition-all duration-300">
                      <TrendingUp className="w-5 h-5 mr-2" />
                      View Details
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Stake Modal */}
        {selectedVault && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-emerald-900 rounded-2xl p-6 shadow-2xl max-w-md w-full mx-4">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Stake in {selectedVault.name}
              </h3>
              
              <div className="space-y-4 mb-6">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-emerald-300">APY</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{selectedVault.apy}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-emerald-300">Lock Period</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{selectedVault.lockPeriod} days</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-emerald-300">Min Stake</span>
                  <span className="font-semibold text-gray-900 dark:text-white">${selectedVault.minStake}</span>
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Amount to Stake
                </label>
                <input
                  type="number"
                  value={stakeAmount}
                  onChange={(e) => setStakeAmount(e.target.value)}
                  placeholder={`Min: $${selectedVault.minStake}`}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-emerald-700 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent bg-white dark:bg-emerald-800 text-gray-900 dark:text-white"
                />
              </div>

              <div className="flex gap-4">
                <button
                  onClick={() => setSelectedVault(null)}
                  className="flex-1 px-6 py-3 border border-gray-300 dark:border-emerald-700 text-gray-700 dark:text-emerald-300 rounded-xl hover:bg-gray-50 dark:hover:bg-emerald-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleStake}
                  disabled={isStaking || !stakeAmount || parseFloat(stakeAmount) < selectedVault.minStake}
                  className="flex-1 px-6 py-3 bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-white rounded-xl transition-colors"
                >
                  {isStaking ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin inline" />
                      Staking...
                    </>
                  ) : (
                    'Stake Tokens'
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 