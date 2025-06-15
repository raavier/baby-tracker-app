# backend/app/models/feeding.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class FeedingTypeEnum(enum.Enum):
    BREASTFEEDING = "breastfeeding"
    BOTTLE = "bottle"
    SOLID_FOOD = "solid_food"


class BreastSideEnum(enum.Enum):
    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"


class Feeding(Base):
    __tablename__ = "feedings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Informações básicas
    feeding_type = Column(Enum(FeedingTypeEnum), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    
    # Para amamentação
    breast_side = Column(Enum(BreastSideEnum), nullable=True)
    
    # Para mamadeira (em ml)
    bottle_amount = Column(Float, nullable=True)
    
    # Para comida sólida
    food_description = Column(String(500), nullable=True)
    
    # Observações gerais
    notes = Column(Text, nullable=True)
    
    # Foreign Key
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    baby = relationship("Baby", back_populates="feedings")
    
    @property
    def duration_minutes(self):
        """Calcula a duração da amamentação em minutos"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return None
    
    def __repr__(self):
        return f"<Feeding(id={self.id}, type='{self.feeding_type}', baby_id={self.baby_id}, start_time='{self.start_time}')>"