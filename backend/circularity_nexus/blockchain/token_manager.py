"""
Token Manager

High-level token management service that orchestrates HTS operations
for waste tokens, carbon credits, and other tokenized assets.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime, timedelta
from .hts_service import HTSService
from .hedera_client import HederaClient
from ..core.exceptions import BlockchainError, ValidationError

logger = logging.getLogger(__name__)

class TokenCategory(Enum):
    """Categories of tokens in the Circularity Nexus ecosystem."""
    WASTE_TOKEN = "waste_token"
    CARBON_CREDIT = "carbon_credit"
    RECYCLING_CERTIFICATE = "recycling_certificate"
    IMPACT_BADGE = "impact_badge"
    UTILITY_TOKEN = "utility_token"

class WasteTokenType(Enum):
    """Specific waste token types."""
    PET_PLASTIC = "PET"
    ALUMINUM = "ALU"
    CARDBOARD = "CDB"
    GLASS = "GLS"
    ELECTRONIC = "EWS"
    TEXTILE = "TXT"
    ORGANIC = "ORG"
    MIXED = "MIX"

class TokenManager:
    """
    High-level token management service for the Circularity Nexus platform.
    
    Manages creation, minting, burning, and transfer of all token types
    with business logic and validation.
    """
    
    def __init__(self):
        self.hts_service = HTSService()
        self.hedera_client = HederaClient()
        self.token_registry: Dict[str, Dict[str, Any]] = {}
        self.waste_token_configs = self._load_waste_token_configs()
    
    async def create_waste_token(
        self,
        waste_type: WasteTokenType,
        region: str = "GLOBAL",
        max_supply: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new waste token for a specific material type.
        
        Args:
            waste_type: Type of waste material
            region: Geographic region for the token
            max_supply: Maximum token supply
            
        Returns:
            Token creation result
        """
        try:
            config = self.waste_token_configs[waste_type]
            
            # Generate token details
            symbol = f"{waste_type.value}-{region}"
            name = f"{config['name']} Token ({region})"
            memo = f"Waste token for {config['name']} in {region} region"
            
            # Create the token
            result = await self.hts_service.create_fungible_token(
                name=name,
                symbol=symbol,
                decimals=config['decimals'],
                initial_supply=0,  # Start with 0, mint as needed
                max_supply=max_supply,
                memo=memo
            )
            
            # Register in token registry
            token_info = {
                **result,
                "category": TokenCategory.WASTE_TOKEN.value,
                "waste_type": waste_type.value,
                "region": region,
                "base_value_per_unit": config['base_value_per_unit'],
                "environmental_impact": config['environmental_impact'],
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            
            self.token_registry[result["token_id"]] = token_info
            
            logger.info(f"Created waste token: {symbol} ({result['token_id']})")
            return token_info
            
        except Exception as e:
            logger.error(f"Waste token creation failed: {str(e)}")
            raise BlockchainError(f"Waste token creation failed: {str(e)}")
    
    async def create_carbon_credit_token(
        self,
        vintage_year: int,
        project_type: str = "WASTE_RECYCLING",
        region: str = "GLOBAL",
        max_supply: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a carbon credit token for a specific vintage year.
        
        Args:
            vintage_year: Year the carbon credits were generated
            project_type: Type of carbon reduction project
            region: Geographic region
            max_supply: Maximum token supply
            
        Returns:
            Token creation result
        """
        try:
            symbol = f"CC{vintage_year}-{region}"
            name = f"Carbon Credit {vintage_year} ({region})"
            memo = f"Carbon credits from {project_type} projects in {vintage_year}"
            
            # Create the token (carbon credits typically have 3 decimals for fractional credits)
            result = await self.hts_service.create_fungible_token(
                name=name,
                symbol=symbol,
                decimals=3,
                initial_supply=0,
                max_supply=max_supply,
                memo=memo
            )
            
            # Register in token registry
            token_info = {
                **result,
                "category": TokenCategory.CARBON_CREDIT.value,
                "vintage_year": vintage_year,
                "project_type": project_type,
                "region": region,
                "verification_standard": "VCS",  # Verified Carbon Standard
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            
            self.token_registry[result["token_id"]] = token_info
            
            logger.info(f"Created carbon credit token: {symbol} ({result['token_id']})")
            return token_info
            
        except Exception as e:
            logger.error(f"Carbon credit token creation failed: {str(e)}")
            raise BlockchainError(f"Carbon credit token creation failed: {str(e)}")
    
    async def create_recycling_certificate_nft(
        self,
        certificate_type: str = "RECYCLING_COMPLETION",
        max_supply: int = 10000
    ) -> Dict[str, Any]:
        """
        Create an NFT collection for recycling certificates.
        
        Args:
            certificate_type: Type of certificate
            max_supply: Maximum number of certificates
            
        Returns:
            NFT collection creation result
        """
        try:
            symbol = f"RC-{certificate_type}"
            name = f"Recycling Certificate - {certificate_type}"
            memo = f"NFT certificates for {certificate_type}"
            
            # Create NFT collection
            result = await self.hts_service.create_nft_collection(
                name=name,
                symbol=symbol,
                max_supply=max_supply,
                memo=memo
            )
            
            # Register in token registry
            token_info = {
                **result,
                "category": TokenCategory.RECYCLING_CERTIFICATE.value,
                "certificate_type": certificate_type,
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            
            self.token_registry[result["token_id"]] = token_info
            
            logger.info(f"Created recycling certificate NFT: {symbol} ({result['token_id']})")
            return token_info
            
        except Exception as e:
            logger.error(f"Recycling certificate NFT creation failed: {str(e)}")
            raise BlockchainError(f"Recycling certificate NFT creation failed: {str(e)}")
    
    async def mint_waste_tokens(
        self,
        token_id: str,
        waste_weight_kg: float,
        quality_grade: str = "GOOD",
        recipient_account: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mint waste tokens based on waste weight and quality.
        
        Args:
            token_id: Waste token ID
            waste_weight_kg: Weight of waste in kg
            quality_grade: Quality grade (EXCELLENT, GOOD, FAIR, POOR)
            recipient_account: Account to receive tokens (None = treasury)
            
        Returns:
            Minting result
        """
        try:
            # Get token info
            token_info = self.token_registry.get(token_id)
            if not token_info or token_info["category"] != TokenCategory.WASTE_TOKEN.value:
                raise ValidationError(f"Invalid waste token ID: {token_id}")
            
            # Calculate token amount based on weight and quality
            base_value = token_info["base_value_per_unit"]
            quality_multiplier = self._get_quality_multiplier(quality_grade)
            decimals = token_info["decimals"]
            
            # Convert weight to token units (accounting for decimals)
            token_amount = int(waste_weight_kg * base_value * quality_multiplier * (10 ** decimals))
            
            # Mint tokens
            result = await self.hts_service.mint_tokens(
                token_id=token_id,
                amount=token_amount
            )
            
            # Transfer to recipient if specified
            if recipient_account:
                await self.hts_service.transfer_tokens(
                    token_id=token_id,
                    from_account=token_info["treasury_account"],
                    to_account=recipient_account,
                    amount=token_amount,
                    memo=f"Waste token reward for {waste_weight_kg}kg {quality_grade} waste"
                )
            
            result.update({
                "waste_weight_kg": waste_weight_kg,
                "quality_grade": quality_grade,
                "quality_multiplier": quality_multiplier,
                "token_amount_raw": token_amount,
                "token_amount_formatted": token_amount / (10 ** decimals),
                "recipient_account": recipient_account
            })
            
            logger.info(f"Minted {token_amount} waste tokens for {waste_weight_kg}kg waste")
            return result
            
        except Exception as e:
            logger.error(f"Waste token minting failed: {str(e)}")
            raise BlockchainError(f"Waste token minting failed: {str(e)}")
    
    async def mint_carbon_credits(
        self,
        token_id: str,
        co2_saved_kg: float,
        verification_data: Dict[str, Any],
        recipient_account: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mint carbon credit tokens based on CO2 savings.
        
        Args:
            token_id: Carbon credit token ID
            co2_saved_kg: Amount of CO2 saved in kg
            verification_data: Verification and audit data
            recipient_account: Account to receive credits
            
        Returns:
            Minting result
        """
        try:
            # Get token info
            token_info = self.token_registry.get(token_id)
            if not token_info or token_info["category"] != TokenCategory.CARBON_CREDIT.value:
                raise ValidationError(f"Invalid carbon credit token ID: {token_id}")
            
            # Convert CO2 savings to carbon credits (1 credit = 1000kg CO2)
            credits = co2_saved_kg / 1000.0
            decimals = token_info["decimals"]
            token_amount = int(credits * (10 ** decimals))
            
            # Mint carbon credits
            result = await self.hts_service.mint_tokens(
                token_id=token_id,
                amount=token_amount
            )
            
            # Transfer to recipient if specified
            if recipient_account:
                await self.hts_service.transfer_tokens(
                    token_id=token_id,
                    from_account=token_info["treasury_account"],
                    to_account=recipient_account,
                    amount=token_amount,
                    memo=f"Carbon credits for {co2_saved_kg}kg CO2 saved"
                )
            
            result.update({
                "co2_saved_kg": co2_saved_kg,
                "carbon_credits": credits,
                "token_amount_raw": token_amount,
                "token_amount_formatted": credits,
                "verification_data": verification_data,
                "recipient_account": recipient_account
            })
            
            logger.info(f"Minted {credits} carbon credits for {co2_saved_kg}kg CO2 saved")
            return result
            
        except Exception as e:
            logger.error(f"Carbon credit minting failed: {str(e)}")
            raise BlockchainError(f"Carbon credit minting failed: {str(e)}")
    
    async def mint_recycling_certificate(
        self,
        token_id: str,
        certificate_data: Dict[str, Any],
        recipient_account: str
    ) -> Dict[str, Any]:
        """
        Mint a recycling certificate NFT.
        
        Args:
            token_id: Certificate NFT collection ID
            certificate_data: Certificate metadata
            recipient_account: Account to receive certificate
            
        Returns:
            Minting result
        """
        try:
            # Get token info
            token_info = self.token_registry.get(token_id)
            if not token_info or token_info["category"] != TokenCategory.RECYCLING_CERTIFICATE.value:
                raise ValidationError(f"Invalid recycling certificate token ID: {token_id}")
            
            # Prepare metadata
            metadata_json = {
                "name": f"Recycling Certificate #{certificate_data.get('certificate_id', 'UNKNOWN')}",
                "description": certificate_data.get("description", "Recycling completion certificate"),
                "image": certificate_data.get("image_url", ""),
                "attributes": [
                    {"trait_type": "Certificate Type", "value": certificate_data.get("type", "RECYCLING")},
                    {"trait_type": "Waste Type", "value": certificate_data.get("waste_type", "MIXED")},
                    {"trait_type": "Weight (kg)", "value": certificate_data.get("weight_kg", 0)},
                    {"trait_type": "CO2 Saved (kg)", "value": certificate_data.get("co2_saved_kg", 0)},
                    {"trait_type": "Issue Date", "value": datetime.utcnow().isoformat()},
                    {"trait_type": "Issuer", "value": "Circularity Nexus"}
                ],
                "external_url": certificate_data.get("external_url", ""),
                "certificate_data": certificate_data
            }
            
            metadata_bytes = json.dumps(metadata_json).encode('utf-8')
            
            # Mint NFT
            result = await self.hts_service.mint_tokens(
                token_id=token_id,
                amount=1,  # Always 1 for NFTs
                metadata=[metadata_bytes]
            )
            
            # Transfer to recipient
            serial_numbers = result.get("serial_numbers", [])
            if serial_numbers:
                await self.hts_service.transfer_tokens(
                    token_id=token_id,
                    from_account=token_info["treasury_account"],
                    to_account=recipient_account,
                    serial_numbers=serial_numbers,
                    memo=f"Recycling certificate for {certificate_data.get('waste_type', 'waste')} recycling"
                )
            
            result.update({
                "certificate_data": certificate_data,
                "metadata": metadata_json,
                "recipient_account": recipient_account
            })
            
            logger.info(f"Minted recycling certificate NFT for {recipient_account}")
            return result
            
        except Exception as e:
            logger.error(f"Recycling certificate minting failed: {str(e)}")
            raise BlockchainError(f"Recycling certificate minting failed: {str(e)}")
    
    async def get_account_portfolio(self, account_id: str) -> Dict[str, Any]:
        """
        Get complete token portfolio for an account.
        
        Args:
            account_id: Account ID to query
            
        Returns:
            Complete portfolio information
        """
        try:
            # Get account balance
            balance_info = await self.hedera_client.get_account_balance(account_id)
            
            portfolio = {
                "account_id": account_id,
                "hbar_balance": balance_info["hbar_balance"],
                "tokens": {},
                "summary": {
                    "total_tokens": 0,
                    "waste_tokens": 0,
                    "carbon_credits": 0,
                    "certificates": 0,
                    "total_value_usd": 0.0
                }
            }
            
            # Process each token
            for token_id, balance in balance_info["tokens"].items():
                if balance > 0:
                    try:
                        token_info = await self.hts_service.get_token_info(token_id)
                        registry_info = self.token_registry.get(token_id, {})
                        
                        formatted_balance = balance / (10 ** token_info["decimals"]) if token_info["decimals"] > 0 else balance
                        
                        token_data = {
                            "token_id": token_id,
                            "symbol": token_info["symbol"],
                            "name": token_info["name"],
                            "balance_raw": balance,
                            "balance_formatted": formatted_balance,
                            "decimals": token_info["decimals"],
                            "token_type": token_info["token_type"],
                            "category": registry_info.get("category", "unknown"),
                            "estimated_value_usd": self._estimate_token_value(token_id, formatted_balance, registry_info)
                        }
                        
                        portfolio["tokens"][token_id] = token_data
                        portfolio["summary"]["total_tokens"] += 1
                        portfolio["summary"]["total_value_usd"] += token_data["estimated_value_usd"]
                        
                        # Categorize tokens
                        category = registry_info.get("category")
                        if category == TokenCategory.WASTE_TOKEN.value:
                            portfolio["summary"]["waste_tokens"] += 1
                        elif category == TokenCategory.CARBON_CREDIT.value:
                            portfolio["summary"]["carbon_credits"] += 1
                        elif category == TokenCategory.RECYCLING_CERTIFICATE.value:
                            portfolio["summary"]["certificates"] += 1
                            
                    except Exception as e:
                        logger.warning(f"Failed to process token {token_id}: {str(e)}")
                        continue
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Portfolio query failed: {str(e)}")
            raise BlockchainError(f"Portfolio query failed: {str(e)}")
    
    def _get_quality_multiplier(self, quality_grade: str) -> float:
        """Get quality multiplier for token calculation."""
        multipliers = {
            "EXCELLENT": 1.0,
            "GOOD": 0.8,
            "FAIR": 0.6,
            "POOR": 0.3
        }
        return multipliers.get(quality_grade.upper(), 0.6)
    
    def _estimate_token_value(self, token_id: str, balance: float, registry_info: Dict[str, Any]) -> float:
        """Estimate USD value of tokens."""
        category = registry_info.get("category")
        
        if category == TokenCategory.WASTE_TOKEN.value:
            base_value = registry_info.get("base_value_per_unit", 0.05)
            return balance * base_value
        elif category == TokenCategory.CARBON_CREDIT.value:
            # Assume $15 per carbon credit
            return balance * 15.0
        elif category == TokenCategory.RECYCLING_CERTIFICATE.value:
            # NFTs have fixed estimated value
            return balance * 10.0  # $10 per certificate
        else:
            return 0.0
    
    def _load_waste_token_configs(self) -> Dict[WasteTokenType, Dict[str, Any]]:
        """Load waste token configurations."""
        return {
            WasteTokenType.PET_PLASTIC: {
                "name": "PET Plastic",
                "decimals": 2,
                "base_value_per_unit": 0.08,  # $0.08 per kg
                "environmental_impact": "high"
            },
            WasteTokenType.ALUMINUM: {
                "name": "Aluminum",
                "decimals": 2,
                "base_value_per_unit": 1.20,  # $1.20 per kg
                "environmental_impact": "very_high"
            },
            WasteTokenType.CARDBOARD: {
                "name": "Cardboard",
                "decimals": 2,
                "base_value_per_unit": 0.03,  # $0.03 per kg
                "environmental_impact": "medium"
            },
            WasteTokenType.GLASS: {
                "name": "Glass",
                "decimals": 2,
                "base_value_per_unit": 0.02,  # $0.02 per kg
                "environmental_impact": "medium"
            },
            WasteTokenType.ELECTRONIC: {
                "name": "Electronic Waste",
                "decimals": 2,
                "base_value_per_unit": 2.50,  # $2.50 per kg
                "environmental_impact": "very_high"
            },
            WasteTokenType.TEXTILE: {
                "name": "Textile",
                "decimals": 2,
                "base_value_per_unit": 0.015,  # $0.015 per kg
                "environmental_impact": "low"
            },
            WasteTokenType.ORGANIC: {
                "name": "Organic Waste",
                "decimals": 2,
                "base_value_per_unit": 0.01,  # $0.01 per kg
                "environmental_impact": "medium"
            },
            WasteTokenType.MIXED: {
                "name": "Mixed Waste",
                "decimals": 2,
                "base_value_per_unit": 0.025,  # $0.025 per kg
                "environmental_impact": "medium"
            }
        }
