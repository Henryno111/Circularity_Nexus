"""
Unit tests for AI Recycling Advisor
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from circularity_nexus.ai.recycling_advisor import RecyclingAdvisor, RecommendationType, UrgencyLevel
from circularity_nexus.core.exceptions import ValidationError


class TestRecyclingAdvisor:
    """Test cases for RecyclingAdvisor"""
    
    @pytest.fixture
    def mock_groq_service(self):
        """Mock GroqService"""
        with patch('circularity_nexus.ai.recycling_advisor.GroqService') as mock_groq:
            mock_service = Mock()
            mock_groq.return_value = mock_service
            yield mock_service
    
    @pytest.fixture
    def recycling_advisor(self, mock_groq_service):
        """RecyclingAdvisor instance with mocked dependencies"""
        advisor = RecyclingAdvisor()
        advisor.groq_service = mock_groq_service
        return advisor
    
    @pytest.mark.asyncio
    async def test_get_recycling_recommendations_success(self, recycling_advisor, mock_groq_service):
        """Test successful recycling recommendations"""
        # Mock Groq response
        mock_groq_service.generate_recycling_tips.return_value = {
            "preparation_steps": ["Clean thoroughly", "Remove labels"],
            "local_facilities": ["EcoRecycle Center"],
            "alternative_uses": ["Plant pot", "Storage container"],
            "environmental_benefits": ["Reduces plastic waste", "Saves energy"],
            "common_mistakes": ["Not cleaning properly"],
            "optimal_timing": "Within 1 week",
            "value_maximization": ["Sort by type", "Bundle similar items"]
        }
        
        # Test recommendations
        result = await recycling_advisor.get_recycling_recommendations(
            waste_type="PET_PLASTIC",
            weight=0.5,
            user_location="San Francisco, CA",
            user_preferences={"priority": "value", "max_travel_distance": 10}
        )
        
        # Assertions
        assert "ai_recommendations" in result
        assert "timing_analysis" in result
        assert "local_facilities" in result
        assert "value_optimization" in result
        assert "urgency_assessment" in result
        assert "action_plan" in result
        assert "impact_potential" in result
        assert "personalization" in result
        assert "metadata" in result
        
        # Check metadata
        assert "recommendation_id" in result["metadata"]
        assert "generated_at" in result["metadata"]
        assert "confidence_score" in result["metadata"]
        
        # Verify Groq service was called
        mock_groq_service.generate_recycling_tips.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_optimize_collection_route(self, recycling_advisor):
        """Test collection route optimization"""
        waste_items = [
            {
                "waste_type": "PET_PLASTIC",
                "weight": 0.5,
                "location": "123 Main St"
            },
            {
                "waste_type": "ALUMINUM",
                "weight": 0.2,
                "location": "456 Oak Ave"
            }
        ]
        
        result = await recycling_advisor.optimize_collection_route(
            waste_items=waste_items,
            user_location="789 Pine St",
            transportation_method="car"
        )
        
        # Assertions
        assert "optimized_route" in result
        assert "cost_analysis" in result
        assert "transport_impact" in result
        assert "recommendations" in result
        assert "best_day" in result["recommendations"]
        assert "time_slots" in result["recommendations"]
        assert "preparation_checklist" in result["recommendations"]
    
    def test_get_market_insights_with_location(self, recycling_advisor):
        """Test market insights with location"""
        result = recycling_advisor.get_market_insights(
            waste_type="PET_PLASTIC",
            location="California"
        )
        
        assert "current_price_range" in result
        assert "demand_level" in result
        assert "market_trend" in result
        assert "seasonal_factors" in result
        assert "price_forecast" in result
        assert "optimal_selling_window" in result
        assert "market_volatility" in result
        assert "last_updated" in result
    
    def test_get_market_insights_without_location(self, recycling_advisor):
        """Test market insights without location"""
        result = recycling_advisor.get_market_insights(waste_type="ALUMINUM")
        
        assert "current_price_range" in result
        assert "demand_level" in result
        # Should still work without location-specific data
    
    def test_analyze_optimal_timing_high_prices(self, recycling_advisor):
        """Test timing analysis with high market prices"""
        market_conditions = {
            "current_price": 115,
            "average_price": 100
        }
        
        result = recycling_advisor._analyze_optimal_timing("PET_PLASTIC", market_conditions)
        
        assert result["recommendation"] == "immediate"
        assert "above average" in result["reason"]
        assert result["price_factor"] == 1.15
    
    def test_analyze_optimal_timing_low_prices(self, recycling_advisor):
        """Test timing analysis with low market prices"""
        market_conditions = {
            "current_price": 85,
            "average_price": 100
        }
        
        result = recycling_advisor._analyze_optimal_timing("PET_PLASTIC", market_conditions)
        
        assert result["recommendation"] == "wait_2_weeks"
        assert "below average" in result["reason"]
        assert result["price_factor"] == 0.85
    
    def test_analyze_optimal_timing_seasonal_factor(self, recycling_advisor):
        """Test timing analysis with seasonal factors"""
        # Mock seasonal factors
        recycling_advisor.seasonal_factors = {"CARDBOARD": 1.2}
        
        result = recycling_advisor._analyze_optimal_timing("CARDBOARD", None)
        
        assert result["recommendation"] == "within_week"
        assert "seasonal" in result["reason"]
        assert result["seasonal_factor"] == 1.2
    
    def test_find_local_facilities(self, recycling_advisor):
        """Test local facility finding"""
        facilities = recycling_advisor._find_local_facilities("PET_PLASTIC", "San Francisco")
        
        assert isinstance(facilities, list)
        assert len(facilities) <= 5  # Should return top 5
        
        if facilities:
            facility = facilities[0]
            assert "name" in facility
            assert "distance_km" in facility
            assert "accepts" in facility
            assert "operating_hours" in facility
            assert "estimated_value" in facility
    
    def test_generate_value_strategies_plastic(self, recycling_advisor):
        """Test value strategies for plastic"""
        result = recycling_advisor._generate_value_strategies(
            "PET_PLASTIC", 0.5, {"trend": "increasing"}
        )
        
        assert "strategies" in result
        assert "potential_value_increase" in result
        assert "effort_level" in result
        assert "time_investment" in result
        
        strategies = result["strategies"]
        assert any("labels" in strategy.lower() for strategy in strategies)
        assert any("clean" in strategy.lower() for strategy in strategies)
    
    def test_generate_value_strategies_metal(self, recycling_advisor):
        """Test value strategies for metal"""
        result = recycling_advisor._generate_value_strategies("ALUMINUM", 0.2, None)
        
        strategies = result["strategies"]
        assert any("metal" in strategy.lower() for strategy in strategies)
        assert any("rust" in strategy.lower() or "corrosion" in strategy.lower() for strategy in strategies)
    
    def test_assess_urgency_hazardous(self, recycling_advisor):
        """Test urgency assessment for hazardous materials"""
        result = recycling_advisor._assess_urgency("BATTERY", 0.1)
        
        assert result["level"] == UrgencyLevel.IMMEDIATE.value
        assert "hazardous" in result["reasons"][0].lower()
    
    def test_assess_urgency_organic(self, recycling_advisor):
        """Test urgency assessment for organic waste"""
        result = recycling_advisor._assess_urgency("ORGANIC", 1.0)
        
        assert result["level"] == UrgencyLevel.HIGH.value
        assert any("degrades" in reason.lower() for reason in result["reasons"])
    
    def test_assess_urgency_large_quantity(self, recycling_advisor):
        """Test urgency assessment for large quantities"""
        result = recycling_advisor._assess_urgency("PLASTIC", 15.0)  # Large quantity
        
        # Should upgrade urgency due to large quantity
        assert result["level"] in [UrgencyLevel.MEDIUM.value, UrgencyLevel.HIGH.value]
        assert any("large quantity" in reason.lower() for reason in result["reasons"])
    
    def test_generate_action_plan(self, recycling_advisor):
        """Test action plan generation"""
        ai_recommendations = {
            "preparation_steps": ["Clean", "Remove labels"]
        }
        timing_analysis = {
            "recommendation": "immediate",
            "optimal_window_days": 3
        }
        urgency_assessment = {
            "level": "high"
        }
        
        plan = recycling_advisor._generate_action_plan(
            "PET_PLASTIC", ai_recommendations, timing_analysis, urgency_assessment
        )
        
        assert isinstance(plan, list)
        assert len(plan) > 0
        
        # Check first step structure
        step = plan[0]
        assert "step" in step
        assert "title" in step
        assert "actions" in step
        assert "estimated_time" in step
        assert "priority" in step
    
    def test_calculate_impact_potential_plastic(self, recycling_advisor):
        """Test impact potential calculation for plastic"""
        result = recycling_advisor._calculate_impact_potential("PET_PLASTIC", 2.0)
        
        assert "co2_saved_kg" in result
        assert "trees_equivalent" in result
        assert "water_saved_liters" in result
        assert "energy_saved_kwh" in result
        assert "impact_score" in result
        
        # Check calculations
        assert result["co2_saved_kg"] == 5.0  # 2.0 * 2.5
        assert result["trees_equivalent"] == 0.24  # 2.0 * 0.12
        assert result["water_saved_liters"] == 50.0  # 2.0 * 25.0
    
    def test_calculate_impact_potential_metal(self, recycling_advisor):
        """Test impact potential calculation for metal"""
        result = recycling_advisor._calculate_impact_potential("ALUMINUM", 1.0)
        
        assert result["co2_saved_kg"] == 8.0  # 1.0 * 8.0
        assert result["trees_equivalent"] == 0.37  # 1.0 * 0.37
    
    def test_personalize_recommendations_convenience(self, recycling_advisor):
        """Test recommendation personalization for convenience priority"""
        user_preferences = {
            "priority": "convenience",
            "max_travel_distance": 5,
            "time_availability": "limited"
        }
        base_recommendations = {}
        
        result = recycling_advisor._personalize_recommendations(user_preferences, base_recommendations)
        
        assert result["personalization_applied"] is True
        assert "convenience" in result["recommended_approach"].lower()
        assert any("nearby" in adj.lower() for adj in result["adjustments_made"])
    
    def test_personalize_recommendations_value(self, recycling_advisor):
        """Test recommendation personalization for value priority"""
        user_preferences = {
            "priority": "value",
            "max_travel_distance": 20
        }
        base_recommendations = {}
        
        result = recycling_advisor._personalize_recommendations(user_preferences, base_recommendations)
        
        assert "value" in result["recommended_approach"].lower()
        assert any("value" in adj.lower() for adj in result["adjustments_made"])
    
    def test_personalize_recommendations_environmental(self, recycling_advisor):
        """Test recommendation personalization for environmental priority"""
        user_preferences = {
            "priority": "environmental"
        }
        base_recommendations = {}
        
        result = recycling_advisor._personalize_recommendations(user_preferences, base_recommendations)
        
        assert "environmental" in result["recommended_approach"].lower()
        assert any("environmental" in adj.lower() for adj in result["adjustments_made"])
    
    def test_personalize_recommendations_none(self, recycling_advisor):
        """Test recommendation personalization with no preferences"""
        result = recycling_advisor._personalize_recommendations(None, {})
        
        assert result["personalization_applied"] is False
    
    def test_get_waste_category(self, recycling_advisor):
        """Test waste category determination"""
        assert recycling_advisor._get_waste_category("PET_PLASTIC") == "PLASTIC"
        assert recycling_advisor._get_waste_category("ALUMINUM_CAN") == "METAL"
        assert recycling_advisor._get_waste_category("CARDBOARD_BOX") == "PAPER"
        assert recycling_advisor._get_waste_category("GLASS_BOTTLE") == "GLASS"
        assert recycling_advisor._get_waste_category("SMARTPHONE") == "ELECTRONIC"
        assert recycling_advisor._get_waste_category("FOOD_WASTE") == "ORGANIC"
        assert recycling_advisor._get_waste_category("UNKNOWN") == "MIXED"
    
    def test_get_action_timeframe(self, recycling_advisor):
        """Test action timeframe calculation"""
        assert recycling_advisor._get_action_timeframe(UrgencyLevel.IMMEDIATE) == "2 hours"
        assert recycling_advisor._get_action_timeframe(UrgencyLevel.HIGH) == "24 hours"
        assert recycling_advisor._get_action_timeframe(UrgencyLevel.MEDIUM) == "3 days"
        assert recycling_advisor._get_action_timeframe(UrgencyLevel.LOW) == "1 week"
    
    def test_get_delay_consequences_hazardous(self, recycling_advisor):
        """Test delay consequences for hazardous materials"""
        consequences = recycling_advisor._get_delay_consequences("BATTERY", UrgencyLevel.IMMEDIATE)
        
        assert "Safety hazard" in consequences
        assert "Legal compliance" in consequences[1]
    
    def test_get_delay_consequences_organic(self, recycling_advisor):
        """Test delay consequences for organic waste"""
        consequences = recycling_advisor._get_delay_consequences("ORGANIC_WASTE", UrgencyLevel.HIGH)
        
        assert any("decomposition" in cons.lower() for cons in consequences)
        assert any("odor" in cons.lower() for cons in consequences)
    
    @pytest.mark.asyncio
    async def test_groq_service_error_handling(self, recycling_advisor, mock_groq_service):
        """Test error handling when Groq service fails"""
        mock_groq_service.generate_recycling_tips.side_effect = Exception("Groq API error")
        
        with pytest.raises(ValidationError) as exc_info:
            await recycling_advisor.get_recycling_recommendations(
                waste_type="PET_PLASTIC",
                weight=0.5
            )
        
        assert "Recommendation generation failed" in str(exc_info.value)
