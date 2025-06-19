# backend/app/api/v1/auth.py
"""
APIs de Autenticação - O "Balcão de Atendimento" do Sistema

Este arquivo é onde toda a magia acontece! Aqui conectamos:
- Os schemas Pydantic (formulários digitais)
- As funções de segurança JWT (fábrica de pulseirinhas)
- O modelo User do banco de dados
- A lógica de negócio de autenticação

É como um balcão de atendimento muito eficiente onde cada operação
(cadastro, login, atualização) tem seu próprio procedimento específico,
mas todos seguem os mesmos padrões de segurança e qualidade.
"""


from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional


# Importando nossos módulos criados anteriormente
from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password, 
    create_access_token,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin, 
    UserUpdate,
    UserResponse,
    TokenResponse,
    MessageResponse,
    ErrorResponse,
    PasswordChange
)

# Configuração do roteador - é como definir o "endereço" deste balcão
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

# Configuração da segurança Bearer Token (para endpoints protegidos)
security = HTTPBearer()

# ============================================================================
# FUNÇÕES AUXILIARES - "Os Assistentes do Balcão"
# ============================================================================

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Busca usuário pelo email no banco de dados.
    
    Esta função é como um fichário bem organizado - você fornece
    o email e ela encontra rapidamente o usuário correspondente.
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Busca usuário pelo ID no banco de dados.
    
    Esta é provavelmente a busca mais rápida, pois ID é a chave primária.
    Usamos principalmente quando validamos tokens JWT.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Busca usuário pelo username no banco de dados.
    
    Similar à função anterior, mas busca pelo nome de usuário.
    Útil quando permitimos login tanto com email quanto username.
    """
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    """
    Autentica um usuário verificando credenciais.
    
    Este é o "processo de verificação de identidade" completo:
    1. Encontra o usuário pelo username OU email
    2. Verifica se a senha está correta
    3. Retorna o usuário se tudo estiver certo, None caso contrário
    
    Por que permitimos login com username OU email?
    - Flexibilidade para o usuário (pode usar o que lembrar)
    - Experiência mais amigável
    - Padrão em muitos apps modernos
    """
    # Primeiro, vamos tentar encontrar o usuário
    user = None
    
    # Tenta encontrar por email (se contém @, provavelmente é email)
    if "@" in username_or_email:
        user = get_user_by_email(db, username_or_email)
    else:
        # Senão, tenta por username
        user = get_user_by_username(db, username_or_email)
    
    # Se não encontrou o usuário, retorna None
    if not user:
        return None
    
    # Se encontrou, verifica a senha
    if not verify_password(password, user.hashed_password):
        return None
    
    # Se chegou até aqui, usuário está autenticado!
    return user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extrai o usuário atual a partir do token JWT.
    
    Esta função é como um "verificador de pulseirinhas" que funciona assim:
    1. Pega o token do cabeçalho Authorization
    2. Verifica se o token é válido
    3. Extrai o user_id do token
    4. Busca o usuário no banco
    5. Retorna o usuário autenticado
    
    Esta função será usada em TODOS os endpoints protegidos.
    É ela que garante que apenas usuários logados acessem certas funcionalidades.
    """
    # Define exceção padrão para credenciais inválidas
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extrai o token do cabeçalho (remove "Bearer " do início)
        token = credentials.credentials
        
        # Verifica e decodifica o token usando nossa função de segurança
        payload = verify_token(token)
        
        if payload is None:
            raise credentials_exception
        
        # Extrai o user_id do payload
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        
        # Busca o usuário no banco
        user = get_user_by_id(db, user_id=int(user_id))
        if user is None:
            raise credentials_exception
        
        # Verifica se o usuário ainda está ativo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo"
            )
        
        return user
        
    except Exception as e:
        raise credentials_exception

# ============================================================================
# ENDPOINTS PÚBLICOS - "Balcão de Atendimento para Visitantes"
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário no sistema.
    
    Este é como o "balcão de inscrições" onde novos usuários se cadastram.
    O processo é rigoroso mas amigável:
    
    1. Valida todos os dados usando o schema UserCreate
    2. Verifica se email e username não estão em uso
    3. Criptografa a senha usando bcrypt
    4. Salva no banco de dados
    5. Retorna os dados do usuário (sem a senha!)
    
    Por que não retornamos um token imediatamente?
    - Separação clara: registro é uma operação, login é outra
    - Permite implementar verificação de email no futuro
    - Experiência mais controlada para o usuário
    """
     # Verifica se email já existe
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está em uso"
        )
    
    

    # Verifica se username já existe
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já está em uso"
        )
    
    # Cria o hash da senha (nunca armazenamos senhas em texto puro!)
    hashed_password = get_password_hash(user_data.password)

     # Cria o objeto User para salvar no banco
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False  # Pode implementar verificação de email no futuro
    )

    # Salva no banco de dados
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Atualiza o objeto com dados do banco (como ID)
    
    # Retorna o usuário criado (o schema UserResponse automaticamente exclui a senha)
    return db_user


@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Realiza login do usuário e retorna token JWT.
    
    Este é o "balcão de identificação" onde usuários apresentam suas credenciais
    e recebem sua "pulseirinha de acesso" (token JWT). O processo é:
    
    1. Valida dados usando schema UserLogin
    2. Autentica usuário (verifica se existe e senha está correta)
    3. Cria token JWT válido por 1 ano (como você configurou)
    4. Retorna token + dados básicos do usuário
    
    Por que retornamos os dados do usuário junto com o token?
    - Evita uma requisição extra do frontend para buscar dados
    - Frontend pode imediatamente exibir "Bem-vindo, João!"
    - Melhora a experiência do usuário
    """
    
    # Tenta autenticar o usuário
    user = authenticate_user(db, login_data.username_or_email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username/email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verifica se usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada. Entre em contato com o suporte."
        )
    
    # Cria o token JWT
    access_token = create_access_token(
        data={"sub": str(user.id)}  # "sub" é padrão JWT para subject (usuário)
    )
    
    # Calcula tempo de expiração em segundos (para informar o frontend)
    expires_in = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Converte minutos para segundos
    
    # Retorna resposta completa com token e dados do usuário
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse.from_orm(user)  # Converte modelo SQLAlchemy para schema Pydantic
    )


# ============================================================================
# ENDPOINTS PROTEGIDOS - "Balcão VIP para Usuários Autenticados"
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Retorna informações do usuário atual.
    
    Este é um endpoint simples mas muito útil. Permite que o frontend
    verifique se o token ainda é válido e obtenha dados atualizados do usuário.
    
    Por que este endpoint é importante?
    - Validação de token: se o token expirou, este endpoint retorna erro
    - Dados atualizados: se o usuário mudou o perfil em outro dispositivo
    - Healthcheck: frontend pode verificar se a conexão está funcionando
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza informações do usuário atual.
    
    Este endpoint permite que o usuário modifique seus dados pessoais.
    Como todos os campos são opcionais no schema UserUpdate, o usuário
    pode atualizar apenas as informações que quiser.
    
    Validações importantes que fazemos:
    - Se mudou email, verifica se o novo não está em uso
    - Se mudou username, verifica se o novo não está em uso
    - Aplica todas as validações do schema (formato email, etc.)
    """
    
    # Verifica se novo email já existe (se fornecido)
    if user_update.email and user_update.email != current_user.email:
        existing_user = get_user_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso por outro usuário"
            )
    
    # Verifica se novo username já existe (se fornecido)
    if user_update.username and user_update.username != current_user.username:
        existing_user = get_user_by_username(db, user_update.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username já está em uso por outro usuário"
            )
    
    # Atualiza apenas os campos fornecidos
    update_data = user_update.model_dump(exclude_unset=True)  # Só campos que foram enviados
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    # Atualiza timestamp de modificação
    current_user.updated_at = datetime.utcnow()
    
    # Salva no banco
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Altera a senha do usuário atual.
    
    Este é um processo de segurança sensível que requer validações extras:
    1. Confirma senha atual (prova que é realmente o usuário)
    2. Valida nova senha (força, confirmação)
    3. Atualiza com hash da nova senha
    
    Por que exigimos a senha atual?
    - Protege contra alguém que tenha acesso temporário ao dispositivo
    - Confirma que é o usuário legítimo fazendo a mudança
    - Padrão de segurança em sistemas modernos
    """
    
    # Verifica se a senha atual está correta
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    # Gera hash da nova senha
    new_hashed_password = get_password_hash(password_data.new_password)
    
    # Atualiza no banco
    current_user.hashed_password = new_hashed_password
    current_user.updated_at = datetime.now(datetime.timezone.utc)
    
    db.commit()
    
    return MessageResponse(
        message="Senha alterada com sucesso",
        success=True
    )

@router.post("/logout", response_model=MessageResponse)
async def logout_user(current_user: User = Depends(get_current_user)):
    """
    Realiza logout do usuário.
    
    Com JWT, o logout é principalmente um processo do lado do cliente
    (frontend descarta o token). Este endpoint serve mais para:
    1. Confirmar que o logout foi intencional
    2. Registrar evento de logout (logs de auditoria)
    3. Permitir logout de outros dispositivos no futuro
    
    Nota: Em implementações mais avançadas, você poderia manter uma
    "blacklist" de tokens invalidados, mas para uso familiar isso
    é provavelmente desnecessário.
    """
    return MessageResponse(
        message=f"Logout realizado com sucesso para {current_user.username}",
        success=True
    )

# ============================================================================
# ENDPOINTS ADMINISTRATIVOS - "Balcão de Gerenciamento" (Para o Futuro)
# ============================================================================


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id_endpoint(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca informações de um usuário específico por ID.
    
    Por enquanto, qualquer usuário autenticado pode ver qualquer outro.
    No futuro, você pode adicionar lógica para:
    - Apenas admins podem ver outros usuários
    - Usuários só podem ver membros da mesma família
    - Implementar permissões granulares
    """
    user = get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user



# ============================================================================
# HEALTHCHECK - "Verificação de Funcionamento"
# ============================================================================

@router.get("/health", response_model=MessageResponse)
async def auth_healthcheck():
    """
    Endpoint simples para verificar se o sistema de autenticação está funcionando.
    
    Útil para monitoramento, testes automatizados, e debugging.
    Não requer autenticação - é como um "sinal de vida" do sistema.
    """
    return MessageResponse(
        message="Sistema de autenticação funcionando corretamente",
        success=True
    )
