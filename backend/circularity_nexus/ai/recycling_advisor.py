"""
Recycling Advisor Service

Provides intelligent recycling recommendations, local facility matching,
and optimization strategies for waste management.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from .groq_service import GroqService
from ..core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class RecommendationType(Enum):
    """Types of recycling recommendations."""
    PREPARATION = "preparation"
    FACILITY = "facility"
    TIMING = "timing"
    VALUE_OPTIMIZATION = "value_optimization"
    ALTERNATIVE_USE = "alternative_use"
    PREVENTION = "prevention"

class UrgencyLevel(Enum):
    """Urgency levels for recycling actions."""
    IMMEDIATE = "immediate"  # Hazardous or degrading materials
    HIGH = "high"           # Time-sensitive value
    MEDIUM = "medium"       # Standard recycling
    LOW = "low"            # Can wait for optimal conditions

class RecyclingAdvisor:
    """Intelligent recycling advisor with AI-powered recommendations."""
    
    def __init__(self):
        self.groq_service = GroqService()
        self.facility_database = self._load_facility_database()
        self.seasonal_factors = self._load_seasonal_factors()
    
    async def get_recycling_recommendations(
        self,
        waste_type: str,
        weight: float,
        user_location: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        current_market_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive recycling recommendations.
        
        Args:
            waste_type: Type of waste material
            weight: Weight in kg
            user_location: User's location (city, state/country)
            user_preferences: User preferences (convenience, value, environmental impact)
            current_market_conditions: Current market prices and demand
            
        Returns:
            Comprehensive recycling recommendations
        """
        try:
            # Get AI-powered recommendations
            ai_recommendations = await self.groq_service.generate_recycling_tips(
                waste_type, user_location
            )
            
            # Analyze optimal timing
            timing_analysis = self._analyze_optimal_timing(
                waste_type, current_market_conditions
            )
            
            # Find local facilities
            local_facilities = self._find_local_facilities(
                waste_type, user_location
            )
            
            # Generate value optimization strategies
            value_strategies = self._generate_value_strategies(
                waste_type, weight, current_market_conditions
            )
            
            # Assess urgency
            urgency_assessment = self._assess_urgency(waste_type, weight)
            
            # Generate step-by-step action plan
            action_plan = self._generate_action_plan(
                waste_type, ai_recommendations, timing_analysis, urgency_assessment
            )
            
            # Calculate environmental impact potential
            impact_potential = self._calculate_impact_potential(waste_type, weight)
            
            result = {
                "ai_recommendations": ai_recommendations,
                "timing_analysis": timing_analysis,
                "local_facilities": local_facilities,
                "value_optimization": value_strategies,
                "urgency_assessment": urgency_assessment,
                "action_plan": action_plan,
                "impact_potential": impact_potential,
                "personalization": self._personalize_recommendations(
                    user_preferences, ai_recommendations
                ),
                "metadata": {
                    "recommendation_id": self._generate_recommendation_id(),
                    "generated_at": self._get_timestamp(),
                    "valid_until": self._calculate_expiry(urgency_assessment["level"]),
                    "confidence_score": self._calculate_confidence_score(
                        waste_type, user_location, current_market_conditions
                    )
                }
            }
            
            logger.info(f"Generated recommendations for {waste_type} ({weight}kg) - Urgency: {urgency_assessment['level']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            raise ValidationError(f"Recommendation generation failed: {str(e)}")
    
    async def optimize_collection_route(
        self,
        waste_items: List[Dict[str, Any]],
        user_location: str,
        transportation_method: str = "car"
    ) -> Dict[str, Any]:
        """
        Optimize collection route for multiple waste items.
        
        Args:
            waste_items: List of waste items with locations
            user_location: Starting location
            transportation_method: Method of transportation
            
        Returns:
            Optimized route with time and cost estimates
        """
        try:
            # Group items by facility type
            facility_groups = self._group_by_facility_type(waste_items)
            
            # Calculate optimal route
            route_optimization = self._calculate_optimal_route(
                facility_groups, user_location, transportation_method
            )
            
            # Estimate costs and time
            cost_analysis = self._estimate_route_costs(
                route_optimization, transportation_method
            )
            
            # Environmental impact of transportation
            transport_impact = self._calculate_transport_impact(
                route_optimization, transportation_method
            )
            
            return {
                "optimized_route": route_optimization,
                "cost_analysis": cost_analysis,
                "transport_impact": transport_impact,
                "recommendations": {
                    "best_day": self._recommend_best_day(facility_groups),
                    "time_slots": self._recommend_time_slots(facility_groups),
                    "preparation_checklist": self._generate_preparation_checklist(waste_items)
                }
            }
            
        except Exception as e:
            logger.error(f"Route optimization failed: {str(e)}")
            raise ValidationError(f"Route optimization failed: {str(e)}")
    
    def get_market_insights(
        self,
        waste_type: str,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get current market insights for waste type."""
        try:
            base_insights = self._get_base_market_data(waste_type)
            
            if location:
                regional_adjustments = self._get_regional_adjustments(waste_type, location)
                base_insights.update(regional_adjustments)
            
            # Add seasonal factors
            seasonal_impact = self._get_seasonal_impact(waste_type)
            
            return {
                "current_price_range": base_insights["price_range"],
                "demand_level": base_insights["demand_level"],
                "market_trend": base_insights["trend"],
                "seasonal_factors": seasonal_impact,
                "price_forecast": self._generate_price_forecast(waste_type),
                "optimal_selling_window": self._calculate_optimal_window(waste_type),
                "market_volatility": base_insights["volatility"],
                "last_updated": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Market insights failed: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_optimal_timing(
        self,
        waste_type: str,
        market_conditions: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze optimal timing for recycling."""
        seasonal_factor = self.seasonal_factors.get(waste_type, 1.0)
        
        # Market-based timing
        if market_conditions:
            current_price = market_conditions.get("current_price", 0)
            avg_price = market_conditions.get("average_price", current_price)
            price_ratio = current_price / avg_price if avg_price > 0 else 1.0
        else:
            price_ratio = 1.0
        
        # Determine optimal timing
        if price_ratio > 1.15:  # 15% above average
            timing_recommendation = "immediate"
            reason = "Prices are significantly above average"
        elif seasonal_factor > 1.1:  # Good seasonal timing
            timing_recommendation = "within_week"
            reason = "Favorable seasonal conditions"
        elif price_ratio < 0.9:  # Below average prices
            timing_recommendation = "wait_2_weeks"
            reason = "Prices below average, consider waiting"
        else:
            timing_recommendation = "flexible"
            reason = "Standard market conditions"
        
        return {
            "recommendation": timing_recommendation,
            "reason": reason,
            "seasonal_factor": seasonal_factor,
            "price_factor": price_ratio,
            "optimal_window_days": self._calculate_optimal_window_days(timing_recommendation),
            "risk_assessment": self._assess_timing_risk(waste_type, timing_recommendation)
        }
    
    def _find_local_facilities(
        self,
        waste_type: str,
        location: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Find local recycling facilities."""
        if not location:
            return []
        
        # Normalize waste type for facility matching
        facility_type = self._map_waste_to_facility_type(waste_type)
        
        # Mock facility data (in real implementation, would query database/API)
        facilities = [
            {
                "name": f"EcoRecycle Center - {location}",
                "type": facility_type,
                "distance_km": 5.2,
                "accepts": [waste_type],
                "operating_hours": "Mon-Sat 8AM-6PM",
                "contact": "+1-555-0123",
                "special_requirements": self._get_facility_requirements(waste_type),
                "estimated_value": self._estimate_facility_value(waste_type),
                "rating": 4.5,
                "processing_time": "Same day",
                "certifications": ["ISO 14001", "R2 Certified"]
            },
            {
                "name": f"Green Solutions - {location}",
                "type": facility_type,
                "distance_km": 8.7,
                "accepts": [waste_type],
                "operating_hours": "Mon-Fri 9AM-5PM",
                "contact": "+1-555-0456",
                "special_requirements": [],
                "estimated_value": self._estimate_facility_value(waste_type) * 0.9,
                "rating": 4.2,
                "processing_time": "1-2 days",
                "certifications": ["ISO 14001"]
            }
        ]
        
        # Sort by distance and value
        facilities.sort(key=lambda x: (x["distance_km"], -x["estimated_value"]))
        
        return facilities[:5]  # Return top 5
    
    def _generate_value_strategies(
        self,
        waste_type: str,
        weight: float,
        market_conditions: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate strategies to maximize value."""
        strategies = []
        
        # Preparation strategies
        if "PLASTIC" in waste_type.upper():
            strategies.extend([
                "Remove all labels and adhesive residue for 15% value increase",
                "Sort by plastic type (check recycling codes)",
                "Clean thoroughly to achieve 'excellent' quality grade"
            ])
        elif "METAL" in waste_type.upper():
            strategies.extend([
                "Remove non-metal components for purity bonus",
                "Clean off rust or corrosion if present",
                "Separate different metal types"
            ])
        
        # Timing strategies
        if market_conditions and market_conditions.get("trend") == "increasing":
            strategies.append("Consider waiting 1-2 weeks for better prices")
        
        # Quantity strategies
        if weight < 1.0:
            strategies.append("Collect more of same material type for bulk pricing")
        
        # Quality strategies
        strategies.extend([
            "Document condition with photos for quality verification",
            "Store in dry, clean environment until processing",
            "Handle carefully to prevent damage"
        ])
        
        return {
            "strategies": strategies,
            "potential_value_increase": self._calculate_potential_increase(strategies),
            "effort_level": self._assess_effort_level(strategies),
            "time_investment": self._estimate_time_investment(strategies)
        }
    
    def _assess_urgency(self, waste_type: str, weight: float) -> Dict[str, Any]:
        """Assess urgency of recycling action."""
        urgency_factors = {
            "HAZARDOUS": UrgencyLevel.IMMEDIATE,
            "BATTERY": UrgencyLevel.IMMEDIATE,
            "ORGANIC": UrgencyLevel.HIGH,
            "ELECTRONIC": UrgencyLevel.MEDIUM,
            "METAL": UrgencyLevel.LOW,
            "PLASTIC": UrgencyLevel.LOW,
            "PAPER": UrgencyLevel.MEDIUM,
            "GLASS": UrgencyLevel.LOW
        }
        
        # Determine base urgency
        waste_category = self._get_waste_category(waste_type)
        base_urgency = urgency_factors.get(waste_category, UrgencyLevel.MEDIUM)
        
        # Adjust for quantity
        if weight > 10.0:  # Large quantities need faster processing
            if base_urgency == UrgencyLevel.LOW:
                base_urgency = UrgencyLevel.MEDIUM
            elif base_urgency == UrgencyLevel.MEDIUM:
                base_urgency = UrgencyLevel.HIGH
        
        urgency_reasons = []
        if base_urgency == UrgencyLevel.IMMEDIATE:
            urgency_reasons.append("Hazardous material requires immediate processing")
        elif "ORGANIC" in waste_type.upper():
            urgency_reasons.append("Organic material degrades quickly")
        elif weight > 10.0:
            urgency_reasons.append("Large quantity requires prompt processing")
        
        return {
            "level": base_urgency.value,
            "reasons": urgency_reasons,
            "recommended_action_within": self._get_action_timeframe(base_urgency),
            "consequences_of_delay": self._get_delay_consequences(waste_type, base_urgency)
        }
    
    def _generate_action_plan(
        self,
        waste_type: str,
        ai_recommendations: Dict[str, Any],
        timing_analysis: Dict[str, Any],
        urgency_assessment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate step-by-step action plan."""
        steps = []
        
        # Step 1: Preparation
        prep_steps = ai_recommendations.get("preparation_steps", [])
        if prep_steps:
            steps.append({
                "step": 1,
                "title": "Prepare the waste item",
                "actions": prep_steps,
                "estimated_time": "10-30 minutes",
                "priority": "high"
            })
        
        # Step 2: Documentation
        steps.append({
            "step": 2,
            "title": "Document and photograph",
            "actions": [
                "Take clear photos of the item",
                "Note any damage or contamination",
                "Weigh the item if possible"
            ],
            "estimated_time": "5 minutes",
            "priority": "medium"
        })
        
        # Step 3: Timing decision
        if timing_analysis["recommendation"] == "wait_2_weeks":
            steps.append({
                "step": 3,
                "title": "Wait for optimal timing",
                "actions": [
                    f"Store safely until {timing_analysis['optimal_window_days']} days",
                    "Monitor market conditions",
                    "Set reminder for optimal timing"
                ],
                "estimated_time": "Ongoing",
                "priority": "low"
            })
        
        # Step 4: Facility selection and transport
        steps.append({
            "step": len(steps) + 1,
            "title": "Select facility and transport",
            "actions": [
                "Choose optimal facility based on distance and value",
                "Check facility operating hours",
                "Plan efficient route if multiple items"
            ],
            "estimated_time": "30-60 minutes",
            "priority": "high" if urgency_assessment["level"] in ["immediate", "high"] else "medium"
        })
        
        return steps
    
    def _calculate_impact_potential(self, waste_type: str, weight: float) -> Dict[str, Any]:
        """Calculate environmental impact potential."""
        # Simplified impact calculation
        impact_factors = {
            "PLASTIC": {"co2_per_kg": 2.5, "trees_equivalent": 0.12},
            "METAL": {"co2_per_kg": 8.0, "trees_equivalent": 0.37},
            "PAPER": {"co2_per_kg": 1.8, "trees_equivalent": 0.08},
            "GLASS": {"co2_per_kg": 0.6, "trees_equivalent": 0.03},
            "ELECTRONIC": {"co2_per_kg": 15.0, "trees_equivalent": 0.69}
        }
        
        category = self._get_waste_category(waste_type)
        factors = impact_factors.get(category, {"co2_per_kg": 3.0, "trees_equivalent": 0.14})
        
        co2_saved = weight * factors["co2_per_kg"]
        trees_equivalent = weight * factors["trees_equivalent"]
        
        return {
            "co2_saved_kg": round(co2_saved, 2),
            "trees_equivalent": round(trees_equivalent, 2),
            "water_saved_liters": round(weight * 25.0, 1),
            "energy_saved_kwh": round(weight * 5.5, 1),
            "impact_score": min(100, round((co2_saved / weight) * 10, 1))
        }
    
    def _personalize_recommendations(
        self,
        user_preferences: Optional[Dict[str, Any]],
        base_recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Personalize recommendations based on user preferences."""
        if not user_preferences:
            return {"personalization_applied": False}
        
        preferences = {
            "priority": user_preferences.get("priority", "balanced"),  # convenience, value, environmental
            "max_travel_distance": user_preferences.get("max_travel_distance", 15),  # km
            "preferred_days": user_preferences.get("preferred_days", []),
            "time_availability": user_preferences.get("time_availability", "flexible")
        }
        
        adjustments = []
        
        if preferences["priority"] == "convenience":
            adjustments.append("Prioritizing nearby facilities and minimal preparation")
        elif preferences["priority"] == "value":
            adjustments.append("Focusing on maximum value optimization strategies")
        elif preferences["priority"] == "environmental":
            adjustments.append("Emphasizing environmental impact and sustainable practices")
        
        return {
            "personalization_applied": True,
            "user_preferences": preferences,
            "adjustments_made": adjustments,
            "recommended_approach": self._get_personalized_approach(preferences)
        }
    
    # Helper methods
    def _get_waste_category(self, waste_type: str) -> str:
        """Get broad waste category."""
        waste_upper = waste_type.upper()
        if "PLASTIC" in waste_upper or "PET" in waste_upper:
            return "PLASTIC"
        elif "METAL" in waste_upper or "ALUMINUM" in waste_upper:
            return "METAL"
        elif "PAPER" in waste_upper or "CARDBOARD" in waste_upper:
            return "PAPER"
        elif "GLASS" in waste_upper:
            return "GLASS"
        elif "ELECTRONIC" in waste_upper:
            return "ELECTRONIC"
        elif "ORGANIC" in waste_upper:
            return "ORGANIC"
        else:
            return "MIXED"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def _generate_recommendation_id(self) -> str:
        """Generate unique recommendation ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _calculate_expiry(self, urgency_level: str) -> str:
        """Calculate recommendation expiry based on urgency."""
        from datetime import datetime, timedelta
        
        expiry_hours = {
            "immediate": 2,
            "high": 24,
            "medium": 72,
            "low": 168  # 1 week
        }
        
        hours = expiry_hours.get(urgency_level, 72)
        expiry = datetime.utcnow() + timedelta(hours=hours)
        return expiry.isoformat() + "Z"
    
    def _calculate_confidence_score(
        self,
        waste_type: str,
        location: Optional[str],
        market_conditions: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for recommendations."""
        base_score = 70.0
        
        # Adjust based on data availability
        if location:
            base_score += 15.0
        if market_conditions:
            base_score += 10.0
        if waste_type in ["PET_PLASTIC", "ALUMINUM_CAN", "CARDBOARD"]:
            base_score += 5.0  # Well-known materials
        
        return min(100.0, base_score)
    
    def _load_facility_database(self) -> Dict[str, Any]:
        """Load facility database (mock implementation)."""
        return {}
    
    def _load_seasonal_factors(self) -> Dict[str, float]:
        """Load seasonal pricing factors."""
        return {
            "CARDBOARD": 1.2,  # Higher demand in Q4
            "PLASTIC": 1.0,
            "METAL": 1.1,
            "GLASS": 1.0,
            "ELECTRONIC": 0.9  # Lower demand in summer
        }
    
    # Additional helper methods would be implemented here...
    def _map_waste_to_facility_type(self, waste_type: str) -> str:
        """Map waste type to facility type."""
        return "general_recycling"
    
    def _get_facility_requirements(self, waste_type: str) -> List[str]:
        """Get facility-specific requirements."""
        return []
    
    def _estimate_facility_value(self, waste_type: str) -> float:
        """Estimate value at facility."""
        return 5.0
    
    def _calculate_potential_increase(self, strategies: List[str]) -> float:
        """Calculate potential value increase from strategies."""
        return len(strategies) * 5.0  # 5% per strategy
    
    def _assess_effort_level(self, strategies: List[str]) -> str:
        """Assess effort level for strategies."""
        return "medium" if len(strategies) > 3 else "low"
    
    def _estimate_time_investment(self, strategies: List[str]) -> str:
        """Estimate time investment."""
        return f"{len(strategies) * 10}-{len(strategies) * 20} minutes"
    
    def _get_action_timeframe(self, urgency: UrgencyLevel) -> str:
        """Get action timeframe for urgency level."""
        timeframes = {
            UrgencyLevel.IMMEDIATE: "2 hours",
            UrgencyLevel.HIGH: "24 hours",
            UrgencyLevel.MEDIUM: "3 days",
            UrgencyLevel.LOW: "1 week"
        }
        return timeframes.get(urgency, "3 days")
    
    def _get_delay_consequences(self, waste_type: str, urgency: UrgencyLevel) -> List[str]:
        """Get consequences of delaying action."""
        if urgency == UrgencyLevel.IMMEDIATE:
            return ["Safety hazard", "Legal compliance issues"]
        elif "ORGANIC" in waste_type.upper():
            return ["Decomposition", "Odor", "Reduced value"]
        else:
            return ["Potential value decrease", "Storage space occupied"]
    
    def _get_personalized_approach(self, preferences: Dict[str, Any]) -> str:
        """Get personalized approach description."""
        priority = preferences.get("priority", "balanced")
        if priority == "convenience":
            return "Quick and easy recycling with minimal effort"
        elif priority == "value":
            return "Maximum value extraction through optimization"
        elif priority == "environmental":
            return "Environmentally optimal recycling practices"
        else:
            return "Balanced approach considering all factors"
