
// ========================================
// BEBIDAMIX - DETALHES DO PRODUTO
// ========================================

// Elementos da página
const produto = document.getElementById("produto-detalhes");

const btnMenos = document.getElementById("detalhes-menos");
const btnMais = document.getElementById("detalhes-mais");
const btnAdicionar = document.getElementById("adicionar-detalhes");

const qtdTexto = document.getElementById("detalhes-qtd");
const mensagem = document.getElementById("mensagem-detalhes");

// Informações da bebida
const id = produto.dataset.id;
const nome = produto.dataset.nome;
const preco = Number(produto.dataset.preco);
const estoque = Number(produto.dataset.estoque);

// Quantidade selecionada
let quantidade = estoque > 0 ? 1 : 0;


// ========================================
// DIMINUIR QUANTIDADE
// ========================================

btnMenos.addEventListener("click", () => {

    if (quantidade > 1) {
        quantidade--;
        qtdTexto.textContent = quantidade;
    }

});


// ========================================
// AUMENTAR QUANTIDADE
// ========================================

btnMais.addEventListener("click", () => {

    if (quantidade < estoque) {
        quantidade++;
        qtdTexto.textContent = quantidade;
    }

});


// ========================================
// ADICIONAR AO CARRINHO
// ========================================

btnAdicionar.addEventListener("click", () => {

    if (estoque <= 0) {
        mensagem.textContent = "Produto esgotado.";
        return;
    }

    // Recuperar carrinho salvo
    let carrinho = [];

    try {
        const salvo = JSON.parse(
            localStorage.getItem("bebidamix_carrinho")
        );

        if (Array.isArray(salvo)) {
            carrinho = salvo;
        }

    } catch (erro) {
        mensagem.textContent = "Erro ao recuperar o carrinho.";
        return;
    }

    // Procurar produto no carrinho
    let item = carrinho.find(p => p.id === id);

    // Quantidade já adicionada
    const atual = item ? Number(item.quantidade) : 0;

    // Validar estoque
    if (atual + quantidade > estoque) {
        mensagem.textContent = "Estoque insuficiente!";
        return;
    }

    // Atualizar produto existente
    if (item) {

        item.quantidade = atual + quantidade;
        item.nome = nome;
        item.preco = preco;
        item.estoque = estoque;

    } else {

        // Adicionar novo produto
        carrinho.push({
            id: id,
            nome: nome,
            preco: preco,
            quantidade: quantidade,
            estoque: estoque
        });

    }

    // Salvar o carrinho
    try {

        localStorage.setItem(
            "bebidamix_carrinho",
            JSON.stringify(carrinho)
        );

    } catch (erro) {

        mensagem.textContent =
            "Não foi possível salvar o carrinho.";

        return;
    }

    // Voltar ao catálogo com o carrinho aberto
    window.location.href = "/?abrir_carrinho=1";

});
