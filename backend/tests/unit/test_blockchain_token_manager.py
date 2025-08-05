"""
Unit tests for Blockchain Token Manager
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from circularity_nexus.blockchain.token_manager import TokenManager, TokenCategory, WasteTokenType
from circularity_nexus.core.exceptions import BlockchainError, ValidationError


class TestTokenManager:
    """Test cases for TokenManager"""
    
    @pytest.fixture
    def mock_hts_service(self):
        """Mock HTSService"""
        with patch('circularity_nexus.blockchain.token_manager.HTSService') as mock_hts:
            mock_service = Mock()
            mock_hts.return_value = mock_service
            yield mock_service
    
    @pytest.fixture
    def mock_hedera_client(self):
        """Mock HederaClient"""
        with patch('circularity_nexus.blockchain.token_manager.HederaClient') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def token_manager(self, mock_hts_service, mock_hedera_client):
        """TokenManager instance with mocked dependencies"""
        manager = TokenManager()
        manager.hts_service = mock_hts_service
        manager.hedera_client = mock_hedera_client
        return manager
    
    @pytest.mark.asyncio
    async def test_create_waste_token_success(self, token_manager, mock_hts_service):
        """Test successful waste token creation"""
        # Mock HTS response
        mock_hts_service.create_fungible_token.return_value = {
            "token_id": "0.0.123456",
            "name": "PET Plastic Token (GLOBAL)",
            "symbol": "PET-GLOBAL",
            "decimals": 2,
            "initial_supply": 0,
            "treasury_account": "0.0.789012",
            "status": "success"
        }
        
        # Test token creation
        result = await token_manager.create_waste_token(
            waste_type=WasteTokenType.PET_PLASTIC,
            region="GLOBAL",
            max_supply=1000000
        )
        
        # Assertions
        assert result["token_id"] == "0.0.123456"
        assert result["category"] == TokenCategory.WASTE_TOKEN.value
        assert result["waste_type"] == WasteTokenType.PET_PLASTIC.value
        assert result["region"] == "GLOBAL"
        assert result["base_value_per_unit"] == 0.08  # From config
        assert "created_at" in result
        
        # Verify HTS service was called correctly
        mock_hts_service.create_fungible_token.assert_called_once()
        call_args = mock_hts_service.create_fungible_token.call_args
        assert call_args[1]["symbol"] == "PET-GLOBAL"
        assert call_args[1]["decimals"] == 2
        assert call_args[1]["max_supply"] == 1000000
    
    @pytest.mark.asyncio
    async def test_create_carbon_credit_token_success(self, token_manager, mock_hts_service):
        """Test successful carbon credit token creation"""
        # Mock HTS response
        mock_hts_service.create_fungible_token.return_value = {
            "token_id": "0.0.654321",
            "name": "Carbon Credit 2024 (GLOBAL)",
            "symbol": "CC2024-GLOBAL",
            "decimals": 3,
            "initial_supply": 0,
            "treasury_account": "0.0.789012",
            "status": "success"
        }
        
        # Test token creation
        result = await token_manager.create_carbon_credit_token(
            vintage_year=2024,
            project_type="WASTE_RECYCLING",
            region="GLOBAL",
            max_supply=500000
        )
        
        # Assertions
        assert result["token_id"] == "0.0.654321"
        assert result["category"] == TokenCategory.CARBON_CREDIT.value
        assert result["vintage_year"] == 2024
        assert result["project_type"] == "WASTE_RECYCLING"
        assert result["verification_standard"] == "VCS"
        
        # Verify HTS service was called correctly
        mock_hts_service.create_fungible_token.assert_called_once()
        call_args = mock_hts_service.create_fungible_token.call_args
        assert call_args[1]["symbol"] == "CC2024-GLOBAL"
        assert call_args[1]["decimals"] == 3
    
    @pytest.mark.asyncio
    async def test_create_recycling_certificate_nft_success(self, token_manager, mock_hts_service):
        """Test successful recycling certificate NFT creation"""
        # Mock HTS response
        mock_hts_service.create_nft_collection.return_value = {
            "token_id": "0.0.987654",
            "name": "Recycling Certificate - RECYCLING_COMPLETION",
            "symbol": "RC-RECYCLING_COMPLETION",
            "max_supply": 10000,
            "treasury_account": "0.0.789012",
            "status": "success"
        }
        
        # Test NFT creation
        result = await token_manager.create_recycling_certificate_nft(
            certificate_type="RECYCLING_COMPLETION",
            max_supply=10000
        )
        
        # Assertions
        assert result["token_id"] == "0.0.987654"
        assert result["category"] == TokenCategory.RECYCLING_CERTIFICATE.value
        assert result["certificate_type"] == "RECYCLING_COMPLETION"
        
        # Verify HTS service was called correctly
        mock_hts_service.create_nft_collection.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mint_waste_tokens_success(self, token_manager, mock_hts_service):
        """Test successful waste token minting"""
        # Setup token registry
        token_manager.token_registry["0.0.123456"] = {
            "category": TokenCategory.WASTE_TOKEN.value,
            "base_value_per_unit": 0.08,
            "decimals": 2,
            "treasury_account": "0.0.789012"
        }
        
        # Mock HTS responses
        mock_hts_service.mint_tokens.return_value = {
            "token_id": "0.0.123456",
            "amount_minted": 240,  # 1.0 kg * 0.08 * 0.8 * 100 (decimals) * 3.75 (quality)
            "status": "success"
        }
        mock_hts_service.transfer_tokens.return_value = {"status": "success"}
        
        # Test minting
        result = await token_manager.mint_waste_tokens(
            token_id="0.0.123456",
            waste_weight_kg=1.0,
            quality_grade="GOOD",
            recipient_account="0.0.111111"
        )
        
        # Assertions
        assert result["waste_weight_kg"] == 1.0
        assert result["quality_grade"] == "GOOD"
        assert result["quality_multiplier"] == 0.8  # GOOD quality
        assert result["recipient_account"] == "0.0.111111"
        assert "token_amount_raw" in result
        assert "token_amount_formatted" in result
        
        # Verify services were called
        mock_hts_service.mint_tokens.assert_called_once()
        mock_hts_service.transfer_tokens.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mint_waste_tokens_invalid_token(self, token_manager):
        """Test waste token minting with invalid token ID"""
        with pytest.raises(ValidationError) as exc_info:
            await token_manager.mint_waste_tokens(
                token_id="0.0.invalid",
                waste_weight_kg=1.0
            )
        
        assert "Invalid waste token ID" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_mint_carbon_credits_success(self, token_manager, mock_hts_service):
        """Test successful carbon credit minting"""
        # Setup token registry
        token_manager.token_registry["0.0.654321"] = {
            "category": TokenCategory.CARBON_CREDIT.value,
            "decimals": 3,
            "treasury_account": "0.0.789012"
        }
        
        # Mock HTS responses
        mock_hts_service.mint_tokens.return_value = {
            "token_id": "0.0.654321",
            "amount_minted": 2500,  # 2.5 kg CO2 / 1000 * 1000 (decimals)
            "status": "success"
        }
        mock_hts_service.transfer_tokens.return_value = {"status": "success"}
        
        # Test minting
        result = await token_manager.mint_carbon_credits(
            token_id="0.0.654321",
            co2_saved_kg=2500.0,  # 2.5 credits
            verification_data={"method": "LCA", "auditor": "Third Party"},
            recipient_account="0.0.222222"
        )
        
        # Assertions
        assert result["co2_saved_kg"] == 2500.0
        assert result["carbon_credits"] == 2.5  # 2500 / 1000
        assert result["token_amount_formatted"] == 2.5
        assert result["recipient_account"] == "0.0.222222"
        assert "verification_data" in result
        
        # Verify services were called
        mock_hts_service.mint_tokens.assert_called_once()
        mock_hts_service.transfer_tokens.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mint_recycling_certificate_success(self, token_manager, mock_hts_service):
        """Test successful recycling certificate minting"""
        # Setup token registry
        token_manager.token_registry["0.0.987654"] = {
            "category": TokenCategory.RECYCLING_CERTIFICATE.value,
            "treasury_account": "0.0.789012"
        }
        
        # Mock HTS responses
        mock_hts_service.mint_tokens.return_value = {
            "token_id": "0.0.987654",
            "amount_minted": 1,
            "serial_numbers": [1],
            "status": "success"
        }
        mock_hts_service.transfer_tokens.return_value = {"status": "success"}
        
        certificate_data = {
            "certificate_id": "CERT-001",
            "type": "RECYCLING",
            "waste_type": "PET_PLASTIC",
            "weight_kg": 5.0,
            "co2_saved_kg": 12.5,
            "description": "Recycling completion certificate"
        }
        
        # Test minting
        result = await token_manager.mint_recycling_certificate(
            token_id="0.0.987654",
            certificate_data=certificate_data,
            recipient_account="0.0.333333"
        )
        
        # Assertions
        assert result["certificate_data"] == certificate_data
        assert result["recipient_account"] == "0.0.333333"
        assert "metadata" in result
        assert result["metadata"]["name"] == "Recycling Certificate #CERT-001"
        
        # Check metadata structure
        metadata = result["metadata"]
        assert "attributes" in metadata
        assert any(attr["trait_type"] == "Waste Type" for attr in metadata["attributes"])
        assert any(attr["trait_type"] == "Weight (kg)" for attr in metadata["attributes"])
    
    @pytest.mark.asyncio
    async def test_get_account_portfolio_success(self, token_manager, mock_hedera_client, mock_hts_service):
        """Test successful account portfolio retrieval"""
        # Mock account balance
        mock_hedera_client.get_account_balance.return_value = {
            "hbar_balance": 25.5,
            "tokens": {
                "0.0.123456": 500,  # Waste tokens
                "0.0.654321": 1500,  # Carbon credits
                "0.0.987654": 3  # NFT certificates
            }
        }
        
        # Mock token info responses
        mock_hts_service.get_token_info.side_effect = [
            {
                "symbol": "PET-GLOBAL",
                "name": "PET Plastic Token",
                "decimals": 2,
                "token_type": "fungible"
            },
            {
                "symbol": "CC2024-GLOBAL",
                "name": "Carbon Credit 2024",
                "decimals": 3,
                "token_type": "fungible"
            },
            {
                "symbol": "RC-RECYCLING",
                "name": "Recycling Certificate",
                "decimals": 0,
                "token_type": "nft"
            }
        ]
        
        # Setup token registry
        token_manager.token_registry.update({
            "0.0.123456": {"category": TokenCategory.WASTE_TOKEN.value, "base_value_per_unit": 0.08},
            "0.0.654321": {"category": TokenCategory.CARBON_CREDIT.value},
            "0.0.987654": {"category": TokenCategory.RECYCLING_CERTIFICATE.value}
        })
        
        # Test portfolio retrieval
        result = await token_manager.get_account_portfolio("0.0.111111")
        
        # Assertions
        assert result["account_id"] == "0.0.111111"
        assert result["hbar_balance"] == 25.5
        assert len(result["tokens"]) == 3
        
        # Check summary
        summary = result["summary"]
        assert summary["total_tokens"] == 3
        assert summary["waste_tokens"] == 1
        assert summary["carbon_credits"] == 1
        assert summary["certificates"] == 1
        assert summary["total_value_usd"] > 0
        
        # Check individual token data
        waste_token = result["tokens"]["0.0.123456"]
        assert waste_token["symbol"] == "PET-GLOBAL"
        assert waste_token["balance_formatted"] == 5.0  # 500 / 100 (decimals)
        assert waste_token["category"] == TokenCategory.WASTE_TOKEN.value
    
    def test_get_quality_multiplier(self, token_manager):
        """Test quality multiplier calculation"""
        assert token_manager._get_quality_multiplier("EXCELLENT") == 1.0
        assert token_manager._get_quality_multiplier("GOOD") == 0.8
        assert token_manager._get_quality_multiplier("FAIR") == 0.6
        assert token_manager._get_quality_multiplier("POOR") == 0.3
        assert token_manager._get_quality_multiplier("unknown") == 0.6  # Default
    
    def test_estimate_token_value_waste_token(self, token_manager):
        """Test token value estimation for waste tokens"""
        registry_info = {
            "category": TokenCategory.WASTE_TOKEN.value,
            "base_value_per_unit": 0.08
        }
        
        value = token_manager._estimate_token_value("0.0.123456", 5.0, registry_info)
        assert value == 0.4  # 5.0 * 0.08
    
    def test_estimate_token_value_carbon_credits(self, token_manager):
        """Test token value estimation for carbon credits"""
        registry_info = {
            "category": TokenCategory.CARBON_CREDIT.value
        }
        
        value = token_manager._estimate_token_value("0.0.654321", 2.5, registry_info)
        assert value == 37.5  # 2.5 * 15.0
    
    def test_estimate_token_value_certificates(self, token_manager):
        """Test token value estimation for certificates"""
        registry_info = {
            "category": TokenCategory.RECYCLING_CERTIFICATE.value
        }
        
        value = token_manager._estimate_token_value("0.0.987654", 3.0, registry_info)
        assert value == 30.0  # 3.0 * 10.0
    
    def test_estimate_token_value_unknown(self, token_manager):
        """Test token value estimation for unknown category"""
        registry_info = {
            "category": "unknown"
        }
        
        value = token_manager._estimate_token_value("0.0.unknown", 1.0, registry_info)
        assert value == 0.0
    
    def test_load_waste_token_configs(self, token_manager):
        """Test waste token configurations loading"""
        configs = token_manager._load_waste_token_configs()
        
        # Check all waste types are configured
        expected_types = [
            WasteTokenType.PET_PLASTIC,
            WasteTokenType.ALUMINUM,
            WasteTokenType.CARDBOARD,
            WasteTokenType.GLASS,
            WasteTokenType.ELECTRONIC,
            WasteTokenType.TEXTILE,
            WasteTokenType.ORGANIC,
            WasteTokenType.MIXED
        ]
        
        for waste_type in expected_types:
            assert waste_type in configs
            config = configs[waste_type]
            assert "name" in config
            assert "decimals" in config
            assert "base_value_per_unit" in config
            assert "environmental_impact" in config
    
    def test_waste_token_config_values(self, token_manager):
        """Test specific waste token configuration values"""
        configs = token_manager.waste_token_configs
        
        # Test PET plastic config
        pet_config = configs[WasteTokenType.PET_PLASTIC]
        assert pet_config["name"] == "PET Plastic"
        assert pet_config["decimals"] == 2
        assert pet_config["base_value_per_unit"] == 0.08
        assert pet_config["environmental_impact"] == "high"
        
        # Test aluminum config (highest value)
        aluminum_config = configs[WasteTokenType.ALUMINUM]
        assert aluminum_config["base_value_per_unit"] == 1.20
        assert aluminum_config["environmental_impact"] == "very_high"
        
        # Test electronic waste config
        electronic_config = configs[WasteTokenType.ELECTRONIC]
        assert electronic_config["base_value_per_unit"] == 2.50
        assert electronic_config["environmental_impact"] == "very_high"
    
    @pytest.mark.asyncio
    async def test_hts_service_error_handling(self, token_manager, mock_hts_service):
        """Test error handling when HTS service fails"""
        mock_hts_service.create_fungible_token.side_effect = Exception("HTS API error")
        
        with pytest.raises(BlockchainError) as exc_info:
            await token_manager.create_waste_token(WasteTokenType.PET_PLASTIC)
        
        assert "Waste token creation failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_mint_tokens_without_recipient(self, token_manager, mock_hts_service):
        """Test minting tokens without specifying recipient (stays in treasury)"""
        # Setup token registry
        token_manager.token_registry["0.0.123456"] = {
            "category": TokenCategory.WASTE_TOKEN.value,
            "base_value_per_unit": 0.08,
            "decimals": 2,
            "treasury_account": "0.0.789012"
        }
        
        # Mock HTS response
        mock_hts_service.mint_tokens.return_value = {
            "token_id": "0.0.123456",
            "amount_minted": 64,  # 1.0 * 0.08 * 0.8 * 100
            "status": "success"
        }
        
        # Test minting without recipient
        result = await token_manager.mint_waste_tokens(
            token_id="0.0.123456",
            waste_weight_kg=1.0,
            quality_grade="GOOD"
            # No recipient_account specified
        )
        
        # Assertions
        assert result["recipient_account"] is None
        
        # Verify only mint was called, not transfer
        mock_hts_service.mint_tokens.assert_called_once()
        mock_hts_service.transfer_tokens.assert_not_called()
