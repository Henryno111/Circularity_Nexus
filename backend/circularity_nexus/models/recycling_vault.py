"""
Recycling vault model for DeFi staking
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
import enum
from circularity_nexus.core.database import Base


class VaultType(str, enum.Enum):
    """Vault types for staking"""
    ESG_CORPORATE = "ESG_CORPORATE"
    RECYCLING_POOL = "RECYCLING_POOL"
    CARBON_OFFSET = "CARBON_OFFSET"
    COMMUNITY = "COMMUNITY"


class StakeStatus(str, enum.Enum):
    """Staking status"""
    ACTIVE = "ACTIVE"
    UNSTAKING = "UNSTAKING"
    COMPLETED = "COMPLETED"


class RecyclingVault(Base):
    """Recycling vault model for DeFi staking"""
    
    __tablename__ = "recycling_vaults"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vault_type = Column(Enum(VaultType), nullable=False)
    token_type = Column(String(50), nullable=False)  # PET, ALUMINUM, etc.
    staked_amount = Column(Integer, nullable=False)  # Amount in grams
    apy_rate = Column(Float, nullable=False)  # Annual percentage yield
    rewards_earned = Column(Float, default=0.0)  # Rewards in USDC
    status = Column(Enum(StakeStatus), default=StakeStatus.ACTIVE)
    stake_date = Column(DateTime(timezone=True), server_default=func.now())
    unstake_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
