"""
Smart bin endpoints
"""

from fastapi import APIRouter
from typing import Dict, Any, List

router = APIRouter()


@router.get("/{bin_id}")
async def get_smart_bin_data(bin_id: str) -> Dict[str, Any]:
    """Get smart bin sensor data"""
    return {
        "bin_id": bin_id,
        "location": {
            "latitude": -1.286389,
            "longitude": 36.817223,
            "address": "Nairobi, Kenya"
        },
        "current_weight_kg": 17.3,
        "capacity_kg": 50.0,
        "fill_percentage": 34.6,
        "last_emptied": "2025-07-29T08:30:00Z",
        "material_detected": "PET",
        "status": "ACTIVE",
        "battery_level": 87
    }


@router.get("/")
async def get_nearby_bins() -> List[Dict[str, Any]]:
    """Get nearby smart bins"""
    return [
        {
            "bin_id": "DEMO-BIN-001",
            "location": {"latitude": -1.286389, "longitude": 36.817223},
            "fill_percentage": 34.6,
            "distance_m": 150
        },
        {
            "bin_id": "DEMO-BIN-002", 
            "location": {"latitude": -1.287000, "longitude": 36.818000},
            "fill_percentage": 67.2,
            "distance_m": 320
        }
    ]
