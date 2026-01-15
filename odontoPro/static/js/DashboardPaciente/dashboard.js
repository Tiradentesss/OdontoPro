/* ================= MENU LATERAL ================= */
function alternarMenu() {
    document.getElementById("menuLateral").classList.toggle("fechado");
}

/* ================= TROCAR DE TELA ================= */
function mostrarTela(id, btn) {
    document.querySelectorAll(".tela").forEach(t => {
        t.classList.remove("ativa");
        t.style.display = "none";
    });

    document.querySelectorAll(".item-menu").forEach(i => i.classList.remove("ativo"));

    const tela = document.getElementById(id);
    if (tela) {
        tela.classList.add("ativa");
        tela.style.display = "block";
        if (btn) btn.classList.add("ativo");
        window.scrollTo({ top: 0, behavior: "smooth" });
        const area = document.querySelector(".area-conteudo");
        if (area) area.scrollTo({ top: 0, behavior: "smooth" });
    }
}

/* ================= BUSCA + CARROSSEL ================= */
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
    inicializarDataHorario();
    inicializarFiltrosConsultas();
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
        pontos[i].classList.remove("ativo");

    slides[indice - 1].style.display = "block";
    if (pontos[indice - 1]) pontos[indice - 1].classList.add("ativo");

    setTimeout(carrosselAutomatico, 5000);
}

/* ================= MODAL DE DETALHES ================= */
function abrirDetalhes(id) {
    const modal = document.getElementById("modal-" + id);
    if (modal) {
        modal.style.display = "flex";
        
        // Fechar quando clicar fora do modal
        modal.onclick = function(event) {
            if (event.target === modal) {
                fecharDetalhes(id);
            }
        }
    } else {
        console.error("Modal não encontrado: modal-" + id);
    }
}

function fecharDetalhes(id) {
    const modal = document.getElementById("modal-" + id);
    if (modal) {
        modal.style.display = "none";
    }
}

/* ================= AGENDAMENTO ================= */
let clinicaSelecionada = null;

function abrirModalAgendamento(clinicaId) {
    clinicaSelecionada = clinicaId;

    const modal1 = document.getElementById("modal-agendamento-1");
    const modal2 = document.getElementById("modal-agendamento-2");

    modal1.style.display = "flex";
    modal2.style.display = "none";

    const selectEspecialidade = modal2.querySelector("select:nth-of-type(1)");
    const selectMedico = modal2.querySelector("select:nth-of-type(2)");
    const horarioSelect = document.getElementById("horarioConsulta");

    selectEspecialidade.innerHTML = `<option value="">Selecione uma Especialidade</option>`;
    selectMedico.innerHTML = `<option value="">Escolha um Profissional</option>`;
    horarioSelect.innerHTML = `<option value="">Selecione o Horário</option>`;

    fetch(`/clinica/${clinicaId}/detalhes/`)
        .then(res => res.json())
        .then(data => {
            data.especialidades.forEach(e => {
                selectEspecialidade.innerHTML +=
                    `<option value="${e[1]}">${e[1]}</option>`;
            });

            data.medicos.forEach(m => {
                selectMedico.innerHTML +=
                    `<option value="${m[0]}">${m[1]}</option>`;
            });
        });
}

function proximaEtapa() {
    document.getElementById("modal-agendamento-1").style.display = "none";
    document.getElementById("modal-agendamento-2").style.display = "flex";
}

/* ================= DATA → HORÁRIOS ================= */
function inicializarDataHorario() {
    const dataInput = document.getElementById("dataConsulta");
    const horarioSelect = document.getElementById("horarioConsulta");

    if (!dataInput || !horarioSelect) return;

    dataInput.addEventListener("change", () => {
        horarioSelect.innerHTML = `<option>Carregando horários...</option>`;

        fetch(`/clinica/${clinicaSelecionada}/horarios/?data=${dataInput.value}`)
            .then(res => res.json())
            .then(data => {
                horarioSelect.innerHTML = `<option value="">Selecione o Horário</option>`;
                if (!data.horarios || !data.horarios.length) {
                    horarioSelect.innerHTML = `<option value="">Sem horários disponíveis</option>`;
                    return;
                }
                data.horarios.forEach(h => {
                    horarioSelect.innerHTML += `<option value="${h}">${h}</option>`;
                });
            });
    });
}

/* ================= CONFIRMAR ================= */
function confirmarAgendamento() {
    const modal2 = document.getElementById("modal-agendamento-2");

    const nomeInput = document.querySelector("#modal-agendamento-1 input[type='text']");
    const emailInput = document.querySelector("#modal-agendamento-1 input[type='email']");
    const telInput = document.querySelector("#modal-agendamento-1 input[type='tel']");

    const especialidade = modal2.querySelector("select:nth-of-type(1)").value;
    const medico = modal2.querySelector("select:nth-of-type(2)").value;
    const data = document.getElementById("dataConsulta").value;
    const hora = document.getElementById("horarioConsulta").value;
    const observacoes = document.querySelector("#modal-agendamento-1 textarea").value;

    if (!medico || !data || !hora) {
        alert("Preencha todos os campos obrigatórios");
        return;
    }

    const body = {
        clinica_id: clinicaSelecionada,
        medico_id: medico,
        especialidade,
        data_hora: `${data} ${hora}`,
        observacoes
    };

    if (nomeInput && emailInput && telInput) {
        body.nome = nomeInput.value;
        body.email = emailInput.value;
        body.telefone = telInput.value;
    }

    fetch("/consulta/agendar/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: new URLSearchParams(body)
    })
    .then(res => res.json())
    .then(res => {
        if (res.success) {
            modal2.style.display = "none";
            document.getElementById("modal-sucesso").style.display = "flex";
        } else {
            alert(res.error || "Erro ao agendar consulta");
        }
    });
}

/* ================= CONSULTAS ================= */
function irParaMeusAgendamentos() {
    const modal = document.getElementById("modal-sucesso");
    if (modal) modal.style.display = "none";
    mostrarTela("consultas", document.querySelectorAll(".item-menu")[1]);
}

/* ================= FILTROS ================= */
function inicializarFiltrosConsultas() {
    const botoes = document.querySelectorAll(".filtro-btn");
    const cards = document.querySelectorAll(".card-agendamento");

    botoes.forEach(btn => {
        btn.addEventListener("click", () => {
            botoes.forEach(b => b.classList.remove("ativo"));
            btn.classList.add("ativo");

            const filtro = btn.dataset.filtro;
            cards.forEach(card => {
                const status = card.dataset.status;
                card.style.display =
                    filtro === "todas" || filtro === status ? "block" : "none";
            });
        });
    });
}

/* ================= CSRF ================= */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie) {
        document.cookie.split(";").forEach(c => {
            c = c.trim();
            if (c.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(c.substring(name.length + 1));
            }
        });
    }
    return cookieValue;
}

/* ================= LOGOUT ================= */
const btnLogout = document.getElementById("btnLogout");
if (btnLogout) {
    btnLogout.addEventListener("click", e => {
        e.preventDefault();
        window.location.href = "../../Login_e_Cadastro/html/login.html";
    });
}

/* ================= CONFIGURAÇÕES / ABAS ================= */
function trocarAba(event, abaId) {
    // Esconde todos os conteúdos das abas
    document.querySelectorAll('.conteudo-aba').forEach(aba => {
        aba.classList.remove('ativa');
        aba.style.display = 'none';
    });

    // Remove classe ativa dos botões
    document.querySelectorAll('.aba-item').forEach(btn => {
        btn.classList.remove('ativa');
    });

    // Mostra a aba selecionada (ID JÁ VEM CORRETO)
    const abaAtiva = document.getElementById(abaId);
    if (abaAtiva) {
        abaAtiva.style.display = 'block'; // ou 'flex' se o layout exigir
        abaAtiva.classList.add('ativa');
    }

    // Ativa o botão clicado
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('ativa');
    }
}

document.getElementById("fileInput").addEventListener("change", function (e) {
    const file = e.target.files[0];
    if (!file) return;

    const img = document.getElementById("previewFoto");
    img.src = URL.createObjectURL(file);
    img.style.display = "block";
});

const fileInput = document.getElementById("fileInput");
const preview = document.getElementById("previewFoto");
const container = document.querySelector(".upload-foto-container");

fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];

    if (file) {
        const reader = new FileReader();

        reader.onload = () => {
            preview.src = reader.result;
            container.classList.add("has-image");
        };

        reader.readAsDataURL(file);
    }
});
