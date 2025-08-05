"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter

from circularity_nexus.api.v1.endpoints import (
    auth,
    waste,
    tokens,
    ai,
    defi,
    carbon,
    users,
    smart_bins,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(waste.router, prefix="/waste", tags=["Waste Management"])
api_router.include_router(tokens.router, prefix="/tokens", tags=["Tokenization"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Processing"])
api_router.include_router(defi.router, prefix="/defi", tags=["DeFi & Staking"])
api_router.include_router(carbon.router, prefix="/carbon", tags=["Carbon Credits"])
api_router.include_router(smart_bins.router, prefix="/smart-bins", tags=["Smart Bins"])
