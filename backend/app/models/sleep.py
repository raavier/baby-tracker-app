# backend/app/models/sleep.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class SleepQualityEnum(enum.Enum):
    EXCELLENT = "excellent"      # 5 estrelas
    GOOD = "good"               # 4 estrelas
    AVERAGE = "average"         # 3 estrelas
    POOR = "poor"              # 2 estrelas
    VERY_POOR = "very_poor"    # 1 estrela


class SleepTypeEnum(enum.Enum):
    NAP = "nap"                # Soneca
    NIGHT_SLEEP = "night_sleep" # Sono noturno


class Sleep(Base):
    __tablename__ = "sleep_records"

    id = Column(Integer, primary_key=True, index=True)
    
    # Informações do sono
    sleep_start = Column(DateTime(timezone=True), nullable=False)
    sleep_end = Column(DateTime(timezone=True), nullable=True)
    sleep_type = Column(Enum(SleepTypeEnum), nullable=False, default=SleepTypeEnum.NAP)
    sleep_quality = Column(Enum(SleepQualityEnum), nullable=True)
    
    # Observações
    notes = Column(Text, nullable=True)
    
    # Foreign Key
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    baby = relationship("Baby", back_populates="sleep_records")
    
    @property
    def duration_minutes(self):
        """Calcula a duração do sono em minutos"""
        if self.sleep_start and self.sleep_end:
            delta = self.sleep_end - self.sleep_start
            return int(delta.total_seconds() / 60)
        return None
    
    @property
    def duration_hours(self):
        """Calcula a duração do sono em horas (formatado)"""
        minutes = self.duration_minutes
        if minutes is not None:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}h {mins}m"
        return None
    
    @property
    def is_active(self):
        """Verifica se o sono está em andamento (sem hora de fim)"""
        return self.sleep_end is None
    
    def __repr__(self):
        return f"<Sleep(id={self.id}, baby_id={self.baby_id}, start='{self.sleep_start}', duration='{self.duration_hours}')>"