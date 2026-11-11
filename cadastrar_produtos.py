
from database.mongodb import produtos

# Bebidas que serão cadastradas
bebidas = [
    {
        "nome": "Cerveja Heineken",
        "descricao": "Lata 350 ml",
        "preco": 5.99,
        "categoria": "Cervejas",
        "imagem": "",
        "estoque": 50,
        "ativo": True
    },
    {
        "nome": "Coca-Cola",
        "descricao": "Lata 350 ml",
        "preco": 4.99,
        "categoria": "Refrigerantes",
        "imagem": "",
        "estoque": 30,
        "ativo": True
    },
    {
        "nome": "Red Bull",
        "descricao": "Lata 250 ml",
        "preco": 9.90,
        "categoria": "Energéticos",
        "imagem": "",
        "estoque": 20,
        "ativo": True
    },
    {
        "nome": "Água Mineral",
        "descricao": "Garrafa 500 ml",
        "preco": 2.50,
        "categoria": "Águas",
        "imagem": "",
        "estoque": 40,
        "ativo": True
    },
    {
        "nome": "Combo Budweiser",
        "descricao": "6 latas de 350 ml",
        "preco": 32.90,
        "categoria": "Combos",
        "imagem": "",
        "estoque": 15,
        "ativo": True
    }
]

# Cadastrar somente produtos que ainda não existem
for bebida in bebidas:

    existente = produtos.find_one({
        "nome": bebida["nome"]
    })

    if existente is None:
        produtos.insert_one(bebida)
        print("Cadastrado:", bebida["nome"])
    else:
        print("Já existe:", bebida["nome"])

print("\nCadastro finalizado!")
