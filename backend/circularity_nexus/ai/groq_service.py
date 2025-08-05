"""
Groq AI Service for Circularity Nexus

Provides core AI functionality using Groq's Llama3 model for waste processing,
classification, and environmental impact analysis.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from groq import Groq
from ..core.config import get_settings
from ..core.exceptions import AIServiceError

logger = logging.getLogger(__name__)

class GroqService:
    """Core Groq AI service for waste analysis and environmental calculations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = Groq(api_key=self.settings.groq_api_key)
        self.model = "llama3-8b-8192"
        
    async def classify_waste(
        self, 
        image_description: str, 
        weight: Optional[float] = None,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classify waste type and quality from image description.
        
        Args:
            image_description: Description of the waste item
            weight: Optional weight in kg
            additional_context: Additional context about the waste
            
        Returns:
            Classification result with waste type, quality, and confidence
        """
        try:
            prompt = self._build_classification_prompt(
                image_description, weight, additional_context
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert waste classification AI for a circular economy platform. Respond only with valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=1024
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Waste classified: {result.get('waste_type')} with confidence {result.get('confidence')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Waste classification failed: {str(e)}")
            raise AIServiceError(f"Failed to classify waste: {str(e)}")
    
    async def calculate_carbon_impact(
        self, 
        waste_type: str, 
        weight: float,
        recycling_method: str = "standard"
    ) -> Dict[str, Any]:
        """
        Calculate carbon impact and offset potential.
        
        Args:
            waste_type: Type of waste material
            weight: Weight in kg
            recycling_method: Recycling method used
            
        Returns:
            Carbon impact analysis with CO2 savings and credits
        """
        try:
            prompt = self._build_carbon_prompt(waste_type, weight, recycling_method)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a carbon footprint expert. Calculate precise CO2 impact and offset potential. Respond only with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=512
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Carbon impact calculated: {result.get('co2_saved_kg')}kg CO2 saved")
            
            return result
            
        except Exception as e:
            logger.error(f"Carbon calculation failed: {str(e)}")
            raise AIServiceError(f"Failed to calculate carbon impact: {str(e)}")
    
    async def generate_recycling_tips(
        self, 
        waste_type: str,
        user_location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized recycling tips and recommendations.
        
        Args:
            waste_type: Type of waste material
            user_location: User's location for local recommendations
            
        Returns:
            Recycling tips and local facility recommendations
        """
        try:
            prompt = self._build_tips_prompt(waste_type, user_location)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a recycling expert providing actionable tips. Respond only with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1024
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Generated recycling tips for {waste_type}")
            
            return result
            
        except Exception as e:
            logger.error(f"Tips generation failed: {str(e)}")
            raise AIServiceError(f"Failed to generate recycling tips: {str(e)}")
    
    def _build_classification_prompt(
        self, 
        image_description: str, 
        weight: Optional[float],
        additional_context: Optional[str]
    ) -> str:
        """Build prompt for waste classification."""
        weight_info = f"Weight: {weight}kg" if weight else "Weight: Unknown"
        context_info = f"Additional context: {additional_context}" if additional_context else ""
        
        return f"""
        Classify this waste item based on the description:
        
        Description: {image_description}
        {weight_info}
        {context_info}
        
        Respond with JSON containing:
        {{
            "waste_type": "specific material type (e.g., PET_PLASTIC, ALUMINUM_CAN, CARDBOARD)",
            "category": "broader category (PLASTIC, METAL, PAPER, GLASS, ORGANIC, ELECTRONIC, TEXTILE)",
            "quality": "condition rating (EXCELLENT, GOOD, FAIR, POOR)",
            "recyclability": "recyclability score 0-100",
            "confidence": "confidence score 0-100",
            "estimated_value": "estimated token value in cents",
            "contamination_level": "contamination level (NONE, LOW, MEDIUM, HIGH)",
            "processing_requirements": ["list of processing steps needed"]
        }}
        """
    
    def _build_carbon_prompt(self, waste_type: str, weight: float, recycling_method: str) -> str:
        """Build prompt for carbon impact calculation."""
        return f"""
        Calculate the carbon impact of recycling this waste:
        
        Waste Type: {waste_type}
        Weight: {weight}kg
        Recycling Method: {recycling_method}
        
        Respond with JSON containing:
        {{
            "co2_saved_kg": "CO2 saved in kg compared to landfill",
            "co2_equivalent_trees": "equivalent trees planted",
            "carbon_credits_earned": "carbon credits earned",
            "energy_saved_kwh": "energy saved in kWh",
            "water_saved_liters": "water saved in liters",
            "landfill_diverted_kg": "waste diverted from landfill in kg",
            "environmental_impact_score": "overall impact score 0-100"
        }}
        """
    
    def _build_tips_prompt(self, waste_type: str, user_location: Optional[str]) -> str:
        """Build prompt for recycling tips generation."""
        location_info = f"User location: {user_location}" if user_location else "Location: Not specified"
        
        return f"""
        Generate recycling tips for this waste type:
        
        Waste Type: {waste_type}
        {location_info}
        
        Respond with JSON containing:
        {{
            "preparation_steps": ["step-by-step preparation instructions"],
            "local_facilities": ["nearby recycling facilities if location provided"],
            "alternative_uses": ["creative reuse suggestions"],
            "environmental_benefits": ["specific environmental benefits"],
            "common_mistakes": ["mistakes to avoid"],
            "optimal_timing": "best time to recycle this item",
            "value_maximization": ["tips to maximize token value"]
        }}
        """
