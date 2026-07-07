import re
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from pymongo.errors import DuplicateKeyError

from backend.services.db_service import db_service
from backend.utils.auth import hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


class UserAuthRequest(BaseModel):
    email: str = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password (min 6 characters)")
    name: str = Field(None, description="User's full name (optional)")


class AuthResponse(BaseModel):
    id: str = Field(..., description="User ID")
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(request: UserAuthRequest):
    """
    Register a new user in the system.
    """
    email = request.email.lower().strip()
    
    # Validate email format
    if not re.match(EMAIL_REGEX, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )

    # Check if user already exists
    existing_user = db_service.get_user_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    # Hash the password and save user
    hashed = hash_password(request.password)
    try:
        user = db_service.create_user(email, hashed, request.name)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during registration: {exc}",
        )

    return AuthResponse(
        id=str(user["_id"]),
        name=user.get("name", ""),
        email=user["email"],
    )


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def login(request: UserAuthRequest):
    """
    Authenticate user and verify credentials.
    """
    email = request.email.lower().strip()
    
    # Validate email format
    if not re.match(EMAIL_REGEX, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )

    # Find user document
    user = db_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password hash
    if not verify_password(request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return AuthResponse(
        id=str(user["_id"]),
        name=user.get("name", ""),
        email=user["email"],
    )
