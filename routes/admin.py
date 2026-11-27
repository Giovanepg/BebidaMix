
import os
import warnings

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from functools import wraps
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from bson import ObjectId
from bson.errors import InvalidId

from flask import (
    Blueprint, abort, current_app, flash, g,
    redirect, render_template, request, session, url_for
)

from flask_wtf.csrf import generate_csrf, validate_csrf
from PIL import Image, UnidentifiedImageError
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from wtforms.validators import ValidationError

from database.mongodb import produtos
from database.supabase_db import conectar_supabase
from database.supabase_storage import conectar_storage


# ==========================================
# CONFIGURAÇÕES
# ==========================================

admin_bp = Blueprint("admin", __name__)

CATEGORIAS = [
    "Cervejas",
    "Refrigerantes",
    "Energéticos",
    "Águas",
    "Combos",
    "Drinks",
    "Petiscos"
]

LIMITE_IMAGEM = 5 * 1024 * 1024

EXTENSOES = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp"
}

pedidos = produtos.database["pedidos"]


class ErroPedido(Exception):
    pass


# ==========================================
# SALVAR IMAGEM NO SUPABASE STORAGE
# ==========================================

def salvar_imagem(arquivo):

    if arquivo is None or not arquivo.filename:
        return None

    conteudo = arquivo.read(LIMITE_IMAGEM + 1)

    if not conteudo or len(conteudo) > LIMITE_IMAGEM:
        raise ValueError("A imagem deve ter até 5 MB.")

    # Validar conteúdo real da imagem
    try:
        with warnings.catch_warnings():
            warnings.simplefilter(
                "error",
                Image.DecompressionBombWarning
            )

            with Image.open(BytesIO(conteudo)) as imagem:
                formato = imagem.format
                imagem.verify()

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombWarning,
        Image.DecompressionBombError
    ):
        raise ValueError(
            "Arquivo de imagem inválido ou muito grande."
        ) from None

    if formato not in EXTENSOES:
        raise ValueError(
            "Escolha uma imagem JPG, PNG ou WebP."
        )

    tipos_mime = {
        "JPEG": "image/jpeg",
        "PNG": "image/png",
        "WEBP": "image/webp"
    }

    # Gerar nome único
    nome = uuid4().hex + EXTENSOES[formato]
    caminho_storage = f"uploads/{nome}"

    try:
        storage = conectar_storage().storage.from_("produtos")

        # Enviar imagem ao Supabase Storage
        storage.upload(
            path=caminho_storage,
            file=conteudo,
            file_options={
                "content-type": tipos_mime[formato],
                "upsert": "false"
            }
        )

        # Retornar URL pública para o MongoDB
        return storage.get_public_url(caminho_storage)

    except Exception:
        current_app.logger.exception(
            "Falha no upload da imagem ao Supabase"
        )

        raise OSError(
            "Não foi possível salvar a imagem no Storage."
        ) from None


# ==========================================
# DESCARTAR IMAGEM NOVA EM CASO DE ERRO
# ==========================================

def descartar_nova_imagem(caminho):

    if not caminho:
        return

    projeto = os.getenv("SUPABASE_URL", "").rstrip("/")

    if not projeto:
        return

    prefixo = (
        f"{projeto}/storage/v1/object/public/"
        "produtos/uploads/"
    )

    if not caminho.startswith(prefixo):
        return

    nome = caminho[len(prefixo):]
    arquivo = Path(nome)

    if (
        not nome
        or "/" in nome
        or "?" in nome
        or "#" in nome
        or arquivo.suffix.lower() not in EXTENSOES.values()
        or len(arquivo.stem) != 32
    ):
        return

    try:
        int(arquivo.stem, 16)
    except ValueError:
        return

    try:
        conectar_storage().storage.from_("produtos").remove(
            [f"uploads/{nome}"]
        )

    except Exception:
        current_app.logger.warning(
            "Não foi possível descartar a imagem do Storage",
            exc_info=True
        )


# ==========================================
# VALIDAR PREÇO E ESTOQUE
# ==========================================

def validar_preco_estoque(preco_texto, estoque_texto):

    try:
        preco = Decimal(preco_texto.replace(",", "."))
        estoque = int(estoque_texto)

    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(
            "Informe preço e estoque válidos."
        ) from None

    if (
        not preco.is_finite()
        or preco <= 0
        or preco > 100000
        or preco.as_tuple().exponent < -2
    ):
        raise ValueError(
            "O preço deve ser positivo e ter até duas casas decimais."
        )

    if not 0 <= estoque <= 1000000:
        raise ValueError(
            "O estoque deve estar entre 0 e 1.000.000."
        )

    return float(preco), estoque


# ==========================================
# VALIDAR CAMPOS DO PRODUTO
# ==========================================

def validar_campos(nome, descricao, categoria):

    if not nome or len(nome) > 120:
        raise ValueError(
            "Informe um nome com até 120 caracteres."
        )

    if len(descricao) > 500:
        raise ValueError(
            "A descrição deve ter até 500 caracteres."
        )

    if categoria not in CATEGORIAS:
        raise ValueError(
            "Selecione uma categoria válida."
        )


# ==========================================
# VERIFICAR ADMINISTRADOR
# ==========================================

def administrador_obrigatorio(funcao):

    @wraps(funcao)
    def verificar(*args, **kwargs):

        access = session.get("access_token")
        refresh = session.get("refresh_token")

        if not access or not refresh:
            return redirect(url_for("admin.login"))

        try:
            supabase = conectar_supabase()

            resposta = supabase.auth.set_session(
                access,
                refresh
            )

            usuario = supabase.auth.get_user().user

            if not usuario or not resposta.session:
                raise ValueError("Sessão inválida")

            # Verificar autorização no PostgreSQL
            resultado = (
                supabase.table("administradores")
                .select("nome, ativo")
                .eq("id", usuario.id)
                .execute()
            )

            if (
                not resultado.data
                or not resultado.data[0]["ativo"]
            ):
                session.clear()
                return redirect(url_for("admin.login"))

            administrador = resultado.data[0]

            session["access_token"] = (
                resposta.session.access_token
            )

            session["refresh_token"] = (
                resposta.session.refresh_token
            )

            g.nome_admin = administrador["nome"]

        except Exception:
            session.clear()
            flash("Sessão expirada ou indisponível.")
            return redirect(url_for("admin.login"))

        return funcao(*args, **kwargs)

    return verificar


# ==========================================
# LOGIN ADMINISTRATIVO
# ==========================================

@admin_bp.route("/admin/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        try:
            validate_csrf(
                request.form.get("csrf_token")
            )

        except ValidationError:
            flash("Formulário expirado. Tente novamente.")
            return redirect(url_for("admin.login"))

        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")

        if not email or not senha:
            flash("Preencha o email e a senha.")
            return redirect(url_for("admin.login"))

        try:
            supabase = conectar_supabase()

            resposta = supabase.auth.sign_in_with_password({
                "email": email,
                "password": senha
            })

            usuario = resposta.user

            if not usuario or not resposta.session:
                flash("Não foi possível realizar o login.")
                return redirect(url_for("admin.login"))

            resultado = (
                supabase.table("administradores")
                .select("nome, ativo")
                .eq("id", usuario.id)
                .execute()
            )

            if (
                not resultado.data
                or not resultado.data[0]["ativo"]
            ):
                flash("Acesso não autorizado.")
                return redirect(url_for("admin.login"))

            session.clear()
            session.permanent = True

            session["access_token"] = (
                resposta.session.access_token
            )

            session["refresh_token"] = (
                resposta.session.refresh_token
            )

            return redirect(url_for("admin.painel"))

        except Exception:
            current_app.logger.exception(
                "Falha no login administrativo"
            )

            flash(
                "Não foi possível entrar. "
                "Confira os dados e a conexão."
            )

    return render_template(
        "login.html",
        csrf_token=generate_csrf()
    )


# ==========================================
# PAINEL ADMINISTRATIVO
# ==========================================

@admin_bp.route("/admin")
@administrador_obrigatorio
def painel():

    return render_template(
        "admin.html",
        nome=g.nome_admin,
        csrf_token=generate_csrf()
    )


# ==========================================
# LOGOUT
# ==========================================

@admin_bp.route("/admin/logout", methods=["POST"])
def logout():

    try:
        validate_csrf(request.form.get("csrf_token"))

    except ValidationError:
        return "Solicitação inválida.", 400

    session.clear()

    return redirect(url_for("admin.login"))


# ==========================================
# CADASTRAR PRODUTO
# ==========================================

@admin_bp.route(
    "/admin/produtos/novo",
    methods=["GET", "POST"]
)
@administrador_obrigatorio
def cadastrar_produto():

    if request.method == "POST":

        try:
            validate_csrf(request.form.get("csrf_token"))

        except ValidationError:
            flash("Formulário inválido. Tente novamente.")
            return redirect(url_for("admin.cadastrar_produto"))

        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        categoria = request.form.get("categoria", "")
        preco_texto = request.form.get("preco", "").strip()
        estoque_texto = request.form.get("estoque", "").strip()
        ativo = request.form.get("ativo") == "on"

        arquivo_imagem = request.files.get("imagem")
        nova_imagem = None

        try:
            validar_campos(nome, descricao, categoria)

            preco, estoque = validar_preco_estoque(
                preco_texto,
                estoque_texto
            )

            nova_imagem = salvar_imagem(arquivo_imagem)

            novo_produto = {
                "nome": nome,
                "descricao": descricao,
                "categoria": categoria,
                "preco": preco,
                "estoque": estoque,
                "imagem": nova_imagem or "",
                "ativo": ativo
            }

            produtos.insert_one(novo_produto)

            flash("Produto cadastrado com sucesso!")

            return redirect(url_for("admin.painel"))

        except ValueError as erro:
            flash(str(erro))

        except (OSError, PyMongoError):
            current_app.logger.exception(
                "Falha ao cadastrar produto"
            )
            flash("Não foi possível salvar o produto.")

        descartar_nova_imagem(nova_imagem)

    return render_template(
        "cadastrar_produto.html",
        categorias=CATEGORIAS,
        csrf_token=generate_csrf()
    )


# ==========================================
# LISTAR PRODUTOS
# ==========================================

@admin_bp.route("/admin/produtos")
@administrador_obrigatorio
def listar_produtos():

    try:
        lista = list(produtos.find().sort("nome", 1))

        for produto in lista:
            produto["id"] = str(produto["_id"])

        return render_template(
            "gerenciar_produtos.html",
            produtos=lista,
            csrf_token=generate_csrf()
        )

    except PyMongoError:
        current_app.logger.exception(
            "Erro ao listar produtos"
        )

        flash("Não foi possível carregar os produtos.")

        return redirect(url_for("admin.painel"))


# ==========================================
# EDITAR PRODUTO
# ==========================================

@admin_bp.route(
    "/admin/produtos/editar/<id_produto>",
    methods=["GET", "POST"]
)
@administrador_obrigatorio
def editar_produto(id_produto):

    try:
        object_id = ObjectId(id_produto)

    except (InvalidId, TypeError):
        abort(404)

    try:
        produto = produtos.find_one({
            "_id": object_id
        })

    except PyMongoError:
        current_app.logger.exception(
            "Erro ao consultar produto"
        )
        abort(503)

    if produto is None:
        abort(404)

    if request.method == "POST":

        try:
            validate_csrf(request.form.get("csrf_token"))

        except ValidationError:
            flash("Formulário inválido ou expirado.")

            return redirect(
                url_for(
                    "admin.editar_produto",
                    id_produto=id_produto
                )
            )

        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        categoria = request.form.get("categoria", "")
        preco_texto = request.form.get("preco", "").strip()
        estoque_texto = request.form.get("estoque", "").strip()
        ativo = request.form.get("ativo") == "on"

        arquivo_imagem = request.files.get("imagem")
        nova_imagem = None

        try:
            validar_campos(nome, descricao, categoria)

            preco, estoque = validar_preco_estoque(
                preco_texto,
                estoque_texto
            )

            # Manter imagem existente
            imagem = produto.get("imagem", "")

            # Enviar nova imagem, caso selecionada
            nova_imagem = salvar_imagem(arquivo_imagem)

            if nova_imagem is not None:
                imagem = nova_imagem

            novos_dados = {
                "nome": nome,
                "descricao": descricao,
                "categoria": categoria,
                "preco": preco,
                "estoque": estoque,
                "imagem": imagem,
                "ativo": ativo
            }

            resultado = produtos.update_one(
                {"_id": object_id},
                {"$set": novos_dados}
            )

            if resultado.matched_count == 0:
                raise ValueError("Produto não encontrado.")

            flash("Produto atualizado com sucesso!")

            return redirect(url_for("admin.listar_produtos"))

        except ValueError as erro:
            flash(str(erro))

        except (OSError, PyMongoError):
            current_app.logger.exception(
                "Erro ao atualizar produto"
            )
            flash("Não foi possível atualizar o produto.")

        descartar_nova_imagem(nova_imagem)

    produto["id"] = str(produto["_id"])

    preco_atual = Decimal(str(produto["preco"]))

    return render_template(
        "editar_produto.html",
        produto=produto,
        preco_atual=f"{preco_atual:.2f}",
        categorias=CATEGORIAS,
        csrf_token=generate_csrf()
    )


# ==========================================
# EXCLUIR PRODUTO
# ==========================================

@admin_bp.route(
    "/admin/produtos/excluir/<id_produto>",
    methods=["POST"]
)
@administrador_obrigatorio
def excluir_produto(id_produto):

    try:
        validate_csrf(request.form.get("csrf_token"))

    except ValidationError:
        flash("Solicitação inválida ou expirada.")
        return redirect(url_for("admin.listar_produtos"))

    try:
        object_id = ObjectId(id_produto)

    except (InvalidId, TypeError):
        abort(404)

    try:
        resultado = produtos.delete_one({
            "_id": object_id
        })

        if resultado.deleted_count == 0:
            flash("Produto não encontrado.")
        else:
            flash("Produto excluído com sucesso!")

    except PyMongoError:
        current_app.logger.exception(
            "Erro ao excluir produto"
        )
        flash("Não foi possível excluir o produto.")

    return redirect(url_for("admin.listar_produtos"))


# ==========================================
# CONTROLE DE ESTOQUE
# ==========================================

@admin_bp.route("/admin/estoque")
@administrador_obrigatorio
def controle_estoque():

    try:
        lista = list(produtos.find().sort("nome", 1))

        total_produtos = len(lista)
        total_unidades = 0
        estoque_baixo = 0
        esgotados = 0
        inativos = 0

        for produto in lista:

            produto["id"] = str(produto["_id"])

            quantidade = produto.get("estoque", 0)
            ativo = produto.get("ativo", False)

            if ativo:
                total_unidades += quantidade

            if not ativo:
                produto["situacao_estoque"] = "Inativo"
                inativos += 1

            elif quantidade <= 0:
                produto["situacao_estoque"] = "Esgotado"
                esgotados += 1

            elif quantidade <= 5:
                produto["situacao_estoque"] = "Estoque baixo"
                estoque_baixo += 1

            else:
                produto["situacao_estoque"] = "Normal"

        return render_template(
            "estoque.html",
            produtos=lista,
            total_produtos=total_produtos,
            total_unidades=total_unidades,
            estoque_baixo=estoque_baixo,
            esgotados=esgotados,
            inativos=inativos
        )

    except PyMongoError:
        current_app.logger.exception(
            "Erro ao consultar estoque"
        )

        flash("Não foi possível carregar o estoque.")

        return redirect(url_for("admin.painel"))


# ==========================================
# GERENCIAR PEDIDOS
# ==========================================

@admin_bp.route("/admin/pedidos")
@administrador_obrigatorio
def listar_pedidos():

    try:
        lista = list(
            pedidos.find()
            .sort("criado_em", -1)
            .limit(100)
        )

        for pedido in lista:

            pedido["id"] = str(pedido["_id"])

            data = pedido.get("criado_em")

            if data:
                pedido["data_formatada"] = (
                    data.strftime("%d/%m/%Y %H:%M") + " UTC"
                )
            else:
                pedido["data_formatada"] = "-"

        return render_template(
            "pedidos.html",
            pedidos=lista,
            csrf_token=generate_csrf()
        )

    except PyMongoError:
        current_app.logger.exception(
            "Erro ao consultar pedidos"
        )

        flash("Não foi possível carregar os pedidos.")

        return redirect(url_for("admin.painel"))


# ==========================================
# CONFIRMAR PEDIDO
# ==========================================

@admin_bp.route(
    "/admin/pedidos/confirmar/<id_pedido>",
    methods=["POST"]
)
@administrador_obrigatorio
def confirmar_pedido(id_pedido):

    try:
        validate_csrf(request.form.get("csrf_token"))

    except ValidationError:
        flash("Formulário inválido ou expirado.")
        return redirect(url_for("admin.listar_pedidos"))

    try:
        object_id = ObjectId(id_pedido)

    except (InvalidId, TypeError):
        abort(404)

    client = produtos.database.client

    # Executar operações dentro de uma transação
    def executar_confirmacao(sessao):

        resultado = pedidos.update_one(
            {
                "_id": object_id,
                "status": "AGUARDANDO_CONFIRMACAO"
            },
            {
                "$set": {
                    "status": "CONFIRMADO",
                    "confirmado_em": datetime.now(timezone.utc)
                }
            },
            session=sessao
        )

        if resultado.modified_count != 1:
            raise ErroPedido(
                "Pedido não encontrado ou já finalizado."
            )

        pedido = pedidos.find_one(
            {
                "_id": object_id,
                "status": "CONFIRMADO"
            },
            session=sessao
        )

        if not pedido or not pedido.get("itens"):
            raise ErroPedido("Pedido sem itens válidos.")

        ids_produtos = set()

        # Validar os itens do pedido
        for item in pedido["itens"]:

            if not isinstance(item, dict):
                raise ErroPedido("Item inválido no pedido.")

            produto_id = item.get("produto_id")
            quantidade = item.get("quantidade")

            if (
                not isinstance(produto_id, ObjectId)
                or type(quantidade) is not int
                or quantidade <= 0
            ):
                raise ErroPedido("Dados inválidos no pedido.")

            if produto_id in ids_produtos:
                raise ErroPedido("Produto duplicado no pedido.")

            ids_produtos.add(produto_id)

        # Descontar estoque
        for item in pedido["itens"]:

            produto_id = item["produto_id"]
            quantidade = item["quantidade"]

            resultado_estoque = produtos.update_one(
                {
                    "_id": produto_id,
                    "ativo": True,
                    "estoque": {"$gte": quantidade}
                },
                {
                    "$inc": {"estoque": -quantidade}
                },
                session=sessao
            )

            if resultado_estoque.modified_count != 1:
                raise ErroPedido(
                    "Produto indisponível ou estoque insuficiente: "
                    + str(item.get("nome", "Produto"))
                )

        return True

    try:
        with client.start_session() as sessao:

            sessao.with_transaction(
                executar_confirmacao,
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority")
            )

        flash("Pedido confirmado e estoque atualizado!")

    except ErroPedido as erro:
        flash(str(erro))

    except PyMongoError:
        current_app.logger.exception(
            "Erro ao confirmar pedido"
        )

        flash(
            "Não foi possível confirmar o pedido. "
            "Confira a situação antes de tentar novamente."
        )

    return redirect(url_for("admin.listar_pedidos"))


# ==========================================
# CANCELAR PEDIDO PENDENTE
# ==========================================

@admin_bp.route(
    "/admin/pedidos/cancelar/<id_pedido>",
    methods=["POST"]
)
@administrador_obrigatorio
def cancelar_pedido(id_pedido):

    try:
        validate_csrf(request.form.get("csrf_token"))

    except ValidationError:
        flash("Formulário inválido ou expirado.")
        return redirect(url_for("admin.listar_pedidos"))

    try:
        object_id = ObjectId(id_pedido)

    except (InvalidId, TypeError):
        abort(404)

    try:
        resultado = pedidos.update_one(
            {
                "_id": object_id,
                "status": "AGUARDANDO_CONFIRMACAO"
            },
            {
                "$set": {
                    "status": "CANCELADO",
                    "cancelado_em": datetime.now(timezone.utc)
                }
            }
        )

        if resultado.modified_count == 1:
            flash("Pedido cancelado com sucesso!")
        else:
            flash("Pedido não encontrado ou já finalizado.")

    except PyMongoError:
        current_app.logger.exception(
            "Erro ao cancelar pedido"
        )

        flash("Não foi possível cancelar o pedido.")

    return redirect(url_for("admin.listar_pedidos"))


# ==========================================
# DASHBOARD DE VENDAS
# ==========================================

@admin_bp.route("/admin/dashboard")
@administrador_obrigatorio
def dashboard_vendas():

    try:
        # Resumo dos pedidos por status
        resumo = list(
            pedidos.aggregate([
                {
                    "$group": {
                        "_id": "$status",
                        "quantidade": {"$sum": 1},
                        "faturamento": {
                            "$sum": {
                                "$cond": [
                                    {"$eq": ["$status", "CONFIRMADO"]},
                                    {"$ifNull": ["$total", 0]},
                                    0
                                ]
                            }
                        }
                    }
                }
            ])
        )

        vendas_confirmadas = 0
        pedidos_pendentes = 0
        pedidos_cancelados = 0
        faturamento = 0

        for grupo in resumo:

            status = grupo["_id"]
            quantidade = grupo["quantidade"]

            if status == "CONFIRMADO":
                vendas_confirmadas = quantidade
                faturamento = grupo["faturamento"]

            elif status == "AGUARDANDO_CONFIRMACAO":
                pedidos_pendentes = quantidade

            elif status == "CANCELADO":
                pedidos_cancelados = quantidade

        # Produtos mais vendidos
        mais_vendidos = list(
            pedidos.aggregate([
                {
                    "$match": {"status": "CONFIRMADO"}
                },
                {
                    "$unwind": "$itens"
                },
                {
                    "$group": {
                        "_id": "$itens.produto_id",
                        "nome": {"$first": "$itens.nome"},
                        "quantidade": {
                            "$sum": "$itens.quantidade"
                        },
                        "faturamento": {
                            "$sum": "$itens.subtotal"
                        }
                    }
                },
                {
                    "$sort": {
                        "quantidade": -1,
                        "nome": 1
                    }
                },
                {
                    "$limit": 5
                }
            ])
        )

        # Últimos cinco pedidos
        ultimos_pedidos = list(
            pedidos.find()
            .sort("criado_em", -1)
            .limit(5)
        )

        for pedido in ultimos_pedidos:

            pedido["id"] = str(pedido["_id"])
            data = pedido.get("criado_em")

            if data:
                pedido["data_formatada"] = (
                    data.strftime("%d/%m/%Y %H:%M") + " UTC"
                )
            else:
                pedido["data_formatada"] = "-"

        # Formatar faturamento em reais
        faturamento_formatado = (
            f"R$ {faturamento:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return render_template(
            "dashboard.html",
            faturamento=faturamento_formatado,
            vendas_confirmadas=vendas_confirmadas,
            pedidos_pendentes=pedidos_pendentes,
            pedidos_cancelados=pedidos_cancelados,
            mais_vendidos=mais_vendidos,
            ultimos_pedidos=ultimos_pedidos
        )

    except PyMongoError:
        current_app.logger.exception(
            "Erro ao carregar dashboard de vendas"
        )

        flash("Não foi possível carregar o dashboard.")

        return redirect(url_for("admin.painel"))
