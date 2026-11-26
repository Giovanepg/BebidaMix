
# 🍻 BebidaMix — E-commerce de Bebidas

O **BebidaMix** é um sistema web de catálogo e pedidos de bebidas, desenvolvido com **Python, Flask, HTML, CSS e JavaScript**.

O projeto utiliza uma arquitetura de **Banco de Dados Poliglota**, integrando três tecnologias de persistência:

- **MongoDB Atlas:** armazenamento de produtos e pedidos.
- **Supabase / PostgreSQL:** autenticação e controle de permissões.
- **Redis:** cache de produtos visualizados recentemente.

> 📚 **Projeto acadêmico:** desenvolvido para a disciplina de Banco de Dados, com foco na integração de bancos relacionais, NoSQL e em memória.

---

## 📑 Sumário

- [📌 Sobre o Projeto](#sobre-o-projeto)
- [🎯 Objetivos](#objetivos)
- [🎥 Vídeo Demonstrativo](#video-demonstrativo)
- [🛠️ Tecnologias Utilizadas](#tecnologias-utilizadas)
- [✨ Funcionalidades](#funcionalidades)
- [🗄️ Banco de Dados Poliglota](#banco-de-dados-poliglota)
  - [MongoDB Atlas](#mongodb-atlas)
  - [Supabase / PostgreSQL](#supabase-postgresql)
  - [Redis](#redis)
- [🔄 Arquitetura do Sistema](#arquitetura-do-sistema)
- [🧪 Demonstração Prática dos Bancos](#demonstracao-pratica-dos-bancos)
  - [Teste do MongoDB](#teste-do-mongodb)
  - [Teste do Supabase](#teste-do-supabase)
  - [Teste do Redis](#teste-do-redis)
- [📸 Demonstração Visual](#demonstracao-visual)
- [📁 Estrutura do Projeto](#estrutura-do-projeto)
- [⚙️ Configuração dos Bancos](#configuracao-dos-bancos)
- [🚀 Instalação e Execução](#instalacao-e-execucao)
- [🔒 Segurança](#seguranca)
- [🎓 Entrega Acadêmica](#entrega-academica)
- [👨‍💻 Autor](#autor)
- [✅ Status do Projeto](#status-do-projeto)

---

<a id="sobre-o-projeto"></a>
## 📌 Sobre o Projeto

O **BebidaMix** é uma aplicação web que permite aos clientes consultar bebidas disponíveis, pesquisar produtos, visualizar detalhes, adicionar itens ao carrinho e realizar pedidos pelo WhatsApp.

O sistema também possui um módulo administrativo, protegido por autenticação, para gerenciamento de produtos, estoque e pedidos.

O principal diferencial do projeto é a utilização de diferentes tecnologias de banco de dados em uma única aplicação.

Cada banco possui uma responsabilidade específica, permitindo demonstrar como diferentes modelos de persistência podem trabalhar em conjunto.

---

<a id="objetivos"></a>
## 🎯 Objetivos

### Objetivo Geral

Desenvolver uma aplicação web de comércio eletrônico utilizando **Banco de Dados Poliglota**, demonstrando a integração entre MongoDB Atlas, Supabase/PostgreSQL e Redis.

### Objetivos Específicos

- Implementar armazenamento de produtos e pedidos no MongoDB.
- Realizar operações CRUD em uma base NoSQL.
- Implementar autenticação utilizando Supabase Auth.
- Utilizar PostgreSQL para gerenciamento de permissões administrativas.
- Implementar cache de produtos visualizados utilizando Redis.
- Desenvolver um catálogo web integrado aos bancos de dados.
- Criar um carrinho de compras com cálculo automático dos valores.
- Integrar a finalização dos pedidos ao WhatsApp.
- Demonstrar, na prática, a comunicação entre o sistema e os bancos de dados.

---

<a id="video-demonstrativo"></a>
## 🎥 Vídeo Demonstrativo

A demonstração em vídeo é a principal evidência prática do funcionamento do BebidaMix.

A gravação apresenta o sistema em execução e comprova a integração entre as três tecnologias de banco de dados utilizadas.

https://github.com/user-attachments/assets/0474e1f5-0726-47a8-96bb-b46ed090acd9


### O que será demonstrado?

**MongoDB Atlas**

- Cadastro de um produto pelo painel administrativo.
- Verificação do documento criado no MongoDB.
- Alteração das informações de um produto.
- Verificação da atualização no banco.
- Registro de pedidos na coleção correspondente.

**Supabase / PostgreSQL**

- Login de um usuário.
- Autenticação pelo Supabase Auth.
- Consulta das permissões administrativas.
- Restrição de acesso ao painel administrativo.

**Redis**

- Conexão com o servidor Redis.
- Visualização de produtos no catálogo.
- Registro dos produtos acessados recentemente.
- Consulta das informações armazenadas no cache.

> A apresentação busca demonstrar não apenas que os bancos estão conectados, mas que as ações realizadas no sistema produzem alterações ou consultas reais nas tecnologias utilizadas.

---

<a id="tecnologias-utilizadas"></a>
## 🛠️ Tecnologias Utilizadas

| Tecnologia | Finalidade |
|------------|------------|
| Python | Desenvolvimento do backend |
| Flask | Framework web |
| HTML5 | Estrutura das páginas |
| CSS3 | Estilização da interface |
| JavaScript | Interatividade e carrinho |
| MongoDB Atlas | Produtos e pedidos |
| PyMongo | Integração Python com MongoDB |
| Supabase Auth | Autenticação |
| PostgreSQL | Permissões administrativas |
| Redis | Cache de produtos recentes |
| Git | Controle de versionamento |
| GitHub | Hospedagem do código-fonte |
| WSL / Linux | Execução local do Redis |

---

<a id="funcionalidades"></a>
## ✨ Funcionalidades

### 🛍️ Módulo do Cliente

O catálogo é público e pode ser acessado sem autenticação.

**Funcionalidades disponíveis:**

- Visualizar produtos cadastrados.
- Pesquisar bebidas pelo nome.
- Filtrar produtos por categoria.
- Consultar preços e descrições.
- Visualizar detalhes dos produtos.
- Adicionar itens ao carrinho.
- Aumentar e diminuir quantidades.
- Remover produtos.
- Calcular automaticamente o total.
- Visualizar produtos acessados recentemente.
- Realizar cadastro e login.
- Finalizar pedidos pelo WhatsApp.

#### Autenticação na Finalização

O cliente pode navegar pelo catálogo e adicionar produtos ao carrinho sem precisar fazer login.

Ao selecionar **Finalizar pedido**, o sistema verifica se existe uma sessão autenticada.

Caso não exista, o usuário é direcionado para a página de login, preservando os itens adicionados anteriormente.

#### Finalização do Pedido

Quando o cliente finaliza a compra:

1. O carrinho envia os produtos e quantidades ao Flask.
2. O backend consulta os dados oficiais no MongoDB.
3. O sistema valida os produtos e as quantidades.
4. O pedido é registrado no MongoDB.
5. O Flask gera um link com a mensagem do pedido.
6. O cliente é direcionado ao WhatsApp para enviar a mensagem.

O sistema utiliza uma chave de identificação da tentativa de compra para reduzir o risco de pedidos duplicados.

### 🔐 Módulo Administrativo

O módulo administrativo possui acesso restrito aos usuários autorizados.

**Funcionalidades disponíveis:**

- Login administrativo.
- Cadastro de produtos.
- Consulta dos produtos cadastrados.
- Atualização de informações.
- Exclusão de produtos.
- Gerenciamento de estoque.
- Visualização dos pedidos.
- Dashboard administrativo.

### Operações CRUD

| Operação | Descrição |
|----------|-----------|
| CREATE | Cadastrar produtos |
| READ | Consultar produtos |
| UPDATE | Atualizar produtos |
| DELETE | Excluir produtos |

As operações são realizadas pela aplicação Flask e refletem nos documentos armazenados no MongoDB Atlas.

---

<a id="banco-de-dados-poliglota"></a>
## 🗄️ Banco de Dados Poliglota

A **Persistência Poliglota** consiste na utilização de diferentes tecnologias de banco de dados em uma mesma aplicação.

Essa abordagem permite escolher uma tecnologia adequada para cada necessidade do sistema.

No BebidaMix, foram utilizados três bancos de dados com responsabilidades distintas.

### Responsabilidades

| Banco | Modelo | Responsabilidade |
|-------|--------|------------------|
| MongoDB Atlas | NoSQL orientado a documentos | Produtos e pedidos |
| Supabase / PostgreSQL | Relacional e autenticação | Usuários e permissões |
| Redis | Chave-valor em memória | Cache de produtos recentes |

<a id="mongodb-atlas"></a>
### 1. MongoDB Atlas

O **MongoDB Atlas** é responsável pelo armazenamento dos produtos e pedidos.

Os dados são armazenados em documentos BSON, permitindo trabalhar com informações estruturadas de maneira flexível.

#### Produtos

Os documentos de produtos possuem informações como:

- Nome.
- Descrição.
- Categoria.
- Preço.
- Estoque.
- Imagem.
- Status de disponibilidade.

#### Pedidos

Os pedidos realizados pelo sistema também são armazenados no MongoDB.

O registro permite consultar informações relacionadas aos produtos selecionados, quantidades, valores e situação do pedido.

#### Operações

O sistema realiza:

- Inserção de documentos.
- Consulta de documentos.
- Atualização de informações.
- Exclusão de produtos.
- Registro e consulta de pedidos.

**Integração:** Python + Flask + PyMongo + MongoDB Atlas.

<a id="supabase-postgresql"></a>
### 2. Supabase / PostgreSQL

O **Supabase** é utilizado para autenticação dos usuários e gerenciamento de permissões.

A solução combina o Supabase Auth com o banco relacional PostgreSQL.

#### Supabase Auth

Responsável por:

- Cadastro de usuários.
- Login.
- Validação da autenticação.
- Gerenciamento de sessões.

#### PostgreSQL

Responsável por:

- Armazenamento de informações relacionadas aos administradores.
- Identificação de usuários autorizados.
- Apoio ao controle de acesso às funcionalidades administrativas.

#### Controle de Acesso

O sistema verifica se o usuário está autenticado e se possui autorização antes de permitir determinadas operações administrativas.

**Integração:** Python + Flask + Supabase Auth + PostgreSQL.

<a id="redis"></a>
### 3. Redis

O **Redis** é um banco de dados em memória utilizado no BebidaMix como mecanismo de cache.

Sua principal responsabilidade é armazenar temporariamente referências aos produtos visualizados recentemente.

#### Funcionamento

1. O cliente acessa a página de detalhes de uma bebida.
2. O Flask registra a referência do produto no Redis.
3. O Redis mantém uma lista dos produtos visualizados.
4. O sistema recupera os produtos correspondentes do MongoDB.
5. O catálogo apresenta a seção **Visualizados recentemente**.

Essa funcionalidade demonstra a utilização de cache para armazenar informações temporárias de navegação.

**Integração:** Python + Flask + Redis.

---

<a id="arquitetura-do-sistema"></a>
## 🔄 Arquitetura do Sistema

O Flask funciona como intermediário entre a interface web e os serviços de persistência.

```mermaid
flowchart TD
    A["Cliente / Navegador"] --> B["Aplicação Flask"]

    B --> C["MongoDB Atlas"]
    B --> D["Supabase / PostgreSQL"]
    B --> E["Redis"]

    C --> F["Produtos e Pedidos"]
    D --> G["Autenticação e Permissões"]
    E --> H["Produtos Visualizados Recentemente"]

    A --> I["Carrinho no Navegador"]
    I --> B

    B --> J["Link do WhatsApp"]
```

### Fluxo de Integração

| Ação no Sistema | Tecnologia Utilizada |
|-----------------|----------------------|
| Abrir catálogo | MongoDB |
| Consultar produto | MongoDB |
| Cadastrar produto | MongoDB |
| Editar produto | MongoDB |
| Fazer login | Supabase Auth |
| Verificar administrador | Supabase / PostgreSQL |
| Visualizar produto recentemente | Redis |
| Finalizar pedido | MongoDB e WhatsApp |

---

<a id="demonstracao-pratica-dos-bancos"></a>
## 🧪 Demonstração Prática dos Bancos

Esta seção apresenta como verificar o funcionamento das integrações durante a apresentação acadêmica.

<a id="teste-do-mongodb"></a>
### 1. Teste do MongoDB

**Objetivo:** comprovar a persistência dos produtos e pedidos.

**Procedimento:**

1. Acessar o painel administrativo do BebidaMix.
2. Cadastrar um produto de demonstração.
3. Abrir o MongoDB Atlas.
4. Consultar a coleção de produtos.
5. Localizar o documento cadastrado.
6. Alterar o preço pelo painel administrativo.
7. Atualizar a consulta no MongoDB.
8. Verificar se o novo valor foi armazenado.

**Resultado esperado:** as operações realizadas na interface são refletidas nos documentos do MongoDB.

#### Teste de Pedidos

1. Adicionar produtos ao carrinho.
2. Realizar login.
3. Finalizar o pedido.
4. Consultar a coleção de pedidos no MongoDB.
5. Verificar a existência do registro correspondente.

**Resultado esperado:** o pedido é registrado no MongoDB após a validação da finalização pelo Flask.

<a id="teste-do-supabase"></a>
### 2. Teste do Supabase

**Objetivo:** comprovar a autenticação e o controle de permissões.

**Procedimento:**

1. Acessar a página de login do BebidaMix.
2. Autenticar um usuário cadastrado.
3. Abrir o painel **Authentication** do Supabase.
4. Demonstrar a existência do usuário.
5. Abrir a tabela de administradores no PostgreSQL.
6. Verificar a autorização do usuário administrativo.
7. Demonstrar o acesso ao painel administrativo.
8. Testar a restrição utilizando uma conta sem permissão administrativa.

**Resultado esperado:** somente usuários autorizados podem acessar as funcionalidades administrativas.

<a id="teste-do-redis"></a>
### 3. Teste do Redis

**Objetivo:** comprovar que o sistema utiliza Redis para armazenar o histórico recente de produtos.

#### Verificar a conexão

No terminal Linux pelo WSL:

```bash
redis-cli ping
```

Resultado esperado:

```text
PONG
```

#### Demonstrar o Cache

1. Acessar o catálogo do BebidaMix.
2. Abrir os detalhes de um produto.
3. Voltar ao catálogo e abrir outro produto.
4. Acessar o terminal Redis.
5. Consultar as chaves utilizadas pelo histórico recente.
6. Verificar os identificadores armazenados.
7. Voltar ao catálogo e conferir a seção **Visualizados recentemente**.

#### Comandos úteis

Acessar o Redis:

```bash
redis-cli
```

Consultar as chaves do histórico recente:

```redis
SCAN 0 MATCH bebidamix:recentes:* COUNT 100
```

Verificar os itens de uma chave encontrada:

```redis
LRANGE NOME_DA_CHAVE 0 -1
```

Verificar o tempo de expiração:

```redis
TTL NOME_DA_CHAVE
```

> Substitua `NOME_DA_CHAVE` pela chave real retornada pelo Redis. O comando `SCAN` pode precisar de novas consultas usando o cursor retornado.

**Resultado esperado:** os identificadores dos produtos acessados aparecem no Redis e o catálogo apresenta os produtos visualizados recentemente.

---

<a id="demonstracao-visual"></a>
## 📸 Demonstração Visual

Esta seção reúne capturas de tela das principais funcionalidades do sistema.

As imagens serão armazenadas na pasta `docs/imagens/`.

### 🏠 Catálogo de Bebidas

Demonstra a listagem dos produtos armazenados no MongoDB.

<img width="1856" height="898" alt="image" src="https://github.com/user-attachments/assets/cbd6594e-3a98-4de6-bbad-79746a96d5ad" />


### 🥤 Detalhes do Produto

Demonstra a consulta das informações de um produto.

<img width="1857" height="900" alt="image" src="https://github.com/user-attachments/assets/d16f4469-7b1e-4f3f-8759-003c311b69a9" />


### 🛒 Carrinho de Compras

Demonstra a seleção de produtos, quantidades e cálculo automático do total.

<img width="1855" height="901" alt="image" src="https://github.com/user-attachments/assets/93b74285-dd60-4afb-aa09-50002ca64bae" />


### 🔐 Login e Cadastro

Demonstra a autenticação de usuários pelo Supabase.

<img width="1847" height="897" alt="image" src="https://github.com/user-attachments/assets/f4f87b3c-5258-4f83-9258-fe95c530b5fc" />


### 📊 Painel Administrativo

Demonstra as funcionalidades disponíveis para o administrador.

<img width="1857" height="896" alt="image" src="https://github.com/user-attachments/assets/74185744-be19-4835-bb14-951f56343200" />


### 📦 Gerenciamento de Produtos

Demonstra as operações CRUD e o controle de estoque.

<img width="1852" height="896" alt="image" src="https://github.com/user-attachments/assets/fdba765c-65e4-4d6e-95e8-46a090f89c1c" />

---
<img width="1856" height="900" alt="image" src="https://github.com/user-attachments/assets/641cbbb8-82f0-4ca0-85ff-b910eed79576" />

---

<img width="1852" height="897" alt="image" src="https://github.com/user-attachments/assets/16e346a6-8512-4888-b1a3-6a0fdf8083ff" />

---

<img width="1857" height="900" alt="image" src="https://github.com/user-attachments/assets/799ef764-a434-46e6-adc1-413c16875189" />

---

<img width="1852" height="897" alt="image" src="https://github.com/user-attachments/assets/43fa1258-d15e-4c1c-8e40-36048644783e" />



### 📱 Finalização pelo WhatsApp

Demonstra a geração da mensagem do pedido.

<img width="1852" height="802" alt="image" src="https://github.com/user-attachments/assets/db7294e0-47bf-4c09-a1e7-8efdc03fe6ed" />


### 🗃️ Evidências dos Bancos de Dados

#### MongoDB Atlas

Captura de tela das coleções de produtos e pedidos.

<img width="1490" height="747" alt="image" src="https://github.com/user-attachments/assets/21fc7c7d-4f89-4628-ae30-29ee76307c02" />

---

<img width="1490" height="747" alt="image" src="https://github.com/user-attachments/assets/36c8cb6b-1314-4de7-89b6-c019bbe3a58b" />



#### Supabase / PostgreSQL

Captura de tela da autenticação e da tabela de administradores.

<img width="1426" height="788" alt="image" src="https://github.com/user-attachments/assets/16be2885-6f3a-4021-9eed-51faef096635" />

---

<img width="1782" height="827" alt="image" src="https://github.com/user-attachments/assets/3eac789f-971c-44e3-9d5e-f8006f1edcd8" />


#### Redis

Captura de tela do terminal demonstrando o cache de produtos recentes.

**Imagem pendente:** `docs/imagens/redis.png`

> As imagens devem ocultar senhas, tokens, chaves de acesso e dados pessoais.

---

<a id="estrutura-do-projeto"></a>
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
│
├── teste_mongodb.py
├── teste_redis.py
├── teste_supabase.py
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

<a id="configuracao-dos-bancos"></a>
## ⚙️ Configuração dos Bancos

O sistema utiliza serviços externos e um servidor Redis.

Para executar o projeto em outro ambiente, é necessário configurar as conexões e permissões.

### MongoDB Atlas

1. Criar um cluster no MongoDB Atlas.
2. Criar um usuário de banco de dados.
3. Autorizar o endereço IP da máquina.
4. Obter a URI de conexão.
5. Definir o nome do banco como `BebidaMix`.
6. Configurar as variáveis `MONGO_URI` e `MONGO_DB_NAME` no arquivo `.env`.

O arquivo `criar_indice_pedidos.py` contém uma rotina auxiliar relacionada à criação do índice utilizado nos pedidos.

O arquivo `cadastrar_produtos.py` também está disponível como script auxiliar de cadastro.

### Supabase / PostgreSQL

1. Criar um projeto no Supabase.
2. Configurar o serviço de autenticação.
3. Copiar a URL e a chave pública do projeto.
4. Configurar `SUPABASE_URL` e `SUPABASE_KEY` no `.env`.
5. Preparar a estrutura de autorização administrativa no PostgreSQL.
6. Criar usuários de teste.
7. Autorizar os usuários administrativos conforme a estrutura utilizada pela aplicação.

> A estrutura da tabela de administradores deve ser compatível com as consultas realizadas pelo código do projeto.

### Redis

Para execução local no Windows com WSL, é necessário ter o Redis instalado na distribuição Linux.

Iniciar o serviço:

```bash
sudo service redis-server start
```

Verificar:

```bash
redis-cli ping
```

O sistema utiliza Redis para o cache de produtos visualizados recentemente.

---

<a id="instalacao-e-execucao"></a>
## 🚀 Instalação e Execução

### Pré-requisitos

- Python instalado.
- Git instalado.
- MongoDB Atlas configurado.
- Projeto Supabase configurado.
- Redis instalado.
- Conexão com a internet.

### 1. Clonar o Repositório

```bash
git clone https://github.com/Giovanepg/BebidaMix.git
cd BebidaMix
```

### 2. Criar o Ambiente Virtual

No Windows:

```powershell
python -m venv .venv
```

### 3. Ativar o Ambiente Virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

Caso a execução de scripts esteja bloqueada, utilize diretamente o executável Python do ambiente virtual.

### 4. Instalar as Dependências

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 5. Configurar o `.env`

Crie um arquivo `.env` na pasta principal utilizando `.env.example` como referência.

```dotenv
WHATSAPP_NUMERO=55DDDNÚMERO

MONGO_URI=mongodb+srv://USUARIO:SENHA@CLUSTER.mongodb.net/
MONGO_DB_NAME=BebidaMix

SUPABASE_URL=https://SEU_PROJETO.supabase.co
SUPABASE_KEY=SUA_CHAVE_PUBLICA

SECRET_KEY=SUA_CHAVE_SECRETA

FLASK_ENV=development
```

As credenciais devem corresponder aos serviços configurados para o ambiente.

### 6. Iniciar o Redis

No WSL:

```bash
sudo service redis-server start
redis-cli ping
```

Resultado esperado:

```text
PONG
```

### 7. Executar a Aplicação

No PowerShell:

```powershell
.\.venv\Scripts\python.exe app.py
```

Acesse no navegador:

**http://127.0.0.1:5000/**

### 8. Testar as Conexões

MongoDB:

```powershell
.\.venv\Scripts\python.exe teste_mongodb.py
```

Supabase:

```powershell
.\.venv\Scripts\python.exe teste_supabase.py
```

Redis:

```powershell
.\.venv\Scripts\python.exe teste_redis.py
```

Esses scripts auxiliam na verificação das conexões com os serviços utilizados.

---

<a id="seguranca"></a>
## 🔒 Segurança

O BebidaMix utiliza medidas de proteção como:

- Autenticação por meio do Supabase.
- Restrição de acesso ao módulo administrativo.
- Gerenciamento de sessões no Flask.
- Variáveis de ambiente para credenciais.
- Arquivo `.gitignore` para evitar o versionamento de arquivos privados.
- Validação dos produtos e quantidades no backend.
- Consulta dos preços oficiais no MongoDB durante a finalização.
- Identificação de tentativas para reduzir a duplicação de pedidos.

> O projeto possui finalidade acadêmica. Uma implantação comercial exigiria medidas adicionais de segurança, infraestrutura e adequação à legislação aplicável.

---

<a id="entrega-academica"></a>
## 🎓 Entrega Acadêmica

O BebidaMix foi desenvolvido como projeto acadêmico da disciplina de **Banco de Dados**, com foco na utilização de persistência poliglota.

### Requisitos da Entrega

Para validação do trabalho na Plataforma A, devem ser apresentados:

**1. Repositório do Projeto**

🔗 [GitHub — BebidaMix](https://github.com/Giovanepg/BebidaMix)

O repositório apresenta o código-fonte, as configurações de exemplo e as instruções de execução e integração dos bancos.

**2. Vídeo Demonstrativo**

Gravação de tela com duração obrigatória de **5 a 10 minutos**, demonstrando:

- O sistema em execução.
- As funcionalidades do cliente e do administrador.
- As operações de persistência no MongoDB.
- A autenticação e as permissões no Supabase/PostgreSQL.
- O funcionamento do cache no Redis.
- A integração entre os três bancos e a aplicação Flask.

**🎥 Link do vídeo:** Em breve.

### Critério Principal da Demonstração

A apresentação prioriza a comprovação prática da integração entre a aplicação e os bancos de dados, demonstrando os efeitos das operações realizadas pelo usuário sobre os dados armazenados.

---

<a id="autor"></a>
## 👨‍💻 Autor

**Giovane**

Projeto acadêmico desenvolvido com Python, Flask, MongoDB Atlas, Supabase/PostgreSQL e Redis.

---

<a id="status-do-projeto"></a>
## ✅ Status do Projeto

**Funcionalidades principais implementadas e testadas localmente.**

- [x] Catálogo público de bebidas.
- [x] CRUD administrativo de produtos.
- [x] Integração com MongoDB Atlas.
- [x] Autenticação com Supabase.
- [x] Controle de permissões administrativas.
- [x] Integração com Redis.
- [x] Cache de produtos visualizados recentemente.
- [x] Carrinho de compras.
- [x] Controle de estoque.
- [x] Registro de pedidos.
- [x] Finalização pelo WhatsApp.
- [x] Versionamento com Git e GitHub.
- [ ] Adicionar capturas de tela ao README.
- [ ] Publicar vídeo demonstrativo de 5 a 10 minutos.

---

**🍻 BebidaMix — Aplicando Banco de Dados Poliglota em um sistema web de comércio eletrônico.**
