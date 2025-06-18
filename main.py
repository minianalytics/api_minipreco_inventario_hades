# main.py
from fastapi import FastAPI, HTTPException, Depends, Header, Body
from pydantic import BaseModel, field_validator, EmailStr, Field, RootModel # Adicionado RootModel
from datetime import datetime, date
import json
import os
import threading
from typing import List, Optional

# Importa as funções de autenticação refatoradas e as configurações
from auth import gerar_novo_token, verificar_token_jwt 
from settings import settings 

# --- Metadados da API para documentação ---
api_description = """
API para recebimento e consulta de dados de contagem de inventário do MiniPreço. 🚀

**Funcionalidades Principais:**
* **Autenticação:** Clientes autorizados podem obter um token JWT para interagir com a API.
* **Envio de Dados:** Permite que a empresa parceira envie dados de contagem de inventário.
* **Consulta de Dados:** Permite a visualização dos dados de inventário que foram salvos.

Utilize o token JWT obtido no endpoint `/auth/token` no header `Authorization` como `Bearer <seu_token>`
para acessar os endpoints protegidos de inventário.
"""

openapi_tags_metadata = [
    {
        "name": "Autenticação",
        "description": "Operações relacionadas à autenticação e geração de tokens de acesso.",
    },
    {
        "name": "Inventário",
        "description": "Operações para enviar e visualizar dados de contagem de inventário.",
    },
]

# Cria instância do FastAPI com documentação aprimorada
app = FastAPI(
    title="API de Inventário MiniPreço",
    version="1.1.0",
    description=api_description,
    openapi_tags=openapi_tags_metadata
)

# Lock para garantir operações thread-safe ao acessar o arquivo JSON
file_lock = threading.Lock()

# --- Modelos Pydantic para Request e Response Bodies ---

class EmailPayload(BaseModel):
    """Corpo da requisição para solicitar um token de autenticação."""
    email: EmailStr = Field(..., example="usuario@grupominipreco.com.br", description="E-mail válido do usuário para gerar o token.")

class TokenResponse(BaseModel):
    """Resposta ao solicitar um token de autenticação."""
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", description="Token JWT de acesso.")
    token_type: str = Field(default="bearer", example="bearer", description="Tipo do token.")

class DadosInventarioPayload(BaseModel):
    """
    Modelo para os dados de contagem de inventário enviados pelo cliente.
    """
    loja_key: int = Field(..., description="Identificador numérico único da loja.", example=101)
    tag_operador: int = Field(..., description="Tag de identificação do operador que realizou a contagem.", example=9001)
    tag_endereco: int = Field(..., description="Tag de identificação do endereço/local da contagem no inventário.", example=404)
    codigo_produto: int = Field(..., description="Código EAN ou SKU (numérico) do produto contado.", example=7890000123456)
    quantidade: int = Field(..., description="Quantidade contada do produto. Deve ser um número inteiro maior que zero.", example=50)
    recontagem: int = Field(..., description="Indica se é uma recontagem. Use 0 para 'não' e 1 para 'sim'.", example=0)
    data_contagem: date = Field(..., description="Data em que a contagem do inventário foi efetivamente realizada (Formato:YYYY-MM-DD).", example="2025-10-20")

    @field_validator("quantidade")
    @classmethod
    def validar_quantidade_positiva(cls, valor: int) -> int:
        if valor <= 0:
            raise ValueError("A quantidade deve ser um número inteiro maior que zero.")
        return valor

    @field_validator("recontagem")
    @classmethod
    def validar_valor_recontagem(cls, valor: int) -> int:
        if valor not in [0, 1]:
            raise ValueError("O campo 'recontagem' deve ser 0 (não) ou 1 (sim).")
        return valor

    class Config:
        json_schema_extra = { 
            "example": {
                "loja_key": 101,
                "tag_operador": 9001,
                "tag_endereco": 404,
                "codigo_produto": 7890000123456,
                "quantidade": 50,
                "recontagem": 0,
                "data_contagem": "2025-10-20"
            }
        }

class DadosInventarioArmazenado(DadosInventarioPayload):
    """Modelo para os dados de inventário como são armazenados, incluindo timestamp da API."""
    horario_recebimento_api: datetime = Field(..., description="Timestamp ISO de quando o dado foi recebido e processado pela API.")

# AQUI: CORREÇÃO PARA PYDANTIC V2 - USANDO ROOTMODEL
class DadosInventarioListResponse(RootModel[List[DadosInventarioArmazenado]]):
    """Resposta para a listagem de dados de inventário (lista direta de registros)."""
    pass # Não é necessário definir __root__ ou qualquer campo aqui

class MensagemResponse(BaseModel):
    """Resposta padrão para operações bem-sucedidas que não retornam outros dados."""
    mensagem: str = Field(..., example="Operação realizada com sucesso.")

class HTTPErrorResponse(BaseModel):
    """Modelo para respostas de erro HTTP."""
    detail: str = Field(..., example="Mensagem de erro detalhada.")


# --- Funções Auxiliares para manipulação de dados ---

def carregar_dados_do_arquivo() -> List[dict]:
    """Carrega os dados do arquivo JSON. Cria o arquivo se não existir."""
    if not os.path.exists(settings.DATA_FILE):
        with open(settings.DATA_FILE, "w", encoding="utf-8") as file:
            json.dump([], file)
            return []
    with open(settings.DATA_FILE, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

def salvar_dados_no_arquivo(dados: List[dict]):
    """Salva a lista de dados no arquivo JSON de forma thread-safe."""
    with file_lock:
        with open(settings.DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(dados, file, indent=4, ensure_ascii=False, default=str)


# --- Endpoints da API ---

@app.post(
    "/auth/token",
    response_model=TokenResponse,
    summary="Obter Token de Acesso",
    description="""Autentica um usuário com base no e-mail e retorna um token JWT.
    O e-mail fornecido deve pertencer a um domínio autorizado nas configurações da API.
    O token JWT resultante deve ser incluído no header `Authorization` como `Bearer <token>`
    para acessar endpoints protegidos.""",
    tags=["Autenticação"],
    responses={
        400: {"model": HTTPErrorResponse, "description": "Requisição mal formatada ou e-mail inválido."},
        403: {"model": HTTPErrorResponse, "description": "Domínio de e-mail não autorizado para gerar token."},
        422: {"model": HTTPErrorResponse, "description": "Entidade não processável (e.g., e-mail não fornecido no corpo)."}
    }
)
async def login_para_gerar_token(payload: EmailPayload):
    """
    Recebe um e-mail, valida o domínio e gera um token JWT.
    """
    try:
        token_data = await gerar_novo_token(payload.email)
        return TokenResponse(**token_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar token: {str(e)}")


@app.post(
    "/inventario/dados",
    response_model=MensagemResponse,
    summary="Enviar Dados de Contagem de Inventário",
    description="""Recebe um novo registro de contagem de inventário.
    Requer autenticação via token JWT. Os dados enviados são validados e, se corretos,
    são armazenados com um timestamp indicando o momento do recebimento pela API.""",
    tags=["Inventário"],
    responses={
        200: {"model": MensagemResponse, "description": "Dados recebidos e salvos com sucesso."},
        401: {"model": HTTPErrorResponse, "description": "Não autorizado (token inválido, expirado ou não fornecido)."},
        422: {"model": HTTPErrorResponse, "description": "Erro de validação nos dados enviados."},
        500: {"model": HTTPErrorResponse, "description": "Erro interno no servidor ao processar os dados."}
    }
)
async def receber_dados_inventario(
    dados_entrada: DadosInventarioPayload,
    payload_token: dict = Depends(verificar_token_jwt)
):
    """
    Recebe dados de contagem do inventário, valida, adiciona timestamp da API e salva.
    """
    try:
        dados_atuais = carregar_dados_do_arquivo()

        novo_registro_dict = dados_entrada.model_dump()
        novo_registro_dict["horario_recebimento_api"] = datetime.now().isoformat()
        
        email_operador = payload_token.get("email")
        if email_operador:
            novo_registro_dict["registrado_por_email"] = email_operador

        dados_atuais.append(novo_registro_dict)
        salvar_dados_no_arquivo(dados_atuais)

        return MensagemResponse(mensagem="Dados de inventário recebidos e salvos com sucesso!")

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar e salvar os dados: {str(e)}")


@app.get(
    "/ver-dados/", # Endpoint para visualização
    response_model=DadosInventarioListResponse, # Usando o RootModel corrigido
    summary="Visualizar Dados de Inventário Salvos",
    description="""Retorna uma lista de todos os dados de contagem de inventário armazenados.
    Requer um token de autorização especial e fixo, configurado na API,
    enviado no header `Authorization` como `Bearer <TOKEN_EXCLUSIVO_GET>`.""",
    tags=["Inventário"],
    responses={
        200: {"description": "Lista de dados de inventário retornada com sucesso."},
        401: {"model": HTTPErrorResponse, "description": "Token de acesso exclusivo inválido ou não fornecido."},
        500: {"model": HTTPErrorResponse, "description": "Erro interno no servidor ao carregar os dados."}
    }
)
async def visualizar_dados_inventario(authorization: Optional[str] = Header(default=None, description="Token de autorização no formato 'Bearer SEU_TOKEN_EXCLUSIVO_GET'.")):
    """
    Retorna todos os dados salvos. Requer o token exclusivo `TOKEN_EXCLUSIVO_GET`.
    """
    if not authorization or authorization != f"Bearer {settings.TOKEN_EXCLUSIVO_GET}":
        raise HTTPException(
            status_code=401,
            detail="Token de acesso exclusivo inválido ou não fornecido."
        )
    try:
        dados_salvos = carregar_dados_do_arquivo()
        # O Pydantic RootModel cuidará da serialização da lista
        return dados_salvos 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar os dados: {str(e)}")

# --- Inicialização (opcional, para rodar com uvicorn main:app --reload) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
