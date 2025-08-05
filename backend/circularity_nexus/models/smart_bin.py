"""
Smart bin model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from circularity_nexus.core.database import Base


class SmartBin(Base):
    """Smart bin model for IoT waste bins"""
    
    __tablename__ = "smart_bins"
    
    id = Column(Integer, primary_key=True, index=True)
    bin_id = Column(String(50), unique=True, index=True, nullable=False)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    address = Column(String(255))
    capacity_kg = Column(Float, default=50.0)
    current_weight_kg = Column(Float, default=0.0)
    battery_level = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    last_emptied = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
