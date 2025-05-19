# auth.py
from fastapi import HTTPException, Depends, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import EmailStr
from datetime import datetime, timedelta

# Configurações de autenticação
SECRET_KEY = "sua_chave_secreta_muito_segura"  # Use uma chave secreta forte
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12  # Expiração do token para envio de dados

# Lista de domínios permitidos para geração de tokens
DOMINIOS_PERMITIDOS = ["grupominopreco.com.br"]

# Classe para autenticação
security = HTTPBearer()


# Função para criar um token JWT
def criar_token(dados: dict):
    to_encode = dados.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Função para verificar o token JWT
def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")


# Função para validar o domínio do e-mail
def validar_dominio(email: str):
    dominio = email.split("@")[-1]
    if dominio not in DOMINIOS_PERMITIDOS:
        raise HTTPException(status_code=403, detail="Domínio não autorizado para gerar tokens.")
    return True


# Endpoint para geração de token de autenticação
async def gerar_token(email: EmailStr = Body(...)):
    """
    Gera um token JWT válido por 12 horas para autenticar o envio de dados.
    O e-mail deve pertencer a um domínio autorizado.
    """
    # Verifica se o domínio do e-mail é permitido
    validar_dominio(email)

    # Gera o token com base no e-mail
    token = criar_token({"email": email})
    return {"token": token}