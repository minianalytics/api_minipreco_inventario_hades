from sqlalchemy import Column, Integer, String
from database import Base

class Dados(Base):
    __tablename__ = "dados"

    id = Column(Integer, primary_key=True, index=True)
    loja_key = Column(String, nullable=False)
    tag_operador = Column(String, nullable=False)
    tag_endereco = Column(String, nullable=False)
    codigo_produto = Column(String, nullable=False)
    quantidade = Column(Integer, nullable=False)