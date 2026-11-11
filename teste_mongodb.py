
from database.mongodb import client, produtos

try:
    client.admin.command("ping")

    print("Conectado ao MongoDB com sucesso!")

    quantidade = produtos.count_documents({})

    print("Produtos cadastrados:", quantidade)

except Exception as erro:
    print("Erro ao conectar ao MongoDB:")
    print(erro)

finally:
    client.close()
