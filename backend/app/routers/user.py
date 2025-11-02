from fastapi import APIRouter, HTTPException, Depends
from app.models import UserCreate, UserResponse
from app.database import get_db
from passlib.context import CryptContext
from datetime import datetime

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        db = get_db()

        # Check if user already exists
        existing_user = await db.user.find_unique(
            where={"email": user.email}
        )

        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        # Hash password
        hashed_password = pwd_context.hash(user.password)

        # Create user
        new_user = await db.user.create(
            data={
                "email": user.email,
                "name": user.name,
                "passwordHash": hashed_password
            }
        )

        # Create initial progress record
        await db.progress.create(
            data={
                "userId": new_user.id
            }
        )

        return new_user

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    try:
        db = get_db()
        user = await db.user.find_unique(
            where={"id": user_id}
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")


@router.get("/{user_id}/sessions")
async def get_user_sessions(user_id: str, limit: int = 10):
    """Get user's learning sessions"""
    try:
        db = get_db()

        sessions = await db.session.find_many(
            where={"userId": user_id},
            order={"startedAt": "desc"},
            take=limit,
            include={
                "conversations": True,
                "corrections": True
            }
        )

        return sessions

    except Exception as e:
        print(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sessions")
