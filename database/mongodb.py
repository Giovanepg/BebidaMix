
import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Buscar configurações no .env
uri = os.getenv("MONGO_URI")
nome_banco = os.getenv("MONGO_DB_NAME", "BebidaMix")

# Verificar se a URI foi configurada
if not uri:
    raise ValueError("MONGO_URI não configurada no .env")

# Criar cliente do MongoDB
client = MongoClient(
    uri,
    serverSelectionTimeoutMS=5000
)

# Selecionar banco e coleção
banco = client[nome_banco]
produtos = banco["produtos"]
