from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar todos os modelos para que o SQLAlchemy os registre
from app.models import User, Baby, Feeding, Sleep, Photo, Diaper
from app.core.database import engine, Base

# Criar as tabelas automaticamente (apenas para desenvolvimento)
# Em produção, use Alembic para migrations
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Baby Tracker API", 
    version="1.0.0",
    description="API para rastreamento de atividades do bebê - amamentação, sono, fraldas e fotos"
)

# Configurar CORS para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "Hello World from Baby Tracker API! 🍼",
        "models_loaded": ["User", "Baby", "Feeding", "Sleep", "Photo", "Diaper"],
        "database": "PostgreSQL connected"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "baby-tracker-api",
        "database_tables": ["users", "babies", "feedings", "sleep_records", "photos", "diaper_changes"]
    }