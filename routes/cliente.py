
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app
)

from flask_wtf.csrf import generate_csrf, validate_csrf
from wtforms.validators import ValidationError

from database.supabase_db import conectar_supabase


cliente_bp = Blueprint("cliente", __name__)


# =====================================
# VERIFICAR SE O USUÁRIO ESTÁ LOGADO
# =====================================

def usuario_autenticado():

    access = session.get("access_token")
    refresh = session.get("refresh_token")

    if not access or not refresh:
        return False

    try:
        supabase = conectar_supabase()

        resposta = supabase.auth.set_session(
            access,
            refresh
        )

        if not resposta.session:
            return False

        usuario = supabase.auth.get_user().user

        if not usuario:
            return False

        # Atualizar os tokens da sessão
        session["access_token"] = (
            resposta.session.access_token
        )

        session["refresh_token"] = (
            resposta.session.refresh_token
        )

        session["usuario_nome"] = (
            (usuario.user_metadata or {}).get("nome")
            or usuario.email
            or "Cliente"
        )

        return True

    except Exception:
        current_app.logger.warning(
            "Não foi possível validar a sessão do usuário."
        )

        session.pop("access_token", None)
        session.pop("refresh_token", None)
        session.pop("usuario_nome", None)

        return False


# =====================================
# TELA INICIAL DE ACESSO
# =====================================

@cliente_bp.route("/acesso")
def acesso():

    if usuario_autenticado():
        return redirect(url_for("inicio"))

    return render_template(
        "acesso.html",
        modo="cadastro",
        csrf_token=generate_csrf()
    )


# =====================================
# CADASTRAR NOVO CLIENTE
# =====================================

@cliente_bp.route(
    "/cadastro",
    methods=["GET", "POST"]
)
def cadastro():

    if request.method == "GET":

        if usuario_autenticado():
            return redirect(url_for("inicio"))

        return render_template(
            "acesso.html",
            modo="cadastro",
            csrf_token=generate_csrf()
        )

    try:
        validate_csrf(request.form.get("csrf_token"))

    except ValidationError:
        flash("Formulário expirado. Atualize a página.")
        return redirect(url_for("cliente.cadastro"))

    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip().lower()
    senha = request.form.get("senha", "")
    confirmar_senha = request.form.get("confirmar_senha", "")

    if not nome or len(nome) > 80:
        flash("Informe um nome com até 80 caracteres.")

    elif not email or len(email) > 254 or "@" not in email:
        flash("Informe um e-mail válido.")

    elif len(senha) < 8 or len(senha) > 128:
        flash("A senha deve ter entre 8 e 128 caracteres.")

    elif senha != confirmar_senha:
        flash("As senhas não coincidem.")

    else:
        try:
            supabase = conectar_supabase()

            resposta = supabase.auth.sign_up({
                "email": email,
                "password": senha,
                "options": {
                    "data": {
                        "nome": nome
                    }
                }
            })

            # Se a confirmação de e-mail estiver desativada,
            # o Supabase pode retornar uma sessão imediatamente.
            if resposta.session:

                session.clear()
                session.permanent = True

                session["access_token"] = (
                    resposta.session.access_token
                )

                session["refresh_token"] = (
                    resposta.session.refresh_token
                )

                session["usuario_nome"] = nome

                flash("Cadastro realizado com sucesso!")

                return redirect(url_for("inicio"))

            # Com confirmação de e-mail ativada,
            # o usuário precisa confirmar e depois entrar.
            flash(
                "Cadastro solicitado! Confira seu e-mail "
                "para confirmar a conta e depois faça login."
            )

            return redirect(url_for("cliente.entrar"))

        except Exception:

            current_app.logger.exception(
                "Não foi possível concluir o cadastro."
            )

            flash(
                "Não foi possível realizar o cadastro. "
                "Confira seus dados ou tente novamente."
            )

    return render_template(
        "acesso.html",
        modo="cadastro",
        csrf_token=generate_csrf()
    )


# =====================================
# LOGIN DE CLIENTES
# =====================================

@cliente_bp.route(
    "/entrar",
    methods=["GET", "POST"]
)
def entrar():

    if request.method == "GET":

        if usuario_autenticado():
            return redirect(url_for("inicio"))

        return render_template(
            "acesso.html",
            modo="login",
            csrf_token=generate_csrf()
        )

    try:
        validate_csrf(request.form.get("csrf_token"))

    except ValidationError:
        flash("Formulário expirado. Atualize a página.")
        return redirect(url_for("cliente.entrar"))

    email = request.form.get("email", "").strip().lower()
    senha = request.form.get("senha", "")

    if not email or not senha:
        flash("Preencha o e-mail e a senha.")

    else:
        try:
            supabase = conectar_supabase()

            resposta = supabase.auth.sign_in_with_password({
                "email": email,
                "password": senha
            })

            if not resposta.user or not resposta.session:
                raise ValueError("Login não autorizado")

            session.clear()
            session.permanent = True

            session["access_token"] = (
                resposta.session.access_token
            )

            session["refresh_token"] = (
                resposta.session.refresh_token
            )

            session["usuario_nome"] = (
                (resposta.user.user_metadata or {}).get("nome")
                or resposta.user.email
                or "Cliente"
            )

            return redirect(url_for("inicio"))

        except Exception:

            current_app.logger.warning(
                "Tentativa de login de cliente não concluída."
            )

            flash(
                "Não foi possível entrar. Verifique o e-mail, "
                "a senha e se sua conta foi confirmada."
            )

    return render_template(
        "acesso.html",
        modo="login",
        csrf_token=generate_csrf()
    )


# =====================================
# SAIR DA CONTA
# =====================================

@cliente_bp.route(
    "/sair",
    methods=["POST"]
)
def sair():

    try:
        validate_csrf(request.form.get("csrf_token"))

    except ValidationError:
        return "Solicitação inválida.", 400

    session.clear()

    return redirect(url_for("cliente.acesso"))
