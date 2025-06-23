import datetime
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Importar todos os modelos para que o SQLAlchemy os registre
from app.models import User, Baby, Feeding, Sleep, Photo, Diaper
from app.core.database import engine, Base, get_db

from app.api.v1.auth import router as auth_router

from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
from sqlalchemy import text 



# ============================================================================
# GERENCIAMENTO DO CICLO DE VIDA DA APLICAÇÃO
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação FastAPI.
    
    Esta função é chamada quando o servidor inicia e quando para.
    É aqui que fazemos configurações que precisam acontecer apenas uma vez,
    como verificar conexão com banco, carregar configurações, etc.
    
    Por que usamos isso?
    - Inicialização controlada: garante que tudo esteja pronto antes de aceitar requisições
    - Cleanup automático: fecha conexões e libera recursos quando servidor para
    - Debugging: permite logging de eventos importantes do ciclo de vida
    """
    
    # ===== STARTUP - Executado quando servidor inicia =====
    print("🚀 Iniciando Baby Tracker API...")
    
    # Verificar se conseguimos conectar no banco
    try:
        # Tenta criar uma sessão de teste
        db = next(get_db())
        db.close()
        print("✅ Conexão com PostgreSQL estabelecida com sucesso")
    except Exception as e:
        print(f"❌ Erro ao conectar com PostgreSQL: {e}")
        raise
    
    # Verificar se tabelas existem (sem criar automaticamente)
    try:
        inspector = engine.inspect(engine)
        existing_tables = inspector.get_table_names()
        expected_tables = ["users", "babies", "feedings", "sleep_records", "photos", "diaper_changes"]
        
        missing_tables = [table for table in expected_tables if table not in existing_tables]
        if missing_tables:
            print(f"⚠️  Tabelas ausentes: {missing_tables}")
            print("💡 Execute 'alembic upgrade head' para criar as tabelas")
        else:
            print("✅ Todas as tabelas do banco estão presentes")
            
    except Exception as e:
        print(f"⚠️  Não foi possível verificar tabelas: {e}")
    
    print("🎯 Baby Tracker API pronta para receber requisições!")
    print("📚 Documentação disponível em: http://localhost:8000/docs")
    print("🔍 Interface alternativa em: http://localhost:8000/redoc")
    
    # ===== YIELD - Aqui a aplicação roda normalmente =====
    yield
    
    # ===== SHUTDOWN - Executado quando servidor para =====
    print("🛑 Encerrando Baby Tracker API...")
    print("👋 Até a próxima!")



# Criar as tabelas automaticamente (apenas para desenvolvimento)
# Em produção, use Alembic para migrations
#Base.metadata.create_all(bind=engine)


# ============================================================================
# CONFIGURAÇÃO PRINCIPAL DA APLICAÇÃO
# ============================================================================

app = FastAPI(
    title="Baby Tracker API", 
    version="1.0.0",
    description="""
    **API completa para rastreamento de atividades do bebê**
    
    ### Funcionalidades Implementadas:
    
    🔐 **Autenticação JWT**: Sistema de login e registro seguro  
    👤 **Gerenciamento de Usuários**: Perfis e configurações  
    🍼 **Registro de Amamentação**: Em desenvolvimento  
    😴 **Controle de Sono**: Em desenvolvimento  
    📷 **Galeria de Fotos**: Em desenvolvimento  
    📊 **Dashboard**: Em desenvolvimento  
    
    ### Como usar:
    
    1. **Registre-se**: `POST /api/v1/auth/register`
    2. **Faça login**: `POST /api/v1/auth/login` 
    3. **Use o token**: Inclua `Authorization: Bearer <seu_token>` nos headers
    4. **Explore**: Teste todos os endpoints autenticados
    
    💡 **Dica**: Use o botão "Authorize" acima para configurar seu token automaticamente!
    """,
    contact={
        "name": "Baby Tracker Team",
        "url": "https://github.com/raavier/baby-tracker-app",
        "email": "flavio.ravier@gmail.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan  # ← Conecta nosso gerenciador de ciclo de vida
)


# ============================================================================
# CONFIGURAÇÃO DE MIDDLEWARE
# ============================================================================

# Middleware CORS - Permite acesso do frontend Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Flutter web em desenvolvimento
        "http://127.0.0.1:3000",   # Alternativa localhost
        "http://localhost:8080",
        "http://localhost:52975",
        # Em produção, adicionar domínios específicos:
        # "https://baby-tracker.app", 
        # "https://www.baby-tracker.app"
    ],
    allow_credentials=True,  # Permite envio de cookies e headers de auth
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # Métodos HTTP permitidos
    allow_headers=["*"],  # Permite todos os headers (Authorization, Content-Type, etc.)
)


# ============================================================================
# REGISTRO DE ROUTERS - "CONECTANDO OS MÓDULOS"
# ============================================================================

# Incluir router de autenticação
app.include_router(
    auth_router,
    # prefix já está definido no router (/api/v1/auth)
    # tags já estão definidas no router (["authentication"])
)

# 💡 Futuros routers serão adicionados aqui:
# app.include_router(feeding_router)
# app.include_router(sleep_router) 
# app.include_router(photos_router)

# ============================================================================
# ENDPOINTS RAIZ - "PÁGINA INICIAL DA API"
# ============================================================================

@app.get("/", tags=["System"])
async def root():
    """
    Endpoint raiz - informações gerais sobre a API.
    
    Este é como a "página inicial" da sua API. Útil para:
    - Verificar se a API está funcionando
    - Ver quais funcionalidades estão implementadas
    - Debugging básico
    """
    return {
        "🍼 message": "Bem-vindo ao Baby Tracker API!",
        "📊 status": "operacional",
        "🔧 version": "1.0.0",
        "📚 documentation": "http://localhost:8000/docs",
        "🔐 modules": {
            "authentication": "✅ Implementado",
            "feeding": "🚧 Em desenvolvimento", 
            "sleep": "🚧 Em desenvolvimento",
            "photos": "🚧 Em desenvolvimento",
            "dashboard": "🚧 Em desenvolvimento"
        },
        "🗃️ database": {
            "type": "PostgreSQL",
            "status": "conectado",
            "tables": ["users", "babies", "feedings", "sleep_records", "photos", "diaper_changes"]
        }
    }


# Configure logging para debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check com logging detalhado para debug.
    """
    logger.info("🏥 Iniciando health check...")
    
    try:
        logger.info("🔗 Tentando obter sessão do banco...")
        db = next(get_db())
        logger.info("✅ Sessão do banco obtida com sucesso")
        
        logger.info("📊 Executando query de teste...")
        result = db.execute(text("SELECT 1")).fetchone()
        logger.info(f"✅ Query executada com sucesso: {result}")
        
        logger.info("🔒 Fechando sessão do banco...")
        db.close()
        logger.info("✅ Sessão fechada com sucesso")
        
        response_data = {
            "status": "healthy",
            "service": "baby-tracker-api",
            "timestamp": datetime.datetime.now().isoformat(),  # Em produção, usar datetime real,
            "checks": {
                "database": "✅ PostgreSQL conectado",
                "authentication": "✅ JWT funcionando", 
                "api": "✅ Endpoints respondendo"
            }
        }
        
        logger.info(f"🎉 Health check concluído com sucesso: {response_data}")
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Erro no health check: {type(e).__name__}: {str(e)}")
        logger.error(f"📍 Traceback completo:", exc_info=True)
        
        # Se algo der errado, retorna erro 503 (Service Unavailable)
        error_detail = {
            "status": "unhealthy",
            "error": f"{type(e).__name__}: {str(e)}",
            "error_type": type(e).__name__,
            "checks": {
                "database": "❌ Erro na conexão",
                "api": "⚠️  Funcional com limitações"
            }
        }
        
        logger.error(f"🚨 Retornando erro 503: {error_detail}")
        
        raise HTTPException(
            status_code=503,
            detail=error_detail
        )


@app.get("/api/v1", tags=["System"])
async def api_info():
    """
    Informações sobre a versão v1 da API.
    
    Lista todos os endpoints disponíveis organizados por categoria.
    """
    return {
        "version": "1.0.0",
        "description": "Baby Tracker API v1",
        "endpoints": {
            "🔐 Authentication": {
                "POST /api/v1/auth/register": "Cadastrar novo usuário",
                "POST /api/v1/auth/login": "Fazer login",
                "GET /api/v1/auth/me": "Dados do usuário atual",
                "PUT /api/v1/auth/me": "Atualizar perfil",
                "POST /api/v1/auth/change-password": "Alterar senha",
                "POST /api/v1/auth/logout": "Fazer logout"
            },
            "🍼 Feeding": "Em desenvolvimento",
            "😴 Sleep": "Em desenvolvimento", 
            "📷 Photos": "Em desenvolvimento",
            "📊 Dashboard": "Em desenvolvimento"
        }
    }



# ============================================================================
# TRATAMENTO GLOBAL DE ERROS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Tratamento customizado para erros 404 (Not Found).
    
    Em vez de retornar uma mensagem genérica, retorna uma resposta
    mais amigável e útil para desenvolvedores.
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint não encontrado",
            "message": f"O endpoint '{request.url.path}' não existe",
            "suggestion": "Verifique a documentação em http://localhost:8000/docs",
            "available_endpoints": [
                "GET /",
                "GET /health", 
                "GET /api/v1",
                "POST /api/v1/auth/register",
                "POST /api/v1/auth/login"
            ]
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """
    Tratamento para erros internos do servidor.
    
    Garante que erros 500 não vazem informações sensíveis,
    mas ainda fornecem informações úteis para debugging.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "message": "Algo deu errado no nosso lado. Tente novamente em alguns momentos.",
            "request_id": str(id(request)),  # ID único para rastreamento
            "support": "Se o problema persistir, entre em contato com o suporte"
        }
    )


# ============================================================================
# EXECUTAR SERVIDOR EM DESENVOLVIMENTO
# ============================================================================

if __name__ == "__main__":
    """
    Executa o servidor em modo de desenvolvimento quando arquivo é executado diretamente.
    
    Em produção, use: uvicorn main:app --host 0.0.0.0 --port 8000
    """
    uvicorn.run(
        "main:app",           # módulo:aplicação
        host="127.0.0.1",     # Localhost apenas
        port=8000,            # Porta padrão FastAPI
        reload=True,          # Auto-reload em mudanças de código
        log_level="info"      # Nível de logging
    )