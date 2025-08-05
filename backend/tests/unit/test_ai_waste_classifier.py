"""
Unit tests for AI Waste Classifier
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from circularity_nexus.ai.waste_classifier import WasteClassifier, WasteCategory, QualityGrade
from circularity_nexus.core.exceptions import ValidationError


class TestWasteClassifier:
    """Test cases for WasteClassifier"""
    
    @pytest.fixture
    def mock_groq_service(self):
        """Mock GroqService"""
        with patch('circularity_nexus.ai.waste_classifier.GroqService') as mock_groq:
            mock_service = Mock()
            mock_groq.return_value = mock_service
            yield mock_service
    
    @pytest.fixture
    def waste_classifier(self, mock_groq_service):
        """WasteClassifier instance with mocked dependencies"""
        classifier = WasteClassifier()
        classifier.groq_service = mock_groq_service
        return classifier
    
    @pytest.mark.asyncio
    async def test_classify_waste_item_success(self, waste_classifier, mock_groq_service):
        """Test successful waste classification"""
        # Mock Groq response
        mock_groq_service.classify_waste.return_value = {
            "waste_type": "PET_PLASTIC",
            "category": "PLASTIC",
            "quality": "GOOD",
            "recyclability": 85,
            "confidence": 92,
            "estimated_value": 8,
            "contamination_level": "LOW",
            "processing_requirements": ["Clean", "Remove labels"]
        }
        
        # Test classification
        result = await waste_classifier.classify_waste_item(
            image_description="Clear plastic water bottle with label",
            weight=0.03,
            user_description="Empty water bottle"
        )
        
        # Assertions
        assert result["waste_type"] == "PET_PLASTIC"
        assert result["category"] == "PLASTIC"
        assert result["quality"] == "GOOD"
        assert result["confidence"] == 92
        assert result["token_value_cents"] > 0
        assert "processing_steps" in result
        assert "classification_timestamp" in result
        
        # Verify Groq service was called
        mock_groq_service.classify_waste.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_classify_waste_item_invalid_description(self, waste_classifier):
        """Test classification with invalid description"""
        with pytest.raises(ValidationError) as exc_info:
            await waste_classifier.classify_waste_item(
                image_description="short",  # Too short
                weight=0.1
            )
        
        assert "at least 10 characters" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_batch_classify_success(self, waste_classifier, mock_groq_service):
        """Test batch classification"""
        # Mock responses for different items
        mock_groq_service.classify_waste.side_effect = [
            {
                "waste_type": "ALUMINUM_CAN",
                "category": "METAL",
                "quality": "EXCELLENT",
                "recyclability": 95,
                "confidence": 98,
                "estimated_value": 120,
                "contamination_level": "NONE",
                "processing_requirements": ["Clean"]
            },
            {
                "waste_type": "CARDBOARD",
                "category": "PAPER",
                "quality": "FAIR",
                "recyclability": 70,
                "confidence": 85,
                "estimated_value": 3,
                "contamination_level": "MEDIUM",
                "processing_requirements": ["Flatten", "Remove tape"]
            }
        ]
        
        items = [
            {
                "image_description": "Aluminum soda can, empty and clean",
                "weight": 0.015
            },
            {
                "image_description": "Cardboard box with some tape",
                "weight": 0.2
            }
        ]
        
        results = await waste_classifier.batch_classify(items)
        
        assert len(results) == 2
        assert results[0]["waste_type"] == "ALUMINUM_CAN"
        assert results[1]["waste_type"] == "CARDBOARD"
        assert mock_groq_service.classify_waste.call_count == 2
    
    def test_get_supported_materials(self, waste_classifier):
        """Test getting supported materials"""
        materials = waste_classifier.get_supported_materials()
        
        assert isinstance(materials, list)
        assert len(materials) > 0
        
        # Check structure of first material
        material = materials[0]
        assert "material_type" in material
        assert "category" in material
        assert "base_value_per_kg" in material
        assert "recyclability_score" in material
    
    def test_calculate_token_value_with_weight(self, waste_classifier):
        """Test token value calculation with weight"""
        classification = {
            "base_value_per_kg": 8.0,
            "quality": "GOOD",
            "recyclability": 85
        }
        
        value = waste_classifier._calculate_token_value(classification, 0.5)
        
        # Expected: 8.0 * 0.5 * 0.8 (GOOD quality) * 0.85 (recyclability) = 2.72
        assert value == pytest.approx(2.72, rel=0.01)
    
    def test_calculate_token_value_without_weight(self, waste_classifier):
        """Test token value calculation without weight (estimated)"""
        classification = {
            "waste_type": "PET_BOTTLE",
            "base_value_per_kg": 8.0,
            "quality": "EXCELLENT",
            "recyclability": 90
        }
        
        value = waste_classifier._calculate_token_value(classification, None)
        
        # Should use estimated weight for PET_BOTTLE (0.03kg)
        # Expected: 8.0 * 0.03 * 1.0 * 0.9 = 0.216
        assert value == pytest.approx(0.22, rel=0.01)  # Rounded to 2 decimals
    
    def test_get_quality_multiplier(self, waste_classifier):
        """Test quality multiplier calculation"""
        assert waste_classifier._get_quality_multiplier("EXCELLENT") == 1.0
        assert waste_classifier._get_quality_multiplier("GOOD") == 0.8
        assert waste_classifier._get_quality_multiplier("FAIR") == 0.6
        assert waste_classifier._get_quality_multiplier("POOR") == 0.3
        assert waste_classifier._get_quality_multiplier("UNUSABLE") == 0.1
        assert waste_classifier._get_quality_multiplier("UNKNOWN") == 0.6  # Default
    
    def test_estimate_weight(self, waste_classifier):
        """Test weight estimation for different waste types"""
        assert waste_classifier._estimate_weight("PET_BOTTLE") == 0.03
        assert waste_classifier._estimate_weight("ALUMINUM_CAN") == 0.015
        assert waste_classifier._estimate_weight("UNKNOWN_TYPE") == 0.1  # Default
    
    def test_generate_processing_steps_plastic(self, waste_classifier):
        """Test processing steps generation for plastic"""
        classification = {
            "waste_type": "PET_PLASTIC",
            "quality": "GOOD",
            "contamination_level": "MEDIUM"
        }
        
        steps = waste_classifier._generate_processing_steps(classification)
        
        assert isinstance(steps, list)
        assert len(steps) > 0
        assert any("labels" in step.lower() for step in steps)
        assert any("plastic type" in step.lower() for step in steps)
    
    def test_generate_processing_steps_metal(self, waste_classifier):
        """Test processing steps generation for metal"""
        classification = {
            "waste_type": "ALUMINUM_CAN",
            "quality": "EXCELLENT",
            "contamination_level": "LOW"
        }
        
        steps = waste_classifier._generate_processing_steps(classification)
        
        assert isinstance(steps, list)
        assert any("metal" in step.lower() for step in steps)
    
    def test_analyze_confidence_factors(self, waste_classifier):
        """Test confidence factors analysis"""
        classification = {
            "confidence": 85,
            "contamination_level": "LOW",
            "base_value_per_kg": 8.0
        }
        context = "Clear plastic bottle with detailed description and good lighting"
        
        factors = waste_classifier._analyze_confidence_factors(classification, context)
        
        assert "image_quality" in factors
        assert "material_clarity" in factors
        assert "contamination_impact" in factors
        assert "database_match" in factors
        assert factors["image_quality"] == "good"  # Long context
        assert factors["material_clarity"] == "high"  # High confidence
    
    @pytest.mark.asyncio
    async def test_groq_service_error_handling(self, waste_classifier, mock_groq_service):
        """Test error handling when Groq service fails"""
        mock_groq_service.classify_waste.side_effect = Exception("Groq API error")
        
        with pytest.raises(ValidationError) as exc_info:
            await waste_classifier.classify_waste_item(
                image_description="Test description for error handling",
                weight=0.1
            )
        
        assert "Classification failed" in str(exc_info.value)
    
    def test_enhance_with_database(self, waste_classifier):
        """Test enhancement with material database"""
        ai_result = {
            "waste_type": "PET_PLASTIC",
            "confidence": 90
        }
        
        enhanced = waste_classifier._enhance_with_database(ai_result)
        
        assert "base_value_per_kg" in enhanced
        assert "processing_complexity" in enhanced
        assert "market_demand" in enhanced
        assert enhanced["base_value_per_kg"] == 8.0  # From database
    
    def test_enhance_with_database_unknown_type(self, waste_classifier):
        """Test enhancement with unknown waste type"""
        ai_result = {
            "waste_type": "UNKNOWN_MATERIAL",
            "confidence": 50
        }
        
        enhanced = waste_classifier._enhance_with_database(ai_result)
        
        # Should not add database fields for unknown types
        assert "base_value_per_kg" not in enhanced
        assert enhanced["confidence"] == 50  # Original data preserved
