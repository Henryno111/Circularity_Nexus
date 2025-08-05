"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Any

router = APIRouter()


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    password: str
    full_name: str
    wallet_address: str


class UserLogin(BaseModel):
    """User login response schema"""
    access_token: str
    token_type: str
    user_id: int
    email: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister) -> dict[str, Any]:
    """Register a new user"""
    # TODO: Implement user registration logic
    return {
        "message": "User registered successfully",
        "user_id": 1,
        "email": user_data.email
    }


@router.post("/login", response_model=UserLogin)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> UserLogin:
    """Login user and return access token"""
    # TODO: Implement authentication logic
    if form_data.username == "demo@circularitynexus.io" and form_data.password == "demo123456":
        return UserLogin(
            access_token="demo_token_12345",
            token_type="bearer",
            user_id=1,
            email=form_data.username
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/logout")
async def logout() -> dict[str, str]:
    """Logout user"""
    # TODO: Implement logout logic (token blacklisting)
    return {"message": "Successfully logged out"}
