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
    
    // Inicializar filtros de clínicas
    initFiltroEstrelas("btnFiltro", "dropdownFiltro");
    initFiltroLocalizacao("btnFiltroLocalizacao", "dropdownFiltroLocalizacao");
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
    if (modal) modal.classList.add("mostrar");
}

function fecharDetalhes(id) {
    const modal = document.getElementById("modal-" + id);
    if (modal) modal.classList.remove("mostrar");
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

/* ================= FILTRO DE ESTRELAS ================= */
let filtroEstrelasSelecionado = 0; // Armazenar filtro selecionado

function initFiltroEstrelas(btnId, dropdownId) {
    const btnFiltro = document.getElementById(btnId);
    const dropdown = document.getElementById(dropdownId);
    const opcoes = dropdown.querySelectorAll(".opcao");
    const listaClinicas = document.getElementById("listaClinicas");

    if (!btnFiltro || !dropdown) return; // segurança

    btnFiltro.addEventListener("click", (e) => {
        e.stopPropagation(); // impede o clique de fechar imediatamente
        dropdown.classList.toggle("mostrar");
    });

    // Adicionar evento click em cada opção de estrelas
    opcoes.forEach((opcao, index) => {
        const estrelas = index + 1; // 1 a 5 estrelas
        
        opcao.style.cursor = "pointer";
        opcao.addEventListener("click", (e) => {
            e.stopPropagation();
            
            console.log(`Filtro de ${estrelas} estrelas selecionado`);
            
            // Armazenar filtro selecionado
            filtroEstrelasSelecionado = estrelas;
            
            // Filtrar clínicas
            aplicarFiltros();
            
            // Fechar dropdown
            dropdown.classList.remove("mostrar");
            
            // Atualizar texto do botão
            const textoOpcao = opcao.textContent.trim();
            btnFiltro.innerHTML = `<i class="fa-solid fa-star"></i> ${textoOpcao} <i class="fa-solid fa-chevron-down"></i>`;
        });
    });

    // Fechar dropdown ao clicar fora
    document.addEventListener("click", (e) => {
        if (!dropdown.contains(e.target) && e.target !== btnFiltro) {
            dropdown.classList.remove("mostrar");
        }
    });
    
    // Adicionar opção "Limpar filtro" (opcional)
    const opcaoLimpar = document.createElement("div");
    opcaoLimpar.className = "opcao";
    opcaoLimpar.textContent = "✕ Limpar filtro";
    opcaoLimpar.style.cursor = "pointer";
    opcaoLimpar.style.color = "#666";
    opcaoLimpar.style.borderTop = "1px solid #ddd";
    opcaoLimpar.style.paddingTop = "8px";
    opcaoLimpar.style.marginTop = "8px";
    
    opcaoLimpar.addEventListener("click", (e) => {
        e.stopPropagation();
        
        console.log("Filtro de estrelas limpo");
        
        // Resetar filtro
        filtroEstrelasSelecionado = 0;
        
        // Resetar texto do botão
        btnFiltro.innerHTML = `<i class="fa-solid fa-star"></i> Avaliação <i class="fa-solid fa-chevron-down"></i>`;
        
        // Aplicar filtros (agora sem filtro de estrelas)
        aplicarFiltros();
        
        // Fechar dropdown
        dropdown.classList.remove("mostrar");
    });
    
    dropdown.appendChild(opcaoLimpar);
}

/* ================= FILTRO DE LOCALIZAÇÃO ================= */
function initFiltroLocalizacao(btnId, dropdownId) {
    const btnFiltro = document.getElementById(btnId);
    const dropdown = document.getElementById(dropdownId);
    const selectEstado = document.getElementById("selectEstado");
    const selectCidade = document.getElementById("selectCidade");
    const btnLimpar = document.getElementById("btnLimparFiltroLocalizacao");
    const listaClinicas = document.getElementById("listaClinicas");

    if (!btnFiltro || !dropdown) return;

    // Obter lista de estados únicos das clínicas
    const estados = new Set();
    const cidades = new Map(); // Map de estado -> Set de cidades

    const cards = listaClinicas.querySelectorAll(".card-clinica");
    cards.forEach(card => {
        const estado = card.getAttribute("data-estado") || "";
        const cidade = card.getAttribute("data-cidade") || "";
        
        if (estado) {
            estados.add(estado);
            if (!cidades.has(estado)) {
                cidades.set(estado, new Set());
            }
            if (cidade) {
                cidades.get(estado).add(cidade);
            }
        }
    });

    // Ordenar e popular select de estados
    const estadosOrdenados = Array.from(estados).sort();
    estadosOrdenados.forEach(estado => {
        const option = document.createElement("option");
        option.value = estado;
        option.textContent = estado;
        selectEstado.appendChild(option);
    });

    // Evento ao mudar estado
    selectEstado.addEventListener("change", () => {
        const estadoSelecionado = selectEstado.value;
        
        // Limpar cidades
        selectCidade.innerHTML = '<option value="">Todas as cidades</option>';
        
        // Poblar cidades do estado selecionado
        if (estadoSelecionado && cidades.has(estadoSelecionado)) {
            const cidadesDoEstado = Array.from(cidades.get(estadoSelecionado)).sort();
            cidadesDoEstado.forEach(cidade => {
                const option = document.createElement("option");
                option.value = cidade;
                option.textContent = cidade;
                selectCidade.appendChild(option);
            });
        }
        
        aplicarFiltros();
    });

    // Evento ao mudar cidade
    selectCidade.addEventListener("change", () => {
        aplicarFiltros();
    });

    // Evento de botão limpar
    btnLimpar.addEventListener("click", () => {
        selectEstado.value = "";
        selectCidade.value = "";
        selectCidade.innerHTML = '<option value="">Todas as cidades</option>';
        aplicarFiltros();
    });

    // Toggle dropdown
    btnFiltro.addEventListener("click", (e) => {
        e.stopPropagation();
        dropdown.classList.toggle("mostrar");
    });

    // Fechar dropdown ao clicar fora
    document.addEventListener("click", (e) => {
        if (!dropdown.contains(e.target) && e.target !== btnFiltro) {
            dropdown.classList.remove("mostrar");
        }
    });
}

/* ================= FUNÇÃO PARA APLICAR TODOS OS FILTROS ================= */
function aplicarFiltros() {
    const cards = document.querySelectorAll(".card-clinica");
    
    // Obter filtros
    const filtroEstrelas = parseInt(obterFiltroEstrelas()) || 0;
    const filtroEstado = document.getElementById("selectEstado").value || "";
    const filtroCidade = document.getElementById("selectCidade").value || "";
    
    console.log(`Aplicando filtros: estrelas=${filtroEstrelas}, estado=${filtroEstado}, cidade=${filtroCidade}`);
    
    cards.forEach(card => {
        const avaliacao = parseFloat(card.getAttribute("data-avaliacao") || 0);
        const estado = card.getAttribute("data-estado") || "";
        const cidade = card.getAttribute("data-cidade") || "";
        
        let mostrar = true;
        
        // Filtro de estrelas
        if (filtroEstrelas > 0 && avaliacao < filtroEstrelas) {
            mostrar = false;
        }
        
        // Filtro de estado
        if (filtroEstado && estado !== filtroEstado) {
            mostrar = false;
        }
        
        // Filtro de cidade
        if (filtroCidade && cidade !== filtroCidade) {
            mostrar = false;
        }
        
        card.style.display = mostrar ? "flex" : "none";
    });
}

/* ================= FUNÇÃO AUXILIAR PARA OBTER FILTRO DE ESTRELAS ================= */
function obterFiltroEstrelas() {
    // Usar a variável global em vez de tentar parsear o texto do botão
    return filtroEstrelasSelecionado;
}

/* ================= AVALIAÇÃO ================= */
let avaliacoesSelecionadas = {}; // Armazenar avaliação por consulta

function mostrarEstrelas(consultaId, clinicaId, medicoId) {
    console.log(`Mostrando estrelas para consulta ${consultaId}`);
    const secao = document.getElementById(`avaliacao-${consultaId}`);
    if (secao) {
        secao.style.display = "block";
        // Scroll suave para a seção
        secao.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } else {
        console.error(`Seção de avaliação não encontrada: avaliacao-${consultaId}`);
    }
}

function ocultarEstrelas(consultaId) {
    const secao = document.getElementById(`avaliacao-${consultaId}`);
    if (secao) {
        secao.style.display = "none";
        // Limpar seleção
        document.querySelectorAll(`#avaliacao-${consultaId} .star`).forEach(star => {
            star.classList.remove("selecionada");
        });
        delete avaliacoesSelecionadas[consultaId];
    }
}

function selecionarEstrela(elemento, consultaId) {
    const valor = parseInt(elemento.getAttribute("data-valor"));
    console.log(`Estrela ${valor} selecionada para consulta ${consultaId}`);
    avaliacoesSelecionadas[consultaId] = valor;
    
    // Remove seleção anterior
    document.querySelectorAll(`#avaliacao-${consultaId} .star`).forEach(star => {
        star.classList.remove("selecionada");
    });
    
    // Seleciona até o valor clicado
    const secao = document.getElementById(`avaliacao-${consultaId}`);
    if (secao) {
        const stars = secao.querySelectorAll(".star");
        for (let i = 0; i < valor; i++) {
            stars[i].classList.add("selecionada");
        }
    }
}

function enviarAvaliacao(consultaId, clinicaId, medicoId) {
    console.log(`Enviando avaliação para consulta ${consultaId}, clínica ${clinicaId}, médico ${medicoId}`);
    console.log(`Avaliações selecionadas:`, avaliacoesSelecionadas);
    
    const nota = avaliacoesSelecionadas[consultaId];
    
    if (!nota || nota === 0) {
        alert("Por favor, selecione uma classificação em estrelas!");
        return;
    }
    
    const comentario = document.getElementById(`comentario-${consultaId}`).value;
    const csrfToken = getCookie("csrftoken");
    
    console.log(`Enviando: nota=${nota}, comentário=${comentario}, csrf=${csrfToken}`);
    
    // Fazer requisição para enviar avaliação
    fetch("/avaliacao/criar/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrfToken
        },
        body: new URLSearchParams({
            consulta_id: consultaId,
            clinica_id: clinicaId,
            medico_id: medicoId,
            nota: nota,
            comentario: comentario
        })
    })
    .then(res => {
        console.log("Resposta recebida, status:", res.status);
        return res.json();
    })
    .then(data => {
        console.log("Dados da resposta:", data);
        if (data.success) {
            alert("Avaliação enviada com sucesso!");
            ocultarEstrelas(consultaId);
            // Desabilitar botão de avaliação
            const btnAvaliar = document.querySelector(`button.btn-avaliar[onclick*="mostrarEstrelas('${consultaId}"]`);
            if (btnAvaliar) {
                btnAvaliar.disabled = true;
                btnAvaliar.textContent = "✅ Avaliado";
                btnAvaliar.style.opacity = "0.6";
            }
        } else {
            alert(data.message || "Erro ao enviar avaliação");
        }
    })
    .catch(err => {
        console.error("Erro na requisição:", err);
        alert("Erro ao enviar avaliação! Verifique o console.");
    });
}