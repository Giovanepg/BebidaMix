
from database.redis_db import redis_client

try:
    # Testar conexão
    resposta = redis_client.ping()

    if resposta:
        print("Conectado ao Redis com sucesso!")

    # Salvar um valor de teste
    redis_client.set(
        "bebidamix:teste",
        "Redis funcionando!",
        ex=60
    )

    # Consultar o valor
    resultado = redis_client.get("bebidamix:teste")

    print("Valor armazenado:", resultado)

except Exception as erro:
    print("Erro ao conectar ao Redis:")
    print(erro)
