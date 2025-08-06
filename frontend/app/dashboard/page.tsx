'use client';

import { useState, useEffect } from 'react';
import { 
  Wallet, 
  TrendingUp, 
  Leaf, 
  Recycle, 
  Coins, 
  Activity,
  Plus,
  Eye,
  ArrowRight
} from 'lucide-react';

interface TokenBalance {
  tokenId: string;
  symbol: string;
  balance: number;
  value: number;
  type: 'waste' | 'carbon' | 'rewards';
}

interface RecentActivity {
  id: string;
  type: 'mint' | 'stake' | 'convert' | 'earn';
  amount: number;
  token: string;
  timestamp: string;
  status: 'completed' | 'pending' | 'failed';
}

export default function Dashboard() {
  const [tokenBalances, setTokenBalances] = useState<TokenBalance[]>([]);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [totalValue, setTotalValue] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // TODO: Fetch data from backend API
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // TODO: Replace with actual API calls
      // const response = await fetch('/api/v1/tokens/balance');
      // const data = await response.json();
      
      // Mock data for now
      setTokenBalances([
        { tokenId: 'PET-001', symbol: 'PET', balance: 1250, value: 125.50, type: 'waste' },
        { tokenId: 'CARBON-001', symbol: 'CO2', balance: 85, value: 42.50, type: 'carbon' },
        { tokenId: 'REWARDS-001', symbol: 'CIRC', balance: 500, value: 250.00, type: 'rewards' }
      ]);
      
      setRecentActivity([
        { id: '1', type: 'mint', amount: 100, token: 'PET', timestamp: '2024-01-15T10:30:00Z', status: 'completed' },
        { id: '2', type: 'stake', amount: 50, token: 'PET', timestamp: '2024-01-14T15:45:00Z', status: 'completed' },
        { id: '3', type: 'convert', amount: 25, token: 'CO2', timestamp: '2024-01-13T09:20:00Z', status: 'completed' }
      ]);
      
      setTotalValue(418.00);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white dark:bg-emerald-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-emerald-950">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 xl:px-16 2xl:px-24 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Welcome back!
          </h1>
          <p className="text-gray-600 dark:text-emerald-200">
            Manage your waste tokens, carbon credits, and rewards
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <button className="flex items-center justify-center p-6 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white rounded-2xl transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105">
            <Plus className="w-6 h-6 mr-3" />
            <span className="text-lg font-semibold">Submit Waste</span>
          </button>
          
          <button className="flex items-center justify-center p-6 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-2xl transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105">
            <Recycle className="w-6 h-6 mr-3" />
            <span className="text-lg font-semibold">Stake Tokens</span>
          </button>
          
          <button className="flex items-center justify-center p-6 bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white rounded-2xl transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105">
            <Leaf className="w-6 h-6 mr-3" />
            <span className="text-lg font-semibold">Convert Carbon</span>
          </button>
        </div>

        {/* Portfolio Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Total Value */}
          <div className="bg-white dark:bg-emerald-900 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-emerald-800">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Total Portfolio Value</h3>
              <Wallet className="w-6 h-6 text-emerald-500" />
            </div>
            <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
              ${totalValue.toFixed(2)}
            </div>
            <div className="flex items-center mt-2 text-green-600 dark:text-green-400">
              <TrendingUp className="w-4 h-4 mr-1" />
              <span className="text-sm">+12.5% this week</span>
            </div>
          </div>

          {/* Waste Tokens */}
          <div className="bg-white dark:bg-emerald-900 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-emerald-800">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Waste Tokens</h3>
              <Recycle className="w-6 h-6 text-emerald-500" />
            </div>
            <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
              {tokenBalances.filter(t => t.type === 'waste').reduce((sum, t) => sum + t.balance, 0)}
            </div>
            <div className="text-sm text-gray-600 dark:text-emerald-300 mt-2">
              {tokenBalances.filter(t => t.type === 'waste').length} different materials
            </div>
          </div>

          {/* Carbon Credits */}
          <div className="bg-white dark:bg-emerald-900 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-emerald-800">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Carbon Credits</h3>
              <Leaf className="w-6 h-6 text-emerald-500" />
            </div>
            <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
              {tokenBalances.filter(t => t.type === 'carbon').reduce((sum, t) => sum + t.balance, 0)} kg CO2
            </div>
            <div className="text-sm text-gray-600 dark:text-emerald-300 mt-2">
              Environmental impact saved
            </div>
          </div>
        </div>

        {/* Token Balances */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Token Holdings */}
          <div className="bg-white dark:bg-emerald-900 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-emerald-800">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Token Holdings</h3>
              <button className="text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 text-sm font-medium">
                View All
              </button>
            </div>
            
            <div className="space-y-4">
              {tokenBalances.map((token) => (
                <div key={token.tokenId} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-emerald-800/50 rounded-xl">
                  <div className="flex items-center">
                    <div className="w-10 h-10 bg-emerald-100 dark:bg-emerald-700 rounded-full flex items-center justify-center mr-3">
                      <Coins className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900 dark:text-white">{token.symbol}</div>
                      <div className="text-sm text-gray-600 dark:text-emerald-300">{token.balance} tokens</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900 dark:text-white">${token.value.toFixed(2)}</div>
                    <div className="text-sm text-gray-600 dark:text-emerald-300">{token.type}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white dark:bg-emerald-900 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-emerald-800">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Recent Activity</h3>
              <button className="text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 text-sm font-medium">
                View All
              </button>
            </div>
            
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-emerald-800/50 rounded-xl">
                  <div className="flex items-center">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center mr-3 ${
                      activity.status === 'completed' ? 'bg-green-100 dark:bg-green-800/50' :
                      activity.status === 'pending' ? 'bg-yellow-100 dark:bg-yellow-800/50' :
                      'bg-red-100 dark:bg-red-800/50'
                    }`}>
                      <Activity className={`w-5 h-5 ${
                        activity.status === 'completed' ? 'text-green-600 dark:text-green-400' :
                        activity.status === 'pending' ? 'text-yellow-600 dark:text-yellow-400' :
                        'text-red-600 dark:text-red-400'
                      }`} />
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900 dark:text-white capitalize">{activity.type}</div>
                      <div className="text-sm text-gray-600 dark:text-emerald-300">
                        {new Date(activity.timestamp).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900 dark:text-white">{activity.amount} {activity.token}</div>
                    <div className={`text-sm capitalize ${
                      activity.status === 'completed' ? 'text-green-600 dark:text-green-400' :
                      activity.status === 'pending' ? 'text-yellow-600 dark:text-yellow-400' :
                      'text-red-600 dark:text-red-400'
                    }`}>
                      {activity.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 