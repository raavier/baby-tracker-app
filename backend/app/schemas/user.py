# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


# ============================================================================
# SCHEMAS PARA ENTRADA DE DADOS (Request) - "Formulários que o usuário preenche"
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="Email do usuário (deve ser válido)",
        example="joao@gmail.com"
    )
    
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        description="Nome de usuário único (3-50 caracteres)",
        example="joao_pai"
    )
    
    full_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Nome completo do usuário",
        example="João Silva"
    )
    
    @validator('username')
    def username_must_be_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Username deve conter apenas letras, números e underscore')
        return v.lower()  # Sempre converte para minúsculo para consistência
    
    @validator('full_name')
    def full_name_must_be_valid(cls, v):
        if len(v.split()) < 2:
            raise ValueError('Nome completo deve ter pelo menos nome e sobrenome')
        return v.title()  # Converte para Primeira Letra Maiúscula


class UserCreate(UserBase):
    password: str = Field(
        ..., 
        min_length=8,
        description="Senha do usuário (mínimo 8 caracteres)",
        example="minhaSenhaSegura123"
    )
    
    @validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        
        # Verifica se tem pelo menos uma letra e um número
        has_letter = any(c.isalpha() for c in v)
        has_number = any(c.isdigit() for c in v)
        
        if not (has_letter and has_number):
            raise ValueError('Senha deve conter pelo menos uma letra e um número')
        
        return v


class UserLogin(BaseModel):
    """
    Schema para login do usuário.
    
    Este é o "formulário de entrada" - bem simples, só username/email e senha.
    Observe que permitimos login tanto com username quanto com email para
    conveniência do usuário.
    """
    
    username_or_email: str = Field(
        ...,
        description="Username ou email para login",
        example="joao_pai ou joao@gmail.com"
    )
    
    password: str = Field(
        ...,
        description="Senha do usuário",
        example="minhaSenhaSegura123"
    )


class UserUpdate(BaseModel): 
    email: Optional[EmailStr] = Field(
        None,
        description="Novo email (opcional)",
        example="novo_email@gmail.com"
    )
    
    username: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=50,
        description="Novo username (opcional)",
        example="joao_pai_2024"
    )
    
    full_name: Optional[str] = Field(
        None, 
        min_length=2, 
        max_length=100,
        description="Novo nome completo (opcional)",
        example="João Santos Silva"
    )
    
    # Aplicamos as mesmas validações do UserBase
    @validator('username')
    def username_must_be_alphanumeric(cls, v):
        if v and not v.replace('_', '').isalnum():
            raise ValueError('Username deve conter apenas letras, números e underscore')
        return v.lower() if v else v
    
    @validator('full_name')
    def full_name_must_be_valid(cls, v):
        if v and len(v.split()) < 2:
            raise ValueError('Nome completo deve ter pelo menos nome e sobrenome')
        return v.title() if v else v


class PasswordChange(BaseModel):
    current_password: str = Field(
        ...,
        description="Senha atual para confirmação",
        example="senhaAtual123"
    )
    
    new_password: str = Field(
        ...,
        min_length=8,
        description="Nova senha (mínimo 8 caracteres)",
        example="novaSenhaSegura456"
    )
    
    confirm_password: str = Field(
        ...,
        description="Confirmação da nova senha",
        example="novaSenhaSegura456"
    )
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """
        Validação para garantir que nova senha e confirmação são iguais.
        """
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Nova senha e confirmação devem ser iguais')
        return v
    
    @validator('new_password')
    def new_password_must_be_strong(cls, v):
        """
        Aplica as mesmas regras de senha forte da criação.
        """
        if len(v) < 8:
            raise ValueError('Nova senha deve ter pelo menos 8 caracteres')
        
        has_letter = any(c.isalpha() for c in v)
        has_number = any(c.isdigit() for c in v)
        
        if not (has_letter and has_number):
            raise ValueError('Nova senha deve conter pelo menos uma letra e um número')
        
        return v


# ============================================================================
# SCHEMAS PARA SAÍDA DE DADOS (Response) - "Recibos que o sistema entrega"
# ============================================================================

class UserResponse(UserBase):  
    id: int = Field(
        ...,
        description="ID único do usuário no sistema",
        example=123
    )
    
    is_active: bool = Field(
        ...,
        description="Se o usuário está ativo no sistema",
        example=True
    )
    
    is_verified: bool = Field(
        ...,
        description="Se o email do usuário foi verificado",
        example=False
    )
    
    created_at: datetime = Field(
        ...,
        description="Data e hora da criação da conta",
        example="2024-01-15T10:30:00Z"
    )
    
    updated_at: Optional[datetime] = Field(
        None,
        description="Data e hora da última atualização",
        example="2024-01-20T15:45:00Z"
    )
    
    class Config:
        """
        Configuração especial do Pydantic para trabalhar com SQLAlchemy.
        
        from_attributes=True permite que o Pydantic leia dados diretamente
        de objetos SQLAlchemy (nossos modelos do banco de dados).
        """
        from_attributes = True


class TokenResponse(BaseModel):
    """
    Schema para resposta do login - retorna o token JWT.
    
    Este é o "ingresso VIP" que o usuário recebe após fazer login com sucesso.
    É basicamente o seu token de acesso por um ano (como você configurou).
    """
    
    access_token: str = Field(
        ...,
        description="Token JWT para autenticação",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    
    token_type: str = Field(
        default="bearer",
        description="Tipo do token (sempre 'bearer' para JWT)",
        example="bearer"
    )
    
    expires_in: int = Field(
        ...,
        description="Tempo de vida do token em segundos",
        example=31536000  # 1 ano em segundos (365 * 24 * 60 * 60)
    )
    
    user: UserResponse = Field(
        ...,
        description="Dados básicos do usuário autenticado"
    )


class UserListResponse(BaseModel):
    """
    Schema para listar usuários (útil para funcionalidades administrativas futuras).
    
    Inclui paginação caso você tenha muitos usuários no futuro.
    """
    
    users: list[UserResponse] = Field(
        ...,
        description="Lista de usuários"
    )
    
    total: int = Field(
        ...,
        description="Total de usuários encontrados",
        example=42
    )
    
    page: int = Field(
        default=1,
        description="Página atual",
        example=1
    )
    
    per_page: int = Field(
        default=10,
        description="Usuários por página",
        example=10
    )


# ============================================================================
# SCHEMAS PARA MENSAGENS DE ERRO E SUCESSO - "Comunicação Clara com o Usuário"
# ============================================================================

class MessageResponse(BaseModel):
    """
    Schema padrão para mensagens de sucesso ou informação.
    
    Usado quando você quer retornar apenas uma mensagem simples,
    como "Usuário criado com sucesso" ou "Email de verificação enviado".
    """
    
    message: str = Field(
        ...,
        description="Mensagem para o usuário",
        example="Usuário criado com sucesso"
    )
    
    success: bool = Field(
        default=True,
        description="Indica se a operação foi bem-sucedida",
        example=True
    )


class ErrorResponse(BaseModel):
    """
    Schema padrão para mensagens de erro.
    
    Garante que todos os erros sejam retornados de forma consistente,
    facilitando o tratamento no frontend Flutter.
    """
    
    error: str = Field(
        ...,
        description="Mensagem de erro principal",
        example="Username já existe"
    )
    
    detail: Optional[str] = Field(
        None,
        description="Detalhes adicionais sobre o erro",
        example="O username 'joao_pai' já está sendo usado por outro usuário"
    )
    
    error_code: Optional[str] = Field(
        None,
        description="Código de erro para tratamento programático",
        example="USERNAME_ALREADY_EXISTS"
    )


# ============================================================================
# EXEMPLO DE USO - Como Estes Schemas Se Conectam
# ============================================================================

if __name__ == "__main__":
    """
    Exemplo prático de como usar estes schemas.
    Execute este arquivo para ver as validações funcionando!
    """
    
    print("📋 Demonstração dos Schemas de Usuário")
    print("=" * 50)
    
    # 1. Exemplo de criação de usuário válida
    try:
        user_data = UserCreate(
            email="joao@gmail.com",
            username="joao_pai",
            full_name="João Silva",
            password="minhasenha123"
        )
        print(f"✅ Usuário válido criado: {user_data.username}")
        print(f"   Email: {user_data.email}")
        print(f"   Nome: {user_data.full_name}")
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
    
    # 2. Exemplo de email inválido
    try:
        invalid_user = UserCreate(
            email="email_sem_arroba",  # Email inválido
            username="test",
            full_name="Teste Silva",
            password="senha123"
        )
    except Exception as e:
        print(f"❌ Email inválido detectado: {e}")
    
    # 3. Exemplo de senha fraca
    try:
        weak_password = UserCreate(
            email="test@gmail.com",
            username="test",
            full_name="Teste Silva",
            password="123"  # Senha muito fraca
        )
    except Exception as e:
        print(f"❌ Senha fraca detectada: {e}")
    
    # 4. Exemplo de login
    login_data = UserLogin(
        username_or_email="joao_pai",
        password="minhasenha123"
    )
    print(f"✅ Login válido: {login_data.username_or_email}")
    
    # 5. Exemplo de resposta de token
    token_response = TokenResponse(
        access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        expires_in=31536000,  # 1 ano
        user=UserResponse(
            id=1,
            email="joao@gmail.com",
            username="joao_pai",
            full_name="João Silva",
            is_active=True,
            is_verified=False,
            created_at=datetime.now()
        )
    )
    print(f"✅ Token criado para: {token_response.user.full_name}")
    print(f"   Expira em: {token_response.expires_in} segundos (1 ano)")