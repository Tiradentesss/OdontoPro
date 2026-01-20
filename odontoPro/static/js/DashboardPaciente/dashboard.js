/* ================= VARIÁVEIS GLOBAIS ================= */
let filtroEstrelasSelecionado = 0;

/* ================= MENU LATERAL ================= */
function alternarMenu() {
    document.getElementById("menuLateral").classList.toggle("aberto");
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
    inicializarFiltrosConsultas();
    
    // Inicializar filtros de clínicas
    initFiltroEstrelas("btnFiltro", "dropdownFiltro");
    initFiltroLocalizacao("btnFiltroLocalizacao", "dropdownFiltroLocalizacao");
    
    // Fechar modais ao clicar fora
    inicializarFechoDeModais();
    
    // Adicionar listener para carregamento de horários quando data é selecionada
    const inputData = document.getElementById('inputData');
    if (inputData) {
        inputData.addEventListener('change', function() {
            if (this.value && clinicaSelecionada) {
                carregarHorarios(clinicaSelecionada, this.value);
            }
        });
    }
    
    // Adicionar listener para validação de email em tempo real
    const emailInput = document.getElementById('inputEmail');
    if (emailInput) {
        emailInput.addEventListener('blur', validarCampoEmail);
    }
    
    // Listener para resize - readjustar dropdowns se necessário
    window.addEventListener("resize", () => {
        const dropdownAtivoAval = document.getElementById("dropdownFiltro");
        const dropdownAtivoLoc = document.getElementById("dropdownFiltroLocalizacao");
        
        if (dropdownAtivoAval && dropdownAtivoAval.classList.contains("mostrar")) {
            ajustarPosicaoDropdown(dropdownAtivoAval, document.getElementById("btnFiltro"));
        }
        
        if (dropdownAtivoLoc && dropdownAtivoLoc.classList.contains("mostrar")) {
            ajustarPosicaoDropdown(dropdownAtivoLoc, document.getElementById("btnFiltroLocalizacao"));
        }
    });
});

/* ================= FUNÇÃO PARA AJUSTAR POSIÇÃO DO DROPDOWN ================= */
function ajustarPosicaoDropdown(dropdown, botao) {
    // Aguardar um pouco para garantir que o dropdown está renderizado com display:flex
    setTimeout(() => {
        const botaoRect = botao.getBoundingClientRect();
        const dropdownRect = dropdown.getBoundingClientRect();
        const parent = botao.parentElement;
        
        // Reset para calcular corretamente
        dropdown.style.left = "0";
        dropdown.style.right = "auto";
        dropdown.style.top = "calc(100% + 5px)";
        dropdown.style.bottom = "auto";
        
        // Recalcular após reset
        const newDropdownRect = dropdown.getBoundingClientRect();
        
        // Verificar se sai da tela à direita
        if (newDropdownRect.right > window.innerWidth - 15) {
            dropdown.style.left = "auto";
            dropdown.style.right = "0";
        } else {
            dropdown.style.left = "0";
        }
        
        // Verificar se sai da tela para baixo
        const finalDropdownRect = dropdown.getBoundingClientRect();
        if (finalDropdownRect.bottom > window.innerHeight - 60) {
            dropdown.style.top = "auto";
            dropdown.style.bottom = "calc(100% + 5px)";
        } else {
            dropdown.style.top = "calc(100% + 5px)";
            dropdown.style.bottom = "auto";
        }
    }, 50);
}

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
    console.log('Abrindo detalhes para ID:', id);
    const modal = document.getElementById("modal-" + id);
    if (modal) {
        modal.classList.add("mostrar");
    } else {
        console.log('Modal não encontrado para ID:', id);
    }
}

function fecharDetalhes(id) {
    const modal = document.getElementById("modal-" + id);
    if (modal) modal.classList.remove("mostrar");
}

/* ================= AGENDAMENTO ================= */
let clinicaSelecionada = null;

function abrirModalAgendamento(clinicaId) {
    clinicaSelecionada = clinicaId;
    mostrarTela('perfil-clinica', null);
    carregarPerfilClinica(clinicaId);
    carregarMedicosClinica(clinicaId);
}

/* Função para abrir o modal de agendamento na página de perfil da clínica */
function abrirModalAgendamentoClinica() {
    const modal = document.getElementById('modal-agendamento-1');
    if (modal) {
        modal.classList.add('mostrar');
    }
}

/* Função para fechar modais ao clicar fora deles */
function inicializarFechoDeModais() {
    const modaisAgendamento = document.querySelectorAll('#modal-agendamento-1, #modal-agendamento-2, #modal-sucesso');
    
    modaisAgendamento.forEach(modal => {
        modal.addEventListener('click', function(event) {
            // Fecha o modal apenas se clicou no fundo (não no conteúdo)
            if (event.target === modal) {
                fecharModalAgendamento();
            }
        });
    });
}

/* ================= UPLOAD DE FOTO ================= */
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

/* ================= UPLOAD DE FOTO ================= */
const fileInput = document.getElementById("fileInput");
const preview = document.getElementById("previewFoto");
const container = document.querySelector(".upload-foto-container");

// Apenas um listener para fileInput
if (fileInput) {
    fileInput.addEventListener("change", function (e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();

        reader.onload = () => {
            if (preview) {
                preview.src = reader.result;
                preview.style.display = "block";
            }
            if (container) {
                container.classList.add("has-image");
            }
        };

        reader.readAsDataURL(file);
    });
}

/* ================= FILTRO DE ESTRELAS ================= */
function initFiltroEstrelas(btnId, dropdownId) {
    const btnFiltro = document.getElementById(btnId);
    const dropdown = document.getElementById(dropdownId);
    const opcoes = dropdown ? dropdown.querySelectorAll(".opcao") : [];
    const listaClinicas = document.getElementById("listaClinicas");

    if (!btnFiltro || !dropdown) return; // segurança

    btnFiltro.addEventListener("click", (e) => {
        e.stopPropagation(); // impede o clique de fechar imediatamente
        
        // Fechar o outro dropdown
        const outroDropdown = document.getElementById("dropdownFiltroLocalizacao");
        if (outroDropdown) {
            outroDropdown.classList.remove("mostrar");
        }
        
        dropdown.classList.toggle("mostrar");
        
        // Ajustar posição do dropdown se necessário
        if (dropdown.classList.contains("mostrar")) {
            setTimeout(() => ajustarPosicaoDropdown(dropdown, btnFiltro), 0);
        }
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
            
            // Atualizar texto do botão - mantendo as estrelas douradas da opção
            const textoOpcao = opcao.textContent.trim();
            btnFiltro.innerHTML = `${textoOpcao} <i class="fa-solid fa-chevron-down"></i>`;
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

    if (!btnFiltro || !dropdown || !selectEstado || !selectCidade) return;

    // Obter lista de estados únicos das clínicas
    const estados = new Set();
    const cidades = new Map(); // Map de estado -> Set de cidades

    const cards = listaClinicas ? listaClinicas.querySelectorAll(".card-clinica") : [];
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
    if (btnLimpar) {
        btnLimpar.addEventListener("click", () => {
            selectEstado.value = "";
            selectCidade.value = "";
            selectCidade.innerHTML = '<option value="">Todas as cidades</option>';
            aplicarFiltros();
        });
    }

    // Toggle dropdown
    btnFiltro.addEventListener("click", (e) => {
        e.stopPropagation();
        
        // Fechar o outro dropdown
        const outroDropdown = document.getElementById("dropdownFiltro");
        if (outroDropdown) {
            outroDropdown.classList.remove("mostrar");
        }
        
        dropdown.classList.toggle("mostrar");
        
        // Ajustar posição do dropdown se necessário
        if (dropdown.classList.contains("mostrar")) {
            setTimeout(() => ajustarPosicaoDropdown(dropdown, btnFiltro), 0);
        }
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
    
    // Obter filtros com verificação de nulidade
    const filtroEstrelas = parseInt(obterFiltroEstrelas()) || 0;
    const selectEstado = document.getElementById("selectEstado");
    const selectCidade = document.getElementById("selectCidade");
    
    const filtroEstado = selectEstado ? (selectEstado.value || "") : "";
    const filtroCidade = selectCidade ? (selectCidade.value || "") : "";
    
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
    
    const comentarioInput = document.getElementById(`comentario-${consultaId}`);
    const comentario = comentarioInput ? comentarioInput.value : "";
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

/* ================= UPLOAD DE FOTO ================= */
document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("fileInput");
    const preview = document.getElementById("previewFoto");
    const container = document.querySelector(".upload-foto-container");

    if (fileInput) {
        fileInput.addEventListener("change", function (e) {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();

            reader.onload = () => {
                preview.src = reader.result;
                if (container) {
                    container.classList.add("has-image");
                }
            };

            reader.readAsDataURL(file);
        });
    }
});

/* ================= PERFIL DA CLÍNICA ================= */
function carregarPerfilClinica(clinicaId) {
    // Função para carregar dados da clínica dinamicamente
    console.log('Perfil da clínica carregado:', clinicaId);
    
    // Buscar o card da clínica para preencher informações
    const clinicaCard = document.querySelector(`[data-clinica-id="${clinicaId}"]`);
    if (clinicaCard) {
        const nome = clinicaCard.querySelector("h3")?.textContent || "Clínica";
        const endereco = clinicaCard.getAttribute("data-endereco") || "Endereço não disponível";
        const telefone = clinicaCard.getAttribute("data-telefone") || "Telefone não disponível";
        
        // Atualizar as informações no perfil (se houver elementos)
        const nomeElemento = document.querySelector("#perfil-clinica .nome-clinica");
        const enderecoElemento = document.querySelector("#perfil-clinica .endereco-clinica");
        const telefoneElemento = document.querySelector("#perfil-clinica .telefone-clinica");
        
        if (nomeElemento) nomeElemento.textContent = nome;
        if (enderecoElemento) enderecoElemento.textContent = endereco;
        if (telefoneElemento) telefoneElemento.textContent = telefone;
    }
}

function carregarMedicosClinica(clinicaId) {
    // Buscar médicos da clínica via AJAX
    fetch(`/clinica/${clinicaId}/detalhes/`)
        .then(response => response.json())
        .then(data => {
            const listaMedicos = document.getElementById('lista-medicos');
            if (!listaMedicos) return;
            
            listaMedicos.innerHTML = ''; // Limpar lista anterior
            
            if (data.medicos && data.medicos.length > 0) {
                data.medicos.forEach(medico => {
                    const medicoCard = document.createElement('div');
                    medicoCard.style.cssText = 'background: #f9f9f9; padding: 15px; border-radius: 8px; text-align: center;';
                    medicoCard.innerHTML = `
                        <div style="font-size: 3rem; margin-bottom: 10px;"><i class="fa-solid fa-user-doctor"></i></div>
                        <h4>${medico[1]}</h4>
                        <p style="font-size: 0.9rem; color: #666;">ID: ${medico[0]}</p>
                    `;
                    listaMedicos.appendChild(medicoCard);
                });
            } else {
                listaMedicos.innerHTML = '<p>Nenhum médico cadastrado nesta clínica.</p>';
            }
        })
        .catch(error => {
            console.error('Erro ao carregar médicos:', error);
            const listaMedicos = document.getElementById('lista-medicos');
            if (listaMedicos) {
                listaMedicos.innerHTML = '<p>Erro ao carregar médicos.</p>';
            }
        });
}

function carregarEspecialidadesEMedicos(clinicaId) {
    // Buscar especialidades e médicos da clínica via AJAX
    fetch(`/clinica/${clinicaId}/detalhes/`)
        .then(response => response.json())
        .then(data => {
            // Preencher especialidades
            const selectEspecialidade = document.getElementById('selectEspecialidade');
            if (selectEspecialidade && data.especialidades) {
                selectEspecialidade.innerHTML = '<option value="">Selecione uma Especialidade</option>';
                data.especialidades.forEach(esp => {
                    const option = document.createElement('option');
                    option.value = esp[0]; // ID
                    option.textContent = esp[1]; // Nome
                    selectEspecialidade.appendChild(option);
                });
            }
            
            // Preencher médicos
            const selectProfissional = document.getElementById('selectProfissional');
            if (selectProfissional && data.medicos) {
                selectProfissional.innerHTML = '<option value="">Escolha um Profissional</option>';
                data.medicos.forEach(medico => {
                    const option = document.createElement('option');
                    option.value = medico[0]; // ID
                    option.textContent = medico[1]; // Nome
                    selectProfissional.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Erro ao carregar especialidades e médicos:', error);
            alert('Erro ao carregar dados. Tente novamente.');
        });
}

function carregarHorarios(clinicaId, data) {
    // Buscar horários disponíveis da clínica para a data selecionada
    fetch(`/clinica/${clinicaId}/horarios/?data=${data}`)
        .then(response => response.json())
        .then(data => {
            const selectHorario = document.getElementById('selectHorario');
            if (!selectHorario) return;
            
            selectHorario.innerHTML = '<option value="">Selecione o Horário</option>';
            
            if (data.horarios && data.horarios.length > 0) {
                data.horarios.forEach(horario => {
                    const option = document.createElement('option');
                    option.value = horario;
                    option.textContent = horario;
                    selectHorario.appendChild(option);
                });
            } else {
                const option = document.createElement('option');
                option.disabled = true;
                option.textContent = 'Nenhum horário disponível';
                selectHorario.appendChild(option);
            }
        })
        .catch(error => {
            console.error('Erro ao carregar horários:', error);
            const selectHorario = document.getElementById('selectHorario');
            if (selectHorario) {
                selectHorario.innerHTML = '<option value="">Erro ao carregar horários</option>';
            }
        });
}

function trocarAbaClinica(event, abaId) {
    // Remove classe ativa de todos os botões e conteúdos
    document.querySelectorAll('.abas-perfil .aba-item').forEach(btn => btn.classList.remove('ativa'));
    document.querySelectorAll('.aba-conteudo').forEach(content => content.classList.remove('ativa'));

    // Ativa o botão clicado
    event.currentTarget.classList.add('ativa');

    // Ativa o conteúdo correspondente
    const abaConteudo = document.getElementById(`aba-${abaId}`);
    if (abaConteudo) {
        abaConteudo.classList.add('ativa');
    }
}

/* ================= VOLTAR PARA INÍCIO ================= */
function voltarParaInicio() {
    mostrarTela('inicio', document.querySelector(".item-menu"));
}

/* ================= FUNÇÕES DE AGENDAMENTO ================= */

/* Função para validar email */
function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/* Função para validar campo de email em tempo real */
function validarCampoEmail() {
    const emailInput = document.getElementById('inputEmail');
    const emailError = document.getElementById('emailError');
    const email = emailInput.value.trim();
    
    if (email && !validarEmail(email)) {
        emailError.style.display = 'block';
        emailInput.style.borderColor = '#e74c3c';
    } else {
        emailError.style.display = 'none';
        emailInput.style.borderColor = '';
    }
}

function proximaEtapa() {
    // Validar campos obrigatórios do primeiro modal
    const nomeInput = document.getElementById('inputNome');
    const emailInput = document.getElementById('inputEmail');
    const telefoneInput = document.getElementById('inputTelefone');
    const genero = document.querySelector('input[name="gender"]:checked');
    const idade = document.querySelector('input[name="age"]:checked');
    
    if (!nomeInput || !emailInput || !telefoneInput) {
        alert('Erro ao acessar formulário. Recarregue a página.');
        return;
    }
    
    const nome = nomeInput.value.trim();
    const email = emailInput.value.trim();
    const telefone = telefoneInput.value.trim();
    
    if (!nome) {
        alert('Por favor, digite seu nome completo.');
        return;
    }
    
    if (!email || !validarEmail(email)) {
        alert('Por favor, digite um email válido (exemplo: usuario@email.com).');
        return;
    }
    
    if (!telefone || telefone.length < 10) {
        alert('Por favor, digite um telefone válido.');
        return;
    }
    
    if (!genero) {
        alert('Por favor, selecione um gênero.');
        return;
    }
    
    if (!idade) {
        alert('Por favor, selecione uma faixa etária.');
        return;
    }
    
    // Se validação passou, prosseguir
    const modal1 = document.getElementById('modal-agendamento-1');
    const modal2 = document.getElementById('modal-agendamento-2');
    
    if (modal1) modal1.classList.remove('mostrar');
    if (modal2) modal2.classList.add('mostrar');
    
    // Carregar especialidades e médicos da clínica selecionada
    carregarEspecialidadesEMedicos(clinicaSelecionada);
}

function confirmarAgendamento() {
    // Validar campos do segundo modal
    const selectEspecialidade = document.getElementById('selectEspecialidade');
    const selectProfissional = document.getElementById('selectProfissional');
    const inputData = document.getElementById('inputData');
    const selectHorario = document.getElementById('selectHorario');
    const inputNome = document.getElementById('inputNome');
    const inputEmail = document.getElementById('inputEmail');
    const inputTelefone = document.getElementById('inputTelefone');
    
    if (!selectEspecialidade || !selectProfissional || !inputData || !selectHorario) {
        alert('Erro ao acessar formulário. Recarregue a página.');
        return;
    }
    
    const especialidade = selectEspecialidade.value;
    const medico_id = selectProfissional.value;
    const data = inputData.value;
    const horario = selectHorario.value;
    const nome = inputNome?.value || '';
    const email = inputEmail?.value || '';
    const telefone = inputTelefone?.value || '';
    
    if (!especialidade) {
        alert('Por favor, selecione uma especialidade.');
        return;
    }
    
    if (!medico_id) {
        alert('Por favor, selecione um profissional.');
        return;
    }
    
    if (!data) {
        alert('Por favor, selecione uma data.');
        return;
    }
    
    if (!horario) {
        alert('Por favor, selecione um horário.');
        return;
    }
    
    // Combinar data e horário em formato ISO 8601
    const data_hora = `${data}T${horario}:00`;
    
    // Preparar dados para envio
    const formData = new FormData();
    formData.append('clinica_id', clinicaSelecionada);
    formData.append('medico_id', medico_id);
    formData.append('especialidade', especialidade);
    formData.append('data_hora', data_hora);
    formData.append('nome', nome);
    formData.append('email', email);
    formData.append('telefone', telefone);
    
    // Enviar para servidor
    fetch('/consulta/agendar/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Se agendamento foi bem-sucedido, mostrar sucesso
            const modal2 = document.getElementById('modal-agendamento-2');
            const modalSucesso = document.getElementById('modal-sucesso');
            
            if (modal2) modal2.classList.remove('mostrar');
            if (modalSucesso) modalSucesso.classList.add('mostrar');
            
            // Recarregar página após 2 segundos para atualizar a lista de consultas
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            alert('Erro ao agendar: ' + (data.error || 'Erro desconhecido'));
        }
    })
    .catch(error => {
        console.error('Erro ao enviar agendamento:', error);
        alert('Erro ao agendar consulta. Tente novamente.');
    });
}

/* Funções para fechar os modais */
function fecharModalAgendamento() {
    const modal1 = document.getElementById('modal-agendamento-1');
    const modal2 = document.getElementById('modal-agendamento-2');
    const modalSucesso = document.getElementById('modal-sucesso');
    
    if (modal1) modal1.classList.remove('mostrar');
    if (modal2) modal2.classList.remove('mostrar');
    if (modalSucesso) modalSucesso.classList.remove('mostrar');
    
    // Resetar formulário
    limparFormularioAgendamento();
}

/* Função para limpar o formulário de agendamento */
function limparFormularioAgendamento() {
    const campos = [
        'inputNome', 'inputEmail', 'inputTelefone', 'inputSintomas',
        'selectEspecialidade', 'selectProfissional', 'inputData', 'selectHorario'
    ];
    
    campos.forEach(id => {
        const campo = document.getElementById(id);
        if (campo) campo.value = '';
    });
    
    // Limpar radio buttons
    document.querySelectorAll('input[name="gender"]').forEach(r => r.checked = false);
    document.querySelectorAll('input[name="age"]').forEach(r => r.checked = false);
}

/* ================= IR PARA MEUS AGENDAMENTOS ================= */
function irParaMeusAgendamentos() {
    mostrarTela('consultas', document.querySelectorAll(".item-menu")[1]);
    fecharModalAgendamento();
}