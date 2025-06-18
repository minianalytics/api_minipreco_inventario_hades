# settings.py
import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Auth settings
    SECRET_KEY: str = "sua_chave_secreta_muito_segura_idealmente_de_env_var"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 12
    DOMINIOS_PERMITIDOS: List[str] = ["grupominopreco.com.br", "inventorybrasil.com.br"]

    # API settings
    DATA_FILE: str = "dados_salvos.json"
    TOKEN_EXCLUSIVO_GET: str = "FDAGHFH$@&@#$&$#%YFHGBSZDGHBSDFHADFHSGHSDFJFJSDFJXCVBQDFG$@&¨¨&#*(&GET12345!" # Use um valor forte e único

    class Config:
        env_file = ".env" # Opcional: para carregar de um arquivo .env
        env_file_encoding = 'utf-8'

settings = Settings()
