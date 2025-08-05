"""
Unit tests for HCS-10 OpenConvAI Agent
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from circularity_nexus.blockchain.hcs10_agent import HCS10Agent, AgentStatus, MessageType, AgentProfile, Connection
from circularity_nexus.core.exceptions import BlockchainError


class TestHCS10Agent:
    """Test cases for HCS10Agent"""
    
    @pytest.fixture
    def agent_profile(self):
        """Sample agent profile"""
        return AgentProfile(
            name="CircularityNexus AI Agent",
            description="AI agent for waste classification and recycling optimization",
            capabilities=["waste_classification", "carbon_calculation", "recycling_advice"],
            version="1.0.0",
            contact_info={"email": "agent@circularitynexus.com"},
            metadata={"platform": "circularity_nexus"}
        )
    
    @pytest.fixture
    def mock_hedera_client(self):
        """Mock HederaClient"""
        with patch('circularity_nexus.blockchain.hcs10_agent.HederaClient') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.operator_private_key.getPublicKey.return_value = Mock()
            yield mock_instance
    
    @pytest.fixture
    def mock_hcs_service(self):
        """Mock HCSService"""
        with patch('circularity_nexus.blockchain.hcs10_agent.HCSService') as mock_hcs:
            mock_instance = Mock()
            mock_hcs.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def hcs10_agent(self, agent_profile, mock_hedera_client, mock_hcs_service):
        """HCS10Agent instance with mocked dependencies"""
        agent = HCS10Agent(
            agent_profile=agent_profile,
            registry_topic_id="0.0.registry"
        )
        agent.hedera_client = mock_hedera_client
        agent.hcs_service = mock_hcs_service
        return agent
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, hcs10_agent, mock_hedera_client, mock_hcs_service):
        """Test successful agent initialization"""
        # Mock account creation
        mock_hedera_client.create_account.return_value = {
            "account_id": "0.0.123456"
        }
        
        # Mock topic creation
        mock_hcs_service.create_topic.side_effect = [
            {"topic_id": "0.0.outbound"},  # Outbound topic
            {"topic_id": "0.0.inbound"},   # Inbound topic
            {"topic_id": "0.0.profile"}    # Profile topic
        ]
        
        # Mock profile publishing
        mock_hcs_service.submit_message.return_value = {"status": "success"}
        
        # Test initialization
        result = await hcs10_agent.initialize()
        
        # Assertions
        assert result["agent_id"] == "0.0.123456"
        assert result["inbound_topic"] == "0.0.inbound"
        assert result["outbound_topic"] == "0.0.outbound"
        assert result["profile_topic"] == "0.0.profile"
        assert result["status"] == AgentStatus.REGISTERED.value
        assert "initialization_timestamp" in result
        
        # Verify agent state
        assert hcs10_agent.status == AgentStatus.REGISTERED
        assert hcs10_agent.account_id == "0.0.123456"
        assert hcs10_agent.inbound_topic_id == "0.0.inbound"
        assert hcs10_agent.outbound_topic_id == "0.0.outbound"
        assert hcs10_agent.profile_topic_id == "0.0.profile"
        
        # Verify service calls
        mock_hedera_client.create_account.assert_called_once()
        assert mock_hcs_service.create_topic.call_count == 3
        mock_hcs_service.submit_message.assert_called_once()  # Profile publishing
    
    @pytest.mark.asyncio
    async def test_register_in_registry_success(self, hcs10_agent, mock_hcs_service):
        """Test successful registry registration"""
        hcs10_agent.account_id = "0.0.123456"
        
        # Mock registry submission
        mock_hcs_service.submit_message.return_value = {
            "transaction_id": "0.0.123456@1234567890.123456789",
            "status": "success"
        }
        
        # Test registration
        result = await hcs10_agent.register_in_registry("0.0.registry")
        
        # Assertions
        assert result["status"] == "success"
        assert "transaction_id" in result
        
        # Verify message format
        call_args = mock_hcs_service.submit_message.call_args
        assert call_args[1]["topic_id"] == "0.0.registry"
        assert call_args[1]["memo"] == "hcs-10:op:0:0"
        
        # Check message content
        import json
        message_content = json.loads(call_args[1]["message"])
        assert message_content["p"] == "hcs-10"
        assert message_content["op"] == "register"
        assert message_content["account_id"] == "0.0.123456"
    
    @pytest.mark.asyncio
    async def test_discover_agents_success(self, hcs10_agent, mock_hcs_service):
        """Test successful agent discovery"""
        hcs10_agent.account_id = "0.0.123456"
        
        # Mock registry messages
        mock_hcs_service.get_topic_messages.return_value = [
            {
                "contents": '{"p": "hcs-10", "op": "register", "account_id": "0.0.789012", "m": "Agent A"}',
                "consensus_timestamp": "1234567890.123456789",
                "sequence_number": 1
            },
            {
                "contents": '{"p": "hcs-10", "op": "register", "account_id": "0.0.345678", "m": "Agent B"}',
                "consensus_timestamp": "1234567891.123456789",
                "sequence_number": 2
            },
            {
                "contents": '{"p": "hcs-10", "op": "register", "account_id": "0.0.123456", "m": "Self"}',
                "consensus_timestamp": "1234567892.123456789",
                "sequence_number": 3
            }
        ]
        
        # Test discovery
        agents = await hcs10_agent.discover_agents("0.0.registry")
        
        # Assertions
        assert len(agents) == 2  # Should exclude self
        assert agents[0]["account_id"] == "0.0.789012"
        assert agents[1]["account_id"] == "0.0.345678"
        assert all("timestamp" in agent for agent in agents)
        assert all("sequence_number" in agent for agent in agents)
    
    @pytest.mark.asyncio
    async def test_request_connection_success(self, hcs10_agent, mock_hcs_service):
        """Test successful connection request"""
        hcs10_agent.account_id = "0.0.123456"
        hcs10_agent.inbound_topic_id = "0.0.inbound"
        
        # Mock finding target agent's inbound topic
        with patch.object(hcs10_agent, '_find_agent_inbound_topic') as mock_find:
            mock_find.return_value = "0.0.target_inbound"
            
            # Mock message submission
            mock_hcs_service.submit_message.return_value = {
                "transaction_id": "0.0.123456@1234567890.123456789",
                "status": "success"
            }
            
            # Test connection request
            result = await hcs10_agent.request_connection("0.0.789012")
            
            # Assertions
            assert result["status"] == "success"
            
            # Verify message format
            call_args = mock_hcs_service.submit_message.call_args
            assert call_args[1]["topic_id"] == "0.0.target_inbound"
            assert call_args[1]["memo"] == "hcs-10:op:3:1"
            
            # Check message content
            import json
            message_content = json.loads(call_args[1]["message"])
            assert message_content["p"] == "hcs-10"
            assert message_content["op"] == "connection_request"
            assert message_content["operator_id"] == "0.0.inbound@0.0.123456"
    
    @pytest.mark.asyncio
    async def test_create_connection_success(self, hcs10_agent, mock_hcs_service):
        """Test successful connection creation"""
        hcs10_agent.account_id = "0.0.123456"
        hcs10_agent.inbound_topic_id = "0.0.inbound"
        
        # Mock connection topic creation
        mock_hcs_service.create_topic.return_value = {
            "topic_id": "0.0.connection"
        }
        
        # Mock connection created message
        mock_hcs_service.submit_message.return_value = {
            "status": "success"
        }
        
        # Mock threshold key creation
        with patch.object(hcs10_agent, '_create_threshold_key') as mock_threshold:
            mock_threshold.return_value = Mock()
            
            # Test connection creation
            result = await hcs10_agent.create_connection(
                requesting_agent_id="0.0.789012",
                requesting_inbound_topic="0.0.requesting_inbound"
            )
            
            # Assertions
            assert result["connection_topic"] == "0.0.connection"
            assert result["remote_agent"] == "0.0.789012"
            assert result["status"] == "active"
            assert "connection_id" in result
            
            # Verify connection is stored
            assert "0.0.789012" in hcs10_agent.connections
            connection = hcs10_agent.connections["0.0.789012"]
            assert connection.remote_agent_id == "0.0.789012"
            assert connection.topic_id == "0.0.connection"
            assert connection.status == "active"
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, hcs10_agent, mock_hcs_service):
        """Test successful message sending"""
        hcs10_agent.account_id = "0.0.123456"
        hcs10_agent.inbound_topic_id = "0.0.inbound"
        
        # Setup connection
        connection = Connection(
            connection_id=12345,
            remote_agent_id="0.0.789012",
            topic_id="0.0.connection",
            status="active",
            created_at=datetime.utcnow()
        )
        hcs10_agent.connections["0.0.789012"] = connection
        
        # Mock message submission
        mock_hcs_service.submit_message.return_value = {
            "transaction_id": "0.0.123456@1234567890.123456789",
            "status": "success"
        }
        
        # Test message sending
        result = await hcs10_agent.send_message(
            target_agent_id="0.0.789012",
            message_data="Hello, Agent B!",
            message_type="greeting"
        )
        
        # Assertions
        assert result["status"] == "success"
        
        # Verify message format
        call_args = mock_hcs_service.submit_message.call_args
        assert call_args[1]["topic_id"] == "0.0.connection"
        assert call_args[1]["memo"] == "hcs-10:op:6:3"
        
        # Check message content
        import json
        message_content = json.loads(call_args[1]["message"])
        assert message_content["p"] == "hcs-10"
        assert message_content["op"] == "message"
        assert message_content["data"] == "Hello, Agent B!"
        
        # Verify connection activity updated
        assert connection.last_activity is not None
    
    @pytest.mark.asyncio
    async def test_send_transaction_request_success(self, hcs10_agent, mock_hcs_service):
        """Test successful transaction request"""
        hcs10_agent.account_id = "0.0.123456"
        hcs10_agent.inbound_topic_id = "0.0.inbound"
        
        # Setup connection
        connection = Connection(
            connection_id=12345,
            remote_agent_id="0.0.789012",
            topic_id="0.0.connection",
            status="active",
            created_at=datetime.utcnow()
        )
        hcs10_agent.connections["0.0.789012"] = connection
        
        # Mock message submission
        mock_hcs_service.submit_message.return_value = {
            "transaction_id": "0.0.123456@1234567890.123456789",
            "status": "success"
        }
        
        transaction_data = {
            "type": "token_transfer",
            "amount": 100,
            "recipient": "0.0.999999"
        }
        
        # Test transaction request
        result = await hcs10_agent.send_transaction_request(
            target_agent_id="0.0.789012",
            transaction_data=transaction_data,
            schedule_id="0.0.schedule123"
        )
        
        # Assertions
        assert result["status"] == "success"
        
        # Verify message format
        call_args = mock_hcs_service.submit_message.call_args
        assert call_args[1]["memo"] == "hcs-10:op:7:3"
        
        # Check message content
        import json
        message_content = json.loads(call_args[1]["message"])
        assert message_content["p"] == "hcs-10"
        assert message_content["op"] == "transaction"
        assert message_content["schedule_id"] == "0.0.schedule123"
        assert json.loads(message_content["data"]) == transaction_data
    
    @pytest.mark.asyncio
    async def test_send_message_no_connection(self, hcs10_agent):
        """Test sending message without active connection"""
        with pytest.raises(BlockchainError) as exc_info:
            await hcs10_agent.send_message(
                target_agent_id="0.0.unknown",
                message_data="Hello"
            )
        
        assert "No active connection" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_agent_status(self, hcs10_agent, agent_profile):
        """Test agent status retrieval"""
        # Setup agent state
        hcs10_agent.account_id = "0.0.123456"
        hcs10_agent.status = AgentStatus.ACTIVE
        hcs10_agent.inbound_topic_id = "0.0.inbound"
        hcs10_agent.outbound_topic_id = "0.0.outbound"
        hcs10_agent.profile_topic_id = "0.0.profile"
        
        # Add some connections
        hcs10_agent.connections["0.0.789012"] = Connection(
            connection_id=1,
            remote_agent_id="0.0.789012",
            topic_id="0.0.conn1",
            status="active",
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        hcs10_agent.connections["0.0.345678"] = Connection(
            connection_id=2,
            remote_agent_id="0.0.345678",
            topic_id="0.0.conn2",
            status="inactive",
            created_at=datetime.utcnow()
        )
        
        # Test status retrieval
        status = await hcs10_agent.get_agent_status()
        
        # Assertions
        assert status["agent_id"] == "0.0.123456"
        assert status["status"] == AgentStatus.ACTIVE.value
        assert status["profile"]["name"] == agent_profile.name
        assert status["profile"]["capabilities"] == agent_profile.capabilities
        assert status["topics"]["inbound"] == "0.0.inbound"
        assert status["topics"]["outbound"] == "0.0.outbound"
        assert status["topics"]["profile"] == "0.0.profile"
        assert status["connections"]["active"] == 1
        assert status["connections"]["total"] == 2
        assert "last_activity" in status
    
    def test_generate_connection_id(self, hcs10_agent):
        """Test connection ID generation"""
        conn_id = hcs10_agent._generate_connection_id()
        
        assert isinstance(conn_id, int)
        assert 10000 <= conn_id <= 99999
    
    @pytest.mark.asyncio
    async def test_initialization_error_handling(self, hcs10_agent, mock_hedera_client):
        """Test error handling during initialization"""
        # Mock account creation failure
        mock_hedera_client.create_account.side_effect = Exception("Account creation failed")
        
        with pytest.raises(BlockchainError) as exc_info:
            await hcs10_agent.initialize()
        
        assert "Agent initialization failed" in str(exc_info.value)
        assert hcs10_agent.status == AgentStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_registry_registration_no_topic(self, hcs10_agent):
        """Test registry registration without topic ID"""
        hcs10_agent.registry_topic_id = None
        
        with pytest.raises(BlockchainError) as exc_info:
            await hcs10_agent.register_in_registry()
        
        assert "No registry topic ID provided" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_discover_agents_invalid_messages(self, hcs10_agent, mock_hcs_service):
        """Test agent discovery with invalid JSON messages"""
        hcs10_agent.account_id = "0.0.123456"
        
        # Mock registry messages with invalid JSON
        mock_hcs_service.get_topic_messages.return_value = [
            {
                "contents": "invalid json",
                "consensus_timestamp": "1234567890.123456789",
                "sequence_number": 1
            },
            {
                "contents": '{"p": "hcs-10", "op": "register", "account_id": "0.0.789012"}',
                "consensus_timestamp": "1234567891.123456789",
                "sequence_number": 2
            }
        ]
        
        # Test discovery (should handle invalid JSON gracefully)
        agents = await hcs10_agent.discover_agents("0.0.registry")
        
        # Should only return valid agents
        assert len(agents) == 1
        assert agents[0]["account_id"] == "0.0.789012"
    
    def test_agent_profile_dataclass(self):
        """Test AgentProfile dataclass"""
        profile = AgentProfile(
            name="Test Agent",
            description="Test description",
            capabilities=["test"],
            version="1.0.0"
        )
        
        assert profile.name == "Test Agent"
        assert profile.description == "Test description"
        assert profile.capabilities == ["test"]
        assert profile.version == "1.0.0"
        assert profile.contact_info is None
        assert profile.metadata is None
    
    def test_connection_dataclass(self):
        """Test Connection dataclass"""
        now = datetime.utcnow()
        connection = Connection(
            connection_id=123,
            remote_agent_id="0.0.789012",
            topic_id="0.0.connection",
            status="active",
            created_at=now
        )
        
        assert connection.connection_id == 123
        assert connection.remote_agent_id == "0.0.789012"
        assert connection.topic_id == "0.0.connection"
        assert connection.status == "active"
        assert connection.created_at == now
        assert connection.last_activity is None
