from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexão com o PostgreSQL
DATABASE_URL = "postgresql://usuario:senha@localhost/nome_do_banco"

# Cria a engine do SQLAlchemy
engine = create_engine(DATABASE_URL)

# Cria uma sessão local para interagir com o banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()