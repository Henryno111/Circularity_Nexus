"""
Carbon credit endpoints
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()


class CarbonConversionRequest(BaseModel):
    """Carbon conversion request schema"""
    waste_token_amount: float
    waste_type: str


@router.post("/convert")
async def convert_to_carbon(conversion_data: CarbonConversionRequest) -> Dict[str, Any]:
    """Convert waste tokens to carbon credits"""
    # Calculate carbon credits based on waste type
    carbon_factors = {
        "PET": 1.5,
        "ALUMINUM": 2.1,
        "GLASS": 0.8,
        "PAPER": 1.2,
        "EWASTE": 3.5
    }
    
    factor = carbon_factors.get(conversion_data.waste_type, 1.0)
    carbon_credits = conversion_data.waste_token_amount * factor / 1000  # kg CO2e
    
    return {
        "message": "Carbon credits generated successfully",
        "waste_tokens_used": conversion_data.waste_token_amount,
        "carbon_credits_generated": carbon_credits,
        "co2e_kg": carbon_credits,
        "transaction_hash": "0x789abc123def456"
    }


@router.get("/balance")
async def get_carbon_balance() -> Dict[str, Any]:
    """Get user's carbon credit balance"""
    return {
        "total_carbon_credits": 15.7,
        "co2e_kg": 15.7,
        "value_usd": 235.50,
        "credits_by_source": {
            "PET": 8.2,
            "ALUMINUM": 5.1,
            "EWASTE": 2.4
        }
    }
