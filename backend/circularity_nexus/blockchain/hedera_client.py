"""
Hedera Client

Core Hedera network client providing connection management and basic operations.
"""

import logging
from typing import Dict, List, Optional, Any
from hedera import (
    Client, 
    AccountId, 
    PrivateKey,
    Hbar,
    AccountCreateTransaction,
    AccountBalanceQuery,
    TransferTransaction,
    Status
)
from ..core.config import get_settings
from ..core.exceptions import BlockchainError

logger = logging.getLogger(__name__)

class HederaClient:
    """Core Hedera network client for blockchain operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.operator_account_id = None
        self.operator_private_key = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Hedera client with network configuration."""
        try:
            # Configure for testnet or mainnet
            if self.settings.hedera_network == "testnet":
                self.client = Client.forTestnet()
            elif self.settings.hedera_network == "mainnet":
                self.client = Client.forMainnet()
            else:
                # Custom network configuration
                self.client = Client.forNetwork(self.settings.hedera_network_nodes)
            
            # Set operator account
            self.operator_account_id = AccountId.fromString(self.settings.hedera_operator_id)
            self.operator_private_key = PrivateKey.fromString(self.settings.hedera_operator_key)
            
            self.client.setOperator(
                self.operator_account_id,
                self.operator_private_key
            )
            
            # Set default transaction fee
            self.client.setDefaultMaxTransactionFee(Hbar.fromTinybars(100_000_000))  # 1 HBAR
            
            logger.info(f"Hedera client initialized for {self.settings.hedera_network}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Hedera client: {str(e)}")
            raise BlockchainError(f"Client initialization failed: {str(e)}")
    
    async def create_account(
        self,
        initial_balance: float = 0.0,
        max_automatic_token_associations: int = 100
    ) -> Dict[str, Any]:
        """
        Create a new Hedera account.
        
        Args:
            initial_balance: Initial HBAR balance
            max_automatic_token_associations: Max automatic token associations
            
        Returns:
            Account creation result with account ID and private key
        """
        try:
            # Generate new key pair
            new_private_key = PrivateKey.generateED25519()
            new_public_key = new_private_key.getPublicKey()
            
            # Create account transaction
            transaction = (
                AccountCreateTransaction()
                .setKey(new_public_key)
                .setInitialBalance(Hbar.from(initial_balance))
                .setMaxAutomaticTokenAssociations(max_automatic_token_associations)
                .freezeWith(self.client)
            )
            
            # Sign and execute
            signed_transaction = transaction.sign(self.operator_private_key)
            response = await signed_transaction.execute(self.client)
            receipt = await response.getReceipt(self.client)
            
            if receipt.status != Status.Success:
                raise BlockchainError(f"Account creation failed: {receipt.status}")
            
            account_id = receipt.accountId
            
            result = {
                "account_id": str(account_id),
                "private_key": str(new_private_key),
                "public_key": str(new_public_key),
                "initial_balance": initial_balance,
                "transaction_id": str(response.transactionId),
                "status": "success"
            }
            
            logger.info(f"Created account: {account_id}")
            return result
            
        except Exception as e:
            logger.error(f"Account creation failed: {str(e)}")
            raise BlockchainError(f"Account creation failed: {str(e)}")
    
    async def get_account_balance(self, account_id: str) -> Dict[str, Any]:
        """
        Get account balance and token holdings.
        
        Args:
            account_id: Account ID to query
            
        Returns:
            Account balance information
        """
        try:
            account = AccountId.fromString(account_id)
            
            query = AccountBalanceQuery().setAccountId(account)
            balance = await query.execute(self.client)
            
            result = {
                "account_id": account_id,
                "hbar_balance": float(balance.hbars.toTinybars()) / 100_000_000,  # Convert to HBAR
                "tokens": {}
            }
            
            # Add token balances
            for token_id, token_balance in balance.tokens.items():
                result["tokens"][str(token_id)] = int(token_balance)
            
            logger.debug(f"Retrieved balance for {account_id}: {result['hbar_balance']} HBAR")
            return result
            
        except Exception as e:
            logger.error(f"Balance query failed for {account_id}: {str(e)}")
            raise BlockchainError(f"Balance query failed: {str(e)}")
    
    async def transfer_hbar(
        self,
        to_account_id: str,
        amount: float,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transfer HBAR between accounts.
        
        Args:
            to_account_id: Recipient account ID
            amount: Amount in HBAR
            memo: Optional transaction memo
            
        Returns:
            Transfer transaction result
        """
        try:
            to_account = AccountId.fromString(to_account_id)
            transfer_amount = Hbar.from(amount)
            
            transaction = (
                TransferTransaction()
                .addHbarTransfer(self.operator_account_id, transfer_amount.negated())
                .addHbarTransfer(to_account, transfer_amount)
            )
            
            if memo:
                transaction.setTransactionMemo(memo)
            
            # Freeze, sign, and execute
            transaction = transaction.freezeWith(self.client)
            signed_transaction = transaction.sign(self.operator_private_key)
            response = await signed_transaction.execute(self.client)
            receipt = await response.getReceipt(self.client)
            
            if receipt.status != Status.Success:
                raise BlockchainError(f"Transfer failed: {receipt.status}")
            
            result = {
                "transaction_id": str(response.transactionId),
                "from_account": str(self.operator_account_id),
                "to_account": to_account_id,
                "amount": amount,
                "memo": memo,
                "status": "success",
                "consensus_timestamp": str(receipt.consensusTimestamp) if receipt.consensusTimestamp else None
            }
            
            logger.info(f"Transferred {amount} HBAR to {to_account_id}")
            return result
            
        except Exception as e:
            logger.error(f"HBAR transfer failed: {str(e)}")
            raise BlockchainError(f"HBAR transfer failed: {str(e)}")
    
    async def get_transaction_record(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get detailed transaction record.
        
        Args:
            transaction_id: Transaction ID to query
            
        Returns:
            Transaction record details
        """
        try:
            from hedera import TransactionId, TransactionRecordQuery
            
            tx_id = TransactionId.fromString(transaction_id)
            query = TransactionRecordQuery().setTransactionId(tx_id)
            record = await query.execute(self.client)
            
            result = {
                "transaction_id": transaction_id,
                "consensus_timestamp": str(record.consensusTimestamp),
                "transaction_fee": float(record.transactionFee.toTinybars()) / 100_000_000,
                "transaction_memo": record.transactionMemo,
                "status": str(record.receipt.status),
                "transfers": []
            }
            
            # Add transfer details
            for account_id, amount in record.transferList.items():
                result["transfers"].append({
                    "account_id": str(account_id),
                    "amount": float(amount.toTinybars()) / 100_000_000
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Transaction record query failed: {str(e)}")
            raise BlockchainError(f"Transaction record query failed: {str(e)}")
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get current network information."""
        return {
            "network": self.settings.hedera_network,
            "operator_account": str(self.operator_account_id),
            "client_status": "connected" if self.client else "disconnected",
            "network_nodes": getattr(self.settings, 'hedera_network_nodes', {}),
            "max_transaction_fee": "1 HBAR"
        }
    
    async def ping_network(self) -> bool:
        """
        Ping the network to check connectivity.
        
        Returns:
            True if network is reachable
        """
        try:
            # Simple balance query to test connectivity
            await self.get_account_balance(str(self.operator_account_id))
            return True
        except Exception as e:
            logger.warning(f"Network ping failed: {str(e)}")
            return False
    
    def close(self):
        """Close the client connection."""
        if self.client:
            self.client.close()
            logger.info("Hedera client connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
