"""
Circularity Nexus AI Module

This module provides AI-powered waste classification, carbon impact calculation,
and recycling recommendations using Groq's Llama3 model.
"""

from .groq_service import GroqService
from .waste_classifier import WasteClassifier
from .carbon_calculator import CarbonCalculator
from .recycling_advisor import RecyclingAdvisor

__all__ = [
    "GroqService",
    "WasteClassifier", 
    "CarbonCalculator",
    "RecyclingAdvisor"
]
