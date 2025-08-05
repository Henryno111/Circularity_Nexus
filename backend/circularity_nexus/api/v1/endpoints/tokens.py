"""
Token management endpoints
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Any

router = APIRouter()


class TokenBalance(BaseModel):
    """Token balance schema"""
    token_type: str
    balance: int  # in grams
    value_usd: float


@router.get("/balance")
async def get_token_balance() -> List[TokenBalance]:
    """Get user's token balance"""
    return [
        TokenBalance(token_type="PET", balance=2500, value_usd=12.50),
        TokenBalance(token_type="ALUMINUM", balance=1200, value_usd=8.40),
    ]


@router.post("/mint/{submission_id}")
async def mint_tokens(submission_id: int) -> Dict[str, Any]:
    """Mint tokens for validated waste submission"""
    return {
        "message": "Tokens minted successfully",
        "submission_id": submission_id,
        "tokens_minted": 2500,
        "token_type": "PET",
        "transaction_hash": "0xabcdef123456789"
    }
