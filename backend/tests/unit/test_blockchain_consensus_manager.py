"""
Unit tests for Blockchain Consensus Manager
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from circularity_nexus.blockchain.consensus_manager import ConsensusManager, TopicType
from circularity_nexus.core.exceptions import BlockchainError, ValidationError


class TestConsensusManager:
    """Test cases for ConsensusManager"""
    
    @pytest.fixture
    def mock_hcs_service(self):
        """Mock HCSService"""
        with patch('circularity_nexus.blockchain.consensus_manager.HCSService') as mock_hcs:
            mock_instance = Mock()
            mock_hcs.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def mock_hedera_client(self):
        """Mock HederaClient"""
        with patch('circularity_nexus.blockchain.consensus_manager.HederaClient') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def consensus_manager(self, mock_hcs_service, mock_hedera_client):
        """ConsensusManager instance with mocked dependencies"""
        manager = ConsensusManager()
        manager.hcs_service = mock_hcs_service
        manager.hedera_client = mock_hedera_client
        return manager
    
    @pytest.mark.asyncio
    async def test_initialize_topics_success(self, consensus_manager, mock_hcs_service):
        """Test successful topic initialization"""
        # Mock topic creation responses
        mock_hcs_service.create_topic.side_effect = [
            {"topic_id": "0.0.100001"},  # waste_submissions
            {"topic_id": "0.0.100002"},  # carbon_verification
            {"topic_id": "0.0.100003"},  # recycling_events
            {"topic_id": "0.0.100004"},  # audit_trail
            {"topic_id": "0.0.100005"},  # marketplace_activity
            {"topic_id": "0.0.100006"}   # smart_bin_data
        ]
        
        # Test initialization
        result = await consensus_manager.initialize_topics()
        
        # Assertions
        assert result["waste_submissions"] == "0.0.100001"
        assert result["carbon_verification"] == "0.0.100002"
        assert result["recycling_events"] == "0.0.100003"
        assert result["audit_trail"] == "0.0.100004"
        assert result["marketplace_activity"] == "0.0.100005"
        assert result["smart_bin_data"] == "0.0.100006"
        
        # Verify topics are stored
        assert consensus_manager.topics[TopicType.WASTE_SUBMISSIONS] == "0.0.100001"
        assert consensus_manager.topics[TopicType.CARBON_VERIFICATION] == "0.0.100002"
        assert consensus_manager.topics[TopicType.RECYCLING_EVENTS] == "0.0.100003"
        assert consensus_manager.topics[TopicType.AUDIT_TRAIL] == "0.0.100004"
        assert consensus_manager.topics[TopicType.MARKETPLACE_ACTIVITY] == "0.0.100005"
        assert consensus_manager.topics[TopicType.SMART_BIN_DATA] == "0.0.100006"
        
        # Verify HCS service was called 6 times
        assert mock_hcs_service.create_topic.call_count == 6
    
    @pytest.mark.asyncio
    async def test_submit_waste_submission_success(self, consensus_manager, mock_hcs_service):
        """Test successful waste submission to consensus"""
        # Setup topics
        consensus_manager.topics[TopicType.WASTE_SUBMISSIONS] = "0.0.100001"
        
        # Mock message submission
        mock_hcs_service.submit_message.return_value = {
            "transaction_id": "0.0.123456@1234567890.123456789",
            "sequence_number": 42,
            "consensus_timestamp": "1234567890.123456789",
            "status": "success"
        }
        
        submission_data = {
            "user_id": "user123",
            "waste_type": "PET_PLASTIC",
            "weight_kg": 2.5,
            "location": {"lat": 40.7128, "lng": -74.0060},
            "image_hash": "abc123def456",
            "classification_confidence": 0.95
        }
        
        # Test submission
        result = await consensus_manager.submit_waste_submission(submission_data)
        
        # Assertions
        assert result["transaction_id"] == "0.0.123456@1234567890.123456789"
        assert result["sequence_number"] == 42
        assert result["consensus_timestamp"] == "1234567890.123456789"
        assert result["topic_id"] == "0.0.100001"
        assert result["status"] == "success"
        
        # Verify message format
        call_args = mock_hcs_service.submit_message.call_args
        assert call_args[1]["topic_id"] == "0.0.100001"
        assert call_args[1]["memo"] == "waste_submission"
        
        # Check message content
        import json
        message_content = json.loads(call_args[1]["message"])
        assert message_content["type"] == "waste_submission"
        assert message_content["data"] == submission_data
        assert "timestamp" in message_content
    
    @pytest.mark.asyncio
    async def test_submit_carbon_verification_success(self, consensus_manager, mock_hcs_service):
        """Test successful carbon verification submission"""
        # Setup topics
        consensus_manager.topics[TopicType.CARBON_VERIFICATION] = "0.0.100002"
        
        # Mock message submission
        mock_hcs_service.submit_message.return_value = {
            "transaction_id": "0.0.123456@1234567890.123456789",
            "status": "success"
        }
        
        verification_data = {
            "submission_id": "sub123",
            "co2_saved_kg": 5.2,
            "carbon_credits": 0.0052,
            "verification_method": "LCA",
            "auditor": "Third Party Verifier",
            "verification_timestamp": "2024-01-15T10:30:00Z"
        }
        
        # Test verification submission
        result = await consensus_manager.submit_carbon_verification(verification_data)
        
        # Assertions
        assert result["status"] == "success"
        
        # Verify message format
        call_args = mock_hcs_service.submit_message.call_args
        assert call_args[1]["topic_id"] == "0.0.100002"
        assert call_args[1]["memo"] == "carbon_verification"
        
        # Check message content
        import json
        message_content = json.loads(call_args[1]["message"])
        assert message_content["type"] == "carbon_verification"
        assert message_content["data"] == verification_data
    
    @pytest.mark.asyncio
    async def test_submit_recycling_event_success(self, consensus_manager, mock_hcs_service):
        """Test successful recycling event submission"""
        # Setup topics
        consensus_manager.topics[TopicType.RECYCLING_EVENTS] = "0.0.100003"
        
        # Mock message submission
        mock_hcs_service.submit_message.return_value = {
            "transaction_id": "0.0.123456@1234567890.123456789",
            "status": "success"
        }
        
        event_data = {
            "event_type": "COLLECTION",
            "waste_submissions": ["sub123", "sub124", "sub125"],
            "facility_id": "facility789",
            "total_weight_kg": 15.7,
            "processing_method": "MECHANICAL_RECYCLING",
            "output_materials": ["PET_FLAKES", "FIBER"],
            "efficiency_rate": 0.85
        }
        
        # Test event submission
        result = await consensus_manager.submit_recycling_event(event_data)
        
        # Assertions
        assert result["status"] == "success"
        
        # Verify message format
        call_args = mock_hcs_service.submit_message.call_args
        assert call_args[1]["topic_id"] == "0.0.100003"
        assert call_args[1]["memo"] == "recycling_event"
        
        # Check message content
        import json
        message_content = json.loads(call_args[1]["message"])
        assert message_content["type"] == "recycling_event"
        assert message_content["data"] == event_data
    
    @pytest.mark.asyncio
    async def test_submit_audit_record_success(self, consensus_manager, mock_hcs_service):
        """Test successful audit record submission"""
        # Setup topics
        consensus_manager.topics[TopicType.AUDIT_TRAIL] = "0.0.100004"
        
        # Mock message submission
        mock_hcs_service.submit_message.return_value = {
            "transaction_id": "0.0.123456@1234567890.123456789",
            "status": "success"
        }
        
        audit_data = {
            "action": "TOKEN_MINT",
            "entity_type": "WASTE_TOKEN",
            "entity_id": "0.0.token123",
            "actor": "0.0.123456",
            "details": {
                "amount": 250,
                "recipient": "0.0.789012",
                "waste_type": "PET_PLASTIC",
                "quality_grade": "GOOD"
            },
            "previous_state": None,
            "new_state": {"total_supply": 250}
        }
        
        # Test audit submission
        result = await consensus_manager.submit_audit_record(audit_data)
        
        # Assertions
        assert result["status"] == "success"
        
        # Verify message format
        call_args = mock_hcs_service.submit_message.call_args
        assert call_args[1]["topic_id"] == "0.0.100004"
        assert call_args[1]["memo"] == "audit_record"
        
        # Check message content
        import json
        message_content = json.loads(call_args[1]["message"])
        assert message_content["type"] == "audit_record"
        assert message_content["data"] == audit_data
    
    @pytest.mark.asyncio
    async def test_submit_marketplace_activity_success(self, consensus_manager, mock_hcs_service):
        """Test successful marketplace activity submission"""
        # Setup topics
        consensus_manager.topics[TopicType.MARKETPLACE_ACTIVITY] = "0.0.100005"
        
        # Mock message submission
        mock_hcs_service.submit_message.return_value = {
            "transaction_id": "0.0.123456@1234567890.123456789",
            "status": "success"
        }
        
        activity_data = {
            "activity_type": "TOKEN_TRADE",
            "seller": "0.0.123456",
            "buyer": "0.0.789012",
            "token_id": "0.0.token123",
            "amount": 100,
            "price_hbar": 5.0,
            "trade_timestamp": "2024-01-15T14:30:00Z"
        }
        
        # Test activity submission
        result = await consensus_manager.submit_marketplace_activity(activity_data)
        
        # Assertions
        assert result["status"] == "success"
        
        # Verify message format
        call_args = mock_hcs_service.submit_message.call_args
        assert call_args[1]["topic_id"] == "0.0.100005"
        assert call_args[1]["memo"] == "marketplace_activity"
    
    @pytest.mark.asyncio
    async def test_submit_smart_bin_data_success(self, consensus_manager, mock_hcs_service):
        """Test successful smart bin data submission"""
        # Setup topics
        consensus_manager.topics[TopicType.SMART_BIN_DATA] = "0.0.100006"
        
        # Mock message submission
        mock_hcs_service.submit_message.return_value = {
            "transaction_id": "0.0.123456@1234567890.123456789",
            "status": "success"
        }
        
        bin_data = {
            "bin_id": "bin_001",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "fill_level": 0.75,
            "weight_kg": 12.3,
            "temperature_c": 22.5,
            "last_emptied": "2024-01-14T08:00:00Z",
            "waste_types_detected": ["PET_PLASTIC", "ALUMINUM"],
            "sensor_readings": {
                "ultrasonic_distance_cm": 25,
                "load_cell_kg": 12.3,
                "temperature_sensor_c": 22.5
            }
        }
        
        # Test bin data submission
        result = await consensus_manager.submit_smart_bin_data(bin_data)
        
        # Assertions
        assert result["status"] == "success"
        
        # Verify message format
        call_args = mock_hcs_service.submit_message.call_args
        assert call_args[1]["topic_id"] == "0.0.100006"
        assert call_args[1]["memo"] == "smart_bin_data"
    
    @pytest.mark.asyncio
    async def test_get_topic_messages_success(self, consensus_manager, mock_hcs_service):
        """Test successful topic message retrieval"""
        # Setup topics
        consensus_manager.topics[TopicType.WASTE_SUBMISSIONS] = "0.0.100001"
        
        # Mock message retrieval
        mock_hcs_service.get_topic_messages.return_value = [
            {
                "contents": '{"type": "waste_submission", "data": {"user_id": "user1"}}',
                "consensus_timestamp": "1234567890.123456789",
                "sequence_number": 1
            },
            {
                "contents": '{"type": "waste_submission", "data": {"user_id": "user2"}}',
                "consensus_timestamp": "1234567891.123456789",
                "sequence_number": 2
            }
        ]
        
        # Test message retrieval
        messages = await consensus_manager.get_topic_messages(
            TopicType.WASTE_SUBMISSIONS,
            limit=10
        )
        
        # Assertions
        assert len(messages) == 2
        assert messages[0]["sequence_number"] == 1
        assert messages[1]["sequence_number"] == 2
        
        # Check parsed content
        import json
        content1 = json.loads(messages[0]["contents"])
        assert content1["type"] == "waste_submission"
        assert content1["data"]["user_id"] == "user1"
        
        # Verify HCS service was called correctly
        mock_hcs_service.get_topic_messages.assert_called_once_with(
            topic_id="0.0.100001",
            limit=10,
            start_time=None
        )
    
    @pytest.mark.asyncio
    async def test_get_topic_messages_with_filters(self, consensus_manager, mock_hcs_service):
        """Test topic message retrieval with filters"""
        # Setup topics
        consensus_manager.topics[TopicType.CARBON_VERIFICATION] = "0.0.100002"
        
        # Mock message retrieval
        mock_hcs_service.get_topic_messages.return_value = [
            {
                "contents": '{"type": "carbon_verification", "data": {"co2_saved_kg": 5.0}}',
                "consensus_timestamp": "1234567890.123456789",
                "sequence_number": 1
            }
        ]
        
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        
        # Test message retrieval with filters
        messages = await consensus_manager.get_topic_messages(
            TopicType.CARBON_VERIFICATION,
            limit=5,
            start_time=start_time
        )
        
        # Verify HCS service was called with correct parameters
        mock_hcs_service.get_topic_messages.assert_called_once_with(
            topic_id="0.0.100002",
            limit=5,
            start_time=start_time
        )
    
    @pytest.mark.asyncio
    async def test_get_consensus_statistics_success(self, consensus_manager, mock_hcs_service):
        """Test successful consensus statistics retrieval"""
        # Setup topics
        consensus_manager.topics = {
            TopicType.WASTE_SUBMISSIONS: "0.0.100001",
            TopicType.CARBON_VERIFICATION: "0.0.100002",
            TopicType.RECYCLING_EVENTS: "0.0.100003"
        }
        
        # Mock topic info responses
        mock_hcs_service.get_topic_info.side_effect = [
            {
                "topic_id": "0.0.100001",
                "sequence_number": 150,
                "running_hash": "hash1",
                "expiry_time": None
            },
            {
                "topic_id": "0.0.100002",
                "sequence_number": 75,
                "running_hash": "hash2",
                "expiry_time": None
            },
            {
                "topic_id": "0.0.100003",
                "sequence_number": 25,
                "running_hash": "hash3",
                "expiry_time": None
            }
        ]
        
        # Test statistics retrieval
        stats = await consensus_manager.get_consensus_statistics()
        
        # Assertions
        assert stats["total_topics"] == 3
        assert stats["total_messages"] == 250  # 150 + 75 + 25
        
        # Check individual topic stats
        topic_stats = stats["topic_statistics"]
        assert len(topic_stats) == 3
        
        waste_stats = next(t for t in topic_stats if t["topic_type"] == "WASTE_SUBMISSIONS")
        assert waste_stats["topic_id"] == "0.0.100001"
        assert waste_stats["message_count"] == 150
        
        carbon_stats = next(t for t in topic_stats if t["topic_type"] == "CARBON_VERIFICATION")
        assert carbon_stats["message_count"] == 75
        
        recycling_stats = next(t for t in topic_stats if t["topic_type"] == "RECYCLING_EVENTS")
        assert recycling_stats["message_count"] == 25
    
    @pytest.mark.asyncio
    async def test_submit_without_topic_initialization(self, consensus_manager):
        """Test submission without topic initialization"""
        with pytest.raises(BlockchainError) as exc_info:
            await consensus_manager.submit_waste_submission({"test": "data"})
        
        assert "Topic not initialized" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_invalid_submission_data(self, consensus_manager):
        """Test submission with invalid data"""
        # Setup topics
        consensus_manager.topics[TopicType.WASTE_SUBMISSIONS] = "0.0.100001"
        
        with pytest.raises(ValidationError) as exc_info:
            await consensus_manager.submit_waste_submission(None)
        
        assert "Submission data cannot be None" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_hcs_service_error_handling(self, consensus_manager, mock_hcs_service):
        """Test error handling when HCS service fails"""
        # Setup topics
        consensus_manager.topics[TopicType.WASTE_SUBMISSIONS] = "0.0.100001"
        
        # Mock HCS service failure
        mock_hcs_service.submit_message.side_effect = Exception("HCS API error")
        
        with pytest.raises(BlockchainError) as exc_info:
            await consensus_manager.submit_waste_submission({"test": "data"})
        
        assert "Failed to submit waste submission" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_topic_initialization_partial_failure(self, consensus_manager, mock_hcs_service):
        """Test topic initialization with partial failures"""
        # Mock some successful and some failed topic creations
        mock_hcs_service.create_topic.side_effect = [
            {"topic_id": "0.0.100001"},  # waste_submissions - success
            Exception("Topic creation failed"),  # carbon_verification - failure
            {"topic_id": "0.0.100003"},  # recycling_events - success
            {"topic_id": "0.0.100004"},  # audit_trail - success
            {"topic_id": "0.0.100005"},  # marketplace_activity - success
            {"topic_id": "0.0.100006"}   # smart_bin_data - success
        ]
        
        with pytest.raises(BlockchainError) as exc_info:
            await consensus_manager.initialize_topics()
        
        assert "Failed to initialize topics" in str(exc_info.value)
    
    def test_topic_type_enum(self):
        """Test TopicType enum values"""
        assert TopicType.WASTE_SUBMISSIONS.value == "waste_submissions"
        assert TopicType.CARBON_VERIFICATION.value == "carbon_verification"
        assert TopicType.RECYCLING_EVENTS.value == "recycling_events"
        assert TopicType.AUDIT_TRAIL.value == "audit_trail"
        assert TopicType.MARKETPLACE_ACTIVITY.value == "marketplace_activity"
        assert TopicType.SMART_BIN_DATA.value == "smart_bin_data"
    
    def test_format_message_content(self, consensus_manager):
        """Test message content formatting"""
        data = {"test": "value", "number": 42}
        
        content = consensus_manager._format_message_content("test_type", data)
        
        import json
        parsed = json.loads(content)
        assert parsed["type"] == "test_type"
        assert parsed["data"] == data
        assert "timestamp" in parsed
        assert "platform" in parsed
        assert parsed["platform"] == "circularity_nexus"
    
    @pytest.mark.asyncio
    async def test_get_topic_messages_invalid_topic(self, consensus_manager):
        """Test getting messages from uninitialized topic"""
        with pytest.raises(BlockchainError) as exc_info:
            await consensus_manager.get_topic_messages(TopicType.WASTE_SUBMISSIONS)
        
        assert "Topic not initialized" in str(exc_info.value)
