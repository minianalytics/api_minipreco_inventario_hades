from fastapi import FastAPI, HTTPException, Depends, Header, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, field_validator
from jose import JWTError, jwt
from datetime import datetime, timedelta
import json
import os
import threading

# Cria instância do FastAPI
app = FastAPI()

# Caminho para salvar os dados em um arquivo JSON
DATA_FILE = "dados_salvos.json"

# Lock para garantir operações thread-safe
lock = threading.Lock()

# Configurações de autenticação
SECRET_KEY = "sua_chave_secreta_muito_segura"  # Use uma chave secreta forte
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12  # Expiração do token para envio de dados

# Token exclusivo para leitura dos dados
TOKEN_EXCLUSIVO_GET = "token_exclusivo_da_sua_maquina"  # Token fixo para acessar o GET

# Lista de domínios permitidos para geração de tokens
DOMINIOS_PERMITIDOS = ["grupominipreco.com.br", "outrodominio.com"]

# Classe para autenticação
security = HTTPBearer()

# Classe para validar os dados enviados
class Dados(BaseModel):
    loja_key: int
    tag_operador: int
    tag_endereco: int
    codigo_produto: int
    quantidade: int

    @field_validator("quantidade")
    @classmethod
    def validar_quantidade(cls, valor):
        if valor <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        return valor


# Função para carregar os dados do arquivo JSON
def carregar_dados():
    if not os.path.exists(DATA_FILE):  # Cria o arquivo se ele não existir
        with open(DATA_FILE, "w") as file:
            json.dump([], file)
    with open(DATA_FILE, "r") as file:
        return json.load(file)


# Função para salvar os dados no arquivo JSON
def salvar_dados(dados):
    with lock:  # Garante que apenas uma thread acesse o arquivo por vez
        with open(DATA_FILE, "w") as file:
            json.dump(dados, file, indent=4)


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


# Rota para gerar o token de autenticação
@app.get("/gerar-token/")
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


# Rota para enviar dados para a API (protegido por token JWT)
@app.post("/enviar-dados/", dependencies=[Depends(verificar_token)])
async def receber_dados(dados: Dados, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dados enviados por um cliente autenticado.
    """
    try:
        # Carrega os dados existentes
        dados_existentes = carregar_dados()

        # Adiciona os novos dados com o horário atual
        dados_com_horario = dados.dict()
        dados_com_horario["horario"] = datetime.now().isoformat()  # Adiciona o horário atual
        dados_existentes.append(dados_com_horario)

        # Salva os dados atualizados
        salvar_dados(dados_existentes)

        return {"mensagem": "Dados recebidos e salvos com sucesso!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar os dados: {str(e)}")


# Rota para visualizar os dados salvos (protegido por token exclusivo)
@app.get("/ver-dados/")
async def ver_dados(authorization: str = Header(None)):
    """
    Retorna todos os dados salvos no servidor. Requer o token exclusivo.
    """
    if authorization != f"Bearer {TOKEN_EXCLUSIVO_GET}":
        raise HTTPException(status_code=401, detail="Token exclusivo inválido.")

    try:
        # Carrega os dados do arquivo
        dados_salvos = carregar_dados()
        return {"dados": dados_salvos}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar os dados: {str(e)}")