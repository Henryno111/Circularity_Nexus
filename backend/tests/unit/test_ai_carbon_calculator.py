"""
Unit tests for AI Carbon Calculator
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from circularity_nexus.ai.carbon_calculator import CarbonCalculator, RecyclingMethod
from circularity_nexus.core.exceptions import ValidationError


class TestCarbonCalculator:
    """Test cases for CarbonCalculator"""
    
    @pytest.fixture
    def mock_groq_service(self):
        """Mock GroqService"""
        with patch('circularity_nexus.ai.carbon_calculator.GroqService') as mock_groq:
            mock_service = Mock()
            mock_groq.return_value = mock_service
            yield mock_service
    
    @pytest.fixture
    def carbon_calculator(self, mock_groq_service):
        """CarbonCalculator instance with mocked dependencies"""
        calculator = CarbonCalculator()
        calculator.groq_service = mock_groq_service
        return calculator
    
    @pytest.mark.asyncio
    async def test_calculate_carbon_impact_success(self, carbon_calculator, mock_groq_service):
        """Test successful carbon impact calculation"""
        # Mock Groq response
        mock_groq_service.calculate_carbon_impact.return_value = {
            "co2_saved_kg": 2.5,
            "co2_equivalent_trees": 0.12,
            "carbon_credits_earned": 0.0025,
            "energy_saved_kwh": 5.5,
            "water_saved_liters": 25.0,
            "landfill_diverted_kg": 1.0,
            "environmental_impact_score": 85
        }
        
        # Test calculation
        result = await carbon_calculator.calculate_carbon_impact(
            waste_type="PET_PLASTIC",
            weight=1.0,
            recycling_method="mechanical",
            transportation_km=15.0,
            energy_source="renewable"
        )
        
        # Assertions
        assert "detailed_analysis" in result
        assert "methodology" in result
        assert result["detailed_analysis"]["net_co2_saved_kg"] > 0
        assert "baseline_impact" in result["detailed_analysis"]
        assert "recycling_impact" in result["detailed_analysis"]
        assert "transportation_impact" in result["detailed_analysis"]
        assert "carbon_credits_generated" in result["detailed_analysis"]
        
        # Verify Groq service was called
        mock_groq_service.calculate_carbon_impact.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_calculate_carbon_impact_invalid_weight(self, carbon_calculator):
        """Test calculation with invalid weight"""
        with pytest.raises(ValidationError) as exc_info:
            await carbon_calculator.calculate_carbon_impact(
                waste_type="PET_PLASTIC",
                weight=0,  # Invalid weight
                recycling_method="mechanical"
            )
        
        assert "Weight must be positive" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_calculate_portfolio_impact(self, carbon_calculator, mock_groq_service):
        """Test portfolio carbon impact calculation"""
        # Mock responses for different items
        mock_groq_service.calculate_carbon_impact.side_effect = [
            {
                "co2_saved_kg": 2.0,
                "carbon_credits_earned": 0.002
            },
            {
                "co2_saved_kg": 8.0,
                "carbon_credits_earned": 0.008
            }
        ]
        
        # Mock detailed analysis for each item
        with patch.object(carbon_calculator, '_calculate_baseline_impact') as mock_baseline, \
             patch.object(carbon_calculator, '_calculate_recycling_impact') as mock_recycling, \
             patch.object(carbon_calculator, '_calculate_transportation_impact') as mock_transport, \
             patch.object(carbon_calculator, '_calculate_carbon_credits') as mock_credits:
            
            mock_baseline.return_value = {"landfill_co2": 3.0}
            mock_recycling.return_value = {"processing_co2": 0.5}
            mock_transport.return_value = {"transport_co2": 0.1}
            mock_credits.return_value = {"total_credits": 0.005}
            
            waste_items = [
                {
                    "waste_type": "PET_PLASTIC",
                    "weight": 1.0,
                    "recycling_method": "mechanical"
                },
                {
                    "waste_type": "ALUMINUM",
                    "weight": 0.5,
                    "recycling_method": "mechanical"
                }
            ]
            
            result = await carbon_calculator.calculate_portfolio_impact(waste_items)
            
            # Assertions
            assert "portfolio_summary" in result
            assert "item_details" in result
            assert result["portfolio_summary"]["total_items"] == 2
            assert result["portfolio_summary"]["total_weight_kg"] == 1.5
            assert result["portfolio_summary"]["total_co2_saved_kg"] > 0
            assert result["portfolio_summary"]["equivalent_trees_planted"] > 0
    
    def test_calculate_baseline_impact_plastic(self, carbon_calculator):
        """Test baseline impact calculation for plastic"""
        result = carbon_calculator._calculate_baseline_impact("PET_PLASTIC", 1.0)
        
        assert "landfill_co2" in result
        assert "methane_co2_equivalent" in result
        assert "total_baseline_co2" in result
        assert "land_use_impact" in result
        assert result["landfill_co2"] == 0.8  # From emission factors
        assert result["methane_co2_equivalent"] == 2.5  # 0.1 * 25 (GWP)
    
    def test_calculate_baseline_impact_metal(self, carbon_calculator):
        """Test baseline impact calculation for metal"""
        result = carbon_calculator._calculate_baseline_impact("ALUMINUM", 1.0)
        
        assert result["landfill_co2"] == 0.3  # From emission factors
        assert result["methane_co2_equivalent"] == 0.5  # 0.02 * 25
    
    def test_calculate_recycling_impact_renewable_energy(self, carbon_calculator):
        """Test recycling impact with renewable energy"""
        result = carbon_calculator._calculate_recycling_impact(
            "PET_PLASTIC", 1.0, "mechanical", "renewable"
        )
        
        assert "processing_co2" in result
        assert "virgin_material_offset_co2" in result
        assert "material_recovery_rate" in result
        assert result["processing_co2"] < 1.0  # Low emissions with renewable energy
    
    def test_calculate_recycling_impact_coal_energy(self, carbon_calculator):
        """Test recycling impact with coal energy"""
        result = carbon_calculator._calculate_recycling_impact(
            "PET_PLASTIC", 1.0, "mechanical", "coal"
        )
        
        assert result["processing_co2"] > 1.0  # Higher emissions with coal
    
    def test_calculate_transportation_impact(self, carbon_calculator):
        """Test transportation impact calculation"""
        result = carbon_calculator._calculate_transportation_impact(1.0, 20.0)
        
        assert "transport_co2" in result
        assert "distance_km" in result
        assert "fuel_consumption_liters" in result
        assert result["distance_km"] == 20.0
        assert result["transport_co2"] == pytest.approx(0.0024, rel=0.01)  # 1.0 * 20.0 * 0.00012
    
    def test_calculate_carbon_credits_electronic(self, carbon_calculator):
        """Test carbon credits calculation for electronic waste"""
        result = carbon_calculator._calculate_carbon_credits(5.0, "ELECTRONIC")
        
        assert "base_credits" in result
        assert "additionality_multiplier" in result
        assert "net_credits" in result
        assert "credit_value_usd" in result
        assert result["additionality_multiplier"] == 1.5  # High multiplier for electronics
    
    def test_calculate_carbon_credits_organic(self, carbon_calculator):
        """Test carbon credits calculation for organic waste"""
        result = carbon_calculator._calculate_carbon_credits(5.0, "ORGANIC")
        
        assert result["additionality_multiplier"] == 0.8  # Lower multiplier for organic
    
    def test_calculate_co_benefits(self, carbon_calculator):
        """Test co-benefits calculation"""
        result = carbon_calculator._calculate_co_benefits("PET_PLASTIC", 2.0, "mechanical")
        
        assert "water_saved_liters" in result
        assert "energy_saved_kwh" in result
        assert "air_pollution_reduced_kg" in result
        assert "jobs_supported" in result
        assert "economic_value_usd" in result
        assert result["water_saved_liters"] == 50.0  # 2.0 * 25.0
    
    def test_normalize_waste_type(self, carbon_calculator):
        """Test waste type normalization"""
        assert carbon_calculator._normalize_waste_type("PET_PLASTIC") == "PLASTIC"
        assert carbon_calculator._normalize_waste_type("ALUMINUM_CAN") == "METAL"
        assert carbon_calculator._normalize_waste_type("CARDBOARD_BOX") == "PAPER"
        assert carbon_calculator._normalize_waste_type("GLASS_BOTTLE") == "GLASS"
        assert carbon_calculator._normalize_waste_type("SMARTPHONE") == "ELECTRONIC"
        assert carbon_calculator._normalize_waste_type("FOOD_WASTE") == "ORGANIC"
        assert carbon_calculator._normalize_waste_type("UNKNOWN_MATERIAL") == "DEFAULT"
    
    def test_get_material_category(self, carbon_calculator):
        """Test material category extraction"""
        assert carbon_calculator._get_material_category("PET_PLASTIC") == "PLASTIC"
        assert carbon_calculator._get_material_category("UNKNOWN") == "MIXED"
    
    def test_get_emission_factors(self, carbon_calculator):
        """Test emission factors retrieval"""
        factors = carbon_calculator.get_emission_factors()
        
        assert isinstance(factors, dict)
        assert "PLASTIC" in factors
        assert "METAL" in factors
        assert "DEFAULT" in factors
        
        # Check plastic factors structure
        plastic_factors = factors["PLASTIC"]
        assert "landfill_co2_per_kg" in plastic_factors
        assert "processing_energy_kwh_per_kg" in plastic_factors
        assert "virgin_material_co2_per_kg" in plastic_factors
    
    def test_load_recycling_efficiency(self, carbon_calculator):
        """Test recycling efficiency factors"""
        efficiency = carbon_calculator._load_recycling_efficiency()
        
        assert isinstance(efficiency, dict)
        assert efficiency["mechanical"] == 0.80
        assert efficiency["chemical"] == 0.90
        assert efficiency["remanufacturing"] == 0.95
    
    @pytest.mark.asyncio
    async def test_groq_service_error_handling(self, carbon_calculator, mock_groq_service):
        """Test error handling when Groq service fails"""
        mock_groq_service.calculate_carbon_impact.side_effect = Exception("Groq API error")
        
        with pytest.raises(ValidationError) as exc_info:
            await carbon_calculator.calculate_carbon_impact(
                waste_type="PET_PLASTIC",
                weight=1.0
            )
        
        assert "Carbon calculation failed" in str(exc_info.value)
    
    def test_emission_factors_completeness(self, carbon_calculator):
        """Test that all required emission factors are present"""
        factors = carbon_calculator.emission_factors
        
        required_materials = ["PLASTIC", "METAL", "PAPER", "GLASS", "ELECTRONIC", "ORGANIC", "DEFAULT"]
        for material in required_materials:
            assert material in factors
            
            material_factors = factors[material]
            required_factors = [
                "landfill_co2_per_kg", "methane_emission_per_kg", "processing_energy_kwh_per_kg",
                "recovery_rate", "virgin_material_co2_per_kg", "water_saved_per_kg"
            ]
            for factor in required_factors:
                assert factor in material_factors
                assert isinstance(material_factors[factor], (int, float))
                assert material_factors[factor] >= 0
