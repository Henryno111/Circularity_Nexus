"""
Waste Classification Service

Advanced waste classification using AI with support for multiple input types
and detailed material analysis.
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from .groq_service import GroqService
from ..core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class WasteCategory(Enum):
    """Standard waste categories for classification."""
    PLASTIC = "PLASTIC"
    METAL = "METAL"
    PAPER = "PAPER"
    GLASS = "GLASS"
    ORGANIC = "ORGANIC"
    ELECTRONIC = "ELECTRONIC"
    TEXTILE = "TEXTILE"
    HAZARDOUS = "HAZARDOUS"
    COMPOSITE = "COMPOSITE"

class QualityGrade(Enum):
    """Quality grades for waste items."""
    EXCELLENT = "EXCELLENT"  # 90-100% value
    GOOD = "GOOD"           # 70-89% value
    FAIR = "FAIR"           # 50-69% value
    POOR = "POOR"           # 10-49% value
    UNUSABLE = "UNUSABLE"   # 0-9% value

class WasteClassifier:
    """Advanced waste classification service with AI-powered analysis."""
    
    def __init__(self):
        self.groq_service = GroqService()
        self.material_database = self._load_material_database()
    
    async def classify_waste_item(
        self,
        image_description: str,
        weight: Optional[float] = None,
        dimensions: Optional[Dict[str, float]] = None,
        user_description: Optional[str] = None,
        location_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classify a waste item with comprehensive analysis.
        
        Args:
            image_description: AI-generated description from image analysis
            weight: Weight in kg
            dimensions: Optional dimensions (length, width, height in cm)
            user_description: User-provided description
            location_context: Geographic context for local recycling rules
            
        Returns:
            Comprehensive classification result
        """
        try:
            # Validate inputs
            if not image_description or len(image_description.strip()) < 10:
                raise ValidationError("Image description must be at least 10 characters")
            
            # Build comprehensive context
            context = self._build_classification_context(
                image_description, weight, dimensions, user_description, location_context
            )
            
            # Get AI classification
            ai_result = await self.groq_service.classify_waste(
                image_description=context,
                weight=weight,
                additional_context=user_description
            )
            
            # Enhance with material database lookup
            enhanced_result = self._enhance_with_database(ai_result)
            
            # Calculate token value
            token_value = self._calculate_token_value(enhanced_result, weight)
            
            # Generate processing recommendations
            processing_steps = self._generate_processing_steps(enhanced_result)
            
            result = {
                **enhanced_result,
                "token_value_cents": token_value,
                "processing_steps": processing_steps,
                "classification_timestamp": self._get_timestamp(),
                "confidence_factors": self._analyze_confidence_factors(enhanced_result, context)
            }
            
            logger.info(f"Classified waste: {result['waste_type']} (confidence: {result['confidence']}%)")
            return result
            
        except Exception as e:
            logger.error(f"Waste classification failed: {str(e)}")
            raise ValidationError(f"Classification failed: {str(e)}")
    
    async def batch_classify(
        self, 
        items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Classify multiple waste items in batch.
        
        Args:
            items: List of item descriptions with metadata
            
        Returns:
            List of classification results
        """
        results = []
        
        for item in items:
            try:
                result = await self.classify_waste_item(**item)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to classify item {item.get('image_description', 'unknown')}: {str(e)}")
                results.append({
                    "error": str(e),
                    "item": item,
                    "classification_timestamp": self._get_timestamp()
                })
        
        return results
    
    def get_supported_materials(self) -> List[Dict[str, Any]]:
        """Get list of all supported waste materials."""
        return [
            {
                "material_type": material_type,
                "category": info["category"],
                "base_value_per_kg": info["base_value_per_kg"],
                "recyclability_score": info["recyclability_score"],
                "processing_complexity": info["processing_complexity"]
            }
            for material_type, info in self.material_database.items()
        ]
    
    def _build_classification_context(
        self,
        image_description: str,
        weight: Optional[float],
        dimensions: Optional[Dict[str, float]],
        user_description: Optional[str],
        location_context: Optional[str]
    ) -> str:
        """Build comprehensive context for classification."""
        context_parts = [f"Visual description: {image_description}"]
        
        if weight:
            context_parts.append(f"Weight: {weight}kg")
            
        if dimensions:
            dim_str = ", ".join([f"{k}: {v}cm" for k, v in dimensions.items()])
            context_parts.append(f"Dimensions: {dim_str}")
            
        if user_description:
            context_parts.append(f"User notes: {user_description}")
            
        if location_context:
            context_parts.append(f"Location: {location_context}")
            
        return " | ".join(context_parts)
    
    def _enhance_with_database(self, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance AI result with material database information."""
        waste_type = ai_result.get("waste_type", "").upper()
        
        if waste_type in self.material_database:
            db_info = self.material_database[waste_type]
            ai_result.update({
                "base_value_per_kg": db_info["base_value_per_kg"],
                "processing_complexity": db_info["processing_complexity"],
                "market_demand": db_info["market_demand"],
                "environmental_impact": db_info["environmental_impact"]
            })
        
        return ai_result
    
    def _calculate_token_value(self, classification: Dict[str, Any], weight: Optional[float]) -> float:
        """Calculate token value based on classification and weight."""
        base_value = classification.get("base_value_per_kg", 5.0)  # cents per kg
        quality_multiplier = self._get_quality_multiplier(classification.get("quality", "FAIR"))
        recyclability_multiplier = classification.get("recyclability", 50) / 100
        
        if weight:
            value = base_value * weight * quality_multiplier * recyclability_multiplier
        else:
            # Estimate based on typical weight for material type
            estimated_weight = self._estimate_weight(classification.get("waste_type", ""))
            value = base_value * estimated_weight * quality_multiplier * recyclability_multiplier
        
        return round(max(value, 0.1), 2)  # Minimum 0.1 cents
    
    def _get_quality_multiplier(self, quality: str) -> float:
        """Get value multiplier based on quality grade."""
        multipliers = {
            "EXCELLENT": 1.0,
            "GOOD": 0.8,
            "FAIR": 0.6,
            "POOR": 0.3,
            "UNUSABLE": 0.1
        }
        return multipliers.get(quality, 0.6)
    
    def _estimate_weight(self, waste_type: str) -> float:
        """Estimate typical weight for waste type."""
        typical_weights = {
            "PET_BOTTLE": 0.03,
            "ALUMINUM_CAN": 0.015,
            "GLASS_BOTTLE": 0.4,
            "CARDBOARD_BOX": 0.1,
            "SMARTPHONE": 0.15,
            "LAPTOP": 2.0,
            "T_SHIRT": 0.2
        }
        return typical_weights.get(waste_type, 0.1)
    
    def _generate_processing_steps(self, classification: Dict[str, Any]) -> List[str]:
        """Generate processing steps based on waste type and condition."""
        waste_type = classification.get("waste_type", "")
        quality = classification.get("quality", "FAIR")
        contamination = classification.get("contamination_level", "LOW")
        
        steps = []
        
        # Basic cleaning steps
        if contamination in ["MEDIUM", "HIGH"]:
            steps.append("Remove all labels and adhesive residue")
            steps.append("Clean thoroughly with appropriate cleaning solution")
            steps.append("Rinse and dry completely")
        elif contamination == "LOW":
            steps.append("Light cleaning to remove surface dirt")
        
        # Material-specific steps
        if "PLASTIC" in waste_type:
            steps.extend([
                "Sort by plastic type (check recycling code)",
                "Remove caps and rings if different plastic type",
                "Compress to save space"
            ])
        elif "METAL" in waste_type:
            steps.extend([
                "Remove any non-metal components",
                "Check for magnetic properties",
                "Flatten if possible to save space"
            ])
        elif "PAPER" in waste_type:
            steps.extend([
                "Remove any plastic coating or staples",
                "Keep dry to prevent mold",
                "Bundle similar paper types together"
            ])
        
        # Quality-based steps
        if quality == "POOR":
            steps.append("Consider repair or refurbishment before recycling")
        
        return steps
    
    def _analyze_confidence_factors(self, classification: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Analyze factors affecting classification confidence."""
        confidence = classification.get("confidence", 50)
        
        factors = {
            "image_quality": "good" if len(context) > 100 else "limited",
            "material_clarity": "high" if confidence > 80 else "medium" if confidence > 60 else "low",
            "contamination_impact": classification.get("contamination_level", "UNKNOWN").lower(),
            "database_match": "exact" if classification.get("base_value_per_kg") else "estimated"
        }
        
        return factors
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def _load_material_database(self) -> Dict[str, Dict[str, Any]]:
        """Load material database with recycling information."""
        return {
            "PET_PLASTIC": {
                "category": "PLASTIC",
                "base_value_per_kg": 8.0,
                "recyclability_score": 85,
                "processing_complexity": "medium",
                "market_demand": "high",
                "environmental_impact": "positive"
            },
            "ALUMINUM_CAN": {
                "category": "METAL",
                "base_value_per_kg": 120.0,
                "recyclability_score": 95,
                "processing_complexity": "low",
                "market_demand": "very_high",
                "environmental_impact": "very_positive"
            },
            "CARDBOARD": {
                "category": "PAPER",
                "base_value_per_kg": 3.0,
                "recyclability_score": 80,
                "processing_complexity": "low",
                "market_demand": "medium",
                "environmental_impact": "positive"
            },
            "GLASS_BOTTLE": {
                "category": "GLASS",
                "base_value_per_kg": 2.0,
                "recyclability_score": 90,
                "processing_complexity": "medium",
                "market_demand": "medium",
                "environmental_impact": "positive"
            },
            "SMARTPHONE": {
                "category": "ELECTRONIC",
                "base_value_per_kg": 50.0,
                "recyclability_score": 60,
                "processing_complexity": "high",
                "market_demand": "high",
                "environmental_impact": "very_positive"
            },
            "COTTON_TEXTILE": {
                "category": "TEXTILE",
                "base_value_per_kg": 1.5,
                "recyclability_score": 40,
                "processing_complexity": "medium",
                "market_demand": "low",
                "environmental_impact": "positive"
            }
        }
