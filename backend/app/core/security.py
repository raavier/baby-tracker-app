
from datetime import datetime, timedelta
from typing import Optional, Union
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "baby-tracker-super-secret-key-change-in-production")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 525600

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
   
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
   
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    # Copia os dados para não modificar o original
    to_encode = data.copy()
    
    # Define quando o token vai expirar
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Adiciona a informação de expiração ao token
    to_encode.update({"exp": expire})
    
    # Cria o token assinado com nossa chave secreta
    # É aqui que a "magia" acontece - o token fica impossível de falsificar
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        # Tenta decodificar o token usando nossa chave secreta
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extrai o identificador do usuário
        user_id: str = payload.get("sub")
        
        # Se não tem user_id, o token é inválido
        if user_id is None:
            return None
            
        # Retorna os dados extraídos do token
        return {"user_id": user_id}
        
    except JWTError:
        # Qualquer erro na decodificação significa token inválido
        return None
    

def create_refresh_token(user_id: str) -> str:
    refresh_data = {
        "sub": str(user_id),
        "type": "refresh"  # Marca que é um token de renovação
    }
    
    # Refresh token dura 7 dias
    expire_delta = timedelta(days=7)
    return create_access_token(refresh_data, expire_delta)

def is_token_expired(token: str) -> bool:
    try:
        # Decodifica sem verificar expiração
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        
        # Pega o timestamp de expiração
        exp_timestamp = payload.get("exp")
        if not exp_timestamp:
            return True  # Se não tem expiração, considera expirado
            
        # Converte para datetime e compara com agora
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        return datetime.utcnow() > exp_datetime
        
    except JWTError:
        return True  # Se não consegue decodificar, considera expirado
    
    
if __name__ == "__main__":
    """
    Exemplo prático de como usar este sistema de segurança.
    Execute este arquivo para ver a magia acontecer!
    """
    
    print("🔐 Demonstração do Sistema de Segurança JWT")
    print("=" * 50)
    
    # 1. Simulando cadastro de usuário
    senha_original = "minha_senha_super_secreta"
    senha_hash = get_password_hash(senha_original)
    print(f"📝 Senha original: {senha_original}")
    print(f"🔒 Hash armazenado: {senha_hash[:50]}...")
    
    # 2. Simulando login
    senha_digitada = "minha_senha_super_secreta"
    login_ok = verify_password(senha_digitada, senha_hash)
    print(f"✅ Login correto: {login_ok}")
    
    # 3. Criando token após login bem-sucedido
    if login_ok:
        token = create_access_token({"sub": "123"})  # user_id = 123
        print(f"🎫 Token criado: {token[:50]}...")
        
        # 4. Verificando token
        dados_token = verify_token(token)
        print(f"👤 Dados do token: {dados_token}")
        
        # 5. Verificando expiração
        expirou = is_token_expired(token)
        print(f"⏰ Token expirado: {expirou}")