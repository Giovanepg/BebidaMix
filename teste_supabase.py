
from getpass import getpass
from database.supabase_db import conectar_supabase

supabase = conectar_supabase()

email = input("Email: ")
senha = getpass("Senha: ")

try:
    resposta = supabase.auth.sign_in_with_password({
        "email": email,
        "password": senha
    })

    if resposta.user:
        print("Login realizado com sucesso!")

        resultado = (
            supabase.table("administradores")
            .select("nome, ativo")
            .eq("id", resposta.user.id)
            .execute()
        )

        if resultado.data and resultado.data[0]["ativo"]:
            print("Administrador autorizado!")
            print("Nome:", resultado.data[0]["nome"])
        else:
            print("Usuário sem permissão administrativa.")

except Exception as erro:
    print("Erro ao autenticar:", type(erro).__name__)
