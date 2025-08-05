#!/usr/bin/env python3
"""
API Demo Script for Circularity Nexus
Demonstrates key API endpoints and functionality
"""

import asyncio
import httpx
import json
import os
from pathlib import Path
from typing import Dict, Any
import time


class CircularityNexusAPIDemo:
    """Demo client for Circularity Nexus API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token = None
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def print_section(self, title: str):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_response(self, response: httpx.Response, description: str = ""):
        """Print formatted API response"""
        print(f"\n{description}")
        print(f"Status: {response.status_code}")
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        except:
            print(f"Response: {response.text}")
    
    async def check_health(self):
        """Check API health"""
        self.print_section("Health Check")
        response = await self.client.get(f"{self.base_url}/health")
        self.print_response(response, "Health check:")
        return response.status_code == 200
    
    async def register_user(self, email: str, password: str, name: str):
        """Register a new user"""
        self.print_section("User Registration")
        data = {
            "email": email,
            "password": password,
            "full_name": name,
            "wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
        }
        response = await self.client.post(f"{self.api_url}/auth/register", json=data)
        self.print_response(response, "User registration:")
        return response.status_code == 201
    
    async def login_user(self, email: str, password: str):
        """Login user and get auth token"""
        self.print_section("User Login")
        data = {
            "username": email,
            "password": password
        }
        response = await self.client.post(
            f"{self.api_url}/auth/login",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        self.print_response(response, "User login:")
        
        if response.status_code == 200:
            token_data = response.json()
            self.auth_token = token_data.get("access_token")
            self.client.headers.update({"Authorization": f"Bearer {self.auth_token}"})
            return True
        return False
    
    async def submit_waste(self, waste_type: str, weight_kg: float, location: Dict[str, float]):
        """Submit waste for tokenization"""
        self.print_section("Waste Submission")
        data = {
            "waste_type": waste_type,
            "estimated_weight_kg": weight_kg,
            "location": location,
            "description": f"Demo submission of {weight_kg}kg {waste_type}",
            "image_urls": ["https://example.com/waste_image.jpg"]
        }
        response = await self.client.post(f"{self.api_url}/waste/submit", json=data)
        self.print_response(response, "Waste submission:")
        
        if response.status_code == 201:
            return response.json().get("id")
        return None
    
    async def process_ai_validation(self, submission_id: str):
        """Process AI validation for waste submission"""
        self.print_section("AI Validation")
        response = await self.client.post(f"{self.api_url}/ai/validate/{submission_id}")
        self.print_response(response, "AI validation:")
        return response.status_code == 200
    
    async def mint_tokens(self, submission_id: str):
        """Mint waste tokens"""
        self.print_section("Token Minting")
        response = await self.client.post(f"{self.api_url}/tokens/mint/{submission_id}")
        self.print_response(response, "Token minting:")
        return response.status_code == 200
    
    async def get_user_tokens(self):
        """Get user's token balance"""
        self.print_section("Token Balance")
        response = await self.client.get(f"{self.api_url}/tokens/balance")
        self.print_response(response, "Token balance:")
        return response.status_code == 200
    
    async def stake_tokens(self, token_type: str, amount: float):
        """Stake tokens in DeFi vault"""
        self.print_section("Token Staking")
        data = {
            "token_type": token_type,
            "amount": amount,
            "vault_type": "ESG_CORPORATE"
        }
        response = await self.client.post(f"{self.api_url}/defi/stake", json=data)
        self.print_response(response, "Token staking:")
        return response.status_code == 200
    
    async def convert_to_carbon(self, waste_token_amount: float):
        """Convert waste tokens to carbon credits"""
        self.print_section("Carbon Conversion")
        data = {
            "waste_token_amount": waste_token_amount,
            "waste_type": "PET"
        }
        response = await self.client.post(f"{self.api_url}/carbon/convert", json=data)
        self.print_response(response, "Carbon conversion:")
        return response.status_code == 200
    
    async def get_smart_bin_data(self, bin_id: str = "DEMO-BIN-001"):
        """Get smart bin sensor data"""
        self.print_section("Smart Bin Data")
        response = await self.client.get(f"{self.api_url}/smart-bins/{bin_id}")
        self.print_response(response, "Smart bin data:")
        return response.status_code == 200
    
    async def run_full_demo(self):
        """Run complete API demonstration"""
        print("🌍 Circularity Nexus API Demo")
        print("Tokenize Trash. Earn Wealth. Heal the Planet.")
        
        # Check if API is running
        if not await self.check_health():
            print("❌ API is not running. Please start the server first.")
            return
        
        # Demo user credentials
        demo_email = "demo@circularitynexus.io"
        demo_password = "demo123456"
        demo_name = "Demo User"
        
        # Register demo user (might fail if already exists)
        await self.register_user(demo_email, demo_password, demo_name)
        
        # Login
        if not await self.login_user(demo_email, demo_password):
            print("❌ Login failed. Demo cannot continue.")
            return
        
        # Submit waste
        submission_id = await self.submit_waste(
            waste_type="PET",
            weight_kg=2.5,
            location={"latitude": -1.286389, "longitude": 36.817223}
        )
        
        if not submission_id:
            print("❌ Waste submission failed.")
            return
        
        # Simulate processing delay
        print("\n⏳ Processing waste submission...")
        await asyncio.sleep(2)
        
        # AI validation
        await self.process_ai_validation(submission_id)
        
        # Mint tokens
        await self.mint_tokens(submission_id)
        
        # Check token balance
        await self.get_user_tokens()
        
        # Stake tokens
        await self.stake_tokens("PET", 1000)  # 1000 grams = 1kg
        
        # Convert to carbon credits
        await self.convert_to_carbon(500)  # 500 grams
        
        # Get smart bin data
        await self.get_smart_bin_data()
        
        print(f"\n✅ Demo completed successfully!")
        print("🎉 You've successfully tokenized waste and earned rewards!")


async def main():
    """Main demo function"""
    try:
        async with CircularityNexusAPIDemo() as demo:
            await demo.run_full_demo()
    except httpx.ConnectError:
        print("❌ Cannot connect to API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")


if __name__ == "__main__":
    print("Starting Circularity Nexus API Demo...")
    asyncio.run(main())
