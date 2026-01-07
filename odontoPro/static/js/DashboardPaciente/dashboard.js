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
let clinicaSelecionada = null;

function abrirModalAgendamento(clinicaId) {
    clinicaSelecionada = clinicaId;

    const modal1 = document.getElementById('modal-agendamento-1');
    const modal2 = document.getElementById('modal-agendamento-2');

    modal1.style.display = 'flex';
    modal2.style.display = 'none';

    // Limpa selects
    const selectEspecialidade = modal2.querySelector("select:nth-of-type(1)");
    const selectMedico = modal2.querySelector("select:nth-of-type(2)");
    selectEspecialidade.innerHTML = `<option>Selecione uma Especialidade</option>`;
    selectMedico.innerHTML = `<option>Escolha um Profissional</option>`;

    fetch(`/clinica/${clinicaId}/detalhes/`)
        .then(res => res.json())
        .then(data => {
            if (data.especialidades) {
                data.especialidades.forEach(e => {
                    let option = document.createElement("option");
                    option.value = e[0];
                    option.textContent = e[1];
                    selectEspecialidade.appendChild(option);
                });
            }
            if (data.medicos) {
                data.medicos.forEach(m => {
                    let option = document.createElement("option");
                    option.value = m[0];
                    option.textContent = m[1];
                    selectMedico.appendChild(option);
                });
            }
        });
}

function proximaEtapa() {
    document.getElementById('modal-agendamento-1').style.display = 'none';
    document.getElementById('modal-agendamento-2').style.display = 'flex';
}

function confirmarAgendamento() {
    const modal2 = document.getElementById('modal-agendamento-2');

    const nome = document.querySelector('#modal-agendamento-1 input[type="text"]').value;
    const email = document.querySelector('#modal-agendamento-1 input[type="email"]').value;
    const telefone = document.querySelector('#modal-agendamento-1 input[type="tel"]').value;
    const especialidadeSelect = modal2.querySelector("select:nth-of-type(1)");
    const medicoSelect = modal2.querySelector("select:nth-of-type(2)");
    const dataInput = modal2.querySelector("input[type='date']");
    const horarioSelect = modal2.querySelector("select:nth-of-type(3)");
    const observacoes = document.querySelector('#modal-agendamento-1 textarea').value;

    const especialidade = especialidadeSelect.value;
    const medico = medicoSelect.value;
    const data = dataInput.value;
    const hora = horarioSelect.value;

    if (!nome || !email || !telefone || !clinicaSelecionada || !especialidade || !medico || !data || !hora) {
        alert("Preencha todos os campos obrigatórios");
        return;
    }

    const data_hora = `${data} ${hora}`;

    fetch('/consulta/agendar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: new URLSearchParams({
            nome, email, telefone,
            clinica_id: clinicaSelecionada,
            medico_id: medico,
            especialidade,
            data_hora,
            observacoes
        })
    })
    .then(res => res.json())
    .then(res => {
        if (res.success) {
            modal2.style.display = 'none';
            document.getElementById('modal-sucesso').style.display = 'flex';
        } else {
            alert(res.error || "Erro ao agendar consulta.");
        }
    });
}

function irParaMeusAgendamentos() {
    document.getElementById('modal-sucesso').style.display = 'none';
    mostrarTela('consultas', document.querySelectorAll(".item-menu")[1]);
}

// Função para pegar cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let c of cookies) {
            c = c.trim();
            if (c.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(c.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
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
