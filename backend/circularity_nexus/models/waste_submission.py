"""
Waste submission model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from circularity_nexus.core.database import Base


class WasteType(str, enum.Enum):
    """Supported waste types"""
    PET = "PET"
    ALUMINUM = "ALUMINUM"
    GLASS = "GLASS"
    PAPER = "PAPER"
    CARDBOARD = "CARDBOARD"
    EWASTE = "EWASTE"
    ORGANIC = "ORGANIC"
    MIXED_PLASTIC = "MIXED_PLASTIC"


class SubmissionStatus(str, enum.Enum):
    """Waste submission status"""
    PENDING = "PENDING"
    AI_PROCESSING = "AI_PROCESSING"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    TOKENIZED = "TOKENIZED"


class WasteSubmission(Base):
    """Waste submission model for tracking user waste submissions"""
    
    __tablename__ = "waste_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    waste_type = Column(Enum(WasteType), nullable=False)
    estimated_weight_kg = Column(Float, nullable=False)
    verified_weight_kg = Column(Float)
    location_lat = Column(Float)
    location_lng = Column(Float)
    description = Column(Text)
    image_urls = Column(Text)  # JSON array of image URLs
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING)
    ai_confidence_score = Column(Float)
    ai_detected_type = Column(String(50))
    smart_bin_id = Column(String(50))
    tokens_minted = Column(Integer, default=0)  # Tokens minted in grams
    carbon_credits_generated = Column(Integer, default=0)
    rejection_reason = Column(Text)
    processed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="waste_submissions")
    
    def __repr__(self):
        return f"<WasteSubmission(id={self.id}, type='{self.waste_type}', weight={self.estimated_weight_kg}kg)>"
