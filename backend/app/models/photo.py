# backend/app/models/photo.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    
    # Informações da foto
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    s3_url = Column(String(500), nullable=False)  # URL completa da foto no S3
    s3_key = Column(String(500), nullable=False)  # Chave do arquivo no S3
    
    # Metadados
    file_size = Column(Integer, nullable=True)  # Tamanho em bytes
    content_type = Column(String(100), nullable=False, default="image/jpeg")
    width = Column(Integer, nullable=True)  # Largura da imagem
    height = Column(Integer, nullable=True)  # Altura da imagem
    
    # Informações contextuais
    caption = Column(Text, nullable=True)  # Legenda da foto
    is_milestone = Column(Boolean, default=False)  # Marco importante
    milestone_description = Column(String(500), nullable=True)  # Descrição do marco
    
    # Data da foto (pode ser diferente da data de upload)
    photo_taken_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign Key
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    baby = relationship("Baby", back_populates="photos")
    
    @property
    def file_size_mb(self):
        """Retorna o tamanho do arquivo em MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None
    
    def __repr__(self):
        return f"<Photo(id={self.id}, filename='{self.filename}', baby_id={self.baby_id})>"