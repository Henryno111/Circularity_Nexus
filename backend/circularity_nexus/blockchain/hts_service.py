"""
Hedera Token Service (HTS) Integration

Provides HTS token creation, management, and operations for waste tokens,
carbon credits, and other tokenized assets in the Circularity Nexus platform.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from hedera import (
    TokenCreateTransaction,
    TokenMintTransaction,
    TokenBurnTransaction,
    TokenAssociateTransaction,
    TokenDissociateTransaction,
    TokenTransferTransaction,
    TokenInfoQuery,
    TokenBalanceQuery,
    TokenId,
    AccountId,
    PublicKey,
    TokenType,
    TokenSupplyType,
    TokenFreezeStatus,
    TokenKycStatus,
    Hbar
)
from .hedera_client import HederaClient
from ..core.exceptions import BlockchainError

logger = logging.getLogger(__name__)

class HTSService:
    """Hedera Token Service integration for token management and operations."""
    
    def __init__(self, hedera_client: Optional[HederaClient] = None):
        self.hedera_client = hedera_client or HederaClient()
        self.token_cache: Dict[str, Dict[str, Any]] = {}
    
    async def create_fungible_token(
        self,
        name: str,
        symbol: str,
        decimals: int = 2,
        initial_supply: int = 0,
        max_supply: Optional[int] = None,
        treasury_account: Optional[str] = None,
        admin_key: Optional[PublicKey] = None,
        supply_key: Optional[PublicKey] = None,
        freeze_key: Optional[PublicKey] = None,
        wipe_key: Optional[PublicKey] = None,
        kyc_key: Optional[PublicKey] = None,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new fungible token (e.g., waste tokens, carbon credits).
        
        Args:
            name: Token name
            symbol: Token symbol
            decimals: Number of decimal places
            initial_supply: Initial token supply
            max_supply: Maximum token supply (None for unlimited)
            treasury_account: Treasury account ID
            admin_key: Admin key for token management
            supply_key: Supply key for minting/burning
            freeze_key: Freeze key for account freezing
            wipe_key: Wipe key for token wiping
            kyc_key: KYC key for account verification
            memo: Token memo/description
            
        Returns:
            Token creation result
        """
        try:
            transaction = TokenCreateTransaction()
            
            # Basic token properties
            transaction.setTokenName(name)
            transaction.setTokenSymbol(symbol)
            transaction.setDecimals(decimals)
            transaction.setTokenType(TokenType.FUNGIBLE_COMMON)
            
            # Supply configuration
            if max_supply is not None:
                transaction.setSupplyType(TokenSupplyType.FINITE)
                transaction.setMaxSupply(max_supply)
            else:
                transaction.setSupplyType(TokenSupplyType.INFINITE)
            
            transaction.setInitialSupply(initial_supply)
            
            # Treasury account
            if treasury_account:
                transaction.setTreasuryAccountId(AccountId.fromString(treasury_account))
            else:
                transaction.setTreasuryAccountId(self.hedera_client.operator_account_id)
            
            # Keys configuration
            if admin_key:
                transaction.setAdminKey(admin_key)
            else:
                transaction.setAdminKey(self.hedera_client.operator_private_key.getPublicKey())
            
            if supply_key:
                transaction.setSupplyKey(supply_key)
            else:
                transaction.setSupplyKey(self.hedera_client.operator_private_key.getPublicKey())
            
            if freeze_key:
                transaction.setFreezeKey(freeze_key)
            
            if wipe_key:
                transaction.setWipeKey(wipe_key)
            
            if kyc_key:
                transaction.setKycKey(kyc_key)
            
            # Optional memo
            if memo:
                transaction.setTokenMemo(memo)
            
            # Default settings
            transaction.setFreezeDefault(False)  # Accounts not frozen by default
            
            # Freeze, sign, and execute
            transaction = transaction.freezeWith(self.hedera_client.client)
            signed_transaction = transaction.sign(self.hedera_client.operator_private_key)
            response = await signed_transaction.execute(self.hedera_client.client)
            receipt = await response.getReceipt(self.hedera_client.client)
            
            token_id = receipt.tokenId
            
            result = {
                "token_id": str(token_id),
                "name": name,
                "symbol": symbol,
                "decimals": decimals,
                "initial_supply": initial_supply,
                "max_supply": max_supply,
                "treasury_account": treasury_account or str(self.hedera_client.operator_account_id),
                "token_type": "fungible",
                "supply_type": "finite" if max_supply else "infinite",
                "transaction_id": str(response.transactionId),
                "status": "success"
            }
            
            # Cache token info
            self.token_cache[str(token_id)] = result
            
            logger.info(f"Created fungible token: {symbol} ({token_id})")
            return result
            
        except Exception as e:
            logger.error(f"Fungible token creation failed: {str(e)}")
            raise BlockchainError(f"Fungible token creation failed: {str(e)}")
    
    async def create_nft_collection(
        self,
        name: str,
        symbol: str,
        max_supply: Optional[int] = None,
        treasury_account: Optional[str] = None,
        admin_key: Optional[PublicKey] = None,
        supply_key: Optional[PublicKey] = None,
        freeze_key: Optional[PublicKey] = None,
        wipe_key: Optional[PublicKey] = None,
        kyc_key: Optional[PublicKey] = None,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new NFT collection (e.g., unique waste items, certificates).
        
        Args:
            name: Collection name
            symbol: Collection symbol
            max_supply: Maximum number of NFTs
            treasury_account: Treasury account ID
            admin_key: Admin key for collection management
            supply_key: Supply key for minting NFTs
            freeze_key: Freeze key for account freezing
            wipe_key: Wipe key for NFT wiping
            kyc_key: KYC key for account verification
            memo: Collection memo/description
            
        Returns:
            NFT collection creation result
        """
        try:
            transaction = TokenCreateTransaction()
            
            # Basic NFT properties
            transaction.setTokenName(name)
            transaction.setTokenSymbol(symbol)
            transaction.setTokenType(TokenType.NON_FUNGIBLE_UNIQUE)
            transaction.setDecimals(0)  # NFTs have 0 decimals
            
            # Supply configuration
            if max_supply is not None:
                transaction.setSupplyType(TokenSupplyType.FINITE)
                transaction.setMaxSupply(max_supply)
            else:
                transaction.setSupplyType(TokenSupplyType.INFINITE)
            
            transaction.setInitialSupply(0)  # NFTs start with 0 supply
            
            # Treasury account
            if treasury_account:
                transaction.setTreasuryAccountId(AccountId.fromString(treasury_account))
            else:
                transaction.setTreasuryAccountId(self.hedera_client.operator_account_id)
            
            # Keys configuration
            if admin_key:
                transaction.setAdminKey(admin_key)
            else:
                transaction.setAdminKey(self.hedera_client.operator_private_key.getPublicKey())
            
            if supply_key:
                transaction.setSupplyKey(supply_key)
            else:
                transaction.setSupplyKey(self.hedera_client.operator_private_key.getPublicKey())
            
            if freeze_key:
                transaction.setFreezeKey(freeze_key)
            
            if wipe_key:
                transaction.setWipeKey(wipe_key)
            
            if kyc_key:
                transaction.setKycKey(kyc_key)
            
            # Optional memo
            if memo:
                transaction.setTokenMemo(memo)
            
            # Default settings
            transaction.setFreezeDefault(False)
            
            # Freeze, sign, and execute
            transaction = transaction.freezeWith(self.hedera_client.client)
            signed_transaction = transaction.sign(self.hedera_client.operator_private_key)
            response = await signed_transaction.execute(self.hedera_client.client)
            receipt = await response.getReceipt(self.hedera_client.client)
            
            token_id = receipt.tokenId
            
            result = {
                "token_id": str(token_id),
                "name": name,
                "symbol": symbol,
                "max_supply": max_supply,
                "treasury_account": treasury_account or str(self.hedera_client.operator_account_id),
                "token_type": "nft",
                "supply_type": "finite" if max_supply else "infinite",
                "transaction_id": str(response.transactionId),
                "status": "success"
            }
            
            # Cache token info
            self.token_cache[str(token_id)] = result
            
            logger.info(f"Created NFT collection: {symbol} ({token_id})")
            return result
            
        except Exception as e:
            logger.error(f"NFT collection creation failed: {str(e)}")
            raise BlockchainError(f"NFT collection creation failed: {str(e)}")
    
    async def mint_tokens(
        self,
        token_id: str,
        amount: int,
        metadata: Optional[List[bytes]] = None
    ) -> Dict[str, Any]:
        """
        Mint new tokens (fungible) or NFTs.
        
        Args:
            token_id: Token ID to mint
            amount: Amount to mint (for fungible tokens)
            metadata: Metadata for NFTs (list of bytes for each NFT)
            
        Returns:
            Minting result
        """
        try:
            token = TokenId.fromString(token_id)
            transaction = TokenMintTransaction().setTokenId(token)
            
            # Get token info to determine type
            token_info = await self.get_token_info(token_id)
            
            if token_info["token_type"] == "nft":
                # Mint NFTs with metadata
                if metadata:
                    transaction.setMetadata(metadata)
                else:
                    # Create default metadata for the number of NFTs
                    default_metadata = [f"NFT #{i+1}".encode('utf-8') for i in range(amount)]
                    transaction.setMetadata(default_metadata)
            else:
                # Mint fungible tokens
                transaction.setAmount(amount)
            
            # Freeze, sign, and execute
            transaction = transaction.freezeWith(self.hedera_client.client)
            signed_transaction = transaction.sign(self.hedera_client.operator_private_key)
            response = await signed_transaction.execute(self.hedera_client.client)
            receipt = await response.getReceipt(self.hedera_client.client)
            
            result = {
                "token_id": token_id,
                "amount_minted": amount,
                "transaction_id": str(response.transactionId),
                "new_total_supply": receipt.totalSupply,
                "serial_numbers": receipt.serials if hasattr(receipt, 'serials') else None,
                "status": "success"
            }
            
            logger.info(f"Minted {amount} tokens for {token_id}")
            return result
            
        except Exception as e:
            logger.error(f"Token minting failed: {str(e)}")
            raise BlockchainError(f"Token minting failed: {str(e)}")
    
    async def burn_tokens(
        self,
        token_id: str,
        amount: Optional[int] = None,
        serial_numbers: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Burn tokens (fungible) or NFTs.
        
        Args:
            token_id: Token ID to burn
            amount: Amount to burn (for fungible tokens)
            serial_numbers: Serial numbers to burn (for NFTs)
            
        Returns:
            Burning result
        """
        try:
            token = TokenId.fromString(token_id)
            transaction = TokenBurnTransaction().setTokenId(token)
            
            # Get token info to determine type
            token_info = await self.get_token_info(token_id)
            
            if token_info["token_type"] == "nft":
                # Burn NFTs by serial numbers
                if not serial_numbers:
                    raise BlockchainError("Serial numbers required for NFT burning")
                transaction.setSerials(serial_numbers)
            else:
                # Burn fungible tokens
                if not amount:
                    raise BlockchainError("Amount required for fungible token burning")
                transaction.setAmount(amount)
            
            # Freeze, sign, and execute
            transaction = transaction.freezeWith(self.hedera_client.client)
            signed_transaction = transaction.sign(self.hedera_client.operator_private_key)
            response = await signed_transaction.execute(self.hedera_client.client)
            receipt = await response.getReceipt(self.hedera_client.client)
            
            result = {
                "token_id": token_id,
                "amount_burned": amount,
                "serial_numbers_burned": serial_numbers,
                "transaction_id": str(response.transactionId),
                "new_total_supply": receipt.totalSupply,
                "status": "success"
            }
            
            logger.info(f"Burned tokens for {token_id}")
            return result
            
        except Exception as e:
            logger.error(f"Token burning failed: {str(e)}")
            raise BlockchainError(f"Token burning failed: {str(e)}")
    
    async def associate_token(
        self,
        account_id: str,
        token_ids: Union[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Associate account with token(s).
        
        Args:
            account_id: Account ID to associate
            token_ids: Token ID(s) to associate
            
        Returns:
            Association result
        """
        try:
            account = AccountId.fromString(account_id)
            
            if isinstance(token_ids, str):
                token_ids = [token_ids]
            
            tokens = [TokenId.fromString(tid) for tid in token_ids]
            
            transaction = (
                TokenAssociateTransaction()
                .setAccountId(account)
                .setTokenIds(tokens)
            )
            
            # Freeze, sign, and execute
            transaction = transaction.freezeWith(self.hedera_client.client)
            signed_transaction = transaction.sign(self.hedera_client.operator_private_key)
            response = await signed_transaction.execute(self.hedera_client.client)
            receipt = await response.getReceipt(self.hedera_client.client)
            
            result = {
                "account_id": account_id,
                "token_ids": token_ids,
                "transaction_id": str(response.transactionId),
                "status": "success"
            }
            
            logger.info(f"Associated account {account_id} with tokens {token_ids}")
            return result
            
        except Exception as e:
            logger.error(f"Token association failed: {str(e)}")
            raise BlockchainError(f"Token association failed: {str(e)}")
    
    async def transfer_tokens(
        self,
        token_id: str,
        from_account: str,
        to_account: str,
        amount: Optional[int] = None,
        serial_numbers: Optional[List[int]] = None,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transfer tokens between accounts.
        
        Args:
            token_id: Token ID to transfer
            from_account: Sender account ID
            to_account: Recipient account ID
            amount: Amount to transfer (for fungible tokens)
            serial_numbers: Serial numbers to transfer (for NFTs)
            memo: Transaction memo
            
        Returns:
            Transfer result
        """
        try:
            token = TokenId.fromString(token_id)
            from_acc = AccountId.fromString(from_account)
            to_acc = AccountId.fromString(to_account)
            
            transaction = TokenTransferTransaction()
            
            # Get token info to determine type
            token_info = await self.get_token_info(token_id)
            
            if token_info["token_type"] == "nft":
                # Transfer NFTs by serial numbers
                if not serial_numbers:
                    raise BlockchainError("Serial numbers required for NFT transfer")
                
                for serial in serial_numbers:
                    transaction.addNftTransfer(token, serial, from_acc, to_acc)
            else:
                # Transfer fungible tokens
                if not amount:
                    raise BlockchainError("Amount required for fungible token transfer")
                
                transaction.addTokenTransfer(token, from_acc, -amount)
                transaction.addTokenTransfer(token, to_acc, amount)
            
            if memo:
                transaction.setTransactionMemo(memo)
            
            # Freeze, sign, and execute
            transaction = transaction.freezeWith(self.hedera_client.client)
            signed_transaction = transaction.sign(self.hedera_client.operator_private_key)
            response = await signed_transaction.execute(self.hedera_client.client)
            receipt = await response.getReceipt(self.hedera_client.client)
            
            result = {
                "token_id": token_id,
                "from_account": from_account,
                "to_account": to_account,
                "amount": amount,
                "serial_numbers": serial_numbers,
                "transaction_id": str(response.transactionId),
                "memo": memo,
                "status": "success"
            }
            
            logger.info(f"Transferred tokens {token_id} from {from_account} to {to_account}")
            return result
            
        except Exception as e:
            logger.error(f"Token transfer failed: {str(e)}")
            raise BlockchainError(f"Token transfer failed: {str(e)}")
    
    async def get_token_info(self, token_id: str) -> Dict[str, Any]:
        """
        Get detailed token information.
        
        Args:
            token_id: Token ID to query
            
        Returns:
            Token information
        """
        try:
            # Check cache first
            if token_id in self.token_cache:
                cached_info = self.token_cache[token_id].copy()
                # Update with fresh supply info
                token = TokenId.fromString(token_id)
                query = TokenInfoQuery().setTokenId(token)
                info = await query.execute(self.hedera_client.client)
                cached_info.update({
                    "total_supply": info.totalSupply,
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                })
                return cached_info
            
            token = TokenId.fromString(token_id)
            query = TokenInfoQuery().setTokenId(token)
            info = await query.execute(self.hedera_client.client)
            
            result = {
                "token_id": token_id,
                "name": info.name,
                "symbol": info.symbol,
                "decimals": info.decimals,
                "total_supply": info.totalSupply,
                "treasury_account": str(info.treasuryAccountId),
                "admin_key": str(info.adminKey) if info.adminKey else None,
                "supply_key": str(info.supplyKey) if info.supplyKey else None,
                "freeze_key": str(info.freezeKey) if info.freezeKey else None,
                "wipe_key": str(info.wipeKey) if info.wipeKey else None,
                "kyc_key": str(info.kycKey) if info.kycKey else None,
                "freeze_default": info.defaultFreezeStatus == TokenFreezeStatus.Frozen,
                "kyc_default": info.defaultKycStatus == TokenKycStatus.Granted,
                "token_type": "nft" if info.tokenType == TokenType.NON_FUNGIBLE_UNIQUE else "fungible",
                "supply_type": "finite" if info.supplyType == TokenSupplyType.FINITE else "infinite",
                "max_supply": info.maxSupply if info.supplyType == TokenSupplyType.FINITE else None,
                "memo": info.tokenMemo,
                "expiration_time": str(info.expirationTime) if info.expirationTime else None,
                "auto_renew_account": str(info.autoRenewAccount) if info.autoRenewAccount else None,
                "auto_renew_period": info.autoRenewPeriod.seconds if info.autoRenewPeriod else None,
                "ledger_id": str(info.ledgerId) if hasattr(info, 'ledgerId') else None
            }
            
            # Cache the result
            self.token_cache[token_id] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Token info query failed: {str(e)}")
            raise BlockchainError(f"Token info query failed: {str(e)}")
    
    async def get_account_token_balance(
        self,
        account_id: str,
        token_id: str
    ) -> Dict[str, Any]:
        """
        Get account's balance for a specific token.
        
        Args:
            account_id: Account ID to query
            token_id: Token ID to check balance for
            
        Returns:
            Token balance information
        """
        try:
            # Use the account balance query from HederaClient
            balance_info = await self.hedera_client.get_account_balance(account_id)
            
            token_balance = balance_info["tokens"].get(token_id, 0)
            
            # Get token info for context
            token_info = await self.get_token_info(token_id)
            
            result = {
                "account_id": account_id,
                "token_id": token_id,
                "token_symbol": token_info["symbol"],
                "balance": token_balance,
                "decimals": token_info["decimals"],
                "formatted_balance": token_balance / (10 ** token_info["decimals"]) if token_info["decimals"] > 0 else token_balance,
                "token_type": token_info["token_type"]
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Token balance query failed: {str(e)}")
            raise BlockchainError(f"Token balance query failed: {str(e)}")
    
    def clear_cache(self):
        """Clear the token info cache."""
        self.token_cache.clear()
        logger.debug("Token cache cleared")
