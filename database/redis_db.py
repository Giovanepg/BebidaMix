
import os
import redis
from dotenv import load_dotenv

load_dotenv()

# Verificar se existe Redis configurado na nuvem
redis_url = os.getenv("REDIS_URL")

if redis_url:
    # Render: conectar pelo endereço completo
    redis_client = redis.Redis.from_url(
        redis_url,
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3
    )
else:
    # Desenvolvimento local: Redis no computador
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0)),
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3
    )
