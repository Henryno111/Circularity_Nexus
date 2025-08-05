"""
DeFi and staking endpoints
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List

router = APIRouter()


class StakeRequest(BaseModel):
    """Staking request schema"""
    token_type: str
    amount: float
    vault_type: str


@router.post("/stake")
async def stake_tokens(stake_data: StakeRequest) -> Dict[str, Any]:
    """Stake tokens in DeFi vault"""
    return {
        "message": "Tokens staked successfully",
        "token_type": stake_data.token_type,
        "amount": stake_data.amount,
        "vault_type": stake_data.vault_type,
        "apy": "5.2%",
        "transaction_hash": "0xdef456789abc123"
    }


@router.get("/vaults")
async def get_available_vaults() -> List[Dict[str, Any]]:
    """Get available staking vaults"""
    return [
        {
            "vault_type": "ESG_CORPORATE",
            "name": "Corporate ESG Vault",
            "apy": "5.2%",
            "min_stake": 1000,
            "total_staked": 50000000
        },
        {
            "vault_type": "RECYCLING_POOL",
            "name": "Recycling Liquidity Pool",
            "apy": "7.8%",
            "min_stake": 500,
            "total_staked": 25000000
        }
    ]
