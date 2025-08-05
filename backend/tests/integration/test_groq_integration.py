"""
Integration tests for Groq AI service
"""

import pytest
from unittest.mock import patch, Mock
from circularity_nexus.services.groq_service import GroqService
from circularity_nexus.core.exceptions import AIProcessingError


@pytest.mark.integration
@pytest.mark.ai
class TestGroqIntegration:
    """Test Groq AI service integration"""
    
    @pytest.fixture
    def groq_service_with_real_client(self):
        """Create GroqService with real client (mocked for testing)"""
        with patch('circularity_nexus.services.groq_service.Groq') as mock_groq:
            with patch('circularity_nexus.services.groq_service.settings') as mock_settings:
                mock_settings.GROQ_API_KEY = "test-api-key"
                mock_settings.GROQ_MODEL = "llama3-8b-8192"
                
                # Create service instance
                service = GroqService()
                service.client = mock_groq.return_value
                
                yield service, mock_groq.return_value
    
    async def test_waste_classification_integration(self, groq_service_with_real_client):
        """Test end-to-end waste classification"""
        service, mock_client = groq_service_with_real_client
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "detected_type": "PET",
            "confidence": 0.94,
            "estimated_weight_kg": 0.5,
            "recyclability_score": 0.92,
            "carbon_impact_kg": 0.75,
            "recommendations": [
                "Remove cap and label",
                "Rinse thoroughly",
                "Crush to save space"
            ]
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test classification
        result = await service.classify_waste_from_description(
            description="Clear plastic water bottle with blue cap",
            estimated_weight=0.5,
            location={"latitude": -1.286389, "longitude": 36.817223}
        )
        
        # Verify results
        assert result["detected_type"] == "PET"
        assert result["confidence"] == 0.94
        assert result["estimated_weight_kg"] == 0.5
        assert result["recyclability_score"] == 0.92
        assert len(result["recommendations"]) == 3
        
        # Verify API was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "llama3-8b-8192"
        assert call_args[1]["temperature"] == 0.1
        assert len(call_args[1]["messages"]) == 2
    
    async def test_recycling_tips_integration(self, groq_service_with_real_client):
        """Test recycling tips generation integration"""
        service, mock_client = groq_service_with_real_client
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        [
            "Clean thoroughly before recycling",
            "Remove all labels and adhesive",
            "Separate caps from bottles",
            "Check local recycling guidelines",
            "Avoid crushing lengthwise"
        ]
        '''
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test tips generation
        tips = await service.generate_recycling_tips("PET")
        
        # Verify results
        assert len(tips) == 5
        assert "Clean thoroughly before recycling" in tips
        assert "Remove all labels and adhesive" in tips
        
        # Verify API call
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert "PET" in call_args[1]["messages"][0]["content"]
    
    async def test_carbon_impact_calculation_integration(self, groq_service_with_real_client):
        """Test carbon impact calculation integration"""
        service, mock_client = groq_service_with_real_client
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "co2_saved_kg": 1.8,
            "energy_saved_kwh": 3.6,
            "water_saved_liters": 18.0,
            "explanation": "Recycling 1.2kg of PET plastic saves approximately 1.8kg of CO2 emissions compared to producing new plastic from virgin materials. This also saves 3.6 kWh of energy and 18 liters of water."
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test carbon impact calculation
        result = await service.calculate_carbon_impact("PET", 1.2)
        
        # Verify results
        assert result["co2_saved_kg"] == 1.8
        assert result["energy_saved_kwh"] == 3.6
        assert result["water_saved_liters"] == 18.0
        assert "explanation" in result
        assert "1.2kg of PET" in result["explanation"]
        
        # Verify API call
        mock_client.chat.completions.create.assert_called_once()
    
    async def test_api_error_handling_integration(self, groq_service_with_real_client):
        """Test API error handling in integration"""
        service, mock_client = groq_service_with_real_client
        
        # Mock API error
        mock_client.chat.completions.create.side_effect = Exception("API rate limit exceeded")
        
        # Test error handling
        with pytest.raises(AIProcessingError) as exc_info:
            await service.classify_waste_from_description(
                description="Test waste",
                estimated_weight=1.0
            )
        
        assert "Failed to classify waste" in str(exc_info.value)
        assert "API rate limit exceeded" in str(exc_info.value)
    
    async def test_invalid_json_response_handling(self, groq_service_with_real_client):
        """Test handling of invalid JSON responses"""
        service, mock_client = groq_service_with_real_client
        
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test fallback behavior
        result = await service.classify_waste_from_description(
            description="Plastic bottle",
            estimated_weight=0.5
        )
        
        # Should use fallback values
        assert result["detected_type"] == "MIXED_PLASTIC"
        assert result["confidence"] == 0.7
        assert result["estimated_weight_kg"] == 0.5
        assert isinstance(result["recommendations"], list)
    
    async def test_multiple_waste_types_classification(self, groq_service_with_real_client):
        """Test classification of different waste types"""
        service, mock_client = groq_service_with_real_client
        
        waste_samples = [
            {
                "description": "Aluminum soda can",
                "expected_type": "ALUMINUM",
                "weight": 0.015
            },
            {
                "description": "Glass wine bottle",
                "expected_type": "GLASS",
                "weight": 0.5
            },
            {
                "description": "Cardboard box",
                "expected_type": "CARDBOARD",
                "weight": 0.2
            },
            {
                "description": "Old smartphone",
                "expected_type": "EWASTE",
                "weight": 0.15
            }
        ]
        
        for sample in waste_samples:
            # Mock response for each waste type
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = f'''
            {{
                "detected_type": "{sample['expected_type']}",
                "confidence": 0.89,
                "estimated_weight_kg": {sample['weight']},
                "recyclability_score": 0.85,
                "carbon_impact_kg": {sample['weight'] * 1.5},
                "recommendations": ["Clean before recycling", "Check local guidelines"]
            }}
            '''
            mock_client.chat.completions.create.return_value = mock_response
            
            # Test classification
            result = await service.classify_waste_from_description(
                description=sample["description"],
                estimated_weight=sample["weight"]
            )
            
            # Verify correct classification
            assert result["detected_type"] == sample["expected_type"]
            assert result["estimated_weight_kg"] == sample["weight"]
            assert result["confidence"] > 0.8
    
    async def test_location_context_integration(self, groq_service_with_real_client):
        """Test location context in waste classification"""
        service, mock_client = groq_service_with_real_client
        
        # Mock response that considers location
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "detected_type": "PET",
            "confidence": 0.91,
            "estimated_weight_kg": 0.5,
            "recyclability_score": 0.88,
            "carbon_impact_kg": 0.75,
            "recommendations": [
                "Kenya has good PET recycling facilities",
                "Clean thoroughly in water-scarce regions",
                "Local recycling centers accept PET bottles"
            ]
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test with location context
        result = await service.classify_waste_from_description(
            description="Plastic water bottle",
            estimated_weight=0.5,
            location={"latitude": -1.286389, "longitude": 36.817223}  # Nairobi, Kenya
        )
        
        # Verify location-aware recommendations
        assert any("Kenya" in rec for rec in result["recommendations"])
        
        # Verify location was included in API call
        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]["messages"][1]["content"]
        assert "latitude" in user_message
        assert "longitude" in user_message
    
    async def test_batch_processing_simulation(self, groq_service_with_real_client):
        """Test simulated batch processing of multiple waste items"""
        service, mock_client = groq_service_with_real_client
        
        # Simulate processing multiple items
        waste_items = [
            "Plastic water bottle",
            "Aluminum can",
            "Glass jar",
            "Cardboard box",
            "Paper newspaper"
        ]
        
        results = []
        
        for i, item in enumerate(waste_items):
            # Mock different response for each item
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = f'''
            {{
                "detected_type": "TYPE_{i}",
                "confidence": 0.9,
                "estimated_weight_kg": {0.1 * (i + 1)},
                "recyclability_score": 0.85,
                "carbon_impact_kg": {0.15 * (i + 1)},
                "recommendations": ["Recommendation for item {i}"]
            }}
            '''
            mock_client.chat.completions.create.return_value = mock_response
            
            result = await service.classify_waste_from_description(
                description=item,
                estimated_weight=0.1 * (i + 1)
            )
            results.append(result)
        
        # Verify all items were processed
        assert len(results) == 5
        assert all(result["confidence"] == 0.9 for result in results)
        assert mock_client.chat.completions.create.call_count == 5
    
    async def test_service_initialization_without_groq(self):
        """Test service behavior when Groq is not available"""
        with patch('circularity_nexus.services.groq_service.Groq', None):
            with pytest.raises(AIProcessingError) as exc_info:
                GroqService()
            
            assert "Groq library not installed" in str(exc_info.value)
    
    async def test_service_initialization_without_api_key(self):
        """Test service behavior without API key"""
        with patch('circularity_nexus.services.groq_service.settings') as mock_settings:
            mock_settings.GROQ_API_KEY = None
            
            with pytest.raises(AIProcessingError) as exc_info:
                GroqService()
            
            assert "Groq API key not configured" in str(exc_info.value)
