# auth.py
from fastapi import HTTPException, Depends, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt # type: ignore
from pydantic import EmailStr
from datetime import datetime, timedelta

# Importa as configurações
from settings import settings

# Classe para autenticação
security = HTTPBearer()

# Função para criar um token JWT
def criar_token_jwt(dados: dict):
    to_encode = dados.copy()
    expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Função para verificar o token JWT
def verificar_token_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Decodifica e valida o token JWT.
    Retorna o payload do token se válido, caso contrário, levanta HTTPException.
    """
    try:
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str | None = payload.get("email")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido: e-mail ausente no payload")
        return payload # Retorna o payload para uso potencial no endpoint
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido ou expirado: {str(e)}")

# Função para validar o domínio do e-mail
def _validar_dominio_email(email: str):
    """
    Valida se o domínio do e-mail está na lista de domínios permitidos.
    Levanta HTTPException se não estiver.
    """
    dominio = email.split("@")[-1]
    if dominio not in settings.DOMINIOS_PERMITIDOS:
        raise HTTPException(
            status_code=403, detail="Domínio não autorizado para gerar tokens."
        )
    return True

# Função de utilidade para ser chamada pelo endpoint de geração de token
async def gerar_novo_token(email: EmailStr):
    """
    Lógica para gerar um novo token JWT.
    Valida o domínio do e-mail e cria o token.
    """
    _validar_dominio_email(email) # Valida o domínio
    token = criar_token_jwt({"email": email}) # Cria o token com o e-mail como parte do payload
    return {"access_token": token, "token_type": "bearer"}