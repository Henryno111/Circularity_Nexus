"""
Integration tests for API endpoints
"""

import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.integration
class TestHealthEndpoint:
    """Test health check endpoint"""
    
    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint returns success"""
        response = await async_client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


@pytest.mark.integration
class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    async def test_register_user_success(self, async_client: AsyncClient, sample_user_data):
        """Test successful user registration"""
        response = await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "message" in data
        assert "user_id" in data
        assert data["email"] == sample_user_data["email"]
    
    async def test_register_user_invalid_data(self, async_client: AsyncClient):
        """Test user registration with invalid data"""
        invalid_data = {
            "email": "invalid-email",  # Invalid email format
            "password": "123",  # Too short
            "full_name": "",  # Empty name
        }
        
        response = await async_client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_login_success(self, async_client: AsyncClient):
        """Test successful user login"""
        login_data = {
            "username": "demo@circularitynexus.io",
            "password": "demo123456"
        }
        
        response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user_id" in data
        assert "email" in data
    
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials"""
        login_data = {
            "username": "wrong@example.com",
            "password": "wrongpassword"
        }
        
        response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
    
    async def test_logout(self, async_client: AsyncClient):
        """Test user logout"""
        response = await async_client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data


@pytest.mark.integration
class TestWasteEndpoints:
    """Test waste management endpoints"""
    
    async def test_submit_waste_success(self, async_client: AsyncClient, sample_waste_submission):
        """Test successful waste submission"""
        response = await async_client.post("/api/v1/waste/submit", json=sample_waste_submission)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data["waste_type"] == sample_waste_submission["waste_type"]
        assert data["estimated_weight_kg"] == sample_waste_submission["estimated_weight_kg"]
        assert data["status"] == "PENDING"
    
    async def test_submit_waste_invalid_data(self, async_client: AsyncClient):
        """Test waste submission with invalid data"""
        invalid_data = {
            "waste_type": "INVALID_TYPE",
            "estimated_weight_kg": -1.0,  # Negative weight
            "location": {"latitude": 200.0, "longitude": 200.0}  # Invalid coordinates
        }
        
        response = await async_client.post("/api/v1/waste/submit", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_get_user_submissions(self, async_client: AsyncClient):
        """Test getting user's waste submissions"""
        response = await async_client.get("/api/v1/waste/submissions")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_specific_submission(self, async_client: AsyncClient):
        """Test getting specific waste submission"""
        submission_id = 1
        response = await async_client.get(f"/api/v1/waste/submissions/{submission_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == submission_id
    
    async def test_get_waste_types(self, async_client: AsyncClient):
        """Test getting supported waste types"""
        response = await async_client.get("/api/v1/waste/types")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure of waste type data
        waste_type = data[0]
        assert "type" in waste_type
        assert "name" in waste_type
        assert "token_rate" in waste_type
        assert "carbon_factor" in waste_type


@pytest.mark.integration
class TestTokenEndpoints:
    """Test token management endpoints"""
    
    async def test_get_token_balance(self, async_client: AsyncClient):
        """Test getting user's token balance"""
        response = await async_client.get("/api/v1/tokens/balance")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        if data:  # If there are tokens
            token = data[0]
            assert "token_type" in token
            assert "balance" in token
            assert "value_usd" in token
    
    async def test_mint_tokens(self, async_client: AsyncClient):
        """Test minting tokens for validated submission"""
        submission_id = 1
        response = await async_client.post(f"/api/v1/tokens/mint/{submission_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "submission_id" in data
        assert "tokens_minted" in data
        assert "token_type" in data
        assert "transaction_hash" in data


@pytest.mark.integration
@pytest.mark.ai
class TestAIEndpoints:
    """Test AI processing endpoints"""
    
    async def test_validate_waste(self, async_client: AsyncClient, mock_groq_service):
        """Test AI validation of waste submission"""
        submission_id = 1
        response = await async_client.post(f"/api/v1/ai/validate/{submission_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "submission_id" in data
        assert "ai_confidence" in data
        assert "detected_type" in data
        assert "estimated_weight" in data
        assert "validation_status" in data
    
    async def test_analyze_waste(self, async_client: AsyncClient, mock_groq_service):
        """Test comprehensive waste analysis"""
        analysis_request = {
            "description": "Clear plastic water bottle",
            "estimated_weight_kg": 0.5,
            "location": {"latitude": -1.286389, "longitude": 36.817223}
        }
        
        response = await async_client.post("/api/v1/ai/analyze", json=analysis_request)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "detected_type" in data
        assert "confidence" in data
        assert "recyclability_score" in data
        assert "carbon_impact_kg" in data
        assert "recommendations" in data
    
    async def test_get_recycling_tips(self, async_client: AsyncClient, mock_groq_service):
        """Test getting recycling tips for waste type"""
        waste_type = "PET"
        response = await async_client.get(f"/api/v1/ai/tips/{waste_type}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "tips" in data
        assert isinstance(data["tips"], list)
        assert len(data["tips"]) > 0
    
    async def test_calculate_carbon_impact(self, async_client: AsyncClient, mock_groq_service):
        """Test carbon impact calculation"""
        params = {"waste_type": "PET", "weight_kg": 1.0}
        response = await async_client.post("/api/v1/ai/carbon-impact", params=params)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "co2_saved_kg" in data
        assert "energy_saved_kwh" in data
        assert "water_saved_liters" in data
        assert "explanation" in data


@pytest.mark.integration
class TestDeFiEndpoints:
    """Test DeFi and staking endpoints"""
    
    async def test_stake_tokens(self, async_client: AsyncClient):
        """Test staking tokens in vault"""
        stake_request = {
            "token_type": "PET",
            "amount": 1000.0,
            "vault_type": "ESG_CORPORATE"
        }
        
        response = await async_client.post("/api/v1/defi/stake", json=stake_request)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "token_type" in data
        assert "amount" in data
        assert "vault_type" in data
        assert "apy" in data
        assert "transaction_hash" in data
    
    async def test_get_available_vaults(self, async_client: AsyncClient):
        """Test getting available staking vaults"""
        response = await async_client.get("/api/v1/defi/vaults")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        vault = data[0]
        assert "vault_type" in vault
        assert "name" in vault
        assert "apy" in vault
        assert "min_stake" in vault
        assert "total_staked" in vault


@pytest.mark.integration
class TestCarbonEndpoints:
    """Test carbon credit endpoints"""
    
    async def test_convert_to_carbon(self, async_client: AsyncClient):
        """Test converting waste tokens to carbon credits"""
        conversion_request = {
            "waste_token_amount": 1000.0,
            "waste_type": "PET"
        }
        
        response = await async_client.post("/api/v1/carbon/convert", json=conversion_request)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "waste_tokens_used" in data
        assert "carbon_credits_generated" in data
        assert "co2e_kg" in data
        assert "transaction_hash" in data
    
    async def test_get_carbon_balance(self, async_client: AsyncClient):
        """Test getting carbon credit balance"""
        response = await async_client.get("/api/v1/carbon/balance")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_carbon_credits" in data
        assert "co2e_kg" in data
        assert "value_usd" in data
        assert "credits_by_source" in data


@pytest.mark.integration
class TestUserEndpoints:
    """Test user management endpoints"""
    
    async def test_get_user_profile(self, async_client: AsyncClient):
        """Test getting user profile"""
        response = await async_client.get("/api/v1/users/profile")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "full_name" in data
        assert "total_waste_kg" in data
        assert "total_tokens_earned" in data
        assert "carbon_credits_earned" in data


@pytest.mark.integration
class TestSmartBinEndpoints:
    """Test smart bin endpoints"""
    
    async def test_get_smart_bin_data(self, async_client: AsyncClient):
        """Test getting smart bin sensor data"""
        bin_id = "DEMO-BIN-001"
        response = await async_client.get(f"/api/v1/smart-bins/{bin_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "bin_id" in data
        assert "location" in data
        assert "current_weight_kg" in data
        assert "capacity_kg" in data
        assert "fill_percentage" in data
        assert "status" in data
        assert "battery_level" in data
    
    async def test_get_nearby_bins(self, async_client: AsyncClient):
        """Test getting nearby smart bins"""
        response = await async_client.get("/api/v1/smart-bins/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        if data:  # If there are bins
            bin_data = data[0]
            assert "bin_id" in bin_data
            assert "location" in bin_data
            assert "fill_percentage" in bin_data
            assert "distance_m" in bin_data


@pytest.mark.integration
class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    async def test_openapi_schema(self, async_client: AsyncClient):
        """Test OpenAPI schema endpoint"""
        response = await async_client.get("/api/v1/openapi.json")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
    
    async def test_docs_endpoint(self, async_client: AsyncClient):
        """Test Swagger UI docs endpoint"""
        response = await async_client.get("/api/v1/docs")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
    
    async def test_redoc_endpoint(self, async_client: AsyncClient):
        """Test ReDoc documentation endpoint"""
        response = await async_client.get("/api/v1/redoc")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
