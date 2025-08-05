"""
Waste token model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from circularity_nexus.core.database import Base


class WasteToken(Base):
    """Waste token model"""
    
    __tablename__ = "waste_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_type = Column(String(50), nullable=False)  # PET, ALUMINUM, etc.
    balance = Column(Integer, default=0)  # Balance in grams
    hedera_token_id = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
