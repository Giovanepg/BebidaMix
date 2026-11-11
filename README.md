
# 🍻 BebidaMix — E-commerce de Bebidas

O **BebidaMix** é um sistema web de comércio eletrônico de bebidas, desenvolvido com **Python, Flask, HTML, CSS e JavaScript**, utilizando uma arquitetura de **Banco de Dados Poliglota** com **MongoDB Atlas, Supabase (PostgreSQL) e Redis**.

O projeto foi desenvolvido para fins acadêmicos, com o objetivo de demonstrar a integração de diferentes tecnologias de banco de dados em uma única aplicação.

---

## 📌 Sobre o Projeto

O BebidaMix permite que os clientes visualizem bebidas disponíveis, consultem preços, adicionem produtos ao carrinho e realizem pedidos pelo WhatsApp.

Além do catálogo público, o sistema possui uma área administrativa com autenticação, gerenciamento de produtos, controle de estoque e acompanhamento dos pedidos.

O principal diferencial do projeto é a utilização de três tecnologias de banco de dados, cada uma responsável por determinadas funcionalidades.

---

## 🎯 Objetivos do Projeto

- Desenvolver uma aplicação web de comércio eletrônico.
- Implementar autenticação utilizando o Supabase.
- Armazenar produtos e pedidos no MongoDB Atlas.
- Utilizar Redis para cache de produtos visualizados recentemente.
- Implementar operações CRUD para gerenciamento de produtos.
- Desenvolver um carrinho de compras com cálculo automático dos valores.
- Integrar a finalização dos pedidos ao WhatsApp.
- Demonstrar a utilização de Banco de Dados Poliglota em uma aplicação funcional.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Utilização |
|------------|------------|
| Python | Linguagem principal do backend |
| Flask | Framework para desenvolvimento web |
| HTML5 | Estrutura das páginas |
| CSS3 | Estilização da interface |
| JavaScript | Interatividade e carrinho de compras |
| MongoDB Atlas | Armazenamento de produtos e pedidos |
| Supabase | Autenticação e gerenciamento de permissões |
| PostgreSQL | Banco relacional utilizado pelo Supabase |
| Redis | Cache de produtos visualizados recentemente |
| Git e GitHub | Versionamento e hospedagem do código |

---

## 🗄️ Arquitetura de Banco de Dados Poliglota

Banco de Dados Poliglota é uma abordagem que utiliza diferentes tipos de bancos de dados em uma mesma aplicação, aproveitando as características de cada tecnologia.

No BebidaMix, essa arquitetura é composta por três bancos.

### 1. MongoDB Atlas — Banco NoSQL

O MongoDB é responsável pelo armazenamento dos produtos e pedidos.

**Principais funcionalidades:**

- Cadastro de novos produtos.
- Consulta de produtos disponíveis.
- Atualização das informações.
- Exclusão de produtos.
- Armazenamento dos pedidos realizados.
- Consulta de preços, categorias e estoque.

Os dados são organizados em documentos, contendo informações como nome, descrição, preço, categoria, estoque e imagem.

### 2. Supabase — PostgreSQL e Autenticação

O Supabase é utilizado para autenticação dos usuários e gerenciamento das permissões administrativas.

**Principais funcionalidades:**

- Cadastro de clientes.
- Login de usuários.
- Gerenciamento de sessões.
- Identificação dos administradores.
- Restrição de acesso ao módulo administrativo.

A autenticação utiliza o Supabase Auth, enquanto o PostgreSQL armazena informações relacionais utilizadas na autorização administrativa.

### 3. Redis — Banco de Dados em Memória

O Redis funciona como mecanismo de cache para armazenar temporariamente os produtos visualizados recentemente.

**Principais funcionalidades:**

- Registrar produtos visualizados.
- Recuperar informações do histórico recente.
- Exibir a seção "Visualizados recentemente".
- Aplicar expiração aos registros armazenados.

O MongoDB continua responsável pelos dados principais dos produtos, enquanto o Redis mantém referências temporárias para consultas rápidas.

---

## 🔄 Diagrama da Arquitetura

```mermaid
flowchart TD
    A["Cliente / Navegador"] --> B["Aplicação Flask"]

    B --> C["MongoDB Atlas"]
    B --> D["Supabase / PostgreSQL"]
    B --> E["Redis"]

    C --> F["Produtos e pedidos"]
    D --> G["Autenticação e permissões"]
    E --> H["Produtos visualizados recentemente"]

    B --> I["Carrinho de compras"]
    I --> J["Finalização do pedido"]
    J --> K["WhatsApp"]
```

---

## 🛍️ Funcionalidades do Cliente

### Catálogo público

O cliente pode acessar o catálogo sem precisar realizar login.

**Funcionalidades:**

- Visualizar bebidas cadastradas.
- Consultar preços e descrições.
- Pesquisar produtos pelo nome.
- Filtrar bebidas por categoria.
- Visualizar detalhes dos produtos.
- Consultar produtos visualizados recentemente.

### Carrinho de Compras

O carrinho permite:

- Adicionar produtos.
- Aumentar ou diminuir quantidades.
- Remover produtos.
- Calcular os subtotais automaticamente.
- Calcular o valor total.
- Respeitar os limites de estoque.
- Preservar os produtos durante o login.

O carrinho utiliza o armazenamento local do navegador para manter os itens selecionados.

### Login e Cadastro

O cliente pode navegar pelo catálogo sem estar autenticado.

Entretanto, ao clicar em **Finalizar pedido**, o sistema verifica se o usuário possui uma sessão válida.

Caso não esteja autenticado, o cliente é direcionado para a página de login.

Após realizar o login, os produtos adicionados anteriormente continuam no carrinho.

### Finalização pelo WhatsApp

Quando o cliente finaliza a compra:

1. O sistema recebe os produtos selecionados.
2. Valida as informações no backend.
3. Consulta os dados oficiais dos produtos no MongoDB.
4. Registra o pedido no banco de dados.
5. Gera uma mensagem com os itens e valores.
6. Abre o WhatsApp para o cliente enviar o pedido.

O sistema também utiliza uma chave de identificação da tentativa de compra para reduzir registros duplicados.

---

## 🔐 Funcionalidades do Administrador

O módulo administrativo possui acesso restrito aos usuários autorizados.

**Funcionalidades disponíveis:**

- Login administrativo.
- Cadastro de bebidas.
- Listagem dos produtos.
- Edição de informações.
- Exclusão de produtos.
- Controle de estoque.
- Consulta de pedidos.
- Painel administrativo.

### Operações CRUD

| Operação | Descrição |
|----------|-----------|
| Create | Cadastrar novos produtos |
| Read | Consultar produtos cadastrados |
| Update | Atualizar informações dos produtos |
| Delete | Excluir produtos |

---

## 📁 Estrutura do Projeto

```text
BebidaMix/
│
├── database/
│   ├── mongodb.py
│   ├── redis_db.py
│   └── supabase_db.py
│
├── routes/
│   ├── admin.py
│   └── cliente.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── detalhes.js
│   │   └── script.js
│   └── uploads/
│
├── templates/
│   ├── acesso.html
│   ├── admin.html
│   ├── cadastrar_produto.html
│   ├── dashboard.html
│   ├── detalhes_produto.html
│   ├── editar_produto.html
│   ├── estoque.html
│   ├── gerenciar_produtos.html
│   ├── index.html
│   ├── login.html
│   └── pedidos.html
│
├── app.py
├── cadastrar_produtos.py
├── criar_indice_pedidos.py
├── teste_mongodb.py
├── teste_redis.py
├── teste_supabase.py
│
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md
```

---

## ⚙️ Instalação e Configuração

### Pré-requisitos

- Python instalado.
- Git instalado.
- MongoDB Atlas configurado.
- Projeto Supabase configurado.
- Redis instalado e funcionando.
- Conexão com a internet.

### 1. Clonar o repositório

```bash
git clone https://github.com/Giovanepg/BebidaMix.git

cd BebidaMix
```

### 2. Criar o ambiente virtual

No Windows:

```powershell
python -m venv .venv
```

### 3. Ativar o ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a execução de scripts, também é possível executar o Python diretamente pelo ambiente virtual.

### 4. Instalar as dependências

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 5. Configurar as variáveis de ambiente

Crie um arquivo `.env` na pasta principal do projeto, utilizando o `.env.example` como referência.

Exemplo:

```dotenv
WHATSAPP_NUMERO=55DDDNÚMERO

MONGO_URI=mongodb+srv://USUARIO:SENHA@CLUSTER.mongodb.net/
MONGO_DB_NAME=BebidaMix

SUPABASE_URL=https://SEU_PROJETO.supabase.co
SUPABASE_KEY=SUA_CHAVE_PUBLICA

SECRET_KEY=SUA_CHAVE_SECRETA

FLASK_ENV=development
```

> **Importante:** nunca publique senhas, tokens ou credenciais reais no GitHub.

### 6. Iniciar o Redis

Para usuários que utilizam Redis no WSL:

```bash
sudo service redis-server start
```

Verifique a conexão:

```bash
redis-cli ping
```

Resultado esperado:

```text
PONG
```

### 7. Executar a aplicação Flask

No PowerShell:

```powershell
.\.venv\Scripts\python.exe app.py
```

Acesse no navegador:

```text
http://127.0.0.1:5000
```

---

## 🧪 Testes de Conexão

O projeto possui scripts específicos para verificar a comunicação com os bancos de dados.

### MongoDB Atlas

```powershell
.\.venv\Scripts\python.exe teste_mongodb.py
```

### Supabase

```powershell
.\.venv\Scripts\python.exe teste_supabase.py
```

### Redis

```powershell
.\.venv\Scripts\python.exe teste_redis.py
```

Esses testes permitem verificar a conectividade antes da utilização do sistema.

---

## 📸 Demonstração do Sistema

Esta seção apresenta as principais telas da aplicação.

> As imagens serão adicionadas à pasta `docs/imagens/`.

### 🏠 Catálogo de Bebidas

Imagem da página inicial com a listagem de bebidas disponíveis.

**Imagem pendente:** `docs/imagens/catalogo.png`

### 🥤 Detalhes do Produto

Imagem da página com informações de uma bebida selecionada.

**Imagem pendente:** `docs/imagens/detalhes-produto.png`

### 🛒 Carrinho de Compras

Imagem demonstrando a inclusão de produtos, as quantidades e o total calculado.

**Imagem pendente:** `docs/imagens/carrinho.png`

### 👤 Login e Cadastro

Imagem da tela de autenticação dos usuários.

**Imagem pendente:** `docs/imagens/login.png`

### 📊 Painel Administrativo

Imagem do dashboard com as funcionalidades administrativas.

**Imagem pendente:** `docs/imagens/dashboard.png`

### 📦 Gerenciamento de Produtos

Imagem das funcionalidades de cadastro, edição e controle de estoque.

**Imagem pendente:** `docs/imagens/gerenciamento.png`

### 📱 Finalização pelo WhatsApp

Imagem demonstrando a mensagem de pedido gerada pelo sistema.

**Imagem pendente:** `docs/imagens/whatsapp.png`

---

## 🗃️ Evidências dos Bancos de Dados

### MongoDB Atlas

O MongoDB Atlas é utilizado para armazenar os produtos e pedidos.

**Imagem pendente:** `docs/imagens/mongodb.png`

### Supabase / PostgreSQL

O Supabase é utilizado para autenticação e gerenciamento de permissões.

**Imagem pendente:** `docs/imagens/supabase.png`

### Redis

O Redis é utilizado para manter o cache dos produtos visualizados recentemente.

**Imagem pendente:** `docs/imagens/redis.png`

> As capturas de tela devem ocultar senhas, tokens e informações privadas.

---

## 🔒 Segurança

O sistema utiliza medidas de segurança como:

- Autenticação pelo Supabase.
- Restrição de acesso ao módulo administrativo.
- Variáveis de ambiente para credenciais.
- Arquivo `.gitignore` para proteger arquivos locais.
- Validação de produtos e quantidades no servidor.
- Gerenciamento de sessões no Flask.
- Identificação de tentativas de pedidos para reduzir duplicações.

**Observação:** o projeto possui finalidade acadêmica. A utilização em ambiente comercial exige medidas adicionais de segurança, infraestrutura e adequação à legislação aplicável.

---

## 📚 Contexto Acadêmico

O BebidaMix foi desenvolvido para demonstrar a aplicação prática de **Banco de Dados Poliglota**.

Essa abordagem permite que diferentes bancos de dados sejam utilizados na mesma aplicação, cada um desempenhando uma função específica.

| Banco de Dados | Responsabilidade |
|----------------|------------------|
| MongoDB Atlas | Produtos e pedidos |
| Supabase / PostgreSQL | Autenticação e permissões |
| Redis | Cache de produtos recentes |

A integração dessas tecnologias demonstra como diferentes modelos de persistência podem trabalhar juntos em um sistema web.

---

## 👨‍💻 Desenvolvedor

**Giovane**

Projeto acadêmico desenvolvido com Python, Flask, MongoDB Atlas, Supabase e Redis.

---

## 📄 Finalidade do Projeto

O BebidaMix foi desenvolvido para fins educacionais, com foco no aprendizado de desenvolvimento web, autenticação, operações CRUD, integração de bancos de dados e arquitetura de persistência poliglota.
