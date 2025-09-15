from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import uuid4
from app.models.database import User, UserProfile
from app.models.schemas import UserCreate, UserUpdate, UserProfileCreate, UserProfileUpdate
from app.services.auth import AuthService


class UserService:
    """Service for user operations"""
    
    def __init__(self):
        self.auth_service = AuthService()
    
    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users"""
        return db.query(User).offset(skip).limit(limit).all()
    
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Create new user"""
        return self.auth_service.create_user_with_hashed_password(db, user_data)
    
    def update_user(self, db: Session, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    def delete_user(self, db: Session, user_id: str) -> bool:
        """Delete user"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True
    
    def activate_user(self, db: Session, user_id: str) -> Optional[User]:
        """Activate user account"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            return None
        
        user.is_active = True
        user.is_verified = True
        db.commit()
        db.refresh(user)
        return user
    
    def deactivate_user(self, db: Session, user_id: str) -> Optional[User]:
        """Deactivate user account"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            return None
        
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
    
    # Profile management
    def get_user_profile(self, db: Session, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    def create_user_profile(self, db: Session, user_id: str, profile_data: UserProfileCreate) -> UserProfile:
        """Create user profile"""
        db_profile = UserProfile(
            user_id=user_id,
            **profile_data.dict()
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    
    def update_user_profile(self, db: Session, user_id: str, profile_data: UserProfileUpdate) -> Optional[UserProfile]:
        """Update user profile"""
        profile = self.get_user_profile(db, user_id)
        if not profile:
            return self.create_user_profile(db, user_id, profile_data)
        
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        return profile
    
    def get_user_with_profile(self, db: Session, user_id: str) -> Optional[User]:
        """Get user with profile information"""
        return db.query(User).filter(User.id == user_id).first()
    
    def count_active_users(self, db: Session) -> int:
        """Count active users"""
        return db.query(User).filter(User.is_active == True).count()