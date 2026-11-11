
import os
import json
import hashlib

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from urllib.parse import quote
from uuid import uuid4, UUID

from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    abort,
    redirect,
    url_for
)

from flask_wtf.csrf import generate_csrf

from pymongo.errors import (
    PyMongoError,
    DuplicateKeyError
)

from redis.exceptions import RedisError

# Bibliotecas para sessoes e login
from cachelib.file import FileSystemCache
from flask_session import Session
from redis import Redis
from werkzeug.middleware.proxy_fix import ProxyFix

# Conexoes com os bancos de dados
from database.mongodb import produtos
from database.redis_db import redis_client

# Rotas administrativas
from routes.admin import admin_bp

# Rotas de cadastro e login de clientes
from routes.cliente import (
    cliente_bp,
    usuario_autenticado
)


# ==================================
# CONFIGURACAO DO FLASK
# ==================================

load_dotenv()

app = Flask(__name__)

# Identificar ambiente de producao
PRODUCAO = (
    os.getenv("FLASK_ENV", "development").lower()
    == "production"
)

# Chave secreta
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

# Configuracoes de seguranca dos cookies
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = PRODUCAO
app.config["SESSION_COOKIE_NAME"] = "bebidamix_session"

# Duracao da sessao
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    hours=8
)

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_USE_SIGNER"] = True

# Limite de 6 MB para requisicoes
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024


# ==================================
# CONFIGURAR SESSOES POR AMBIENTE
# ==================================

if PRODUCAO:

    # Aplicacao atras do proxy HTTPS
    # Usar somente com um proxy confiavel
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1
    )

    # Redis gerenciado para sessoes
    url_redis_sessoes = os.getenv("REDIS_URL")

    if not url_redis_sessoes:

        raise RuntimeError(
            "REDIS_URL nao configurada. "
            "E necessario Redis gerenciado "
            "para sessoes em producao."
        )

    app.config["SESSION_TYPE"] = "redis"

    app.config["SESSION_REDIS"] = Redis.from_url(
        url_redis_sessoes,
        socket_connect_timeout=5,
        socket_timeout=5
    )

else:

    # Desenvolvimento local
    app.config["SESSION_TYPE"] = "cachelib"

    app.config["SESSION_CACHELIB"] = FileSystemCache(
        cache_dir=".flask_sessions",
        threshold=500
    )


Session(app)


# ==================================
# CABECALHOS DE SEGURANCA
# ==================================

@app.after_request
def adicionar_cabecalhos_seguranca(resposta):

    resposta.headers["X-Content-Type-Options"] = (
        "nosniff"
    )

    resposta.headers["Referrer-Policy"] = (
        "strict-origin-when-cross-origin"
    )

    resposta.headers["X-Frame-Options"] = (
        "DENY"
    )

    # HSTS somente em producao
    if PRODUCAO:

        resposta.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000"

    return resposta


# ==================================
# REGISTRAR ROTAS
# ==================================

# Rotas do administrador
app.register_blueprint(admin_bp)

# Rotas de cadastro e login de clientes
app.register_blueprint(cliente_bp)


# ==================================
# PROTEGER FINALIZACAO DO PEDIDO
# ==================================

@app.before_request
def verificar_acesso_cliente():

    # Catalogo e detalhes sao publicos
    # Somente finalizar pedidos exige login
    if request.endpoint != "finalizar_pedido":
        return

    # Verificar se esta autenticado
    if usuario_autenticado():
        return

    # Visitante precisa fazer login
    return jsonify({
        "erro": "Faca login para finalizar seu pedido.",
        "login_url": url_for("cliente.entrar")
    }), 401


# ==================================
# COLECAO DE PEDIDOS DO MONGODB
# ==================================

pedidos = produtos.database["pedidos"]


# ==================================
# FORMATAR PRECOS
# ==================================

def formatar_preco(valor):

    return f"R$ {valor:.2f}".replace(".", ",")


# ==================================
# IDENTIFICAR VISITANTE
# ==================================

def obter_id_visitante():

    if "visitante_id" not in session:

        session["visitante_id"] = str(
            uuid4()
        )

    return session["visitante_id"]


# ==================================
# REGISTRAR VISUALIZACAO NO REDIS
# ==================================

def registrar_visualizacao(id_produto):

    visitante = obter_id_visitante()

    chave = f"bebidamix:recentes:{visitante}"

    try:

        with redis_client.pipeline() as pipe:

            # Remover se ja estiver na lista
            pipe.lrem(chave, 0, id_produto)

            # Adicionar ao inicio da lista
            pipe.lpush(chave, id_produto)

            # Manter os ultimos cinco produtos
            pipe.ltrim(chave, 0, 4)

            # Expirar apos sete dias
            pipe.expire(chave, 604800)

            pipe.execute()

    except RedisError as erro:

        app.logger.warning(
            "Redis indisponivel ao registrar visualizacao: %s",
            erro
        )


# ==================================
# CONSULTAR PRODUTOS RECENTES
# ==================================

def buscar_produtos_recentes():

    visitante = obter_id_visitante()

    chave = f"bebidamix:recentes:{visitante}"

    try:

        ids = redis_client.lrange(
            chave, 0, 4
        )

    except RedisError as erro:

        app.logger.warning(
            "Redis indisponivel ao buscar recentes: %s",
            erro
        )

        return []

    if not ids:
        return []

    # Converter IDs para ObjectId
    ids_validos = []

    for id_produto in ids:

        try:

            ids_validos.append(
                ObjectId(id_produto)
            )

        except (InvalidId, TypeError):
            continue

    if not ids_validos:
        return []

    # Buscar dados verdadeiros no MongoDB
    encontrados = list(
        produtos.find({
            "_id": {"$in": ids_validos},
            "ativo": True
        })
    )

    produtos_por_id = {}

    for produto in encontrados:

        produto["id"] = str(
            produto["_id"]
        )

        produtos_por_id[produto["id"]] = produto

    recentes = []

    # Organizar os produtos na ordem do Redis
    for id_produto in ids:

        if id_produto in produtos_por_id:

            recentes.append(
                produtos_por_id[id_produto]
            )

    return recentes


# ==================================
# CATALOGO DE PRODUTOS
# ==================================

@app.route("/")
def inicio():

    try:

        # Buscar produtos ativos
        lista_produtos = list(
            produtos.find({
                "ativo": True
            })
        )

        # Converter IDs para texto
        for produto in lista_produtos:

            produto["id"] = str(
                produto["_id"]
            )

        # Buscar visualizados recentemente
        try:

            recentes = buscar_produtos_recentes()

        except PyMongoError as erro:

            app.logger.warning(
                "Erro ao carregar produtos recentes: %s",
                erro
            )

            recentes = []

        # Verificar tokens apenas se existirem
        # Visitantes nao precisam fazer login
        possui_tokens = bool(
            session.get("access_token")
            and session.get("refresh_token")
        )

        usuario_logado = (
            possui_tokens and usuario_autenticado()
        )

        # Nome exibido no cabecalho
        nome_cliente = (
            session.get("usuario_nome", "Cliente")
            if usuario_logado
            else "Visitante"
        )

        return render_template(
            "index.html",
            produtos=lista_produtos,
            recentes=recentes,
            nome_cliente=nome_cliente,
            usuario_logado=usuario_logado,
            csrf_token=generate_csrf()
        )

    except PyMongoError as erro:

        app.logger.error(
            "Erro no MongoDB: %s",
            erro
        )

        return "Erro ao carregar catalogo.", 503


# ==================================
# DETALHES DO PRODUTO
# ==================================

@app.route("/produto/<id_produto>")
def detalhes_produto(id_produto):

    try:

        object_id = ObjectId(
            id_produto
        )

    except (InvalidId, TypeError):
        abort(404)

    try:

        produto = produtos.find_one({
            "_id": object_id,
            "ativo": True
        })

    except PyMongoError as erro:

        app.logger.error(
            "Erro ao buscar produto: %s",
            erro
        )

        return "Erro ao carregar produto.", 503

    if produto is None:
        abort(404)

    produto["id"] = str(
        produto["_id"]
    )

    # Registrar visualizacao no Redis
    registrar_visualizacao(
        produto["id"]
    )

    return render_template(
        "detalhes_produto.html",
        produto=produto,
        nome_cliente=session.get(
            "usuario_nome", "Cliente"
        ),
        csrf_token=generate_csrf()
    )


# ==================================
# GERAR LINK DO WHATSAPP
# ==================================

def gerar_link_pedido(pedido, numero):

    id_pedido = str(
        pedido["_id"]
    )

    mensagem = [
        "*NOVO PEDIDO - BEBIDAMIX*",
        "",
        f"*Pedido:* {id_pedido}",
        "",
        "Ola! Gostaria de fazer o seguinte pedido:",
        ""
    ]

    # Adicionar os itens do pedido
    for item in pedido["itens"]:

        subtotal = Decimal(
            str(item["subtotal"])
        )

        mensagem.append(
            f"{item['quantidade']}x "
            f"{item['nome']} - "
            f"{formatar_preco(subtotal)}"
        )

    total = Decimal(
        str(pedido["total"])
    )

    mensagem.extend([
        "",
        f"*TOTAL: {formatar_preco(total)}*",
        "",
        "Aguardo a confirmacao do pedido."
    ])

    texto = "\n".join(mensagem)

    # Gerar link para o WhatsApp
    return (
        f"https://wa.me/{numero}"
        f"?text={quote(texto)}"
    )


# ==================================
# RECUPERAR PEDIDO EXISTENTE
# ==================================

def recuperar_pedido(chave, assinatura, numero):

    pedido = pedidos.find_one({
        "chave_idempotencia": chave
    })

    if pedido is None:
        return None

    # Impedir usar uma chave com outro carrinho
    if pedido.get("assinatura_carrinho") != assinatura:

        return jsonify({
            "erro": (
                "Esta chave ja foi utilizada "
                "com outro carrinho."
            )
        }), 409

    # Impedir reutilizar pedidos finalizados
    if pedido.get("status") != "AGUARDANDO_CONFIRMACAO":

        return jsonify({
            "erro": (
                "Esta tentativa ja foi finalizada. "
                "Inicie um novo pedido."
            ),
            "pedido_id": str(
                pedido["_id"]
            )
        }), 409

    # Recuperar pedido pendente
    link = gerar_link_pedido(
        pedido,
        numero
    )

    return jsonify({
        "link": link,
        "pedido_id": str(pedido["_id"]),
        "reutilizado": True
    })


# ==================================
# FINALIZAR PEDIDO COM IDEMPOTENCIA
# ==================================

@app.route("/finalizar-pedido", methods=["POST"])
def finalizar_pedido():

    # Receber dados enviados pelo JavaScript
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):

        return jsonify({
            "erro": "Pedido invalido."
        }), 400

    itens = dados.get("itens")
    chave = dados.get("chave_pedido")

    # ==================================
    # VALIDAR CARRINHO
    # ==================================

    if (
        not isinstance(itens, list)
        or not 1 <= len(itens) <= 50
    ):

        return jsonify({
            "erro": "Carrinho invalido."
        }), 400

    # ==================================
    # VALIDAR CHAVE DO PEDIDO
    # ==================================

    try:

        if not isinstance(chave, str):
            raise ValueError()

        identificador = UUID(chave)

        if identificador.version != 4:
            raise ValueError()

        chave = str(identificador)

    except (ValueError, TypeError, AttributeError):

        return jsonify({
            "erro": "Chave do pedido invalida."
        }), 400

    # ==================================
    # VALIDAR WHATSAPP
    # ==================================

    numero = os.getenv(
        "WHATSAPP_NUMERO", ""
    )

    if (
        not numero.isdigit()
        or not 12 <= len(numero) <= 15
    ):

        return jsonify({
            "erro": "WhatsApp nao configurado."
        }), 503

    # ==================================
    # VALIDAR IDs E QUANTIDADES
    # ==================================

    itens_validados = []
    ids_recebidos = set()

    for item in itens:

        if not isinstance(item, dict):

            return jsonify({
                "erro": "Item invalido."
            }), 400

        id_produto = item.get("id")
        quantidade = item.get("quantidade")

        if not isinstance(id_produto, str):

            return jsonify({
                "erro": "ID invalido."
            }), 400

        try:

            object_id = ObjectId(
                id_produto
            )

        except (InvalidId, TypeError):

            return jsonify({
                "erro": "ID invalido."
            }), 400

        if (
            type(quantidade) is not int
            or not 1 <= quantidade <= 1000
        ):

            return jsonify({
                "erro": "Quantidade invalida."
            }), 400

        # Normalizar ID para texto
        id_normalizado = str(
            object_id
        )

        # Evitar produtos duplicados no carrinho
        if id_normalizado in ids_recebidos:

            return jsonify({
                "erro": "Produto duplicado."
            }), 400

        ids_recebidos.add(
            id_normalizado
        )

        itens_validados.append({
            "id": id_normalizado,
            "object_id": object_id,
            "quantidade": quantidade
        })

    # ==================================
    # ASSINATURA DO CARRINHO
    # ==================================

    # Gerar a mesma assinatura para
    # produtos e quantidades iguais
    resumo = sorted(
        [
            {
                "id": item["id"],
                "quantidade": item["quantidade"]
            }
            for item in itens_validados
        ],
        key=lambda item: item["id"]
    )

    conteudo = json.dumps(
        resumo,
        sort_keys=True,
        separators=(",", ":")
    )

    assinatura = hashlib.sha256(
        conteudo.encode("utf-8")
    ).hexdigest()

    # ==================================
    # VERIFICAR PEDIDO EXISTENTE
    # ==================================

    try:

        resposta_existente = recuperar_pedido(
            chave,
            assinatura,
            numero
        )

        if resposta_existente is not None:
            return resposta_existente

    except PyMongoError:

        app.logger.exception(
            "Erro ao consultar chave do pedido"
        )

        return jsonify({
            "erro": "Nao foi possivel verificar o pedido."
        }), 503

    # ==================================
    # CONSULTAR PRODUTOS NO MONGODB
    # ==================================

    total = Decimal("0.00")
    itens_pedido = []

    try:

        for item in itens_validados:

            produto = produtos.find_one({
                "_id": item["object_id"],
                "ativo": True
            })

            if produto is None:

                return jsonify({
                    "erro": "Produto indisponivel."
                }), 400

            quantidade = item["quantidade"]
            estoque = produto.get("estoque", 0)

            if (
                type(estoque) is not int
                or quantidade > estoque
            ):

                return jsonify({
                    "erro": (
                        "Estoque insuficiente: "
                        f"{produto['nome']}."
                    )
                }), 400

            # Consultar preco verdadeiro
            preco = Decimal(
                str(produto["preco"])
            )

            if (
                not preco.is_finite()
                or preco <= 0
                or preco.as_tuple().exponent < -2
            ):

                raise ValueError(
                    "Preco invalido no banco."
                )

            subtotal = preco * quantidade
            total += subtotal

            # Guardar dados dos produtos no pedido
            itens_pedido.append({
                "produto_id": item["object_id"],
                "nome": produto["nome"],
                "preco": float(preco),
                "quantidade": quantidade,
                "subtotal": float(subtotal)
            })

        # ==================================
        # REGISTRAR NOVO PEDIDO
        # ==================================

        novo_pedido = {
            "chave_idempotencia": chave,
            "assinatura_carrinho": assinatura,
            "itens": itens_pedido,
            "total": float(total),
            "status": "AGUARDANDO_CONFIRMACAO",
            "criado_em": datetime.now(
                timezone.utc
            )
        }

        # Salvar no MongoDB
        resultado = pedidos.insert_one(
            novo_pedido
        )

        novo_pedido["_id"] = resultado.inserted_id

        # Gerar mensagem do WhatsApp
        link = gerar_link_pedido(
            novo_pedido,
            numero
        )

        return jsonify({
            "link": link,
            "pedido_id": str(
                resultado.inserted_id
            ),
            "reutilizado": False
        })

    # ==================================
    # CHAVE DUPLICADA
    # ==================================

    except DuplicateKeyError:

        try:

            resposta_existente = recuperar_pedido(
                chave,
                assinatura,
                numero
            )

            if resposta_existente is not None:
                return resposta_existente

            return jsonify({
                "erro": (
                    "Pedido em processamento. "
                    "Tente novamente."
                )
            }), 503

        except PyMongoError:

            app.logger.exception(
                "Erro ao recuperar pedido duplicado"
            )

            return jsonify({
                "erro": (
                    "Nao foi possivel recuperar o pedido."
                )
            }), 503

    except (
        PyMongoError,
        ValueError,
        TypeError,
        KeyError,
        ArithmeticError
    ):

        app.logger.exception(
            "Erro ao registrar pedido"
        )

        return jsonify({
            "erro": "Nao foi possivel registrar o pedido."
        }), 503


# ==================================
# INICIAR APLICACAO
# ==================================

if __name__ == "__main__":

    # Desenvolvimento local
    # Em producao sera utilizado Gunicorn
    app.run(debug=not PRODUCAO)
