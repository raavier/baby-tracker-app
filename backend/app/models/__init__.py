# backend/app/models/__init__.py
"""
Models package for Baby Tracker application.

This package contains all SQLAlchemy models for the database.
Import this module to ensure all models are registered with SQLAlchemy.
"""

from app.core.database import Base

# Import all models to register them with SQLAlchemy
from .user import User
from .baby import Baby
from .feeding import Feeding
from .sleep import Sleep
from .photo import Photo
from .diaper import Diaper

# Export all models for easy importing
__all__ = [
    "Base",
    "User", 
    "Baby", 
    "Feeding", 
    "Sleep", 
    "Photo", 
    "Diaper"
]