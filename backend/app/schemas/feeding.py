"""
Schemas Pydantic para o módulo Feeding - Validação e serialização de dados
Localização: backend/app/schemas/feeding.py
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class BreastSide(str, Enum):
    """Enum para indicar qual seio foi usado na amamentação"""
    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"

class FeedingType(str, Enum):
    """Enum para tipo de alimentação"""
    BREAST = "breast"        # Amamentação no seio
    BOTTLE = "bottle"        # Mamadeira
    SOLID = "solid"          # Alimentação sólida


# ===== SCHEMAS DE REQUEST (entrada) =====

class FeedingCreat(BaseModel):
    """Schema para criar uma nova amamentação"""
    feeding_type: FeedingType = Field(..., description="Tipo de alimentação")
    start_time: datetime = Field(..., description= "Horário de início")
    end_time: Optional[datetime] = Field(None, description="Horário fim (opcional para feeds em andamento)")
    breast_side: Optional[BreastSide] = Field(None, description="Lado do seio, apenas para amamentação")
    notes: Optional[str] = Field(None, max_length=500, description="Observações adicionais")

    @validator('end_time')
    def validate_end_time(cls, v, values):
        """"Validar que end_time é posterior ao start_time"""
        if v and 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time deve ser posterior ao start_time')
        return v
    
    @validator('breast_side')
    def validate_breast_side(cls,v,values):
        """Validar que breast_side é obrigatório para amamentação no seio"""
        if "feeding_type" in values and values["feeding_type"] == FeedingType.BREAST:
            if not v:
                raise ValueError('breast_side é obrigatório para amamentação no seio')
            return v
        
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "end_time": "2025-06-25T08:50:00",
                "notes": "Bebê mamou bem e dormiu em seguida"
            }
        } 
