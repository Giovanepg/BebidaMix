
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()


def conectar_storage():
    url = os.getenv("SUPABASE_URL")
    chave = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not chave:
        raise ValueError("Supabase Storage não configurado.")

    return create_client(url, chave)
