# database.py - Database configuration and connection management

import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to local SQLite for development
    DATABASE_URL = "sqlite:///./smallprintchecker.db"

# Create SQLAlchemy engine
if DATABASE_URL.startswith("postgres"):
    # PostgreSQL connection
    engine = create_engine(DATABASE_URL)
else:
    # SQLite connection (for local development)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    subscription = Column(String, default="free")
    created_at = Column(DateTime, default=datetime.utcnow)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    subscription_status = Column(String, default="free")
    subscription_expires = Column(DateTime, nullable=True)
    
    # Usage tracking (stored as JSON)
    usage_data = Column(JSON, default={
        "current_month": None,
        "documents_this_month": 0,
        "total_documents": 0,
        "last_upload": None
    })
    
    # Upgrade tracking (stored as JSON)
    upgrade_tracking_data = Column(JSON, default={
        "upgrade_attempts": 0,
        "last_upgrade_attempt": None,
        "abandoned_upgrades": 0,
        "upgrade_abandoned_at": None
    })

class SavedAnalysis(Base):
    __tablename__ = "saved_analyses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    analysis_name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    analysis_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for performance
    __table_args__ = (
        Index('idx_saved_analyses_user_id', 'user_id'),
        Index('idx_saved_analyses_created_at', 'created_at'),
    )

class DatabaseManager:
    """Database manager for user operations"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def get_db(self) -> Session:
        """Get database session"""
        db = self.SessionLocal()
        try:
            return db
        finally:
            db.close()
    
    def create_tables(self):
        """Create all database tables (only if they don't exist)"""
        # Use checkfirst=True to prevent dropping existing tables
        # This prevents data loss on redeployment
        Base.metadata.create_all(bind=self.engine, checkfirst=True)
    
    def test_connection(self):
        """Test database connection and check persistence"""
        try:
            db = self.SessionLocal()
            try:
                # Check if we can query the database
                from sqlalchemy import text
                result = db.execute(text("SELECT 1")).scalar()
                print(f"✅ Database connection successful: {DATABASE_URL[:50]}...")
                
                # Check if we're using PostgreSQL (persistent) or SQLite (ephemeral)
                if DATABASE_URL.startswith("postgres"):
                    print("✅ Using PostgreSQL - data will persist across deployments")
                else:
                    print("⚠️ Using SQLite - data will NOT persist on Railway deployments")
                    print("⚠️ Add a PostgreSQL database to Railway to enable persistence")
                
                return True
            finally:
                db.close()
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def user_exists(self, user_id: str) -> bool:
        """Check if user exists"""
        db = self.SessionLocal()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            return user is not None
        except Exception as e:
            print(f"Error checking if user exists: {e}")
            return False
        finally:
            db.close()
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        db = self.SessionLocal()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                return self._user_to_dict(user)
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
        finally:
            db.close()
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        db = self.SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user:
                return self._user_to_dict(user)
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
        finally:
            db.close()
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        db = self.SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user:
                return self._user_to_dict(user)
            return None
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
        finally:
            db.close()
    
    def create_user(self, user_id: str, email: str, password_hash: str, username: str) -> Dict:
        """Create a new user"""
        from sqlalchemy.exc import IntegrityError
        
        db = self.SessionLocal()
        try:
            # Check if user already exists by email or username
            existing_user = db.query(User).filter(
                (User.email == email) | (User.username == username)
            ).first()
            
            if existing_user:
                if existing_user.email == email:
                    raise ValueError(f"User with email {email} already exists")
                if existing_user.username == username:
                    raise ValueError(f"Username {username} already taken")
            
            # Create new user
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                subscription="free",
                created_at=datetime.utcnow(),
                usage_data={
                    "current_month": datetime.utcnow().strftime("%Y-%m"),
                    "documents_this_month": 0,
                    "total_documents": 0,
                    "last_upload": None
                },
                upgrade_tracking_data={
                    "upgrade_attempts": 0,
                    "last_upgrade_attempt": None,
                    "abandoned_upgrades": 0,
                    "upgrade_abandoned_at": None
                }
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return self._user_to_dict(user)
        except IntegrityError as e:
            db.rollback()
            print(f"Database integrity error: {e}")
            raise ValueError("User with this email or username already exists")
        except Exception as e:
            db.rollback()
            print(f"Error creating user: {e}")
            raise
        finally:
            db.close()
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user data"""
        db = self.SessionLocal()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error updating user: {e}")
            return False
        finally:
            db.close()
    
    def update_usage(self, user_id: str, usage_data: Dict) -> bool:
        """Update user usage data"""
        return self.update_user(user_id, usage_data=usage_data)
    
    def update_upgrade_tracking(self, user_id: str, upgrade_tracking_data: Dict) -> bool:
        """Update user upgrade tracking data"""
        return self.update_user(user_id, upgrade_tracking_data=upgrade_tracking_data)
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        db = self.get_db()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                db.delete(user)
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    def _user_to_dict(self, user: User) -> Dict:
        """Convert User model to dictionary"""
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "password_hash": user.password_hash,
            "subscription": user.subscription,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "stripe_customer_id": user.stripe_customer_id,
            "stripe_subscription_id": user.stripe_subscription_id,
            "subscription_status": user.subscription_status,
            "subscription_expires": user.subscription_expires.isoformat() if user.subscription_expires else None,
            "usage": user.usage_data or {},
            "upgrade_tracking": user.upgrade_tracking_data or {}
        }
    
    # Saved Analysis Methods
    def create_saved_analysis(self, user_id: str, analysis_name: str, original_filename: str, 
                            notes: str, analysis_data: Dict) -> Optional[Dict]:
        """Create a new saved analysis"""
        db = self.SessionLocal()
        try:
            saved_analysis = SavedAnalysis(
                user_id=user_id,
                analysis_name=analysis_name,
                original_filename=original_filename,
                notes=notes,
                analysis_data=analysis_data,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(saved_analysis)
            db.commit()
            db.refresh(saved_analysis)
            
            return self._saved_analysis_to_dict(saved_analysis)
        except Exception as e:
            db.rollback()
            print(f"Error creating saved analysis: {e}")
            return None
        finally:
            db.close()
    
    def get_saved_analyses(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get user's saved analyses (metadata only)"""
        db = self.SessionLocal()
        try:
            analyses = db.query(SavedAnalysis).filter(
                SavedAnalysis.user_id == user_id
            ).order_by(SavedAnalysis.created_at.desc()).offset(offset).limit(limit).all()
            
            return [self._saved_analysis_to_dict(analysis) for analysis in analyses]
        except Exception as e:
            print(f"Error getting saved analyses: {e}")
            return []
        finally:
            db.close()
    
    def get_saved_analysis(self, analysis_id: int, user_id: str) -> Optional[Dict]:
        """Get specific saved analysis by ID"""
        db = self.SessionLocal()
        try:
            analysis = db.query(SavedAnalysis).filter(
                SavedAnalysis.id == analysis_id,
                SavedAnalysis.user_id == user_id
            ).first()
            
            if analysis:
                return self._saved_analysis_to_dict(analysis)
            return None
        except Exception as e:
            print(f"Error getting saved analysis: {e}")
            return None
        finally:
            db.close()
    
    def update_saved_analysis(self, analysis_id: int, user_id: str, 
                            analysis_name: str = None, notes: str = None) -> bool:
        """Update saved analysis name and/or notes"""
        db = self.SessionLocal()
        try:
            analysis = db.query(SavedAnalysis).filter(
                SavedAnalysis.id == analysis_id,
                SavedAnalysis.user_id == user_id
            ).first()
            
            if not analysis:
                return False
            
            if analysis_name is not None:
                analysis.analysis_name = analysis_name
            if notes is not None:
                analysis.notes = notes
            
            analysis.updated_at = datetime.utcnow()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error updating saved analysis: {e}")
            return False
        finally:
            db.close()
    
    def delete_saved_analysis(self, analysis_id: int, user_id: str) -> bool:
        """Delete saved analysis"""
        db = self.SessionLocal()
        try:
            analysis = db.query(SavedAnalysis).filter(
                SavedAnalysis.id == analysis_id,
                SavedAnalysis.user_id == user_id
            ).first()
            
            if analysis:
                db.delete(analysis)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            print(f"Error deleting saved analysis: {e}")
            return False
        finally:
            db.close()
    
    def count_user_saved_analyses(self, user_id: str) -> int:
        """Count user's saved analyses"""
        db = self.SessionLocal()
        try:
            count = db.query(SavedAnalysis).filter(SavedAnalysis.user_id == user_id).count()
            return count
        except Exception as e:
            print(f"Error counting saved analyses: {e}")
            return 0
        finally:
            db.close()
    
    def _saved_analysis_to_dict(self, analysis: SavedAnalysis) -> Dict:
        """Convert SavedAnalysis model to dictionary"""
        return {
            "id": analysis.id,
            "user_id": analysis.user_id,
            "analysis_name": analysis.analysis_name,
            "original_filename": analysis.original_filename,
            "notes": analysis.notes,
            "analysis_data": analysis.analysis_data,
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
            "updated_at": analysis.updated_at.isoformat() if analysis.updated_at else None
        }

# Global database manager instance
db_manager = DatabaseManager()

# Initialize database tables
def init_database():
    """Initialize database tables"""
    db_manager.create_tables()
    print("✅ Database tables created successfully")
    # Test connection and warn about persistence
    db_manager.test_connection()

if __name__ == "__main__":
    init_database()
