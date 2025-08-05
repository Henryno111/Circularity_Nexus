"""
Unit tests for Hedera Consensus Service (HCS) Integration
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from circularity_nexus.blockchain.hcs_service import HCSService
from circularity_nexus.core.exceptions import BlockchainError, ValidationError


class TestHCSService:
    """Test cases for HCSService"""
    
    @pytest.fixture
    def mock_hedera_client(self):
        """Mock HederaClient"""
        with patch('circularity_nexus.blockchain.hcs_service.HederaClient') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            
            # Mock client properties
            mock_instance.client = Mock()
            mock_instance.operator_id = "0.0.123456"
            mock_instance.operator_private_key = Mock()
            
            yield mock_instance
    
    @pytest.fixture
    def hcs_service(self, mock_hedera_client):
        """HCSService instance with mocked dependencies"""
        service = HCSService()
        service.hedera_client = mock_hedera_client
        return service
    
    @pytest.mark.asyncio
    async def test_create_topic_success(self, hcs_service, mock_hedera_client):
        """Test successful topic creation"""
        # Mock Hedera SDK objects
        mock_transaction = Mock()
        mock_receipt = Mock()
        mock_receipt.topicId = Mock()
        mock_receipt.topicId.__str__ = Mock(return_value="0.0.100001")
        
        # Mock transaction execution
        with patch('hedera.TopicCreateTransaction') as mock_topic_create:
            mock_topic_create.return_value = mock_transaction
            mock_transaction.setTopicMemo.return_value = mock_transaction
            mock_transaction.setAdminKey.return_value = mock_transaction
            mock_transaction.setSubmitKey.return_value = mock_transaction
            mock_transaction.setAutoRenewAccountId.return_value = mock_transaction
            mock_transaction.setAutoRenewPeriod.return_value = mock_transaction
            mock_transaction.execute.return_value = Mock()
            mock_transaction.execute.return_value.getReceipt.return_value = mock_receipt
            
            # Test topic creation
            result = await hcs_service.create_topic(
                memo="Test Topic",
                enable_private_submit_key=True
            )
            
            # Assertions
            assert result["topic_id"] == "0.0.100001"
            assert result["memo"] == "Test Topic"
            assert result["admin_key_required"] is True
            assert result["submit_key_required"] is True
            assert result["status"] == "success"
            assert "created_at" in result
            
            # Verify transaction was configured correctly
            mock_transaction.setTopicMemo.assert_called_once_with("Test Topic")
            mock_transaction.setAdminKey.assert_called_once()
            mock_transaction.setSubmitKey.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_topic_public(self, hcs_service, mock_hedera_client):
        """Test public topic creation (no submit key)"""
        # Mock Hedera SDK objects
        mock_transaction = Mock()
        mock_receipt = Mock()
        mock_receipt.topicId = Mock()
        mock_receipt.topicId.__str__ = Mock(return_value="0.0.100002")
        
        # Mock transaction execution
        with patch('hedera.TopicCreateTransaction') as mock_topic_create:
            mock_topic_create.return_value = mock_transaction
            mock_transaction.setTopicMemo.return_value = mock_transaction
            mock_transaction.setAdminKey.return_value = mock_transaction
            mock_transaction.setAutoRenewAccountId.return_value = mock_transaction
            mock_transaction.setAutoRenewPeriod.return_value = mock_transaction
            mock_transaction.execute.return_value = Mock()
            mock_transaction.execute.return_value.getReceipt.return_value = mock_receipt
            
            # Test public topic creation
            result = await hcs_service.create_topic(
                memo="Public Topic",
                enable_private_submit_key=False
            )
            
            # Assertions
            assert result["topic_id"] == "0.0.100002"
            assert result["submit_key_required"] is False
            
            # Verify submit key was NOT set
            mock_transaction.setSubmitKey.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_submit_message_success(self, hcs_service, mock_hedera_client):
        """Test successful message submission"""
        # Mock Hedera SDK objects
        mock_transaction = Mock()
        mock_receipt = Mock()
        mock_receipt.topicSequenceNumber = 42
        mock_receipt.topicRunningHash = b"running_hash_bytes"
        
        # Mock transaction execution
        with patch('hedera.TopicMessageSubmitTransaction') as mock_message_submit:
            mock_message_submit.return_value = mock_transaction
            mock_transaction.setTopicId.return_value = mock_transaction
            mock_transaction.setMessage.return_value = mock_transaction
            mock_transaction.setTransactionMemo.return_value = mock_transaction
            mock_transaction.execute.return_value = Mock()
            mock_transaction.execute.return_value.getReceipt.return_value = mock_receipt
            mock_transaction.execute.return_value.transactionId = Mock()
            mock_transaction.execute.return_value.transactionId.__str__ = Mock(
                return_value="0.0.123456@1234567890.123456789"
            )
            
            # Test message submission
            result = await hcs_service.submit_message(
                topic_id="0.0.100001",
                message="Hello, HCS!",
                memo="test_message"
            )
            
            # Assertions
            assert result["topic_id"] == "0.0.100001"
            assert result["sequence_number"] == 42
            assert result["transaction_id"] == "0.0.123456@1234567890.123456789"
            assert result["status"] == "success"
            assert "submitted_at" in result
            assert "running_hash" in result
            
            # Verify transaction was configured correctly
            mock_transaction.setTopicId.assert_called_once()
            mock_transaction.setMessage.assert_called_once_with("Hello, HCS!")
            mock_transaction.setTransactionMemo.assert_called_once_with("test_message")
    
    @pytest.mark.asyncio
    async def test_submit_message_with_json(self, hcs_service, mock_hedera_client):
        """Test message submission with JSON data"""
        # Mock Hedera SDK objects
        mock_transaction = Mock()
        mock_receipt = Mock()
        mock_receipt.topicSequenceNumber = 43
        mock_receipt.topicRunningHash = b"running_hash_bytes"
        
        # Mock transaction execution
        with patch('hedera.TopicMessageSubmitTransaction') as mock_message_submit:
            mock_message_submit.return_value = mock_transaction
            mock_transaction.setTopicId.return_value = mock_transaction
            mock_transaction.setMessage.return_value = mock_transaction
            mock_transaction.setTransactionMemo.return_value = mock_transaction
            mock_transaction.execute.return_value = Mock()
            mock_transaction.execute.return_value.getReceipt.return_value = mock_receipt
            mock_transaction.execute.return_value.transactionId = Mock()
            mock_transaction.execute.return_value.transactionId.__str__ = Mock(
                return_value="0.0.123456@1234567890.123456789"
            )
            
            # Test JSON message submission
            json_data = {"type": "waste_submission", "user_id": "user123", "weight": 2.5}
            result = await hcs_service.submit_message(
                topic_id="0.0.100001",
                message=json_data
            )
            
            # Assertions
            assert result["status"] == "success"
            
            # Verify JSON was serialized
            call_args = mock_transaction.setMessage.call_args
            import json
            submitted_message = call_args[0][0]
            parsed_data = json.loads(submitted_message)
            assert parsed_data == json_data
    
    @pytest.mark.asyncio
    async def test_get_topic_messages_success(self, hcs_service, mock_hedera_client):
        """Test successful topic message retrieval"""
        # Mock mirror node response
        mock_response = Mock()
        mock_response.json.return_value = {
            "messages": [
                {
                    "contents": "SGVsbG8sIEhDUyE=",  # Base64 encoded "Hello, HCS!"
                    "consensus_timestamp": "1234567890.123456789",
                    "sequence_number": 1,
                    "topic_id": "0.0.100001",
                    "payer_account_id": "0.0.123456",
                    "running_hash": "running_hash_hex",
                    "running_hash_version": 3
                },
                {
                    "contents": "V29ybGQh",  # Base64 encoded "World!"
                    "consensus_timestamp": "1234567891.123456789",
                    "sequence_number": 2,
                    "topic_id": "0.0.100001",
                    "payer_account_id": "0.0.123456",
                    "running_hash": "running_hash_hex_2",
                    "running_hash_version": 3
                }
            ],
            "links": {
                "next": None
            }
        }
        
        # Mock HTTP client
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            # Test message retrieval
            messages = await hcs_service.get_topic_messages(
                topic_id="0.0.100001",
                limit=10
            )
            
            # Assertions
            assert len(messages) == 2
            
            # Check first message
            msg1 = messages[0]
            assert msg1["contents"] == "Hello, HCS!"  # Decoded from base64
            assert msg1["consensus_timestamp"] == "1234567890.123456789"
            assert msg1["sequence_number"] == 1
            assert msg1["topic_id"] == "0.0.100001"
            
            # Check second message
            msg2 = messages[1]
            assert msg2["contents"] == "World!"
            assert msg2["sequence_number"] == 2
    
    @pytest.mark.asyncio
    async def test_get_topic_messages_with_filters(self, hcs_service, mock_hedera_client):
        """Test topic message retrieval with time filters"""
        # Mock mirror node response
        mock_response = Mock()
        mock_response.json.return_value = {
            "messages": [],
            "links": {"next": None}
        }
        
        # Mock HTTP client
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session_instance = Mock()
            mock_get = Mock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            mock_session_instance.get.return_value.__aenter__.return_value = mock_response
            mock_session_instance.get.return_value = mock_get
            
            start_time = datetime(2024, 1, 1, 12, 0, 0)
            
            # Test message retrieval with filters
            messages = await hcs_service.get_topic_messages(
                topic_id="0.0.100001",
                limit=5,
                start_time=start_time
            )
            
            # Verify URL was constructed with correct parameters
            call_args = mock_session_instance.get.call_args
            url = call_args[0][0]
            assert "limit=5" in url
            assert "timestamp=gte:1704110400.000000000" in url  # Unix timestamp for start_time
    
    @pytest.mark.asyncio
    async def test_get_topic_info_success(self, hcs_service, mock_hedera_client):
        """Test successful topic info retrieval"""
        # Mock Hedera SDK objects
        mock_query = Mock()
        mock_topic_info = Mock()
        mock_topic_info.topicId = Mock()
        mock_topic_info.topicId.__str__ = Mock(return_value="0.0.100001")
        mock_topic_info.topicMemo = "Test Topic"
        mock_topic_info.runningHash = b"running_hash_bytes"
        mock_topic_info.sequenceNumber = 150
        mock_topic_info.expirationTime = None
        mock_topic_info.adminKey = Mock()
        mock_topic_info.submitKey = Mock()
        mock_topic_info.autoRenewPeriod = Mock()
        mock_topic_info.autoRenewPeriod.seconds = 7776000  # 90 days
        mock_topic_info.autoRenewAccountId = Mock()
        mock_topic_info.autoRenewAccountId.__str__ = Mock(return_value="0.0.123456")
        
        # Mock query execution
        with patch('hedera.TopicInfoQuery') as mock_topic_info_query:
            mock_topic_info_query.return_value = mock_query
            mock_query.setTopicId.return_value = mock_query
            mock_query.execute.return_value = mock_topic_info
            
            # Test topic info retrieval
            result = await hcs_service.get_topic_info("0.0.100001")
            
            # Assertions
            assert result["topic_id"] == "0.0.100001"
            assert result["memo"] == "Test Topic"
            assert result["sequence_number"] == 150
            assert result["auto_renew_period_seconds"] == 7776000
            assert result["auto_renew_account"] == "0.0.123456"
            assert result["admin_key"] is not None
            assert result["submit_key"] is not None
            assert "running_hash" in result
            
            # Verify query was configured correctly
            mock_query.setTopicId.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_subscribe_to_topic_success(self, hcs_service, mock_hedera_client):
        """Test successful topic subscription"""
        # Mock subscription callback
        callback_messages = []
        
        def test_callback(message):
            callback_messages.append(message)
        
        # Mock Hedera SDK subscription
        mock_subscription = Mock()
        
        with patch('hedera.TopicMessageQuery') as mock_topic_query:
            mock_query = Mock()
            mock_topic_query.return_value = mock_query
            mock_query.setTopicId.return_value = mock_query
            mock_query.setStartTime.return_value = mock_query
            mock_query.subscribe.return_value = mock_subscription
            
            # Test subscription
            subscription = await hcs_service.subscribe_to_topic(
                topic_id="0.0.100001",
                callback=test_callback
            )
            
            # Assertions
            assert subscription["topic_id"] == "0.0.100001"
            assert subscription["status"] == "subscribed"
            assert "subscription_id" in subscription
            assert "subscribed_at" in subscription
            
            # Verify query was configured correctly
            mock_query.setTopicId.assert_called_once()
            mock_query.subscribe.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_topic_validation_error(self, hcs_service):
        """Test topic creation with invalid parameters"""
        with pytest.raises(ValidationError) as exc_info:
            await hcs_service.create_topic(memo="")  # Empty memo
        
        assert "Topic memo cannot be empty" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_submit_message_validation_error(self, hcs_service):
        """Test message submission with invalid parameters"""
        with pytest.raises(ValidationError) as exc_info:
            await hcs_service.submit_message(
                topic_id="",  # Empty topic ID
                message="Hello"
            )
        
        assert "Topic ID cannot be empty" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            await hcs_service.submit_message(
                topic_id="0.0.100001",
                message=""  # Empty message
            )
        
        assert "Message cannot be empty" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_hedera_sdk_error_handling(self, hcs_service, mock_hedera_client):
        """Test error handling when Hedera SDK fails"""
        with patch('hedera.TopicCreateTransaction') as mock_topic_create:
            mock_transaction = Mock()
            mock_topic_create.return_value = mock_transaction
            mock_transaction.setTopicMemo.return_value = mock_transaction
            mock_transaction.setAdminKey.return_value = mock_transaction
            mock_transaction.setAutoRenewAccountId.return_value = mock_transaction
            mock_transaction.setAutoRenewPeriod.return_value = mock_transaction
            mock_transaction.execute.side_effect = Exception("Hedera SDK error")
            
            with pytest.raises(BlockchainError) as exc_info:
                await hcs_service.create_topic(memo="Test Topic")
            
            assert "Topic creation failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_mirror_node_error_handling(self, hcs_service, mock_hedera_client):
        """Test error handling when mirror node fails"""
        # Mock HTTP client error
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.side_effect = Exception("Mirror node error")
            
            with pytest.raises(BlockchainError) as exc_info:
                await hcs_service.get_topic_messages("0.0.100001")
            
            assert "Failed to retrieve topic messages" in str(exc_info.value)
    
    def test_format_consensus_timestamp(self, hcs_service):
        """Test consensus timestamp formatting"""
        timestamp_str = "1234567890.123456789"
        formatted = hcs_service._format_consensus_timestamp(timestamp_str)
        
        # Should return datetime object
        assert isinstance(formatted, datetime)
        assert formatted.year == 2009  # Unix timestamp 1234567890
    
    def test_encode_message_string(self, hcs_service):
        """Test message encoding for strings"""
        message = "Hello, HCS!"
        encoded = hcs_service._encode_message(message)
        
        assert encoded == "Hello, HCS!"
    
    def test_encode_message_dict(self, hcs_service):
        """Test message encoding for dictionaries"""
        message = {"type": "test", "data": "value"}
        encoded = hcs_service._encode_message(message)
        
        import json
        parsed = json.loads(encoded)
        assert parsed == message
    
    def test_decode_base64_message(self, hcs_service):
        """Test base64 message decoding"""
        # "Hello, HCS!" encoded in base64
        base64_message = "SGVsbG8sIEhDUyE="
        decoded = hcs_service._decode_base64_message(base64_message)
        
        assert decoded == "Hello, HCS!"
    
    def test_decode_base64_message_invalid(self, hcs_service):
        """Test base64 message decoding with invalid input"""
        invalid_base64 = "invalid_base64"
        decoded = hcs_service._decode_base64_message(invalid_base64)
        
        # Should return original string if decoding fails
        assert decoded == invalid_base64
