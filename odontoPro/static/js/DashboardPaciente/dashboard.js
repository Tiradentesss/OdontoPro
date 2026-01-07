/* ================= MENU LATERAL ================= */
function alternarMenu() {
    document.getElementById("menuLateral").classList.toggle("fechado");
}

/* ================= TROCAR DE TELA ================= */
function mostrarTela(id, btn) {
    const telas = document.querySelectorAll(".tela");
    const itens = document.querySelectorAll(".item-menu");

    telas.forEach(t => t.classList.remove("ativa"));
    document.getElementById(id).classList.add("ativa");

    itens.forEach(i => i.classList.remove("ativo"));
    if (btn) btn.classList.add("ativo");

    // sobe pro topo quando troca
    document.querySelector(".area-conteudo").scrollTo({ top: 0, behavior: "smooth" });
}

/* ================= CARROSSEL + BUSCA ================= */
document.addEventListener("DOMContentLoaded", () => {
    const inputBusca = document.getElementById("inputBuscaClinica");

    if (inputBusca) {
        inputBusca.addEventListener("input", function () {
            const termo = this.value.toLowerCase();
            document.querySelectorAll(".card-clinica").forEach(card => {
                const nome = card.querySelector("h3").textContent.toLowerCase();
                card.style.display = nome.includes(termo) ? "flex" : "none";
            });
        });
    }

    carrosselAutomatico();
});

let indice = 0;
function carrosselAutomatico() {
    const slides = document.getElementsByClassName("slide-carrossel");
    const pontos = document.getElementsByClassName("ponto");

    if (!slides.length) return;

    for (let i = 0; i < slides.length; i++) slides[i].style.display = "none";
    indice++;
    if (indice > slides.length) indice = 1;

    for (let i = 0; i < pontos.length; i++)
        pontos[i].className = pontos[i].className.replace(" ativo", "");

    slides[indice - 1].style.display = "block";
    if (pontos[indice - 1]) pontos[indice - 1].classList.add("ativo");

    setTimeout(carrosselAutomatico, 5000);
}

/* ================= MODAL DE CONSULTAS ================= */
function abrirDetalhes(id) {
    const modal = document.getElementById("modal-" + id);
    if (modal) modal.classList.add("mostrar");
}

function fecharDetalhes(id) {
    const modal = document.getElementById("modal-" + id);
    if (modal) modal.classList.remove("mostrar");
}

/* ================= POPUPS DE AGENDAMENTO ================= */
document.addEventListener("DOMContentLoaded", function () {
    const btnAbrir = document.getElementById("btn-abrir-agendamento");
    const modal1 = document.getElementById("modal-agendamento-1");
    const modal2 = document.getElementById("modal-agendamento-2");
    const modalSucesso = document.getElementById("modal-sucesso");

    if (btnAbrir) btnAbrir.onclick = () => modal1.style.display = "flex";

    window.proximaEtapa = () => {
        modal1.style.display = "none";
        modal2.style.display = "flex";
    };

    window.confirmarAgendamento = () => {
        modal2.style.display = "none";
        modalSucesso.style.display = "flex";
    };

    window.onclick = function (event) {
        if (event.target.className === "modal") event.target.style.display = "none";
    };
});

function irParaMeusAgendamentos() {
    document.querySelectorAll(".tela").forEach(t => t.style.display = "none");
    document.getElementById("consultas").style.display = "block";
}

/* ================= LOGOUT ================= */
const btnLogout = document.getElementById("btnLogout");
if (btnLogout) {
    btnLogout.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "../../Login_e_Cadastro/html/login.html";
    });
}

/* ================= FILTROS DAS CONSULTAS ================= */
document.addEventListener("DOMContentLoaded", function () {
    const botoesFiltro = document.querySelectorAll(".filtro-btn");
    const cards = document.querySelectorAll(".card-agendamento");

    botoesFiltro.forEach(botao => {
        botao.addEventListener("click", () => {

            botoesFiltro.forEach(b => b.classList.remove("ativo"));
            botao.classList.add("ativo");

            const filtro = botao.dataset.filtro;

            cards.forEach(card => {
                const status = card.dataset.status;
                card.style.display =
                    (filtro === "todas" || filtro === status) ? "block" : "none";
            });
        });
    });
});
