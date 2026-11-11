
 // ========================================
 // BEBIDAMIX - CARRINHO DE COMPRAS
 // Catálogo público; login só ao finalizar
 // ========================================

 let categoriaAtual = "Todas";
 let carrinho = [];
 let tempoNotificacao;
 let finalizandoPedido = false;

 const CHAVE_CARRINHO = "bebidamix_carrinho";
 const CHAVE_TENTATIVA = "bebidamix_tentativa_pedido";
 const CHAVE_REABRIR = "bebidamix_reabrir_carrinho";

 // Recuperar carrinho salvo, inclusive após cadastro ou login
 try {
     const salvo = JSON.parse(localStorage.getItem(CHAVE_CARRINHO));
     if (Array.isArray(salvo)) carrinho = salvo;
 } catch (erro) {
     console.warn("Não foi possível recuperar o carrinho.");
 }

 const painel = document.getElementById("painel-carrinho");
 const fundo = document.getElementById("fundo-carrinho");
 const listaCarrinho = document.getElementById("itens-carrinho");
 const contador = document.getElementById("contador-carrinho");
 const totalCarrinho = document.getElementById("total-carrinho");
 const finalizar = document.getElementById("finalizar-pedido");

 function formatarMoeda(valor) {
     return Number(valor).toLocaleString("pt-BR", {
         style: "currency",
         currency: "BRL"
     });
 }

 function salvarCarrinho() {
     try {
         localStorage.setItem(CHAVE_CARRINHO, JSON.stringify(carrinho));
     } catch (erro) {
         console.warn("Não foi possível salvar o carrinho.");
     }
 }

 function notificar(mensagem) {
     const aviso = document.getElementById("notificacao");
     if (!aviso) return;
     aviso.textContent = mensagem;
     aviso.classList.add("visivel");
     clearTimeout(tempoNotificacao);
     tempoNotificacao = setTimeout(() => aviso.classList.remove("visivel"), 3000);
 }

 function abrirCarrinho() {
     painel.classList.add("ativo");
     fundo.classList.add("ativo");
     document.body.style.overflow = "hidden";
 }

 function fecharCarrinho() {
     painel.classList.remove("ativo");
     fundo.classList.remove("ativo");
     document.body.style.overflow = "";
 }

 document.getElementById("abrir-carrinho").addEventListener("click", abrirCarrinho);
 document.getElementById("fechar-carrinho").addEventListener("click", fecharCarrinho);
 document.getElementById("continuar-comprando").addEventListener("click", fecharCarrinho);
 fundo.addEventListener("click", fecharCarrinho);
 document.addEventListener("keydown", evento => {
     if (evento.key === "Escape") fecharCarrinho();
 });

 // A mesma combinação de produtos e quantidades gera a mesma assinatura
 function assinaturaCarrinho(itens) {
     const resumo = itens.map(item => ({
         id: String(item.id),
         quantidade: Number(item.quantidade)
     }));
     resumo.sort((a, b) => a.id.localeCompare(b.id));
     return JSON.stringify(resumo);
 }

 function lerTentativaPedido() {
     try {
         const tentativa = JSON.parse(localStorage.getItem(CHAVE_TENTATIVA));
         if (tentativa && typeof tentativa === "object") return tentativa;
     } catch (erro) {
         console.warn("Tentativa de pedido inválida.");
     }
     return null;
 }

 function obterChavePedido(itens) {
     const assinatura = assinaturaCarrinho(itens);
     const tentativa = lerTentativaPedido();

     if (tentativa && tentativa.assinatura === assinatura &&
         typeof tentativa.chave === "string") {
         return tentativa.chave;
     }

     const chave = crypto.randomUUID();
     localStorage.setItem(CHAVE_TENTATIVA, JSON.stringify({
         chave,
         assinatura,
         pedido_id: null,
         registrado: false
     }));
     return chave;
 }

 function marcarPedidoRegistrado(itens, dados) {
     const tentativa = lerTentativaPedido();
     if (!tentativa || tentativa.assinatura !== assinaturaCarrinho(itens)) return;
     tentativa.pedido_id = dados.pedido_id;
     tentativa.registrado = true;
     try {
         localStorage.setItem(CHAVE_TENTATIVA, JSON.stringify(tentativa));
     } catch (erro) {
         console.warn("Não foi possível salvar a tentativa do pedido.");
     }
 }

 function prepararNovaCompra() {
     if (carrinho.length !== 0) return;
     const tentativa = lerTentativaPedido();
     if (tentativa && tentativa.registrado === true) {
         localStorage.removeItem(CHAVE_TENTATIVA);
     }
 }

 // Opção para iniciar nova compra mantendo os itens do carrinho
 const botaoNovoPedido = document.createElement("button");
 botaoNovoPedido.id = "novo-pedido";
 botaoNovoPedido.type = "button";
 botaoNovoPedido.className = "btn-continuar";
 botaoNovoPedido.textContent = "Iniciar novo pedido";
 botaoNovoPedido.style.display = "none";
 botaoNovoPedido.style.marginTop = "10px";
 botaoNovoPedido.style.width = "100%";
 finalizar.insertAdjacentElement("afterend", botaoNovoPedido);

 function atualizarBotaoNovoPedido() {
     const tentativa = lerTentativaPedido();
     const itens = carrinho.map(item => ({ id: item.id, quantidade: item.quantidade }));
     const mesmoCarrinho = tentativa &&
         tentativa.assinatura === assinaturaCarrinho(itens);
     botaoNovoPedido.style.display = (
         carrinho.length > 0 && mesmoCarrinho && tentativa.registrado === true
     ) ? "block" : "none";
 }

 botaoNovoPedido.addEventListener("click", () => {
     if (finalizandoPedido) return;
     if (!window.confirm(
         "Deseja iniciar uma nova compra? Os produtos permanecerão no carrinho."
     )) return;
     try {
         localStorage.removeItem(CHAVE_TENTATIVA);
         atualizarBotaoNovoPedido();
         notificar("Nova compra iniciada!");
     } catch (erro) {
         notificar("Não foi possível iniciar um novo pedido.");
     }
 });

 // ========================================
 // CARDS DE PRODUTOS
 // ========================================
 document.querySelectorAll(".card").forEach(card => {
     const btnMenos = card.querySelector(".btn-menos");
     const btnMais = card.querySelector(".btn-mais");
     const btnAdicionar = card.querySelector(".adicionar");
     const qtdTexto = card.querySelector(".qtd");
     const estoque = Number(card.dataset.estoque);
     let quantidade = estoque > 0 ? 1 : 0;

     if (estoque <= 0) {
         btnMenos.disabled = true;
         btnMais.disabled = true;
         btnAdicionar.disabled = true;
         qtdTexto.textContent = "0";
     }

     btnMenos.addEventListener("click", () => {
         if (quantidade > 1) {
             quantidade--;
             qtdTexto.textContent = quantidade;
         }
     });

     btnMais.addEventListener("click", () => {
         if (quantidade < estoque) {
             quantidade++;
             qtdTexto.textContent = quantidade;
         }
     });

     btnAdicionar.addEventListener("click", () => {
         if (finalizandoPedido) return;

         const id = card.dataset.id;
         const nome = card.dataset.nome;
         const preco = Number(card.dataset.preco);
         const item = carrinho.find(p => p.id === id);
         const atual = item ? item.quantidade : 0;

         if (atual + quantidade > estoque) {
             notificar("Estoque insuficiente!");
             return;
         }

         prepararNovaCompra();

         if (item) {
             item.quantidade += quantidade;
             item.nome = nome;
             item.preco = preco;
             item.estoque = estoque;
         } else {
             carrinho.push({ id, nome, preco, quantidade, estoque });
         }

         salvarCarrinho();
         atualizarCarrinho();
         notificar(nome + " adicionado ao carrinho!");
     });
 });

 function alterarItem(id, valor) {
     if (finalizandoPedido) return;
     const item = carrinho.find(p => p.id === id);
     if (!item) return;
     const novaQuantidade = item.quantidade + valor;

     if (novaQuantidade > item.estoque) {
         notificar("Estoque insuficiente!");
         return;
     }
     if (novaQuantidade <= 0) {
         removerItem(id);
         return;
     }
     item.quantidade = novaQuantidade;
     salvarCarrinho();
     atualizarCarrinho();
 }

 function removerItem(id) {
     if (finalizandoPedido) return;
     carrinho = carrinho.filter(item => item.id !== id);
     salvarCarrinho();
     atualizarCarrinho();
     notificar("Produto removido do carrinho.");
 }

 // ========================================
 // DESENHAR CARRINHO
 // ========================================
 function atualizarCarrinho() {
     listaCarrinho.innerHTML = "";
     let quantidadeTotal = 0;
     let valorTotalCentavos = 0;

     if (carrinho.length === 0) {
         const vazio = document.createElement("p");
         vazio.className = "carrinho-vazio";
         vazio.textContent = "Seu carrinho está vazio.";
         listaCarrinho.appendChild(vazio);
     }

     carrinho.forEach(item => {
         quantidadeTotal += item.quantidade;
         const precoCentavos = Math.round(item.preco * 100);
         const subtotalCentavos = precoCentavos * item.quantidade;
         valorTotalCentavos += subtotalCentavos;

         const div = document.createElement("div");
         div.className = "item-carrinho";

         const nome = document.createElement("h3");
         nome.textContent = item.nome;

         const preco = document.createElement("p");
         preco.textContent = formatarMoeda(item.preco) + " / un.";

         const subtotal = document.createElement("strong");
         subtotal.textContent = formatarMoeda(subtotalCentavos / 100);

         const acoes = document.createElement("div");
         acoes.className = "item-acoes";
         const controle = document.createElement("div");
         controle.className = "item-quantidade";

         const menos = document.createElement("button");
         menos.type = "button";
         menos.textContent = "−";
         menos.setAttribute("aria-label", "Diminuir quantidade");
         menos.addEventListener("click", () => alterarItem(item.id, -1));

         const qtd = document.createElement("span");
         qtd.textContent = item.quantidade;

         const mais = document.createElement("button");
         mais.type = "button";
         mais.textContent = "+";
         mais.setAttribute("aria-label", "Aumentar quantidade");
         mais.addEventListener("click", () => alterarItem(item.id, 1));

         const remover = document.createElement("button");
         remover.type = "button";
         remover.className = "btn-remover";
         remover.textContent = "Remover";
         remover.addEventListener("click", () => removerItem(item.id));

         controle.append(menos, qtd, mais);
         acoes.append(controle, remover);
         div.append(nome, preco, subtotal, acoes);
         listaCarrinho.appendChild(div);
     });

     contador.textContent = quantidadeTotal;
     totalCarrinho.textContent = formatarMoeda(valorTotalCentavos / 100);
     finalizar.disabled = carrinho.length === 0 || finalizandoPedido;
     atualizarBotaoNovoPedido();
 }

 // ========================================
 // PESQUISA E FILTROS
 // ========================================
 function filtrarCategoria(categoria) {
     categoriaAtual = categoria;
     filtrarProdutos();
 }

 document.querySelectorAll("[data-filtro]").forEach(botao => {
     botao.addEventListener("click", () => filtrarCategoria(botao.dataset.filtro));
 });

 function filtrarProdutos() {
     const texto = document.getElementById("busca").value.toLowerCase().trim();
     document.querySelectorAll(".card").forEach(card => {
         const nome = card.dataset.nome.toLowerCase();
         const categoria = card.dataset.categoria;
         const combinaNome = nome.includes(texto);
         const combinaCategoria = categoriaAtual === "Todas" || categoria === categoriaAtual;
         card.style.display = combinaNome && combinaCategoria ? "" : "none";
     });
 }

 document.getElementById("busca").addEventListener("input", filtrarProdutos);

 // ========================================
 // FINALIZAR PELO WHATSAPP
 // ========================================
 finalizar.addEventListener("click", async () => {
     if (finalizandoPedido) return;
     if (carrinho.length === 0) {
         notificar("Seu carrinho está vazio!");
         return;
     }

     const itens = carrinho.map(item => ({
         id: item.id,
         quantidade: item.quantidade
     }));

     finalizandoPedido = true;
     finalizar.disabled = true;
     finalizar.textContent = "Preparando pedido...";

     try {
         // A chave permanece guardada caso o cliente precise fazer login.
         const chavePedido = obterChavePedido(itens);
         const resposta = await fetch("/finalizar-pedido", {
             method: "POST",
             headers: { "Content-Type": "application/json" },
             credentials: "same-origin",
             body: JSON.stringify({
                 itens,
                 chave_pedido: chavePedido
             })
         });

         const dados = await resposta.json();

         // NOVO: visitante deve entrar antes de finalizar.
         // Nao esvaziar carrinho nem apagar chave de idempotencia.
         if (resposta.status === 401) {
             salvarCarrinho();
             sessionStorage.setItem(CHAVE_REABRIR, "1");
             window.location.assign("/entrar");
             return;
         }

         if (!resposta.ok) {
             notificar(dados.erro || "Erro ao finalizar pedido.");

             // Pedido anterior já confirmado/cancelado: permitir nova tentativa.
             if (resposta.status === 409 &&
                 typeof dados.erro === "string" &&
                 dados.erro.toLowerCase().includes("tentativa") &&
                 dados.erro.toLowerCase().includes("finalizada")) {
                 const tentativa = lerTentativaPedido();
                 if (tentativa && tentativa.chave === chavePedido) {
                     tentativa.registrado = true;
                     localStorage.setItem(CHAVE_TENTATIVA, JSON.stringify(tentativa));
                     atualizarBotaoNovoPedido();
                 }
             }
             return;
         }

         if (typeof dados.link !== "string" ||
             !dados.link.startsWith("https://wa.me/")) {
             notificar("O servidor não retornou um link válido do WhatsApp.");
             return;
         }

         marcarPedidoRegistrado(itens, dados);

         // Apenas depois de o servidor registrar o pedido.
         carrinho = [];
         salvarCarrinho();
         atualizarCarrinho();

         // O cliente ainda precisa ENVIAR a mensagem no WhatsApp.
         window.location.href = dados.link;

     } catch (erro) {
         console.error("Erro ao finalizar:", erro);
         notificar("Não foi possível finalizar o pedido. Tente novamente.");
     } finally {
         finalizandoPedido = false;
         finalizar.disabled = carrinho.length === 0;
         finalizar.textContent = "Finalizar pedido";
     }
 });

 // ========================================
 // INICIALIZAR CARRINHO
 // ========================================
 atualizarCarrinho();

 // Abrir carrinho depois de voltar de uma página de detalhes
 const parametros = new URLSearchParams(window.location.search);
 if (parametros.get("abrir_carrinho") === "1") {
     abrirCarrinho();
     window.history.replaceState({}, "", window.location.pathname);
 }

 // NOVO: reabrir carrinho após cadastro/login, se necessário
 if (sessionStorage.getItem(CHAVE_REABRIR) === "1") {
     sessionStorage.removeItem(CHAVE_REABRIR);
     if (carrinho.length > 0) {
         abrirCarrinho();
         notificar("Seu carrinho foi preservado. Finalize o pedido quando quiser.");
     }
 }

 // Ao sair da conta explicitamente, limpar dados do navegador.
 // Nao executar esta limpeza quando o visitante for redirecionado ao login.
 const formularioSair = document.querySelector(".form-sair-cliente");
 if (formularioSair) {
     formularioSair.addEventListener("submit", () => {
         localStorage.removeItem(CHAVE_CARRINHO);
         localStorage.removeItem(CHAVE_TENTATIVA);
         sessionStorage.removeItem(CHAVE_REABRIR);
     });
 }

 console.log("Carrinho BebidaMix funcionando!");
