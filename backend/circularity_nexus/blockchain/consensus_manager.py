"""
Consensus Manager

High-level consensus service that manages HCS operations for waste tracking,
carbon verification, and audit trails in the Circularity Nexus platform.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime, timedelta
from .hcs_service import HCSService
from .hedera_client import HederaClient
from ..core.exceptions import BlockchainError, ValidationError

logger = logging.getLogger(__name__)

class ConsensusTopicType(Enum):
    """Types of consensus topics in the platform."""
    WASTE_SUBMISSIONS = "waste_submissions"
    CARBON_VERIFICATION = "carbon_verification"
    RECYCLING_EVENTS = "recycling_events"
    AUDIT_TRAIL = "audit_trail"
    MARKETPLACE_ACTIVITY = "marketplace_activity"
    SMART_BIN_DATA = "smart_bin_data"

class MessagePriority(Enum):
    """Message priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ConsensusManager:
    """
    High-level consensus management service for the Circularity Nexus platform.
    
    Manages HCS topics for different types of consensus data and provides
    business logic for waste tracking, verification, and audit trails.
    """
    
    def __init__(self):
        self.hcs_service = HCSService()
        self.hedera_client = HederaClient()
        self.topic_registry: Dict[str, Dict[str, Any]] = {}
        self.active_subscriptions: Dict[str, bool] = {}
    
    async def initialize_platform_topics(self) -> Dict[str, Any]:
        """
        Initialize all platform consensus topics.
        
        Returns:
            Initialization result with topic IDs
        """
        try:
            topics = {}
            
            # Create waste submissions topic
            waste_topic = await self.create_consensus_topic(
                topic_type=ConsensusTopicType.WASTE_SUBMISSIONS,
                description="Waste submission and classification records"
            )
            topics["waste_submissions"] = waste_topic["topic_id"]
            
            # Create carbon verification topic
            carbon_topic = await self.create_consensus_topic(
                topic_type=ConsensusTopicType.CARBON_VERIFICATION,
                description="Carbon impact calculations and verifications"
            )
            topics["carbon_verification"] = carbon_topic["topic_id"]
            
            # Create recycling events topic
            recycling_topic = await self.create_consensus_topic(
                topic_type=ConsensusTopicType.RECYCLING_EVENTS,
                description="Recycling facility events and processing records"
            )
            topics["recycling_events"] = recycling_topic["topic_id"]
            
            # Create audit trail topic
            audit_topic = await self.create_consensus_topic(
                topic_type=ConsensusTopicType.AUDIT_TRAIL,
                description="System audit trail and compliance records"
            )
            topics["audit_trail"] = audit_topic["topic_id"]
            
            # Create marketplace activity topic
            marketplace_topic = await self.create_consensus_topic(
                topic_type=ConsensusTopicType.MARKETPLACE_ACTIVITY,
                description="Token marketplace transactions and activities"
            )
            topics["marketplace_activity"] = marketplace_topic["topic_id"]
            
            # Create smart bin data topic
            smart_bin_topic = await self.create_consensus_topic(
                topic_type=ConsensusTopicType.SMART_BIN_DATA,
                description="Smart bin sensor data and status updates"
            )
            topics["smart_bin_data"] = smart_bin_topic["topic_id"]
            
            result = {
                "platform_topics": topics,
                "total_topics": len(topics),
                "initialization_timestamp": datetime.utcnow().isoformat() + "Z",
                "status": "success"
            }
            
            logger.info(f"Initialized {len(topics)} platform consensus topics")
            return result
            
        except Exception as e:
            logger.error(f"Platform topics initialization failed: {str(e)}")
            raise BlockchainError(f"Platform topics initialization failed: {str(e)}")
    
    async def create_consensus_topic(
        self,
        topic_type: ConsensusTopicType,
        description: str,
        admin_key: Optional[Any] = None,
        submit_key: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Create a consensus topic for a specific purpose.
        
        Args:
            topic_type: Type of consensus topic
            description: Topic description
            admin_key: Admin key for topic management
            submit_key: Submit key for message submission
            
        Returns:
            Topic creation result
        """
        try:
            memo = f"circularity-nexus:{topic_type.value}:{description}"
            
            result = await self.hcs_service.create_topic(
                memo=memo,
                admin_key=admin_key,
                submit_key=submit_key
            )
            
            # Register topic
            topic_info = {
                **result,
                "topic_type": topic_type.value,
                "description": description,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "message_count": 0,
                "last_activity": None
            }
            
            self.topic_registry[result["topic_id"]] = topic_info
            
            logger.info(f"Created consensus topic: {topic_type.value} ({result['topic_id']})")
            return topic_info
            
        except Exception as e:
            logger.error(f"Consensus topic creation failed: {str(e)}")
            raise BlockchainError(f"Consensus topic creation failed: {str(e)}")
    
    async def submit_waste_submission(
        self,
        topic_id: str,
        submission_data: Dict[str, Any],
        priority: MessagePriority = MessagePriority.MEDIUM
    ) -> Dict[str, Any]:
        """
        Submit waste submission record to consensus.
        
        Args:
            topic_id: Waste submissions topic ID
            submission_data: Waste submission data
            priority: Message priority
            
        Returns:
            Submission result
        """
        try:
            # Validate submission data
            required_fields = ["user_id", "waste_type", "weight_kg", "location", "timestamp"]
            for field in required_fields:
                if field not in submission_data:
                    raise ValidationError(f"Missing required field: {field}")
            
            # Create consensus message
            message = {
                "type": "waste_submission",
                "version": "1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "priority": priority.value,
                "data": submission_data,
                "metadata": {
                    "platform": "circularity_nexus",
                    "source": "mobile_app",
                    "verification_status": "pending"
                }
            }
            
            # Submit to consensus
            result = await self.hcs_service.submit_message(
                topic_id=topic_id,
                message=json.dumps(message),
                memo=f"waste_submission:{priority.value}"
            )
            
            # Update topic registry
            if topic_id in self.topic_registry:
                self.topic_registry[topic_id]["message_count"] += 1
                self.topic_registry[topic_id]["last_activity"] = datetime.utcnow().isoformat() + "Z"
            
            result.update({
                "submission_id": submission_data.get("submission_id"),
                "message_type": "waste_submission",
                "priority": priority.value
            })
            
            logger.info(f"Submitted waste submission to consensus: {submission_data.get('submission_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Waste submission to consensus failed: {str(e)}")
            raise BlockchainError(f"Waste submission to consensus failed: {str(e)}")
    
    async def submit_carbon_verification(
        self,
        topic_id: str,
        verification_data: Dict[str, Any],
        priority: MessagePriority = MessagePriority.HIGH
    ) -> Dict[str, Any]:
        """
        Submit carbon verification record to consensus.
        
        Args:
            topic_id: Carbon verification topic ID
            verification_data: Carbon verification data
            priority: Message priority
            
        Returns:
            Verification submission result
        """
        try:
            # Validate verification data
            required_fields = ["calculation_id", "co2_saved_kg", "methodology", "verification_timestamp"]
            for field in required_fields:
                if field not in verification_data:
                    raise ValidationError(f"Missing required field: {field}")
            
            # Create consensus message
            message = {
                "type": "carbon_verification",
                "version": "1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "priority": priority.value,
                "data": verification_data,
                "metadata": {
                    "platform": "circularity_nexus",
                    "verifier": "groq_ai_service",
                    "standard": "ISO_14067"
                }
            }
            
            # Submit to consensus
            result = await self.hcs_service.submit_message(
                topic_id=topic_id,
                message=json.dumps(message),
                memo=f"carbon_verification:{priority.value}"
            )
            
            # Update topic registry
            if topic_id in self.topic_registry:
                self.topic_registry[topic_id]["message_count"] += 1
                self.topic_registry[topic_id]["last_activity"] = datetime.utcnow().isoformat() + "Z"
            
            result.update({
                "calculation_id": verification_data.get("calculation_id"),
                "message_type": "carbon_verification",
                "priority": priority.value
            })
            
            logger.info(f"Submitted carbon verification to consensus: {verification_data.get('calculation_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Carbon verification submission failed: {str(e)}")
            raise BlockchainError(f"Carbon verification submission failed: {str(e)}")
    
    async def submit_recycling_event(
        self,
        topic_id: str,
        event_data: Dict[str, Any],
        priority: MessagePriority = MessagePriority.MEDIUM
    ) -> Dict[str, Any]:
        """
        Submit recycling facility event to consensus.
        
        Args:
            topic_id: Recycling events topic ID
            event_data: Recycling event data
            priority: Message priority
            
        Returns:
            Event submission result
        """
        try:
            # Validate event data
            required_fields = ["facility_id", "event_type", "waste_processed_kg", "timestamp"]
            for field in required_fields:
                if field not in event_data:
                    raise ValidationError(f"Missing required field: {field}")
            
            # Create consensus message
            message = {
                "type": "recycling_event",
                "version": "1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "priority": priority.value,
                "data": event_data,
                "metadata": {
                    "platform": "circularity_nexus",
                    "source": "facility_system",
                    "certification": event_data.get("certification", "ISO_14001")
                }
            }
            
            # Submit to consensus
            result = await self.hcs_service.submit_message(
                topic_id=topic_id,
                message=json.dumps(message),
                memo=f"recycling_event:{priority.value}"
            )
            
            # Update topic registry
            if topic_id in self.topic_registry:
                self.topic_registry[topic_id]["message_count"] += 1
                self.topic_registry[topic_id]["last_activity"] = datetime.utcnow().isoformat() + "Z"
            
            result.update({
                "event_id": event_data.get("event_id"),
                "facility_id": event_data.get("facility_id"),
                "message_type": "recycling_event",
                "priority": priority.value
            })
            
            logger.info(f"Submitted recycling event to consensus: {event_data.get('event_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Recycling event submission failed: {str(e)}")
            raise BlockchainError(f"Recycling event submission failed: {str(e)}")
    
    async def submit_audit_record(
        self,
        topic_id: str,
        audit_data: Dict[str, Any],
        priority: MessagePriority = MessagePriority.HIGH
    ) -> Dict[str, Any]:
        """
        Submit audit record to consensus.
        
        Args:
            topic_id: Audit trail topic ID
            audit_data: Audit record data
            priority: Message priority
            
        Returns:
            Audit submission result
        """
        try:
            # Validate audit data
            required_fields = ["action", "user_id", "resource_type", "resource_id", "timestamp"]
            for field in required_fields:
                if field not in audit_data:
                    raise ValidationError(f"Missing required field: {field}")
            
            # Create consensus message
            message = {
                "type": "audit_record",
                "version": "1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "priority": priority.value,
                "data": audit_data,
                "metadata": {
                    "platform": "circularity_nexus",
                    "audit_type": "system_audit",
                    "compliance_standard": "SOX_404"
                }
            }
            
            # Submit to consensus
            result = await self.hcs_service.submit_message(
                topic_id=topic_id,
                message=json.dumps(message),
                memo=f"audit_record:{priority.value}"
            )
            
            # Update topic registry
            if topic_id in self.topic_registry:
                self.topic_registry[topic_id]["message_count"] += 1
                self.topic_registry[topic_id]["last_activity"] = datetime.utcnow().isoformat() + "Z"
            
            result.update({
                "audit_id": audit_data.get("audit_id"),
                "action": audit_data.get("action"),
                "message_type": "audit_record",
                "priority": priority.value
            })
            
            logger.info(f"Submitted audit record to consensus: {audit_data.get('action')}")
            return result
            
        except Exception as e:
            logger.error(f"Audit record submission failed: {str(e)}")
            raise BlockchainError(f"Audit record submission failed: {str(e)}")
    
    async def submit_smart_bin_data(
        self,
        topic_id: str,
        sensor_data: Dict[str, Any],
        priority: MessagePriority = MessagePriority.LOW
    ) -> Dict[str, Any]:
        """
        Submit smart bin sensor data to consensus.
        
        Args:
            topic_id: Smart bin data topic ID
            sensor_data: Sensor data from smart bins
            priority: Message priority
            
        Returns:
            Data submission result
        """
        try:
            # Validate sensor data
            required_fields = ["bin_id", "location", "fill_level", "timestamp"]
            for field in required_fields:
                if field not in sensor_data:
                    raise ValidationError(f"Missing required field: {field}")
            
            # Create consensus message
            message = {
                "type": "smart_bin_data",
                "version": "1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "priority": priority.value,
                "data": sensor_data,
                "metadata": {
                    "platform": "circularity_nexus",
                    "source": "iot_sensor",
                    "data_quality": "verified"
                }
            }
            
            # Submit to consensus
            result = await self.hcs_service.submit_message(
                topic_id=topic_id,
                message=json.dumps(message),
                memo=f"smart_bin_data:{priority.value}"
            )
            
            # Update topic registry
            if topic_id in self.topic_registry:
                self.topic_registry[topic_id]["message_count"] += 1
                self.topic_registry[topic_id]["last_activity"] = datetime.utcnow().isoformat() + "Z"
            
            result.update({
                "bin_id": sensor_data.get("bin_id"),
                "fill_level": sensor_data.get("fill_level"),
                "message_type": "smart_bin_data",
                "priority": priority.value
            })
            
            logger.debug(f"Submitted smart bin data to consensus: {sensor_data.get('bin_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Smart bin data submission failed: {str(e)}")
            raise BlockchainError(f"Smart bin data submission failed: {str(e)}")
    
    async def query_consensus_history(
        self,
        topic_id: str,
        message_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Query consensus history from a topic.
        
        Args:
            topic_id: Topic ID to query
            message_type: Filter by message type
            start_time: Start time for query range
            end_time: End time for query range
            limit: Maximum number of messages
            
        Returns:
            Consensus history query result
        """
        try:
            # Get messages from HCS
            messages = await self.hcs_service.get_topic_messages(
                topic_id=topic_id,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )
            
            # Filter and process messages
            processed_messages = []
            for message in messages:
                try:
                    content = json.loads(message["contents"])
                    
                    # Filter by message type if specified
                    if message_type and content.get("type") != message_type:
                        continue
                    
                    processed_message = {
                        "consensus_timestamp": message["consensus_timestamp"],
                        "sequence_number": message["sequence_number"],
                        "message_type": content.get("type"),
                        "priority": content.get("priority"),
                        "data": content.get("data"),
                        "metadata": content.get("metadata"),
                        "running_hash": message["running_hash"]
                    }
                    
                    processed_messages.append(processed_message)
                    
                except json.JSONDecodeError:
                    logger.warning(f"Failed to decode message: {message['sequence_number']}")
                    continue
            
            result = {
                "topic_id": topic_id,
                "message_type_filter": message_type,
                "total_messages": len(processed_messages),
                "messages": processed_messages,
                "query_timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            logger.info(f"Queried {len(processed_messages)} consensus messages from {topic_id}")
            return result
            
        except Exception as e:
            logger.error(f"Consensus history query failed: {str(e)}")
            raise BlockchainError(f"Consensus history query failed: {str(e)}")
    
    async def subscribe_to_consensus_updates(
        self,
        topic_id: str,
        message_handler: callable,
        message_type_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Subscribe to real-time consensus updates.
        
        Args:
            topic_id: Topic ID to subscribe to
            message_handler: Function to handle incoming messages
            message_type_filter: Optional filter for message types
            
        Returns:
            Subscription result
        """
        try:
            # Wrapper to filter and process messages
            def filtered_handler(message):
                try:
                    content = json.loads(message["contents"])
                    
                    # Apply message type filter
                    if message_type_filter and content.get("type") != message_type_filter:
                        return
                    
                    processed_message = {
                        "topic_id": message["topic_id"],
                        "consensus_timestamp": message["consensus_timestamp"],
                        "sequence_number": message["sequence_number"],
                        "message_type": content.get("type"),
                        "priority": content.get("priority"),
                        "data": content.get("data"),
                        "metadata": content.get("metadata")
                    }
                    
                    message_handler(processed_message)
                    
                except json.JSONDecodeError:
                    logger.warning(f"Failed to decode consensus message")
                except Exception as e:
                    logger.error(f"Message handler error: {str(e)}")
            
            # Subscribe to HCS topic
            result = await self.hcs_service.subscribe_to_topic(
                topic_id=topic_id,
                message_handler=filtered_handler
            )
            
            self.active_subscriptions[topic_id] = True
            
            result.update({
                "message_type_filter": message_type_filter,
                "subscription_active": True
            })
            
            logger.info(f"Subscribed to consensus updates: {topic_id}")
            return result
            
        except Exception as e:
            logger.error(f"Consensus subscription failed: {str(e)}")
            raise BlockchainError(f"Consensus subscription failed: {str(e)}")
    
    def get_topic_registry(self) -> Dict[str, Any]:
        """Get current topic registry."""
        return {
            "registered_topics": self.topic_registry,
            "active_subscriptions": list(self.active_subscriptions.keys()),
            "total_topics": len(self.topic_registry)
        }
    
    def get_consensus_statistics(self) -> Dict[str, Any]:
        """Get consensus platform statistics."""
        total_messages = sum(topic.get("message_count", 0) for topic in self.topic_registry.values())
        
        topic_stats = {}
        for topic_id, topic_info in self.topic_registry.items():
            topic_stats[topic_info["topic_type"]] = {
                "topic_id": topic_id,
                "message_count": topic_info.get("message_count", 0),
                "last_activity": topic_info.get("last_activity")
            }
        
        return {
            "total_topics": len(self.topic_registry),
            "total_messages": total_messages,
            "active_subscriptions": len(self.active_subscriptions),
            "topic_statistics": topic_stats,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }
