# backend/app/models/diaper.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class DiaperTypeEnum(enum.Enum):
    WET = "wet"        # Apenas xixi
    DIRTY = "dirty"    # Apenas cocô
    MIXED = "mixed"    # Ambos


class StoolConsistencyEnum(enum.Enum):
    LIQUID = "liquid"          # Líquido
    SOFT = "soft"              # Mole
    FORMED = "formed"          # Formado
    HARD = "hard"              # Duro


class StoolColorEnum(enum.Enum):
    YELLOW = "yellow"          # Amarelo (normal para bebês amamentados)
    BROWN = "brown"            # Marrom (normal)
    GREEN = "green"            # Verde
    BLACK = "black"            # Preto (mecônio ou preocupante)
    RED = "red"                # Vermelho (sangue - preocupante)
    WHITE = "white"            # Branco (preocupante)


class Diaper(Base):
    __tablename__ = "diaper_changes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Informações básicas
    change_time = Column(DateTime(timezone=True), nullable=False)
    diaper_type = Column(Enum(DiaperTypeEnum), nullable=False)
    
    # Informações sobre o cocô (se aplicável)
    stool_consistency = Column(Enum(StoolConsistencyEnum), nullable=True)
    stool_color = Column(Enum(StoolColorEnum), nullable=True)
    
    # Flags booleanas
    has_rash = Column(Boolean, default=False)  # Assadura
    applied_cream = Column(Boolean, default=False)  # Aplicou pomada
    
    # Observações
    notes = Column(Text, nullable=True)
    
    # Foreign Key
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    baby = relationship("Baby", back_populates="diaper_changes")
    
    @property
    def has_stool(self):
        """Verifica se a fralda contém cocô"""
        return self.diaper_type in [DiaperTypeEnum.DIRTY, DiaperTypeEnum.MIXED]
    
    @property
    def has_urine(self):
        """Verifica se a fralda contém xixi"""
        return self.diaper_type in [DiaperTypeEnum.WET, DiaperTypeEnum.MIXED]
    
    def __repr__(self):
        return f"<Diaper(id={self.id}, baby_id={self.baby_id}, type='{self.diaper_type}', time='{self.change_time}')>"