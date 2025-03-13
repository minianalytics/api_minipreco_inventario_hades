from pydantic import BaseModel

class DadosCreate(BaseModel):
    loja_key: str
    tag_operador: str
    tag_endereco: str
    codigo_produto: str
    quantidade: int