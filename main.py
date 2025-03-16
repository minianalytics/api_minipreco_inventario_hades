from fastapi import FastAPI, HTTPException, Depends, Header, Body
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
from datetime import datetime
from auth import gerar_token, verificar_token  # Importa do auth.py
import json
import os
import threading

# Cria instância do FastAPI
app = FastAPI()

# Caminho para salvar os dados em um arquivo JSON
DATA_FILE = "dados_salvos.json"

# Lock para garantir operações thread-safe
lock = threading.Lock()

# Token exclusivo para leitura dos dados
TOKEN_EXCLUSIVO_GET = "token_exclusivo_da_sua_maquina"  # Token fixo para acessar o GET


# Classe para validar os dados enviados
class Dados(BaseModel):
    loja_key: int
    tag_operador: int
    tag_endereco: int
    codigo_produto: int
    quantidade: int
    recontagem: int  # Nova coluna adicionada

    @field_validator("quantidade")
    @classmethod
    def validar_quantidade(cls, valor):
        if valor <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        return valor

    @field_validator("recontagem")
    @classmethod
    def validar_recontagem(cls, valor):
        if valor not in [0, 1]:
            raise ValueError("O campo 'recontagem' deve ser 0 (não) ou 1 (sim).")
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


# Rota para gerar o token de autenticação
@app.post("/auth/gerar-token/")
async def gerar_token_endpoint(email: str = Body(...)):
    """
    Recebe um email no corpo da requisição e retorna um token JWT válido.
    """
    return await gerar_token(email)


# Rota para enviar dados para a API (protegido por token JWT)
@app.post("/enviar_dados/enviar-dados/", dependencies=[Depends(verificar_token)])
async def receber_dados(
    dados: Dados, credentials: HTTPAuthorizationCredentials = Depends(verificar_token)
):
    """
    Recebe dados enviados por um cliente autenticado e os salva no servidor.
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
@app.get("/recebendo_dados/ver-dados/")
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