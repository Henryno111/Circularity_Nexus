"""
User model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from circularity_nexus.core.database import Base


class User(Base):
    """User model for authentication and profile management"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    wallet_address = Column(String(42), unique=True, index=True)
    hedera_account_id = Column(String(50), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    profile_image_url = Column(Text)
    bio = Column(Text)
    location = Column(String(255))
    total_waste_kg = Column(Integer, default=0)  # Total waste submitted in grams
    total_tokens_earned = Column(Integer, default=0)  # Total tokens earned
    carbon_credits_earned = Column(Integer, default=0)  # Total carbon credits
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.full_name}')>"
