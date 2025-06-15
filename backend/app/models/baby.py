# backend/app/models/baby.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class GenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Baby(Base):
    __tablename__ = "babies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    birth_weight = Column(Integer, nullable=True)  # Peso em gramas
    birth_height = Column(Integer, nullable=True)  # Altura em centímetros
    notes = Column(Text, nullable=True)
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="babies")
    feedings = relationship("Feeding", back_populates="baby", cascade="all, delete-orphan")
    sleep_records = relationship("Sleep", back_populates="baby", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="baby", cascade="all, delete-orphan")
    diaper_changes = relationship("Diaper", back_populates="baby", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Baby(id={self.id}, name='{self.name}', birth_date='{self.birth_date}')>"