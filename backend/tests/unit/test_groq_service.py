"""
Unit tests for Groq service
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from circularity_nexus.services.groq_service import GroqService
from circularity_nexus.core.exceptions import AIProcessingError


class TestGroqService:
    """Test cases for GroqService"""
    
    @pytest.fixture
    def mock_groq_client(self):
        """Mock Groq client"""
        with patch('circularity_nexus.services.groq_service.Groq') as mock_groq:
            mock_client = Mock()
            mock_groq.return_value = mock_client
            yield mock_client
    
    @pytest.fixture
    def groq_service(self, mock_groq_client):
        """GroqService instance with mocked client"""
        with patch('circularity_nexus.services.groq_service.settings') as mock_settings:
            mock_settings.GROQ_API_KEY = "test-key"
            mock_settings.GROQ_MODEL = "llama3-8b-8192"
            service = GroqService()
            service.client = mock_groq_client
            return service
    
    @pytest.mark.asyncio
    async def test_classify_waste_from_description_success(self, groq_service, mock_groq_client):
        """Test successful waste classification"""
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "detected_type": "PET",
            "confidence": 0.92,
            "estimated_weight_kg": 0.5,
            "recyclability_score": 0.9,
            "carbon_impact_kg": 0.75,
            "recommendations": ["Clean thoroughly", "Remove labels"]
        }
        '''
        mock_groq_client.chat.completions.create.return_value = mock_response
        
        # Test
        result = await groq_service.classify_waste_from_description(
            description="Clear plastic water bottle",
            estimated_weight=0.5
        )
        
        # Assertions
        assert result["detected_type"] == "PET"
        assert result["confidence"] == 0.92
        assert result["estimated_weight_kg"] == 0.5
        assert "Clean thoroughly" in result["recommendations"]
        mock_groq_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_classify_waste_json_parse_error(self, groq_service, mock_groq_client):
        """Test fallback when JSON parsing fails"""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON response"
        mock_groq_client.chat.completions.create.return_value = mock_response
        
        # Test
        result = await groq_service.classify_waste_from_description(
            description="Some waste",
            estimated_weight=1.0
        )
        
        # Should use fallback values
        assert result["detected_type"] == "MIXED_PLASTIC"
        assert result["confidence"] == 0.7
        assert result["estimated_weight_kg"] == 1.0
    
    @pytest.mark.asyncio
    async def test_generate_recycling_tips_success(self, groq_service, mock_groq_client):
        """Test successful recycling tips generation"""
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '["Rinse thoroughly", "Remove caps", "Sort by color"]'
        mock_groq_client.chat.completions.create.return_value = mock_response
        
        # Test
        tips = await groq_service.generate_recycling_tips("PET")
        
        # Assertions
        assert len(tips) == 3
        assert "Rinse thoroughly" in tips
        assert "Remove caps" in tips
    
    @pytest.mark.asyncio
    async def test_calculate_carbon_impact_success(self, groq_service, mock_groq_client):
        """Test successful carbon impact calculation"""
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "co2_saved_kg": 1.5,
            "energy_saved_kwh": 3.0,
            "water_saved_liters": 15.0,
            "explanation": "Recycling PET saves significant resources"
        }
        '''
        mock_groq_client.chat.completions.create.return_value = mock_response
        
        # Test
        result = await groq_service.calculate_carbon_impact("PET", 1.0)
        
        # Assertions
        assert result["co2_saved_kg"] == 1.5
        assert result["energy_saved_kwh"] == 3.0
        assert result["water_saved_liters"] == 15.0
        assert "explanation" in result
    
    @pytest.mark.asyncio
    async def test_groq_api_error_handling(self, groq_service, mock_groq_client):
        """Test error handling when Groq API fails"""
        # Mock API error
        mock_groq_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Test should raise AIProcessingError
        with pytest.raises(AIProcessingError) as exc_info:
            await groq_service.classify_waste_from_description(
                description="Test waste",
                estimated_weight=1.0
            )
        
        assert "Failed to classify waste" in str(exc_info.value)
    
    def test_groq_service_initialization_without_api_key(self):
        """Test GroqService initialization without API key"""
        with patch('circularity_nexus.services.groq_service.settings') as mock_settings:
            mock_settings.GROQ_API_KEY = None
            
            with pytest.raises(AIProcessingError) as exc_info:
                GroqService()
            
            assert "Groq API key not configured" in str(exc_info.value)
