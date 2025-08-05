"""
User management endpoints
"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()


@router.get("/profile")
async def get_user_profile() -> Dict[str, Any]:
    """Get user profile"""
    return {
        "id": 1,
        "email": "demo@circularitynexus.io",
        "full_name": "Demo User",
        "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
        "total_waste_kg": 25.7,
        "total_tokens_earned": 25700,
        "carbon_credits_earned": 38.5,
        "created_at": "2025-01-01T00:00:00Z"
    }
