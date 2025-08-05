"""
Hedera Consensus Service (HCS) Integration

Provides HCS topic management, message submission, and consensus operations
for the Circularity Nexus platform.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from hedera import (
    TopicCreateTransaction,
    TopicMessageSubmitTransaction,
    TopicInfoQuery,
    TopicMessageQuery,
    TopicId,
    PublicKey,
    Timestamp
)
from .hedera_client import HederaClient
from ..core.exceptions import BlockchainError

logger = logging.getLogger(__name__)

class HCSService:
    """Hedera Consensus Service integration for topic management and messaging."""
    
    def __init__(self, hedera_client: Optional[HederaClient] = None):
        self.hedera_client = hedera_client or HederaClient()
        self.subscribed_topics: Dict[str, bool] = {}
        self.message_handlers: Dict[str, callable] = {}
    
    async def create_topic(
        self,
        memo: Optional[str] = None,
        admin_key: Optional[PublicKey] = None,
        submit_key: Optional[PublicKey] = None,
        auto_renew_period: int = 7776000  # 90 days in seconds
    ) -> Dict[str, Any]:
        """
        Create a new HCS topic.
        
        Args:
            memo: Topic memo/description
            admin_key: Admin key for topic management
            submit_key: Submit key for message submission (None = public)
            auto_renew_period: Auto-renewal period in seconds
            
        Returns:
            Topic creation result with topic ID
        """
        try:
            transaction = TopicCreateTransaction()
            
            if memo:
                transaction.setTopicMemo(memo)
            
            if admin_key:
                transaction.setAdminKey(admin_key)
            else:
                # Use operator key as admin key
                transaction.setAdminKey(self.hedera_client.operator_private_key.getPublicKey())
            
            if submit_key:
                transaction.setSubmitKey(submit_key)
            
            transaction.setAutoRenewPeriod(auto_renew_period)
            
            # Freeze, sign, and execute
            transaction = transaction.freezeWith(self.hedera_client.client)
            signed_transaction = transaction.sign(self.hedera_client.operator_private_key)
            response = await signed_transaction.execute(self.hedera_client.client)
            receipt = await response.getReceipt(self.hedera_client.client)
            
            topic_id = receipt.topicId
            
            result = {
                "topic_id": str(topic_id),
                "memo": memo,
                "admin_key": str(admin_key) if admin_key else None,
                "submit_key": str(submit_key) if submit_key else "public",
                "auto_renew_period": auto_renew_period,
                "transaction_id": str(response.transactionId),
                "consensus_timestamp": str(receipt.consensusTimestamp) if receipt.consensusTimestamp else None,
                "status": "success"
            }
            
            logger.info(f"Created HCS topic: {topic_id}")
            return result
            
        except Exception as e:
            logger.error(f"Topic creation failed: {str(e)}")
            raise BlockchainError(f"Topic creation failed: {str(e)}")
    
    async def submit_message(
        self,
        topic_id: str,
        message: Union[str, bytes, Dict[str, Any]],
        memo: Optional[str] = None,
        chunk_size: int = 1024
    ) -> Dict[str, Any]:
        """
        Submit message to HCS topic.
        
        Args:
            topic_id: Target topic ID
            message: Message content (string, bytes, or dict)
            memo: Transaction memo
            chunk_size: Chunk size for large messages
            
        Returns:
            Message submission result
        """
        try:
            topic = TopicId.fromString(topic_id)
            
            # Convert message to bytes
            if isinstance(message, dict):
                message_bytes = json.dumps(message).encode('utf-8')
            elif isinstance(message, str):
                message_bytes = message.encode('utf-8')
            else:
                message_bytes = message
            
            # Handle large messages by chunking
            if len(message_bytes) > chunk_size:
                return await self._submit_chunked_message(
                    topic, message_bytes, memo, chunk_size
                )
            
            # Submit single message
            transaction = (
                TopicMessageSubmitTransaction()
                .setTopicId(topic)
                .setMessage(message_bytes)
            )
            
            if memo:
                transaction.setTransactionMemo(memo)
            
            # Freeze, sign, and execute
            transaction = transaction.freezeWith(self.hedera_client.client)
            signed_transaction = transaction.sign(self.hedera_client.operator_private_key)
            response = await signed_transaction.execute(self.hedera_client.client)
            receipt = await response.getReceipt(self.hedera_client.client)
            
            result = {
                "topic_id": topic_id,
                "message_size": len(message_bytes),
                "transaction_id": str(response.transactionId),
                "consensus_timestamp": str(receipt.consensusTimestamp) if receipt.consensusTimestamp else None,
                "sequence_number": receipt.topicSequenceNumber,
                "running_hash": receipt.topicRunningHash.hex() if receipt.topicRunningHash else None,
                "status": "success"
            }
            
            logger.debug(f"Message submitted to topic {topic_id}: {len(message_bytes)} bytes")
            return result
            
        except Exception as e:
            logger.error(f"Message submission failed: {str(e)}")
            raise BlockchainError(f"Message submission failed: {str(e)}")
    
    async def get_topic_info(self, topic_id: str) -> Dict[str, Any]:
        """
        Get topic information and metadata.
        
        Args:
            topic_id: Topic ID to query
            
        Returns:
            Topic information
        """
        try:
            topic = TopicId.fromString(topic_id)
            query = TopicInfoQuery().setTopicId(topic)
            info = await query.execute(self.hedera_client.client)
            
            result = {
                "topic_id": topic_id,
                "memo": info.topicMemo,
                "running_hash": info.runningHash.hex() if info.runningHash else None,
                "sequence_number": info.sequenceNumber,
                "expiration_time": str(info.expirationTime) if info.expirationTime else None,
                "admin_key": str(info.adminKey) if info.adminKey else None,
                "submit_key": str(info.submitKey) if info.submitKey else "public",
                "auto_renew_period": info.autoRenewPeriod.seconds if info.autoRenewPeriod else None,
                "auto_renew_account": str(info.autoRenewAccount) if info.autoRenewAccount else None,
                "ledger_id": str(info.ledgerId) if hasattr(info, 'ledgerId') else None
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Topic info query failed: {str(e)}")
            raise BlockchainError(f"Topic info query failed: {str(e)}")
    
    async def get_topic_messages(
        self,
        topic_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get messages from HCS topic.
        
        Args:
            topic_id: Topic ID to query
            start_time: Start time for message range
            end_time: End time for message range
            limit: Maximum number of messages to return
            
        Returns:
            List of topic messages
        """
        try:
            topic = TopicId.fromString(topic_id)
            query = TopicMessageQuery().setTopicId(topic)
            
            if start_time:
                query.setStartTime(Timestamp.fromDate(start_time))
            
            if end_time:
                query.setEndTime(Timestamp.fromDate(end_time))
            
            query.setLimit(limit)
            
            messages = []
            
            # Execute query and collect messages
            def message_handler(message):
                try:
                    content = message.contents.decode('utf-8')
                    messages.append({
                        "consensus_timestamp": str(message.consensusTimestamp),
                        "sequence_number": message.sequenceNumber,
                        "running_hash": message.runningHash.hex() if message.runningHash else None,
                        "contents": content,
                        "chunk_info": {
                            "initial_transaction_id": str(message.initialTransactionId) if hasattr(message, 'initialTransactionId') else None,
                            "chunk_number": getattr(message, 'chunkNumber', None),
                            "total_chunks": getattr(message, 'totalChunks', None)
                        }
                    })
                except Exception as e:
                    logger.warning(f"Failed to decode message: {str(e)}")
            
            await query.subscribe(self.hedera_client.client, message_handler)
            
            logger.debug(f"Retrieved {len(messages)} messages from topic {topic_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Topic message query failed: {str(e)}")
            raise BlockchainError(f"Topic message query failed: {str(e)}")
    
    async def subscribe_to_topic(
        self,
        topic_id: str,
        message_handler: callable,
        start_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Subscribe to real-time topic messages.
        
        Args:
            topic_id: Topic ID to subscribe to
            message_handler: Function to handle incoming messages
            start_time: Start time for subscription
            
        Returns:
            Subscription result
        """
        try:
            topic = TopicId.fromString(topic_id)
            query = TopicMessageQuery().setTopicId(topic)
            
            if start_time:
                query.setStartTime(Timestamp.fromDate(start_time))
            else:
                # Start from now
                query.setStartTime(Timestamp.fromDate(datetime.utcnow()))
            
            # Wrapper to handle message processing
            def wrapped_handler(message):
                try:
                    processed_message = {
                        "topic_id": topic_id,
                        "consensus_timestamp": str(message.consensusTimestamp),
                        "sequence_number": message.sequenceNumber,
                        "contents": message.contents.decode('utf-8'),
                        "running_hash": message.runningHash.hex() if message.runningHash else None
                    }
                    message_handler(processed_message)
                except Exception as e:
                    logger.error(f"Message handler error: {str(e)}")
            
            # Start subscription
            await query.subscribe(self.hedera_client.client, wrapped_handler)
            
            self.subscribed_topics[topic_id] = True
            self.message_handlers[topic_id] = message_handler
            
            result = {
                "topic_id": topic_id,
                "subscription_status": "active",
                "start_time": start_time.isoformat() + "Z" if start_time else datetime.utcnow().isoformat() + "Z"
            }
            
            logger.info(f"Subscribed to topic {topic_id}")
            return result
            
        except Exception as e:
            logger.error(f"Topic subscription failed: {str(e)}")
            raise BlockchainError(f"Topic subscription failed: {str(e)}")
    
    async def unsubscribe_from_topic(self, topic_id: str) -> Dict[str, Any]:
        """
        Unsubscribe from topic messages.
        
        Args:
            topic_id: Topic ID to unsubscribe from
            
        Returns:
            Unsubscription result
        """
        try:
            if topic_id in self.subscribed_topics:
                del self.subscribed_topics[topic_id]
            
            if topic_id in self.message_handlers:
                del self.message_handlers[topic_id]
            
            result = {
                "topic_id": topic_id,
                "subscription_status": "inactive",
                "unsubscribed_at": datetime.utcnow().isoformat() + "Z"
            }
            
            logger.info(f"Unsubscribed from topic {topic_id}")
            return result
            
        except Exception as e:
            logger.error(f"Topic unsubscription failed: {str(e)}")
            raise BlockchainError(f"Topic unsubscription failed: {str(e)}")
    
    async def _submit_chunked_message(
        self,
        topic: TopicId,
        message_bytes: bytes,
        memo: Optional[str],
        chunk_size: int
    ) -> Dict[str, Any]:
        """Submit large message in chunks."""
        chunks = [message_bytes[i:i + chunk_size] for i in range(0, len(message_bytes), chunk_size)]
        total_chunks = len(chunks)
        
        results = []
        initial_transaction_id = None
        
        for i, chunk in enumerate(chunks):
            transaction = (
                TopicMessageSubmitTransaction()
                .setTopicId(topic)
                .setMessage(chunk)
            )
            
            if memo:
                chunk_memo = f"{memo}:chunk:{i + 1}/{total_chunks}"
                transaction.setTransactionMemo(chunk_memo)
            
            # Freeze, sign, and execute
            transaction = transaction.freezeWith(self.hedera_client.client)
            signed_transaction = transaction.sign(self.hedera_client.operator_private_key)
            response = await signed_transaction.execute(self.hedera_client.client)
            receipt = await response.getReceipt(self.hedera_client.client)
            
            if i == 0:
                initial_transaction_id = str(response.transactionId)
            
            results.append({
                "chunk_number": i + 1,
                "transaction_id": str(response.transactionId),
                "sequence_number": receipt.topicSequenceNumber
            })
        
        return {
            "topic_id": str(topic),
            "message_size": len(message_bytes),
            "total_chunks": total_chunks,
            "initial_transaction_id": initial_transaction_id,
            "chunks": results,
            "status": "success"
        }
    
    def get_subscription_status(self) -> Dict[str, Any]:
        """Get current subscription status."""
        return {
            "subscribed_topics": list(self.subscribed_topics.keys()),
            "active_subscriptions": len(self.subscribed_topics),
            "handlers_registered": len(self.message_handlers)
        }
