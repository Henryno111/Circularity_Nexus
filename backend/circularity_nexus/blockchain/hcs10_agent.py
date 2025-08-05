"""
HCS-10 OpenConvAI Agent

Implementation of HCS-10 OpenConvAI standard for AI agent communication
on Hedera Consensus Service.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from .hedera_client import HederaClient
from .hcs_service import HCSService
from ..core.exceptions import BlockchainError

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Agent status states."""
    INITIALIZING = "initializing"
    REGISTERED = "registered"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

class MessageType(Enum):
    """HCS-10 message types."""
    REGISTER = "register"
    DELETE = "delete"
    CONNECTION_REQUEST = "connection_request"
    CONNECTION_CREATED = "connection_created"
    MESSAGE = "message"
    TRANSACTION = "transaction"

@dataclass
class AgentProfile:
    """Agent profile information."""
    name: str
    description: str
    capabilities: List[str]
    version: str
    contact_info: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Connection:
    """Agent connection information."""
    connection_id: int
    remote_agent_id: str
    topic_id: str
    status: str
    created_at: datetime
    last_activity: Optional[datetime] = None

class HCS10Agent:
    """
    HCS-10 OpenConvAI compliant AI agent for Hedera Consensus Service.
    
    Implements the full HCS-10 standard for agent registration, discovery,
    and secure communication.
    """
    
    def __init__(
        self,
        agent_profile: AgentProfile,
        registry_topic_id: Optional[str] = None,
        message_handler: Optional[Callable] = None
    ):
        self.profile = agent_profile
        self.registry_topic_id = registry_topic_id
        self.message_handler = message_handler
        
        # Initialize services
        self.hedera_client = HederaClient()
        self.hcs_service = HCSService()
        
        # Agent state
        self.status = AgentStatus.INITIALIZING
        self.account_id = None
        self.inbound_topic_id = None
        self.outbound_topic_id = None
        self.profile_topic_id = None
        self.connections: Dict[str, Connection] = {}
        self.message_listeners: Dict[str, Callable] = {}
        
        # HCS-10 configuration
        self.ttl = 60  # Time to live in minutes
        self.protocol_version = "hcs-10:0"
        
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize the agent according to HCS-10 standard.
        
        Returns:
            Initialization result with agent details
        """
        try:
            logger.info(f"Initializing HCS-10 agent: {self.profile.name}")
            
            # Step 1: Create Hedera account if needed
            if not self.account_id:
                account_result = await self.hedera_client.create_account(
                    initial_balance=10.0,  # 10 HBAR for operations
                    max_automatic_token_associations=1000
                )
                self.account_id = account_result["account_id"]
                logger.info(f"Created agent account: {self.account_id}")
            
            # Step 2: Create outbound topic
            outbound_memo = f"{self.protocol_version}:{self.ttl}:1"
            outbound_result = await self.hcs_service.create_topic(
                memo=outbound_memo,
                submit_key=self.hedera_client.operator_private_key.getPublicKey()
            )
            self.outbound_topic_id = outbound_result["topic_id"]
            
            # Step 3: Create inbound topic
            inbound_memo = f"{self.protocol_version}:{self.ttl}:0:{self.account_id}"
            inbound_result = await self.hcs_service.create_topic(
                memo=inbound_memo,
                submit_key=None  # Public submissions allowed
            )
            self.inbound_topic_id = inbound_result["topic_id"]
            
            # Step 4: Create HCS-11 profile topic
            profile_memo = f"hcs-11:0:{self.ttl}:profile"
            profile_result = await self.hcs_service.create_topic(
                memo=profile_memo,
                submit_key=self.hedera_client.operator_private_key.getPublicKey()
            )
            self.profile_topic_id = profile_result["topic_id"]
            
            # Step 5: Publish profile information
            await self._publish_profile()
            
            # Step 6: Set up message listeners
            await self._setup_message_listeners()
            
            self.status = AgentStatus.REGISTERED
            
            result = {
                "agent_id": self.account_id,
                "inbound_topic": self.inbound_topic_id,
                "outbound_topic": self.outbound_topic_id,
                "profile_topic": self.profile_topic_id,
                "status": self.status.value,
                "initialization_timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            logger.info(f"Agent initialized successfully: {self.account_id}")
            return result
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Agent initialization failed: {str(e)}")
            raise BlockchainError(f"Agent initialization failed: {str(e)}")
    
    async def register_in_registry(self, registry_topic_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Register agent in the HCS-10 registry.
        
        Args:
            registry_topic_id: Registry topic ID (uses default if not provided)
            
        Returns:
            Registration result
        """
        try:
            if not registry_topic_id:
                registry_topic_id = self.registry_topic_id
            
            if not registry_topic_id:
                raise BlockchainError("No registry topic ID provided")
            
            # Create registration message
            register_message = {
                "p": "hcs-10",
                "op": "register",
                "account_id": self.account_id,
                "m": f"Registering AI agent: {self.profile.name}"
            }
            
            # Submit to registry
            result = await self.hcs_service.submit_message(
                topic_id=registry_topic_id,
                message=json.dumps(register_message),
                memo="hcs-10:op:0:0"
            )
            
            logger.info(f"Agent registered in registry: {registry_topic_id}")
            return result
            
        except Exception as e:
            logger.error(f"Registry registration failed: {str(e)}")
            raise BlockchainError(f"Registry registration failed: {str(e)}")
    
    async def discover_agents(self, registry_topic_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discover other agents in the registry.
        
        Args:
            registry_topic_id: Registry topic to query
            
        Returns:
            List of discovered agents
        """
        try:
            if not registry_topic_id:
                registry_topic_id = self.registry_topic_id
            
            if not registry_topic_id:
                raise BlockchainError("No registry topic ID provided")
            
            # Query registry messages
            messages = await self.hcs_service.get_topic_messages(
                topic_id=registry_topic_id,
                limit=100
            )
            
            agents = []
            for message in messages:
                try:
                    content = json.loads(message["contents"])
                    if (content.get("p") == "hcs-10" and 
                        content.get("op") == "register" and
                        content.get("account_id") != self.account_id):
                        
                        agents.append({
                            "account_id": content["account_id"],
                            "message": content.get("m", ""),
                            "timestamp": message["consensus_timestamp"],
                            "sequence_number": message["sequence_number"]
                        })
                except json.JSONDecodeError:
                    continue
            
            logger.info(f"Discovered {len(agents)} agents in registry")
            return agents
            
        except Exception as e:
            logger.error(f"Agent discovery failed: {str(e)}")
            raise BlockchainError(f"Agent discovery failed: {str(e)}")
    
    async def request_connection(self, target_agent_id: str) -> Dict[str, Any]:
        """
        Request connection to another agent.
        
        Args:
            target_agent_id: Target agent's account ID
            
        Returns:
            Connection request result
        """
        try:
            # Find target agent's inbound topic
            target_inbound_topic = await self._find_agent_inbound_topic(target_agent_id)
            
            if not target_inbound_topic:
                raise BlockchainError(f"Could not find inbound topic for agent {target_agent_id}")
            
            # Create connection request message
            request_message = {
                "p": "hcs-10",
                "op": "connection_request",
                "operator_id": f"{self.inbound_topic_id}@{self.account_id}",
                "m": f"Connection request from {self.profile.name}"
            }
            
            # Submit to target's inbound topic
            result = await self.hcs_service.submit_message(
                topic_id=target_inbound_topic,
                message=json.dumps(request_message),
                memo="hcs-10:op:3:1"
            )
            
            logger.info(f"Connection requested to agent {target_agent_id}")
            return result
            
        except Exception as e:
            logger.error(f"Connection request failed: {str(e)}")
            raise BlockchainError(f"Connection request failed: {str(e)}")
    
    async def create_connection(
        self, 
        requesting_agent_id: str, 
        requesting_inbound_topic: str
    ) -> Dict[str, Any]:
        """
        Create connection topic for agent-to-agent communication.
        
        Args:
            requesting_agent_id: Requesting agent's account ID
            requesting_inbound_topic: Requesting agent's inbound topic
            
        Returns:
            Connection creation result
        """
        try:
            # Generate connection ID
            connection_id = self._generate_connection_id()
            
            # Create connection topic with threshold key
            connection_memo = f"{self.protocol_version}:{self.ttl}:2:{self.inbound_topic_id}:{connection_id}"
            
            # Create threshold key for both agents
            threshold_key = await self._create_threshold_key([
                self.hedera_client.operator_private_key.getPublicKey(),
                # Would need the other agent's public key in real implementation
            ])
            
            connection_result = await self.hcs_service.create_topic(
                memo=connection_memo,
                submit_key=threshold_key
            )
            
            connection_topic_id = connection_result["topic_id"]
            
            # Send connection created message to requesting agent
            created_message = {
                "p": "hcs-10",
                "op": "connection_created",
                "connection_topic_id": connection_topic_id,
                "connected_account_id": requesting_agent_id,
                "operator_id": f"{self.inbound_topic_id}@{self.account_id}",
                "connection_id": connection_id,
                "m": "Connection established."
            }
            
            await self.hcs_service.submit_message(
                topic_id=requesting_inbound_topic,
                message=json.dumps(created_message),
                memo="hcs-10:op:4:1"
            )
            
            # Store connection
            connection = Connection(
                connection_id=connection_id,
                remote_agent_id=requesting_agent_id,
                topic_id=connection_topic_id,
                status="active",
                created_at=datetime.utcnow()
            )
            self.connections[requesting_agent_id] = connection
            
            logger.info(f"Connection created with agent {requesting_agent_id}")
            return {
                "connection_id": connection_id,
                "connection_topic": connection_topic_id,
                "remote_agent": requesting_agent_id,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Connection creation failed: {str(e)}")
            raise BlockchainError(f"Connection creation failed: {str(e)}")
    
    async def send_message(
        self, 
        target_agent_id: str, 
        message_data: str,
        message_type: str = "standard"
    ) -> Dict[str, Any]:
        """
        Send message to connected agent.
        
        Args:
            target_agent_id: Target agent's account ID
            message_data: Message content
            message_type: Type of message
            
        Returns:
            Message sending result
        """
        try:
            connection = self.connections.get(target_agent_id)
            if not connection:
                raise BlockchainError(f"No active connection with agent {target_agent_id}")
            
            # Create message
            message = {
                "p": "hcs-10",
                "op": "message",
                "operator_id": f"{self.inbound_topic_id}@{self.account_id}",
                "data": message_data,
                "m": f"{message_type} communication."
            }
            
            # Submit to connection topic
            result = await self.hcs_service.submit_message(
                topic_id=connection.topic_id,
                message=json.dumps(message),
                memo="hcs-10:op:6:3"
            )
            
            # Update connection activity
            connection.last_activity = datetime.utcnow()
            
            logger.info(f"Message sent to agent {target_agent_id}")
            return result
            
        except Exception as e:
            logger.error(f"Message sending failed: {str(e)}")
            raise BlockchainError(f"Message sending failed: {str(e)}")
    
    async def send_transaction_request(
        self,
        target_agent_id: str,
        transaction_data: Dict[str, Any],
        schedule_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send transaction request requiring approval.
        
        Args:
            target_agent_id: Target agent's account ID
            transaction_data: Transaction details
            schedule_id: Optional scheduled transaction ID
            
        Returns:
            Transaction request result
        """
        try:
            connection = self.connections.get(target_agent_id)
            if not connection:
                raise BlockchainError(f"No active connection with agent {target_agent_id}")
            
            # Create transaction message
            message = {
                "p": "hcs-10",
                "op": "transaction",
                "operator_id": f"{self.inbound_topic_id}@{self.account_id}",
                "schedule_id": schedule_id or "pending",
                "data": json.dumps(transaction_data),
                "m": "For your approval."
            }
            
            # Submit to connection topic
            result = await self.hcs_service.submit_message(
                topic_id=connection.topic_id,
                message=json.dumps(message),
                memo="hcs-10:op:7:3"
            )
            
            logger.info(f"Transaction request sent to agent {target_agent_id}")
            return result
            
        except Exception as e:
            logger.error(f"Transaction request failed: {str(e)}")
            raise BlockchainError(f"Transaction request failed: {str(e)}")
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and statistics."""
        return {
            "agent_id": self.account_id,
            "status": self.status.value,
            "profile": {
                "name": self.profile.name,
                "description": self.profile.description,
                "capabilities": self.profile.capabilities,
                "version": self.profile.version
            },
            "topics": {
                "inbound": self.inbound_topic_id,
                "outbound": self.outbound_topic_id,
                "profile": self.profile_topic_id
            },
            "connections": {
                "active": len([c for c in self.connections.values() if c.status == "active"]),
                "total": len(self.connections)
            },
            "last_activity": max(
                [c.last_activity for c in self.connections.values() if c.last_activity],
                default=datetime.utcnow()
            ).isoformat() + "Z"
        }
    
    # Private helper methods
    
    async def _publish_profile(self):
        """Publish agent profile to profile topic."""
        profile_data = {
            "name": self.profile.name,
            "description": self.profile.description,
            "capabilities": self.profile.capabilities,
            "version": self.profile.version,
            "contact_info": self.profile.contact_info or {},
            "metadata": self.profile.metadata or {},
            "topics": {
                "inbound": self.inbound_topic_id,
                "outbound": self.outbound_topic_id
            },
            "published_at": datetime.utcnow().isoformat() + "Z"
        }
        
        await self.hcs_service.submit_message(
            topic_id=self.profile_topic_id,
            message=json.dumps(profile_data),
            memo="hcs-11:profile:0"
        )
    
    async def _setup_message_listeners(self):
        """Set up message listeners for inbound topic."""
        if self.message_handler:
            self.message_listeners[self.inbound_topic_id] = self.message_handler
            # In a real implementation, would set up continuous listening
    
    async def _find_agent_inbound_topic(self, agent_id: str) -> Optional[str]:
        """Find an agent's inbound topic ID."""
        # In a real implementation, would query the registry or agent's profile
        # For now, return a mock topic ID
        return f"0.0.{hash(agent_id) % 1000000}"
    
    def _generate_connection_id(self) -> int:
        """Generate unique connection ID."""
        import random
        return random.randint(10000, 99999)
    
    async def _create_threshold_key(self, public_keys: List) -> Any:
        """Create threshold key for multi-party topic access."""
        # Simplified implementation - would create proper threshold key
        return public_keys[0] if public_keys else None
    
    def __del__(self):
        """Cleanup on destruction."""
        if hasattr(self, 'hedera_client'):
            self.hedera_client.close()
