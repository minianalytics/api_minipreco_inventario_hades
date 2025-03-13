from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from typing import List
import os

# Cria uma instância do FastAPI
app = FastAPI()

# Define o modelo de dados usando Pydantic
class Dados(BaseModel):
    loja_key: str
    tag_operador: str
    tag_endereco: str
    codigo_produto: str
    quantidade: int

# Caminho para salvar os dados em um arquivo JSON
DATA_FILE = "dados_salvos.json"

# Verifica se o arquivo já existe; se não, cria um arquivo vazio
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as file:
        json.dump([], file)

# Rota para receber os dados via POST
@app.post("/receber-dados/")
async def receber_dados(dados: Dados):
    try:
        # Carrega os dados existentes do arquivo
        with open(DATA_FILE, "r") as file:
            dados_existentes = json.load(file)

        # Adiciona os novos dados à lista
        dados_existentes.append({
            "loja_key": dados.loja_key,
            "tag_operador": dados.tag_operador,
            "tag_endereco": dados.tag_endereco,
            "codigo_produto": dados.codigo_produto,
            "quantidade": dados.quantidade,
        })

        # Salva os dados atualizados no arquivo
        with open(DATA_FILE, "w") as file:
            json.dump(dados_existentes, file, indent=4)

        return {"mensagem": "Dados recebidos e salvos com sucesso!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar os dados: {str(e)}")

# Rota para visualizar todos os dados salvos via GET
@app.get("/ver-dados/")
async def ver_dados():
    try:
        # Carrega os dados do arquivo
        with open(DATA_FILE, "r") as file:
            dados_salvos = json.load(file)

        return {"dados": dados_salvos}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar os dados: {str(e)}")