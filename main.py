from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
import json
import os
import threading

# Cria uma instância do FastAPI
app = FastAPI()

# Caminho para salvar os dados em um arquivo JSON
DATA_FILE = "dados_salvos.json"

# Lock para garantir que operações com o arquivo sejam thread-safe
lock = threading.Lock()

# Classe para validar os dados enviados
class Dados(BaseModel):
    loja_key: str
    tag_operador: str
    tag_endereco: str
    codigo_produto: str
    quantidade: int

    # Validação adicional: a quantidade deve ser maior que zero
    @validator("quantidade")
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


# Rota para receber os dados via POST
@app.post("/receber-dados/")
async def receber_dados(dados: Dados):
    try:
        # Carrega os dados existentes
        dados_existentes = carregar_dados()

        # Adiciona os novos dados
        dados_existentes.append(dados.dict())

        # Salva os dados atualizados
        salvar_dados(dados_existentes)

        return {"mensagem": "Dados recebidos e salvos com sucesso!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar os dados: {str(e)}")


# Rota para visualizar todos os dados salvos via GET
@app.get("/ver-dados/")
async def ver_dados():
    try:
        # Carrega os dados do arquivo
        dados_salvos = carregar_dados()
        return {"dados": dados_salvos}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar os dados: {str(e)}")
    
    #Fim porograma