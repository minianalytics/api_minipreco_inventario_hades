from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from .database import SessionLocal, engine

# Cria as tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Função para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rota para receber dados via POST
@app.post("/dados/", response_model=schemas.DadosCreate)
def criar_dados(dados: schemas.DadosCreate, db: Session = Depends(get_db)):
    db_dados = models.Dados(
        loja_key=dados.loja_key,
        tag_operador=dados.tag_operador,
        tag_endereco=dados.tag_endereco,
        codigo_produto=dados.codigo_produto,
        quantidade=dados.quantidade,
    )
    db.add(db_dados)
    db.commit()
    db.refresh(db_dados)
    return db_dados