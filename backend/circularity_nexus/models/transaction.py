"""
Transaction model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
import enum
from circularity_nexus.core.database import Base


class TransactionType(str, enum.Enum):
    """Transaction types"""
    MINT = "MINT"
    TRANSFER = "TRANSFER"
    STAKE = "STAKE"
    UNSTAKE = "UNSTAKE"
    CONVERT = "CONVERT"


class Transaction(Base):
    """Transaction model for tracking all token operations"""
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    token_type = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    hedera_transaction_id = Column(String(100), unique=True, index=True)
    status = Column(String(20), default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
