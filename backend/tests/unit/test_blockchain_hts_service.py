"""
Unit tests for Hedera Token Service (HTS) Integration
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from circularity_nexus.blockchain.hts_service import HTSService
from circularity_nexus.core.exceptions import BlockchainError, ValidationError


class TestHTSService:
    """Test cases for HTSService"""
    
    @pytest.fixture
    def mock_hedera_client(self):
        """Mock HederaClient"""
        with patch('circularity_nexus.blockchain.hts_service.HederaClient') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            
            # Mock client properties
            mock_instance.client = Mock()
            mock_instance.operator_id = "0.0.123456"
            mock_instance.operator_private_key = Mock()
            
            yield mock_instance
    
    @pytest.fixture
    def hts_service(self, mock_hedera_client):
        """HTSService instance with mocked dependencies"""
        service = HTSService()
        service.hedera_client = mock_hedera_client
        return service
    
    @pytest.mark.asyncio
    async def test_create_fungible_token_success(self, hts_service, mock_hedera_client):
        """Test successful fungible token creation"""
        # Mock Hedera SDK objects
        mock_transaction = Mock()
        mock_receipt = Mock()
        mock_receipt.tokenId = Mock()
        mock_receipt.tokenId.__str__ = Mock(return_value="0.0.123456")
        
        # Mock transaction execution
        with patch('hedera.TokenCreateTransaction') as mock_token_create:
            mock_token_create.return_value = mock_transaction
            mock_transaction.setTokenName.return_value = mock_transaction
            mock_transaction.setTokenSymbol.return_value = mock_transaction
            mock_transaction.setDecimals.return_value = mock_transaction
            mock_transaction.setInitialSupply.return_value = mock_transaction
            mock_transaction.setTreasuryAccountId.return_value = mock_transaction
            mock_transaction.setAdminKey.return_value = mock_transaction
            mock_transaction.setSupplyKey.return_value = mock_transaction
            mock_transaction.setFreezeDefault.return_value = mock_transaction
            mock_transaction.setMaxSupply.return_value = mock_transaction
            mock_transaction.setSupplyType.return_value = mock_transaction
            mock_transaction.execute.return_value = Mock()
            mock_transaction.execute.return_value.getReceipt.return_value = mock_receipt
            
            # Test token creation
            result = await hts_service.create_fungible_token(
                name="Test Token",
                symbol="TEST",
                decimals=2,
                initial_supply=1000,
                max_supply=10000
            )
            
            # Assertions
            assert result["token_id"] == "0.0.123456"
            assert result["name"] == "Test Token"
            assert result["symbol"] == "TEST"
            assert result["decimals"] == 2
            assert result["initial_supply"] == 1000
            assert result["max_supply"] == 10000
            assert result["treasury_account"] == "0.0.123456"
            assert result["status"] == "success"
            
            # Verify transaction was configured correctly
            mock_transaction.setTokenName.assert_called_once_with("Test Token")
            mock_transaction.setTokenSymbol.assert_called_once_with("TEST")
            mock_transaction.setDecimals.assert_called_once_with(2)
            mock_transaction.setInitialSupply.assert_called_once_with(1000)
    
    @pytest.mark.asyncio
    async def test_create_nft_collection_success(self, hts_service, mock_hedera_client):
        """Test successful NFT collection creation"""
        # Mock Hedera SDK objects
        mock_transaction = Mock()
        mock_receipt = Mock()
        mock_receipt.tokenId = Mock()
        mock_receipt.tokenId.__str__ = Mock(return_value="0.0.654321")
        
        # Mock transaction execution
        with patch('hedera.TokenCreateTransaction') as mock_token_create:
            mock_token_create.return_value = mock_transaction
            mock_transaction.setTokenName.return_value = mock_transaction
            mock_transaction.setTokenSymbol.return_value = mock_transaction
            mock_transaction.setTokenType.return_value = mock_transaction
            mock_transaction.setSupplyType.return_value = mock_transaction
            mock_transaction.setMaxSupply.return_value = mock_transaction
            mock_transaction.setTreasuryAccountId.return_value = mock_transaction
            mock_transaction.setAdminKey.return_value = mock_transaction
            mock_transaction.setSupplyKey.return_value = mock_transaction
            mock_transaction.execute.return_value = Mock()
            mock_transaction.execute.return_value.getReceipt.return_value = mock_receipt
            
            # Test NFT creation
            result = await hts_service.create_nft_collection(
                name="Test NFT Collection",
                symbol="TESTNFT",
                max_supply=1000
            )
            
            # Assertions
            assert result["token_id"] == "0.0.654321"
            assert result["name"] == "Test NFT Collection"
            assert result["symbol"] == "TESTNFT"
            assert result["token_type"] == "nft"
            assert result["max_supply"] == 1000
            assert result["treasury_account"] == "0.0.123456"
            assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_mint_tokens_fungible_success(self, hts_service, mock_hedera_client):
        """Test successful fungible token minting"""
        # Mock Hedera SDK objects
        mock_transaction = Mock()
        mock_receipt = Mock()
        mock_receipt.totalSupply = 1500
        
        # Mock transaction execution
        with patch('hedera.TokenMintTransaction') as mock_token_mint:
            mock_token_mint.return_value = mock_transaction
            mock_transaction.setTokenId.return_value = mock_transaction
            mock_transaction.setAmount.return_value = mock_transaction
            mock_transaction.execute.return_value = Mock()
            mock_transaction.execute.return_value.getReceipt.return_value = mock_receipt
            
            # Test token minting
            result = await hts_service.mint_tokens(
                token_id="0.0.123456",
                amount=500
            )
            
            # Assertions
            assert result["token_id"] == "0.0.123456"
            assert result["amount_minted"] == 500
            assert result["total_supply"] == 1500
            assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_mint_tokens_nft_success(self, hts_service, mock_hedera_client):
        """Test successful NFT minting"""
        # Mock Hedera SDK objects
        mock_transaction = Mock()
        mock_receipt = Mock()
        mock_receipt.serials = [1, 2, 3]
        mock_receipt.totalSupply = 3
        
        # Mock transaction execution
        with patch('hedera.TokenMintTransaction') as mock_token_mint:
            mock_token_mint.return_value = mock_transaction
            mock_transaction.setTokenId.return_value = mock_transaction
            mock_transaction.setMetadata.return_value = mock_transaction
            mock_transaction.execute.return_value = Mock()
            mock_transaction.execute.return_value.getReceipt.return_value = mock_receipt
            
            metadata_list = [b"metadata1", b"metadata2", b"metadata3"]
            
            # Test NFT minting
            result = await hts_service.mint_tokens(
                token_id="0.0.654321",
                metadata=metadata_list
            )
            
            # Assertions
            assert result["token_id"] == "0.0.654321"
            assert result["serial_numbers"] == [1, 2, 3]
            assert result["amount_minted"] == 3
            assert result["total_supply"] == 3
            assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_transfer_tokens_success(self, hts_service, mock_hedera_client):
        """Test successful token transfer"""
        # Mock Hedera SDK objects
        mock_transaction = Mock()
        mock_receipt = Mock()
        
        # Mock transaction execution
        with patch('hedera.TransferTransaction') as mock_transfer:
            mock_transfer.return_value = mock_transaction
            mock_transaction.addTokenTransfer.return_value = mock_transaction
            mock_transaction.execute.return_value = Mock()
            mock_transaction.execute.return_value.getReceipt.return_value = mock_receipt
            
            # Test token transfer
            result = await hts_service.transfer_tokens(
                token_id="0.0.123456",
                from_account="0.0.123456",
                to_account="0.0.789012",
                amount=100
            )
            
            # Assertions
            assert result["token_id"] == "0.0.123456"
            assert result["from_account"] == "0.0.123456"
            assert result["to_account"] == "0.0.789012"
            assert result["amount"] == 100
            assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_get_token_info_success(self, hts_service, mock_hedera_client):
        """Test successful token info retrieval"""
        # Mock Hedera SDK objects
        mock_query = Mock()
        mock_token_info = Mock()
        mock_token_info.tokenId = Mock()
        mock_token_info.tokenId.__str__ = Mock(return_value="0.0.123456")
        mock_token_info.name = "Test Token"
        mock_token_info.symbol = "TEST"
        mock_token_info.decimals = 2
        mock_token_info.totalSupply = 1000
        mock_token_info.maxSupply = 10000
        mock_token_info.treasuryAccountId = Mock()
        mock_token_info.treasuryAccountId.__str__ = Mock(return_value="0.0.treasury")
        mock_token_info.tokenType = Mock()
        mock_token_info.tokenType.name = "FUNGIBLE_COMMON"
        
        # Mock query execution
        with patch('hedera.TokenInfoQuery') as mock_token_info_query:
            mock_token_info_query.return_value = mock_query
            mock_query.setTokenId.return_value = mock_query
            mock_query.execute.return_value = mock_token_info
            
            # Test token info retrieval
            result = await hts_service.get_token_info("0.0.123456")
            
            # Assertions
            assert result["token_id"] == "0.0.123456"
            assert result["name"] == "Test Token"
            assert result["symbol"] == "TEST"
            assert result["decimals"] == 2
            assert result["total_supply"] == 1000
            assert result["max_supply"] == 10000
            assert result["treasury_account"] == "0.0.treasury"
            assert result["token_type"] == "fungible"
    
    @pytest.mark.asyncio
    async def test_create_token_validation_error(self, hts_service):
        """Test token creation with invalid parameters"""
        with pytest.raises(ValidationError) as exc_info:
            await hts_service.create_fungible_token(
                name="",  # Empty name
                symbol="TEST"
            )
        
        assert "Token name cannot be empty" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_hedera_sdk_error_handling(self, hts_service, mock_hedera_client):
        """Test error handling when Hedera SDK fails"""
        with patch('hedera.TokenCreateTransaction') as mock_token_create:
            mock_transaction = Mock()
            mock_token_create.return_value = mock_transaction
            mock_transaction.setTokenName.return_value = mock_transaction
            mock_transaction.setTokenSymbol.return_value = mock_transaction
            mock_transaction.setDecimals.return_value = mock_transaction
            mock_transaction.setInitialSupply.return_value = mock_transaction
            mock_transaction.setTreasuryAccountId.return_value = mock_transaction
            mock_transaction.setAdminKey.return_value = mock_transaction
            mock_transaction.setSupplyKey.return_value = mock_transaction
            mock_transaction.setFreezeDefault.return_value = mock_transaction
            mock_transaction.setMaxSupply.return_value = mock_transaction
            mock_transaction.setSupplyType.return_value = mock_transaction
            mock_transaction.execute.side_effect = Exception("Hedera SDK error")
            
            with pytest.raises(BlockchainError) as exc_info:
                await hts_service.create_fungible_token(
                    name="Test Token",
                    symbol="TEST"
                )
            
            assert "Token creation failed" in str(exc_info.value)
