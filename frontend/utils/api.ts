// API Service Layer for Circularity Nexus Frontend
// Handles all communication with the backend API

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

interface User {
  id: string;
  email: string;
  username: string;
  wallet_address?: string;
  created_at: string;
}

interface WasteSubmission {
  id: string;
  user_id: string;
  waste_type: string;
  quantity: number;
  quality: 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR' | 'UNUSABLE';
  estimated_value: number;
  carbon_impact: number;
  image_url: string;
  status: 'pending' | 'validating' | 'approved' | 'rejected';
  created_at: string;
  updated_at: string;
}

interface TokenBalance {
  token_id: string;
  symbol: string;
  balance: number;
  value: number;
  type: 'waste' | 'carbon' | 'rewards';
}

interface AIAnalysis {
  waste_type: string;
  confidence: number;
  quantity: number;
  quality: 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR' | 'UNUSABLE';
  estimated_value: number;
  carbon_impact: number;
  recycling_tips: string[];
}

interface Vault {
  id: string;
  name: string;
  description: string;
  token_type: string;
  apy: number;
  total_staked: number;
  max_capacity: number;
  min_stake: number;
  lock_period: number;
  partner: string;
  risk_level: 'low' | 'medium' | 'high';
  rewards: string[];
}

interface StakingPosition {
  id: string;
  vault_id: string;
  vault_name: string;
  staked_amount: number;
  earned_rewards: number;
  start_date: string;
  end_date: string;
  status: 'active' | 'locked' | 'completed';
  apy: number;
}

class ApiService {
  private token: string | null = null;

  constructor() {
    // Load token from localStorage on initialization
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || 'API request failed');
      }

      return { success: true, data };
    } catch (error) {
      console.error('API Error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // Authentication Methods
  async register(email: string, password: string, username: string): Promise<ApiResponse<User>> {
    return this.request<User>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, username }),
    });
  }

  async login(email: string, password: string): Promise<ApiResponse<{ user: User; token: string }>> {
    const response = await this.request<{ user: User; token: string }>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    if (response.success && response.data?.token) {
      this.token = response.data.token;
      localStorage.setItem('auth_token', response.data.token);
    }

    return response;
  }

  async logout(): Promise<ApiResponse> {
    const response = await this.request('/api/v1/auth/logout', {
      method: 'POST',
    });

    if (response.success) {
      this.token = null;
      localStorage.removeItem('auth_token');
    }

    return response;
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.request<User>('/api/v1/auth/me');
  }

  // Waste Management Methods
  async submitWaste(
    wasteType: string,
    quantity: number,
    quality: string,
    imageFile: File
  ): Promise<ApiResponse<WasteSubmission>> {
    const formData = new FormData();
    formData.append('waste_type', wasteType);
    formData.append('quantity', quantity.toString());
    formData.append('quality', quality);
    formData.append('image', imageFile);

    return this.request<WasteSubmission>('/api/v1/waste/submit', {
      method: 'POST',
      headers: {}, // Let browser set Content-Type for FormData
      body: formData,
    });
  }

  async getWasteSubmissions(): Promise<ApiResponse<WasteSubmission[]>> {
    return this.request<WasteSubmission[]>('/api/v1/waste/submissions');
  }

  async getWasteTypes(): Promise<ApiResponse<string[]>> {
    return this.request<string[]>('/api/v1/waste/types');
  }

  // AI Analysis Methods
  async analyzeWaste(imageFile: File): Promise<ApiResponse<AIAnalysis>> {
    const formData = new FormData();
    formData.append('image', imageFile);

    return this.request<AIAnalysis>('/api/v1/ai/analyze', {
      method: 'POST',
      headers: {}, // Let browser set Content-Type for FormData
      body: formData,
    });
  }

  async getRecyclingTips(wasteType: string): Promise<ApiResponse<string[]>> {
    return this.request<string[]>(`/api/v1/ai/tips/${wasteType}`);
  }

  async calculateCarbonImpact(wasteType: string, quantity: number): Promise<ApiResponse<number>> {
    return this.request<number>('/api/v1/ai/carbon-impact', {
      method: 'POST',
      body: JSON.stringify({ waste_type: wasteType, quantity }),
    });
  }

  // Token Management Methods
  async getTokenBalances(): Promise<ApiResponse<TokenBalance[]>> {
    return this.request<TokenBalance[]>('/api/v1/tokens/balance');
  }

  async mintTokens(wasteSubmissionId: string): Promise<ApiResponse<{ transaction_hash: string }>> {
    return this.request<{ transaction_hash: string }>(`/api/v1/tokens/mint/${wasteSubmissionId}`, {
      method: 'POST',
    });
  }

  // DeFi Methods
  async getVaults(): Promise<ApiResponse<Vault[]>> {
    return this.request<Vault[]>('/api/v1/defi/vaults');
  }

  async getStakingPositions(): Promise<ApiResponse<StakingPosition[]>> {
    return this.request<StakingPosition[]>('/api/v1/defi/positions');
  }

  async stakeTokens(vaultId: string, amount: number): Promise<ApiResponse<{ position_id: string }>> {
    return this.request<{ position_id: string }>('/api/v1/defi/stake', {
      method: 'POST',
      body: JSON.stringify({ vault_id: vaultId, amount }),
    });
  }

  async unstakeTokens(positionId: string): Promise<ApiResponse<{ transaction_hash: string }>> {
    return this.request<{ transaction_hash: string }>(`/api/v1/defi/unstake/${positionId}`, {
      method: 'POST',
    });
  }

  // Carbon Credits Methods
  async convertToCarbon(wasteAmount: number, wasteType: string): Promise<ApiResponse<{ carbon_credits: number }>> {
    return this.request<{ carbon_credits: number }>('/api/v1/carbon/convert', {
      method: 'POST',
      body: JSON.stringify({ waste_amount: wasteAmount, waste_type: wasteType }),
    });
  }

  async getCarbonBalance(): Promise<ApiResponse<number>> {
    return this.request<number>('/api/v1/carbon/balance');
  }

  // Smart Bin Methods
  async getSmartBinData(binId: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/api/v1/smart-bins/${binId}`);
  }

  async getNearbyBins(latitude: number, longitude: number): Promise<ApiResponse<any[]>> {
    return this.request<any[]>(`/api/v1/smart-bins?lat=${latitude}&lng=${longitude}`);
  }

  // Health Check
  async healthCheck(): Promise<ApiResponse<{ status: string; timestamp: string }>> {
    return this.request<{ status: string; timestamp: string }>('/health');
  }

  // Utility Methods
  isAuthenticated(): boolean {
    return !!this.token;
  }

  getToken(): string | null {
    return this.token;
  }

  setToken(token: string): void {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken(): void {
    this.token = null;
    localStorage.removeItem('auth_token');
  }
}

// Create and export a singleton instance
export const apiService = new ApiService();

// Export types for use in components
export type {
  User,
  WasteSubmission,
  TokenBalance,
  AIAnalysis,
  Vault,
  StakingPosition,
  ApiResponse,
}; 