"""
Waste management endpoints
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter()


class WasteSubmissionCreate(BaseModel):
    """Waste submission creation schema"""
    waste_type: str
    estimated_weight_kg: float
    location: Dict[str, float]  # {"latitude": float, "longitude": float}
    description: Optional[str] = None
    image_urls: Optional[List[str]] = []


class WasteSubmissionResponse(BaseModel):
    """Waste submission response schema"""
    id: int
    waste_type: str
    estimated_weight_kg: float
    status: str
    created_at: datetime


@router.post("/submit", status_code=status.HTTP_201_CREATED)
async def submit_waste(submission: WasteSubmissionCreate) -> WasteSubmissionResponse:
    """Submit waste for tokenization"""
    # TODO: Implement waste submission logic
    return WasteSubmissionResponse(
        id=1,
        waste_type=submission.waste_type,
        estimated_weight_kg=submission.estimated_weight_kg,
        status="PENDING",
        created_at=datetime.now()
    )


@router.get("/submissions")
async def get_user_submissions() -> List[WasteSubmissionResponse]:
    """Get user's waste submissions"""
    # TODO: Implement get submissions logic
    return [
        WasteSubmissionResponse(
            id=1,
            waste_type="PET",
            estimated_weight_kg=2.5,
            status="TOKENIZED",
            created_at=datetime.now()
        )
    ]


@router.get("/submissions/{submission_id}")
async def get_submission(submission_id: int) -> WasteSubmissionResponse:
    """Get specific waste submission"""
    # TODO: Implement get submission logic
    return WasteSubmissionResponse(
        id=submission_id,
        waste_type="PET",
        estimated_weight_kg=2.5,
        status="TOKENIZED",
        created_at=datetime.now()
    )


@router.get("/types")
async def get_waste_types() -> List[Dict[str, Any]]:
    """Get supported waste types"""
    return [
        {"type": "PET", "name": "PET Plastic", "token_rate": 1000, "carbon_factor": 1.5},
        {"type": "ALUMINUM", "name": "Aluminum Cans", "token_rate": 1200, "carbon_factor": 2.1},
        {"type": "GLASS", "name": "Glass Bottles", "token_rate": 800, "carbon_factor": 0.8},
        {"type": "PAPER", "name": "Paper", "token_rate": 600, "carbon_factor": 1.2},
        {"type": "EWASTE", "name": "Electronic Waste", "token_rate": 2000, "carbon_factor": 3.5},
    ]
