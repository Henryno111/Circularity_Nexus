"""
Groq AI service for waste classification and processing
"""

from typing import Dict, Any, Optional, List
import base64
import json
from loguru import logger

try:
    from groq import Groq
except ImportError:
    logger.warning("Groq library not installed. AI features will be disabled.")
    Groq = None

from circularity_nexus.core.config import settings
from circularity_nexus.core.exceptions import AIProcessingError


class GroqService:
    """Service for interacting with Groq API for AI processing"""
    
    def __init__(self):
        if not Groq:
            raise AIProcessingError("Groq library not installed")
        
        if not settings.GROQ_API_KEY:
            raise AIProcessingError("Groq API key not configured")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
    
    async def classify_waste_from_description(
        self, 
        description: str, 
        estimated_weight: float,
        location: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Classify waste type from text description using Groq
        """
        try:
            system_prompt = """You are an expert waste classification AI for the Circularity Nexus platform. 
            Your job is to classify waste materials and estimate their recyclability.
            
            Supported waste types: PET, ALUMINUM, GLASS, PAPER, CARDBOARD, EWASTE, ORGANIC, MIXED_PLASTIC
            
            Respond with a JSON object containing:
            - detected_type: one of the supported waste types
            - confidence: float between 0.0 and 1.0
            - estimated_weight_kg: refined weight estimate
            - recyclability_score: float between 0.0 and 1.0
            - carbon_impact_kg: estimated CO2 reduction from recycling this waste
            - recommendations: array of recycling tips
            """
            
            user_prompt = f"""
            Classify this waste submission:
            Description: {description}
            Estimated weight: {estimated_weight} kg
            Location: {location or 'Not provided'}
            
            Provide classification and analysis.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                result = {
                    "detected_type": "MIXED_PLASTIC",
                    "confidence": 0.7,
                    "estimated_weight_kg": estimated_weight,
                    "recyclability_score": 0.8,
                    "carbon_impact_kg": estimated_weight * 1.5,
                    "recommendations": ["Sort by material type", "Clean before recycling"]
                }
            
            logger.info(f"Waste classified: {result['detected_type']} with confidence {result['confidence']}")
            return result
            
        except Exception as e:
            logger.error(f"Error in waste classification: {e}")
            raise AIProcessingError(f"Failed to classify waste: {str(e)}")
    
    async def analyze_waste_image(self, image_url: str) -> Dict[str, Any]:
        """
        Analyze waste from image URL (placeholder - Groq doesn't support vision yet)
        """
        # Note: Groq doesn't currently support vision models
        # This is a placeholder that would work with vision-capable models
        logger.warning("Image analysis not yet supported with Groq. Using text-based fallback.")
        
        return {
            "detected_type": "PET",
            "confidence": 0.85,
            "estimated_weight_kg": 1.0,
            "recyclability_score": 0.9,
            "carbon_impact_kg": 1.5,
            "recommendations": ["Clean container", "Remove labels if possible"],
            "analysis_method": "fallback"
        }
    
    async def generate_recycling_tips(self, waste_type: str) -> List[str]:
        """
        Generate recycling tips for specific waste type
        """
        try:
            prompt = f"""
            Generate 3-5 practical recycling tips for {waste_type} waste.
            Focus on preparation, sorting, and maximizing recyclability.
            Keep tips concise and actionable.
            Return as a JSON array of strings.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content
            
            try:
                tips = json.loads(result_text)
                return tips if isinstance(tips, list) else [result_text]
            except json.JSONDecodeError:
                return [result_text]
                
        except Exception as e:
            logger.error(f"Error generating recycling tips: {e}")
            return [
                "Clean the item before recycling",
                "Check local recycling guidelines",
                "Sort by material type"
            ]
    
    async def calculate_carbon_impact(
        self, 
        waste_type: str, 
        weight_kg: float
    ) -> Dict[str, Any]:
        """
        Calculate carbon impact of recycling specific waste
        """
        try:
            prompt = f"""
            Calculate the carbon impact of recycling {weight_kg} kg of {waste_type}.
            
            Provide a JSON response with:
            - co2_saved_kg: CO2 emissions saved by recycling vs landfill
            - energy_saved_kwh: Energy saved through recycling
            - water_saved_liters: Water saved through recycling
            - explanation: brief explanation of the calculation
            
            Use realistic environmental data.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=400
            )
            
            result_text = response.choices[0].message.content
            
            try:
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError:
                # Fallback calculation
                carbon_factors = {
                    "PET": 1.5,
                    "ALUMINUM": 2.1,
                    "GLASS": 0.8,
                    "PAPER": 1.2,
                    "EWASTE": 3.5
                }
                factor = carbon_factors.get(waste_type, 1.0)
                
                return {
                    "co2_saved_kg": weight_kg * factor,
                    "energy_saved_kwh": weight_kg * factor * 2,
                    "water_saved_liters": weight_kg * factor * 10,
                    "explanation": f"Recycling {waste_type} saves approximately {factor} kg CO2 per kg"
                }
                
        except Exception as e:
            logger.error(f"Error calculating carbon impact: {e}")
            raise AIProcessingError(f"Failed to calculate carbon impact: {str(e)}")


# Global service instance
groq_service = GroqService() if Groq and settings.GROQ_API_KEY else None
