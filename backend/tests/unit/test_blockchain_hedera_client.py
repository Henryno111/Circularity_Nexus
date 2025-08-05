"""
Unit tests for Hedera Client
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from circularity_nexus.blockchain.hedera_client import HederaClient
from circularity_nexus.core.exceptions import BlockchainError


class TestHederaClient:
    """Test cases for HederaClient"""
    
    @pytest.fixture
    def mock_hedera_imports(self):
        """Mock Hedera SDK imports"""
        with patch.multiple(
            'circularity_nexus.blockchain.hedera_client',
            Client=Mock(),
            AccountId=Mock(),
            PrivateKey=Mock(),
            Hbar=Mock(),
            AccountCreateTransaction=Mock(),
            AccountBalanceQuery=Mock(),
            TransferTransaction=Mock(),
            Status=Mock()
        ) as mocks:
            yield mocks
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings"""
        with patch('circularity_nexus.blockchain.hedera_client.get_settings') as mock_get_settings:
            mock_settings = Mock()
            mock_settings.hedera_network = "testnet"
            mock_settings.hedera_operator_id = "0.0.123456"
            mock_settings.hedera_operator_key = "test-private-key"
            mock_get_settings.return_value = mock_settings
            yield mock_settings
    
    @pytest.fixture
    def hedera_client(self, mock_hedera_imports, mock_settings):
        """HederaClient instance with mocked dependencies"""
        with patch.object(HederaClient, '_initialize_client'):
            client = HederaClient()
            client.client = Mock()
            client.operator_account_id = Mock()
            client.operator_private_key = Mock()
            return client
    
    def test_initialization_testnet(self, mock_hedera_imports, mock_settings):
        """Test client initialization for testnet"""
        mock_settings.hedera_network = "testnet"
        
        with patch.object(HederaClient, '_initialize_client') as mock_init:
            client = HederaClient()
            mock_init.assert_called_once()
    
    def test_initialization_mainnet(self, mock_hedera_imports, mock_settings):
        """Test client initialization for mainnet"""
        mock_settings.hedera_network = "mainnet"
        
        with patch.object(HederaClient, '_initialize_client') as mock_init:
            client = HederaClient()
            mock_init.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_account_success(self, hedera_client, mock_hedera_imports):
        """Test successful account creation"""
        # Mock transaction components
        mock_transaction = Mock()
        mock_response = Mock()
        mock_receipt = Mock()
        mock_account_id = Mock()
        mock_private_key = Mock()
        mock_public_key = Mock()
        
        # Configure mocks
        mock_hedera_imports['AccountCreateTransaction'].return_value = mock_transaction
        mock_hedera_imports['PrivateKey'].generateED25519.return_value = mock_private_key
        mock_private_key.getPublicKey.return_value = mock_public_key
        mock_hedera_imports['Hbar'].from.return_value = Mock()
        mock_hedera_imports['Status'].Success = "SUCCESS"
        
        # Configure transaction flow
        mock_transaction.setKey.return_value = mock_transaction
        mock_transaction.setInitialBalance.return_value = mock_transaction
        mock_transaction.setMaxAutomaticTokenAssociations.return_value = mock_transaction
        mock_transaction.freezeWith.return_value = mock_transaction
        mock_transaction.sign.return_value = mock_transaction
        mock_transaction.execute.return_value = mock_response
        mock_response.getReceipt.return_value = mock_receipt
        mock_receipt.status = "SUCCESS"
        mock_receipt.accountId = mock_account_id
        mock_response.transactionId = "0.0.123456@1234567890.123456789"
        
        # Configure string representations
        str(mock_account_id) == "0.0.789012"
        str(mock_private_key) == "test-private-key"
        str(mock_public_key) == "test-public-key"
        
        # Test account creation
        result = await hedera_client.create_account(
            initial_balance=5.0,
            max_automatic_token_associations=50
        )
        
        # Assertions
        assert result["status"] == "success"
        assert "account_id" in result
        assert "private_key" in result
        assert "public_key" in result
        assert result["initial_balance"] == 5.0
        assert "transaction_id" in result
    
    @pytest.mark.asyncio
    async def test_create_account_failure(self, hedera_client, mock_hedera_imports):
        """Test account creation failure"""
        # Mock transaction failure
        mock_transaction = Mock()
        mock_response = Mock()
        mock_receipt = Mock()
        
        mock_hedera_imports['AccountCreateTransaction'].return_value = mock_transaction
        mock_hedera_imports['PrivateKey'].generateED25519.return_value = Mock()
        mock_hedera_imports['Status'].Success = "SUCCESS"
        
        # Configure transaction flow
        mock_transaction.setKey.return_value = mock_transaction
        mock_transaction.setInitialBalance.return_value = mock_transaction
        mock_transaction.setMaxAutomaticTokenAssociations.return_value = mock_transaction
        mock_transaction.freezeWith.return_value = mock_transaction
        mock_transaction.sign.return_value = mock_transaction
        mock_transaction.execute.return_value = mock_response
        mock_response.getReceipt.return_value = mock_receipt
        mock_receipt.status = "FAILED"  # Failure status
        
        with pytest.raises(BlockchainError) as exc_info:
            await hedera_client.create_account()
        
        assert "Account creation failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_account_balance_success(self, hedera_client, mock_hedera_imports):
        """Test successful account balance query"""
        # Mock balance query components
        mock_query = Mock()
        mock_balance = Mock()
        mock_account_id = Mock()
        
        mock_hedera_imports['AccountId'].fromString.return_value = mock_account_id
        mock_hedera_imports['AccountBalanceQuery'].return_value = mock_query
        
        # Configure query flow
        mock_query.setAccountId.return_value = mock_query
        mock_query.execute.return_value = mock_balance
        mock_balance.hbars.toTinybars.return_value = 500_000_000  # 5 HBAR
        mock_balance.tokens = {"0.0.111111": 1000, "0.0.222222": 2000}
        
        # Test balance query
        result = await hedera_client.get_account_balance("0.0.123456")
        
        # Assertions
        assert result["account_id"] == "0.0.123456"
        assert result["hbar_balance"] == 5.0  # 500_000_000 / 100_000_000
        assert result["tokens"]["0.0.111111"] == 1000
        assert result["tokens"]["0.0.222222"] == 2000
    
    @pytest.mark.asyncio
    async def test_transfer_hbar_success(self, hedera_client, mock_hedera_imports):
        """Test successful HBAR transfer"""
        # Mock transfer components
        mock_transaction = Mock()
        mock_response = Mock()
        mock_receipt = Mock()
        mock_account_id = Mock()
        mock_hbar = Mock()
        
        mock_hedera_imports['AccountId'].fromString.return_value = mock_account_id
        mock_hedera_imports['Hbar'].from.return_value = mock_hbar
        mock_hedera_imports['TransferTransaction'].return_value = mock_transaction
        mock_hedera_imports['Status'].Success = "SUCCESS"
        
        # Configure transaction flow
        mock_hbar.negated.return_value = mock_hbar
        mock_transaction.addHbarTransfer.return_value = mock_transaction
        mock_transaction.setTransactionMemo.return_value = mock_transaction
        mock_transaction.freezeWith.return_value = mock_transaction
        mock_transaction.sign.return_value = mock_transaction
        mock_transaction.execute.return_value = mock_response
        mock_response.getReceipt.return_value = mock_receipt
        mock_receipt.status = "SUCCESS"
        mock_receipt.consensusTimestamp = "1234567890.123456789"
        mock_response.transactionId = "0.0.123456@1234567890.123456789"
        
        # Test transfer
        result = await hedera_client.transfer_hbar(
            to_account_id="0.0.789012",
            amount=2.5,
            memo="Test transfer"
        )
        
        # Assertions
        assert result["status"] == "success"
        assert result["to_account"] == "0.0.789012"
        assert result["amount"] == 2.5
        assert result["memo"] == "Test transfer"
        assert "transaction_id" in result
        assert "consensus_timestamp" in result
    
    @pytest.mark.asyncio
    async def test_transfer_hbar_failure(self, hedera_client, mock_hedera_imports):
        """Test HBAR transfer failure"""
        # Mock transfer failure
        mock_transaction = Mock()
        mock_response = Mock()
        mock_receipt = Mock()
        
        mock_hedera_imports['AccountId'].fromString.return_value = Mock()
        mock_hedera_imports['Hbar'].from.return_value = Mock()
        mock_hedera_imports['TransferTransaction'].return_value = mock_transaction
        mock_hedera_imports['Status'].Success = "SUCCESS"
        
        # Configure transaction flow with failure
        mock_transaction.addHbarTransfer.return_value = mock_transaction
        mock_transaction.freezeWith.return_value = mock_transaction
        mock_transaction.sign.return_value = mock_transaction
        mock_transaction.execute.return_value = mock_response
        mock_response.getReceipt.return_value = mock_receipt
        mock_receipt.status = "INSUFFICIENT_ACCOUNT_BALANCE"  # Failure status
        
        with pytest.raises(BlockchainError) as exc_info:
            await hedera_client.transfer_hbar("0.0.789012", 100.0)
        
        assert "Transfer failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_transaction_record_success(self, hedera_client, mock_hedera_imports):
        """Test successful transaction record query"""
        # Mock record query components
        mock_tx_id = Mock()
        mock_query = Mock()
        mock_record = Mock()
        mock_receipt = Mock()
        
        mock_hedera_imports['TransactionId'].fromString.return_value = mock_tx_id
        mock_hedera_imports['TransactionRecordQuery'].return_value = mock_query
        
        # Configure query flow
        mock_query.setTransactionId.return_value = mock_query
        mock_query.execute.return_value = mock_record
        mock_record.consensusTimestamp = "1234567890.123456789"
        mock_record.transactionFee.toTinybars.return_value = 5_000_000  # 0.05 HBAR
        mock_record.transactionMemo = "Test memo"
        mock_record.receipt = mock_receipt
        mock_receipt.status = "SUCCESS"
        mock_record.transferList = {}
        
        # Test record query
        result = await hedera_client.get_transaction_record("0.0.123456@1234567890.123456789")
        
        # Assertions
        assert result["transaction_id"] == "0.0.123456@1234567890.123456789"
        assert result["consensus_timestamp"] == "1234567890.123456789"
        assert result["transaction_fee"] == 0.05
        assert result["transaction_memo"] == "Test memo"
        assert result["status"] == "SUCCESS"
        assert "transfers" in result
    
    def test_get_network_info(self, hedera_client):
        """Test network information retrieval"""
        hedera_client.settings.hedera_network = "testnet"
        hedera_client.operator_account_id = "0.0.123456"
        
        info = hedera_client.get_network_info()
        
        assert info["network"] == "testnet"
        assert info["operator_account"] == "0.0.123456"
        assert info["client_status"] == "connected"
        assert info["max_transaction_fee"] == "1 HBAR"
    
    @pytest.mark.asyncio
    async def test_ping_network_success(self, hedera_client):
        """Test successful network ping"""
        with patch.object(hedera_client, 'get_account_balance') as mock_balance:
            mock_balance.return_value = {"hbar_balance": 10.0}
            
            result = await hedera_client.ping_network()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_ping_network_failure(self, hedera_client):
        """Test network ping failure"""
        with patch.object(hedera_client, 'get_account_balance') as mock_balance:
            mock_balance.side_effect = Exception("Network error")
            
            result = await hedera_client.ping_network()
            assert result is False
    
    def test_close_connection(self, hedera_client):
        """Test client connection closure"""
        mock_client = Mock()
        hedera_client.client = mock_client
        
        hedera_client.close()
        mock_client.close.assert_called_once()
    
    def test_context_manager(self, hedera_client):
        """Test context manager functionality"""
        with patch.object(hedera_client, 'close') as mock_close:
            with hedera_client as client:
                assert client is hedera_client
            mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_exception_handling(self, hedera_client, mock_hedera_imports):
        """Test exception handling in operations"""
        # Mock exception during account creation
        mock_hedera_imports['AccountCreateTransaction'].side_effect = Exception("SDK error")
        
        with pytest.raises(BlockchainError) as exc_info:
            await hedera_client.create_account()
        
        assert "Account creation failed" in str(exc_info.value)
        assert "SDK error" in str(exc_info.value)
