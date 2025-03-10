#Construção de uma API para receber dados de invenatario
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Instância do FastAPI
app = FastAPI()

# Modelo para validar os dados recebidos no corpo da requisição
class InventarioItem(BaseModel):
    loja_key: str
    codigo: str
    quantidade: int

# Rota POST para receber os dados do inventário
@app.post("/inventario")
async def receber_inventario(item: InventarioItem):
    # Validação simples (opcional)
    if item.quantidade < 0:
        raise HTTPException(status_code=400, detail="A quantidade não pode ser negativa")

    # Processar os dados (aqui você pode salvar em um banco de dados)
    print(f"Dados recebidos: Loja: {item.loja_key}, Código: {item.codigo}, Quantidade: {item.quantidade}")

    # Retornar uma resposta de sucesso
    return {"message": "Dados recebidos com sucesso!", "data": item}