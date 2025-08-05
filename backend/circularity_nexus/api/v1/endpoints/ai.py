"""
AI processing endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from loguru import logger

from circularity_nexus.services.groq_service import groq_service
from circularity_nexus.core.exceptions import AIProcessingError

router = APIRouter()


class WasteAnalysisRequest(BaseModel):
    """Waste analysis request schema"""
    description: str
    estimated_weight_kg: float
    location: Optional[Dict[str, float]] = None
    image_url: Optional[str] = None


@router.post("/validate/{submission_id}")
async def validate_waste(submission_id: int) -> Dict[str, Any]:
    """Process AI validation for waste submission"""
    # TODO: Get actual submission data from database
    # For demo, using mock data
    mock_description = "Plastic water bottle, clear PET material"
    mock_weight = 0.025  # 25 grams
    
    try:
        if groq_service:
            result = await groq_service.classify_waste_from_description(
                description=mock_description,
                estimated_weight=mock_weight
            )
            
            return {
                "submission_id": submission_id,
                "ai_confidence": result["confidence"],
                "detected_type": result["detected_type"],
                "estimated_weight": result["estimated_weight_kg"],
                "validation_status": "VALIDATED" if result["confidence"] > 0.8 else "NEEDS_REVIEW",
                "recyclability_score": result["recyclability_score"],
                "carbon_impact_kg": result["carbon_impact_kg"],
                "recommendations": result["recommendations"]
            }
        else:
            # Fallback when Groq is not available
            return {
                "submission_id": submission_id,
                "ai_confidence": 0.92,
                "detected_type": "PET",
                "estimated_weight": 2.3,
                "validation_status": "VALIDATED",
                "note": "Using fallback validation (Groq not configured)"
            }
    except AIProcessingError as e:
        logger.error(f"AI processing failed: {e}")
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/analyze")
async def analyze_waste(request: WasteAnalysisRequest) -> Dict[str, Any]:
    """Analyze waste from description and/or image"""
    try:
        if not groq_service:
            raise HTTPException(status_code=503, detail="AI service not available")
        
        # Analyze from description
        result = await groq_service.classify_waste_from_description(
            description=request.description,
            estimated_weight=request.estimated_weight_kg,
            location=request.location
        )
        
        # If image URL provided, analyze image too (placeholder)
        if request.image_url:
            image_result = await groq_service.analyze_waste_image(request.image_url)
            # Combine results (weighted average)
            result["confidence"] = (result["confidence"] + image_result["confidence"]) / 2
        
        return result
        
    except AIProcessingError as e:
        logger.error(f"Waste analysis failed: {e}")
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/tips/{waste_type}")
async def get_recycling_tips(waste_type: str) -> Dict[str, List[str]]:
    """Get recycling tips for specific waste type"""
    try:
        if not groq_service:
            # Fallback tips
            fallback_tips = {
                "PET": ["Clean thoroughly", "Remove labels", "Separate caps"],
                "ALUMINUM": ["Rinse cans", "Crush to save space", "Check for food residue"],
                "GLASS": ["Remove lids", "Sort by color", "Handle carefully"]
            }
            return {"tips": fallback_tips.get(waste_type, ["Check local guidelines"])}
        
        tips = await groq_service.generate_recycling_tips(waste_type)
        return {"tips": tips}
        
    except Exception as e:
        logger.error(f"Error getting recycling tips: {e}")
        return {"tips": ["Clean the item", "Check local recycling guidelines"]}


@router.post("/carbon-impact")
async def calculate_carbon_impact(waste_type: str, weight_kg: float) -> Dict[str, Any]:
    """Calculate carbon impact of recycling waste"""
    try:
        if not groq_service:
            # Fallback calculation
            carbon_factors = {"PET": 1.5, "ALUMINUM": 2.1, "GLASS": 0.8}
            factor = carbon_factors.get(waste_type, 1.0)
            return {
                "co2_saved_kg": weight_kg * factor,
                "energy_saved_kwh": weight_kg * factor * 2,
                "water_saved_liters": weight_kg * factor * 10,
                "explanation": f"Fallback calculation for {waste_type}"
            }
        
        result = await groq_service.calculate_carbon_impact(waste_type, weight_kg)
        return result
        
    except AIProcessingError as e:
        logger.error(f"Carbon impact calculation failed: {e}")
        raise HTTPException(status_code=422, detail=str(e))
