
from database.mongodb import produtos

pedidos = produtos.database["pedidos"]

try:
    resultado = pedidos.create_index(
        [("chave_idempotencia", 1)],
        unique=True,
        partialFilterExpression={
            "chave_idempotencia": {"$type": "string"}
        },
        name="chave_idempotencia_unica"
    )

    print("Índice criado:", resultado)

except Exception as erro:
    print("Erro ao criar índice:", erro)
