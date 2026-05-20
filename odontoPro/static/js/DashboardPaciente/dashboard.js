/* ================= VARIÁVEIS GLOBAIS ================= */
let filtroEstrelasSelecionado = 0;

function aplicarTema(tema) {
    const body = document.body;
    body.classList.remove('theme-light', 'theme-dark');
    if (tema === 'dark') {
        body.classList.add('theme-dark');
    } else {
        body.classList.add('theme-light');
    }
    localStorage.setItem('dashboardTheme', tema);
    atualizarBotaoTema();
}

function definirTemaInicial() {
    const savedTheme = localStorage.getItem('dashboardTheme');
    const tema = savedTheme === 'dark' ? 'dark' : 'light';
    aplicarTema(tema);
    return tema;
}

function atualizarBotaoTema() {
    const botao = document.getElementById('btnToggleTheme');
    if (!botao) return;
    const isDark = document.body.classList.contains('theme-dark');
    botao.textContent = isDark ? 'Tema claro' : 'Tema escuro';
}

/* ================= FUNÇÃO PARA CARREGAR HORÁRIOS ================= */
function carregarHorariosHandler() {
    if (this.value && clinicaSelecionada) {
        carregarHorarios(clinicaSelecionada, this.value);
    }
}

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
                const nome = card.querySelector("h3")?.textContent?.toLowerCase() || "";
                const local = card.querySelector("p")?.textContent?.toLowerCase() || "";
                const matches = nome.includes(termo) || local.includes(termo);
                card.style.display = matches ? "flex" : "none";
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
    
    // Inicializar ações de cartão de consulta
    inicializarInteracaoCartoes();
    
    // Adicionar listener para carregamento de horários quando data é selecionada
    const inputData = document.getElementById('inputData');
    if (inputData) {
        // Remover listener anterior se existir
        inputData.removeEventListener('change', carregarHorariosHandler);
        // Adicionar novo listener
        inputData.addEventListener('change', carregarHorariosHandler);
    }
    
    // Adicionar listener para validação de email em tempo real
    const emailInput = document.getElementById('inputEmail');
    if (emailInput) {
        emailInput.addEventListener('blur', validarCampoEmail);
    }

    definirTemaInicial();
    const themeToggleButton = document.getElementById('btnToggleTheme');
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            const isDark = document.body.classList.contains('theme-dark');
            aplicarTema(isDark ? 'light' : 'dark');
        });
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

function inicializarInteracaoCartoes() {
    const grid = document.querySelector('.grid-agendamentos');
    if (!grid) return;

    grid.addEventListener('click', event => {
        const detalheBtn = event.target.closest('.btn-detalhes');
        if (detalheBtn) {
            abrirDetalhes(detalheBtn.dataset.consultaId);
            return;
        }

        const cancelarBtn = event.target.closest('.btn-cancelar-consulta');
        if (cancelarBtn) {
            confirmarCancelamentoConsulta(cancelarBtn.dataset.consultaId);
            return;
        }

        const avaliarBtn = event.target.closest('.btn-avaliar');
        if (avaliarBtn) {
            mostrarEstrelas(avaliarBtn.dataset.consultaId, avaliarBtn.dataset.clinicaId, avaliarBtn.dataset.medicoId);
            avaliarBtn.setAttribute('aria-expanded', 'true');
            return;
        }

        const enviarBtn = event.target.closest('.btn-enviar-avaliacao');
        if (enviarBtn) {
            enviarAvaliacao(enviarBtn.dataset.consultaId, enviarBtn.dataset.clinicaId, enviarBtn.dataset.medicoId);
            return;
        }

        const cancelarAvaliacaoBtn = event.target.closest('.btn-cancelar-avaliacao');
        if (cancelarAvaliacaoBtn) {
            ocultarEstrelas(cancelarAvaliacaoBtn.dataset.consultaId);
            return;
        }

        const starBtn = event.target.closest('.star');
        if (starBtn) {
            selecionarEstrela(starBtn, starBtn.dataset.consultaId);
            return;
        }
    });
}

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

// ===== CANCELAMENTO DE CONSULTA COM MODAL CUSTOMIZADO =====
let consultaIdParaCancelar = null;

function confirmarCancelamentoConsulta(consultaId) {
    consultaIdParaCancelar = consultaId;
    const modal = document.getElementById('modal-cancelar-consulta');
    if (modal) {
        modal.classList.add('mostrar');
        modal.style.display = 'flex';
    }
}

function fecharModalCancelar() {
    const modal = document.getElementById('modal-cancelar-consulta');
    if (modal) {
        modal.classList.remove('mostrar');
        modal.style.display = 'none';
    }
    consultaIdParaCancelar = null;
}

function confirmarCancelamento() {
    if (consultaIdParaCancelar) {
        cancelarConsulta(consultaIdParaCancelar);
        fecharModalCancelar();
    }
}

// ===== MODAL GENÉRICO PARA MENSAGENS =====
function mostrarMensagem(titulo, texto, tipo = 'info') {
    const modal = document.getElementById('modal-mensagem');
    const tituloEl = document.getElementById('modal-mensagem-titulo');
    const iconeEl = document.getElementById('modal-mensagem-icone');
    const textoEl = document.getElementById('modal-mensagem-texto');

    if (modal && tituloEl && iconeEl && textoEl) {
        tituloEl.textContent = titulo;
        textoEl.textContent = texto;

        // Define o ícone baseado no tipo
        switch (tipo) {
            case 'success':
                iconeEl.textContent = '✅';
                break;
            case 'error':
                iconeEl.textContent = '❌';
                break;
            case 'warning':
                iconeEl.textContent = '⚠️';
                break;
            default:
                iconeEl.textContent = 'ℹ️';
        }

        modal.classList.add('mostrar');
        modal.style.display = 'flex';
    }
}

function fecharModalMensagem() {
    const modal = document.getElementById('modal-mensagem');
    if (modal) {
        modal.classList.remove('mostrar');
        modal.style.display = 'none';
    }
}

// ===== MODAL DE CONFIRMAÇÃO DE LOGOUT =====
function mostrarConfirmacaoLogout() {
    const modal = document.getElementById('modal-logout');
    if (modal) {
        modal.classList.add('mostrar');
        modal.style.display = 'flex';
    }
}

function fecharModalLogout() {
    const modal = document.getElementById('modal-logout');
    if (modal) {
        modal.classList.remove('mostrar');
        modal.style.display = 'none';
    }
}

function confirmarLogout() {
    const formLogout = document.getElementById('formLogout');
    if (formLogout) {
        formLogout.submit();
    }
}

function cancelarConsulta(consultaId) {
    fetch(`/consulta/${consultaId}/cancelar/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            removerCardConsulta(consultaId);
            mostrarMensagem('Consulta Cancelada', data.message, 'success');
        } else {
            mostrarMensagem('Erro', 'Erro: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Erro ao cancelar consulta:', error);
        mostrarMensagem('Erro', 'Erro ao cancelar a consulta', 'error');
    });
}

function removerCardConsulta(consultaId) {
    const card = document.querySelector(`.card-agendamento[data-consulta-id="${consultaId}"]`);
    if (card) {
        const grid = card.closest('.grid-agendamentos');
        card.remove();
        if (grid && !grid.querySelector('.card-agendamento')) {
            const vazio = document.createElement('div');
            vazio.className = 'empty-consultas';
            vazio.textContent = 'Nenhuma consulta encontrada.';
            grid.appendChild(vazio);
        }
    }
}

// ===== REAGENDAMENTO EM TEMPO REAL =====
function abrirReagendamento(consultaId) {
    const modal = document.getElementById('modal-reagendar-consulta');
    const dateInput = document.getElementById('reagendar-data');
    const timeInput = document.getElementById('reagendar-hora');
    const card = document.querySelector(`.card-agendamento[data-consulta-id="${consultaId}"]`);
    if (card && card.dataset.hora) {
        const dt = new Date(card.dataset.hora);
        if (!isNaN(dt.getTime())) {
            dateInput.value = dt.toISOString().slice(0,10);
            timeInput.value = dt.toTimeString().slice(0,5);
        }
    }
    modal.dataset.consultaId = consultaId;
    modal.classList.add('mostrar');
    modal.style.display = 'flex';
}

function fecharModalReagendar() {
    const modal = document.getElementById('modal-reagendar-consulta');
    if (modal) {
        modal.classList.remove('mostrar');
        modal.style.display = 'none';
        delete modal.dataset.consultaId;
    }
}

function submitReagendamento() {
    const modal = document.getElementById('modal-reagendar-consulta');
    const consultaId = modal.dataset.consultaId;
    const date = document.getElementById('reagendar-data').value;
    const time = document.getElementById('reagendar-hora').value;
    if (!date || !time) {
        mostrarMensagem('Erro', 'Informe data e hora válidas', 'error');
        return;
    }
    const data_hora = `${date}T${time}:00`;
    const formData = new FormData();
    formData.append('data_hora', data_hora);

    fetch(`/consulta/${consultaId}/reagendar/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken()
        },
        body: formData,
        credentials: 'same-origin'
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            updateCardConsulta(consultaId, data.data_hora, data.status);
            fecharModalReagendar();
            mostrarMensagem('Consulta Reagendada', data.message, 'success');
        } else {
            mostrarMensagem('Erro', data.error || 'Erro ao reagendar', 'error');
        }
    })
    .catch(err => {
        console.error('Erro no reagendamento:', err);
        mostrarMensagem('Erro', 'Erro ao reagendar consulta', 'error');
    });
}

function updateCardConsulta(consultaId, isoDataHora, status) {
    const card = document.querySelector(`.card-agendamento[data-consulta-id="${consultaId}"]`);
    if (!card) return;
    card.dataset.hora = isoDataHora;
    const dt = new Date(isoDataHora);
    const dataStr = dt.toLocaleDateString('pt-BR', {day:'2-digit', month:'2-digit', year:'numeric'});
    const timeStr = dt.toTimeString().slice(0,5);
    const headerData = card.querySelector('.header-agendamento .data-consulta');
    if (headerData) headerData.innerHTML = `<i class="fa-regular fa-calendar"></i> ${dataStr}`;
    const horaText = card.querySelector('.hora-text');
    if (horaText) horaText.textContent = timeStr;
    const badge = card.querySelector('.status-badge');
    if (badge) {
        badge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        badge.className = 'status-badge ' + status;
    }
}

// Função auxiliar para pegar CSRF token
function getCsrfToken() {
    let csrfToken = null;
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim();
        if (c.startsWith('csrftoken=')) {
            csrfToken = c.substring('csrftoken='.length);
            break;
        }
    }
    // Se não encontrar no cookie, tentar no formulário
    if (!csrfToken) {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) {
            csrfToken = csrfInput.value;
        }
    }
    return csrfToken || '';
}

/* ================= AGENDAMENTO ================= */
let clinicaSelecionada = null;

function abrirModalAgendamento(clinicaId) {

    console.log("CLINICA CLICADA:", clinicaId);
    clinicaSelecionada = clinicaId;

    // Vai para tela perfil da clínica
    mostrarTela('perfil-clinica', null);

    // Carrega dados da clínica via Django
    fetch(`/clinica/${clinicaId}/detalhes/`)
        .then(response => response.json())
        .then(data => {

            if (data.error) {
                alert(data.error);
                return;
            }

            document.getElementById("detalheNomeClinica").innerText = data.nome;
            document.getElementById("detalheEmailClinica").innerText = data.email;
            document.getElementById("detalheTelefoneClinica").innerText = data.telefone;
            document.getElementById("detalheDescricaoClinica").innerText = data.descricao;

            document.getElementById("detalheEnderecoClinica").innerText =
                `${data.rua}, ${data.numero} - ${data.bairro}, ${data.cidade} - ${data.estado}, CEP: ${data.cep}`;

            const logoImg = document.getElementById("detalheLogoClinica");
            if (logoImg) {
                logoImg.onerror = function() {
                    this.onerror = null;
                    this.src = "/static/img/SemIcon.png";
                };

                if (data.logo_url) {
                    logoImg.src = data.logo_url;
                } else if (data.images && data.images.length > 0) {
                    logoImg.src = data.images[0];
                } else {
                    logoImg.src = "/static/img/SemIcon.png";
                }
            }

            atualizarEnderecoCarousel(data.images || [], data.banner_url || data.logo_url || "/static/img/default-banner.jpg");

            // ===== ESPECIALIDADES =====
            const selectEspecialidade = document.getElementById("selectEspecialidade");
            if (selectEspecialidade) {
                selectEspecialidade.innerHTML = "<option value=''>Selecione</option>";

                data.especialidades.forEach(function(esp) {
                    const option = document.createElement("option");
                    option.value = esp[0];
                    option.textContent = esp[1];
                    selectEspecialidade.appendChild(option);
                });

                selectEspecialidade.removeEventListener('change', atualizarMedicosPorEspecialidade);
                selectEspecialidade.addEventListener('change', atualizarMedicosPorEspecialidade);
            }

            // Preencher lista de serviços disponíveis com especialidades + número de médicos
            const detalheServicos = document.getElementById("detalheServicosClinica");
            if (detalheServicos) {
                detalheServicos.innerHTML = "";
                const medicosList = Array.isArray(data.medicos) ? data.medicos : [];
                const countsByEspecialidade = {};

                medicosList.forEach(function(medico) {
                    if (Array.isArray(medico.especialidades)) {
                        medico.especialidades.forEach(function(espId) {
                            const key = String(espId);
                            countsByEspecialidade[key] = (countsByEspecialidade[key] || 0) + 1;
                        });
                    }
                });

                if (Array.isArray(data.especialidades) && data.especialidades.length > 0) {
                    data.especialidades.forEach(function(esp) {
                        const espId = String(esp[0]);
                        const espNome = esp[1];
                        const espPreco = Number(esp[2] || 0);
                        const count = countsByEspecialidade[espId] || 0;
                        const item = document.createElement("li");
                        item.textContent = `${espNome} - R$ ${espPreco.toFixed(2).replace('.', ',')} (${count} médico${count === 1 ? "" : "s"})`;
                        detalheServicos.appendChild(item);
                    });
                } else {
                    detalheServicos.innerHTML = "<li>Nenhuma especialidade cadastrada.</li>";
                }
            }

            // Inicializar médicos e especialidades globais
            window.medicosClinica = data.medicos || [];
            window.especialidadesClinica = data.especialidades || [];
            atualizarMedicosPorEspecialidade();

            // ===== LISTA DE MÉDICOS (ABA PERFIL) =====
            const listaMedicos = document.getElementById("lista-medicos");

            if (listaMedicos) {
                listaMedicos.innerHTML = "";

                if (data.medicos.length === 0) {
                    listaMedicos.innerHTML = "<p>Nenhum médico cadastrado nesta clínica.</p>";
                } else {
                    data.medicos.forEach(function(med) {

                        const card = document.createElement("div");
                        card.className = "card-medico";
                        card.style.cssText = `
                            background: #f8fafc;
                            padding: 20px;
                            border-radius: 12px;
                            text-align: center;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                        `;

                        const foto = med.foto_url ? med.foto_url : "/static/img/SemIcon.png";

                        // Buscar nomes das especialidades
                        const especialidadesNomes = [];
                        if (med.especialidades && med.especialidades.length > 0) {
                            med.especialidades.forEach(espId => {
                                if (data.especialidades) {
                                    const esp = data.especialidades.find(e => e[0] === espId);
                                    if (esp) {
                                        especialidadesNomes.push(esp[1]);
                                    }
                                }
                            });
                        }

                        const especialidadesHtml = especialidadesNomes.length > 0 
                            ? `<p style="font-size: 12px; color: #666; margin-top: 5px;">${especialidadesNomes.join(", ")}</p>`
                            : '';

                        card.innerHTML = `
                            <img src="${foto}" 
                                style="width:80px;height:80px;border-radius:50%;object-fit:contain;margin-bottom:10px;" onerror="this.onerror=null;this.src='/static/img/SemIcon.png';">
                            <h4 style="margin-bottom: 5px;">Dr(a). ${med.nome}</h4>
                            ${especialidadesHtml}
                        `;

                        listaMedicos.appendChild(card);
                    });
                }
            }
            // ===== AVALIAÇÕES =====
            const listaAvaliacoes = document.getElementById("lista-avaliacoes");

            if (listaAvaliacoes) {
                listaAvaliacoes.innerHTML = "";

                if (data.avaliacoes && data.avaliacoes.length > 0) {
                    data.avaliacoes.forEach(function(av) {

                        const card = document.createElement("div");
                        card.className = "card-feedback";

                        // ⭐ Estrelas simples (SEM FontAwesome)
                        let estrelas = "";
                        for (let i = 1; i <= 5; i++) {
                            estrelas += i <= av.nota ? "★" : "☆";
                        }

                        card.innerHTML = `
                            <div class="linha-nomes">
                                <span class="nome-paciente">${av.paciente}</span>
                                <span class="separador"> - </span>
                                <span class="nome-medico">${av.medico}</span>
                            </div>

                            <div class="estrelas">${estrelas}</div>

                            ${av.comentario ? `<p>${av.comentario}</p>` : ""}
                            <small class="data-avaliacao">${av.data}</small>
                        `;

                        listaAvaliacoes.appendChild(card);
                    });
                } else {
                    listaAvaliacoes.innerHTML = "<p>Esta clínica ainda não possui avaliações.</p>";
                }
            }

        })
        .catch(error => {
            console.error("Erro ao carregar clínica:", error);
        });
}

function inicializarCarouselsDeClinica() {
    document.querySelectorAll('.card-clinica .banner-carousel').forEach(carousel => {
        const slides = Array.from(carousel.querySelectorAll('.banner-slide'));
        if (slides.length < 2) {
            const controls = carousel.querySelectorAll('.carousel-control');
            controls.forEach(control => control.style.display = 'none');
            return;
        }

        carousel.dataset.currentSlide = '0';
        const prev = carousel.querySelector('.carousel-control.prev');
        const next = carousel.querySelector('.carousel-control.next');

        const atualizarSlide = (index) => {
            const normalized = (index + slides.length) % slides.length;
            carousel.dataset.currentSlide = String(normalized);
            slides.forEach((slide, idx) => {
                slide.classList.toggle('active', idx === normalized);
            });
        };

        if (prev) {
            prev.addEventListener('click', () => {
                atualizarSlide(Number(carousel.dataset.currentSlide) - 1);
            });
        }
        if (next) {
            next.addEventListener('click', () => {
                atualizarSlide(Number(carousel.dataset.currentSlide) + 1);
            });
        }
    });
}

function atualizarEnderecoCarousel(images, fallback) {
    const carousel = document.getElementById('enderecoCarousel');
    if (!carousel) return;

    const slidesWrapper = carousel.querySelector('.endereco-slides');
    const prev = carousel.querySelector('.carousel-control.prev');
    const next = carousel.querySelector('.carousel-control.next');

    const fotos = Array.isArray(images) && images.length ? images : [fallback || '/static/img/default-banner.jpg'];

    slidesWrapper.innerHTML = '';
    fotos.forEach((url, index) => {
        const slide = document.createElement('div');
        slide.className = 'endereco-slide' + (index === 0 ? ' active' : '');
        slide.innerHTML = `<img src="${url}" alt="Imagem da clínica">`;
        slidesWrapper.appendChild(slide);
    });

    carousel.dataset.currentSlide = '0';
    if (fotos.length > 1) {
        prev.style.display = 'flex';
        next.style.display = 'flex';
    } else {
        prev.style.display = 'none';
        next.style.display = 'none';
    }

    const mudarSlide = (direction) => {
        const current = Number(carousel.dataset.currentSlide || 0);
        const nextIndex = (current + direction + fotos.length) % fotos.length;
        carousel.dataset.currentSlide = String(nextIndex);
        slidesWrapper.querySelectorAll('.endereco-slide').forEach((slide, idx) => {
            slide.classList.toggle('active', idx === nextIndex);
        });
    };

    prev.onclick = () => mudarSlide(-1);
    next.onclick = () => mudarSlide(1);
}


document.addEventListener('DOMContentLoaded', () => {
    inicializarCarouselsDeClinica();
});


/* Função para abrir o modal de agendamento na página de perfil da clínica */
function calcularIdade(dataNascimentoStr) {
    if (!dataNascimentoStr) return null;

    const hoje = new Date();
    const nasc = new Date(dataNascimentoStr);
    if (Number.isNaN(nasc.getTime())) return null;

    let idade = hoje.getFullYear() - nasc.getFullYear();
    const mes = hoje.getMonth() - nasc.getMonth();
    if (mes < 0 || (mes === 0 && hoje.getDate() < nasc.getDate())) {
        idade -= 1;
    }
    return idade;
}

function preencherFormularioAgendamentoComDadosUsuario() {
    const pacienteNome = document.getElementById('pacienteNome')?.value || '';
    const pacienteEmail = document.getElementById('pacienteEmail')?.value || '';
    const pacienteTelefone = document.getElementById('pacienteTelefone')?.value || '';
    const pacienteSexo = document.getElementById('pacienteSexo')?.value || '';
    const pacienteDataNascimento = document.getElementById('pacienteDataNascimento')?.value || '';

    const inputNome = document.getElementById('inputNome');
    const inputEmail = document.getElementById('inputEmail');
    const inputTelefone = document.getElementById('inputTelefone');

    if (inputNome) inputNome.value = pacienteNome;
    if (inputEmail) inputEmail.value = pacienteEmail;
    if (inputTelefone) inputTelefone.value = pacienteTelefone;

    // Gênero
    document.querySelectorAll('input[name="gender"]').forEach(r => {
        if (pacienteSexo && r.value.toLowerCase() === pacienteSexo.toLowerCase()) {
            r.checked = true;
        }
    });

    // Faixa etária (se tiver data_nascimento)
    const idade = calcularIdade(pacienteDataNascimento);
    if (idade !== null) {
        const radioAdulto = document.querySelector('input[name="age"][value="Adulto"]');
        const radioInfantil = document.querySelector('input[name="age"][value="Infantil"]');

        if (radioAdulto && radioInfantil) {
            if (idade >= 18) {
                radioAdulto.checked = true;
            } else {
                radioInfantil.checked = true;
            }
        }
    }
}

function abrirModalAgendamentoClinica() {
    preencherFormularioAgendamentoComDadosUsuario();

    const modal = document.getElementById('modal-agendamento-1');
    if (modal) {
        modal.classList.add('mostrar');
        modal.style.display = 'flex';
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
    const selectEspecialidade = document.getElementById("selectFiltroEspecialidade");
    const inputData = document.getElementById("inputFiltroData");
    const inputFiltroTexto = document.getElementById("inputFiltroTexto");

    const aplicarFiltrosConsultas = () => {
        const filtroStatus = document.querySelector(".filtro-btn.ativo")?.dataset.filtro || "todas";
        const especialidadeSelecionada = selectEspecialidade?.value || "";
        const dataSelecionada = inputData?.value || "";
        const pesquisa = inputFiltroTexto?.value.trim().toLowerCase() || "";

        const agora = new Date();

        cards.forEach(card => {
            const status = (card.dataset.status || "").toLowerCase();
            const especialidade = card.dataset.especialidade || "";
            const dataHora = card.dataset.hora || "";
            const dataConsulta = dataHora ? new Date(dataHora) : null;
            const textoCard = card.textContent.toLowerCase();
            const isPerdida = isConsultaPerdida(status, dataConsulta, agora);

            card.classList.toggle("perdida-card", isPerdida);

            const statusMatch = filtroStatus === "todas"
                || (filtroStatus === "perdidas" ? isPerdida : status === filtroStatus);

            const especialidadeMatch = !especialidadeSelecionada || especialidade === especialidadeSelecionada;
            const dataMatch = !dataSelecionada || (dataHora ? dataHora.startsWith(dataSelecionada) : false);
            const pesquisaMatch = !pesquisa || textoCard.includes(pesquisa);

            card.style.display = statusMatch && especialidadeMatch && dataMatch && pesquisaMatch ? "block" : "none";
        });
    };

    botoes.forEach(btn => {
        btn.addEventListener("click", () => {
            botoes.forEach(b => b.classList.remove("ativo"));
            btn.classList.add("ativo");
            aplicarFiltrosConsultas();
        });
    });

    if (selectEspecialidade) {
        selectEspecialidade.addEventListener("change", aplicarFiltrosConsultas);
    }

    if (inputData) {
        inputData.addEventListener("change", aplicarFiltrosConsultas);
    }

    if (inputFiltroTexto) {
        inputFiltroTexto.addEventListener("input", aplicarFiltrosConsultas);
    }

    aplicarFiltrosConsultas();
}

function isConsultaPerdida(status, dataConsulta, agora) {
    return status === "perdida";
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
document.addEventListener("DOMContentLoaded", () => {

    const btnLogout = document.getElementById("btnLogout");

    if (btnLogout) {
        btnLogout.addEventListener("click", e => {
            e.preventDefault();
            window.location.href = "../../Login_e_Cadastro/html/login.html";
        });
    }

});

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
        
        const estaAberto = dropdown.classList.toggle("mostrar");
        btnFiltro.classList.toggle("ativo", estaAberto);
        
        // Ajustar posição do dropdown se necessário
        if (estaAberto) {
            setTimeout(() => ajustarPosicaoDropdown(dropdown, btnFiltro), 0);
        }
    });

    // Adicionar evento click em cada opção de estrelas
    opcoes.forEach((opcao) => {
        const estrelas = parseInt(opcao.dataset.value, 10) || 0;
        
        opcao.style.cursor = "pointer";
        opcao.addEventListener("click", (e) => {
            e.stopPropagation();
            
            console.log(`Filtro de ${estrelas} estrelas selecionado`);
            
            // Armazenar filtro selecionado
            filtroEstrelasSelecionado = estrelas;
            
            // Atualizar opção selecionada
            opcoes.forEach(item => item.classList.remove("selecionada"));
            opcao.classList.add("selecionada");
            
            // Filtrar clínicas
            aplicarFiltros();
            
            // Fechar dropdown
            dropdown.classList.remove("mostrar");
            btnFiltro.classList.remove("ativo");
            
            // Atualizar texto do botão mantendo o layout novo
            const tituloFiltro = btnFiltro.querySelector("#tituloFiltro");
            if (tituloFiltro) {
                tituloFiltro.innerHTML = `<i class="fa-solid fa-star star-yellow"></i> ${estrelas} estrela${estrelas > 1 ? "s" : ""}`;
                // Repetir estrela para cada número
                const starsHTML = Array(estrelas).fill(0).map(() => '<i class="fa-solid fa-star star-yellow"></i>').join(' ');
                tituloFiltro.innerHTML = `${starsHTML} ${estrelas} estrela${estrelas > 1 ? "s" : ""}`;

            }
        });
    });

    // Fechar dropdown ao clicar fora
    document.addEventListener("click", (e) => {
        if (!dropdown.contains(e.target) && !btnFiltro.contains(e.target)) {
            dropdown.classList.remove("mostrar");
            btnFiltro.classList.remove("ativo");
        }
    });
    
    // Adicionar opção "Limpar filtro" (opcional)
    const opcaoLimpar = document.createElement("button");
    opcaoLimpar.type = "button";
    opcaoLimpar.className = "opcao limpar-filtro";
    opcaoLimpar.textContent = "✕ Limpar filtro";
    
    opcaoLimpar.addEventListener("click", (e) => {
        e.stopPropagation();
        
        console.log("Filtro de estrelas limpo");
        
        // Resetar filtro
        filtroEstrelasSelecionado = 0;
        
        // Resetar texto do botão
        const tituloFiltro = btnFiltro.querySelector("#tituloFiltro");
        if (tituloFiltro) {
            tituloFiltro.textContent = "Avaliação";
        }
        
        // Limpar seleção visual
        opcoes.forEach(item => item.classList.remove("selecionada"));
        
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
            document.getElementById("btnFiltro").classList.remove("ativo");
        }
        
        const estaAberto = dropdown.classList.toggle("mostrar");
        btnFiltro.classList.toggle("ativo", estaAberto);
        
        // Ajustar posição do dropdown se necessário
        if (estaAberto) {
            setTimeout(() => ajustarPosicaoDropdown(dropdown, btnFiltro), 0);
        }
    });

    // Fechar dropdown ao clicar fora
    document.addEventListener("click", (e) => {
        if (!dropdown.contains(e.target) && !btnFiltro.contains(e.target)) {
            dropdown.classList.remove("mostrar");
            btnFiltro.classList.remove("ativo");
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
    const card = document.querySelector(`.card-agendamento[data-consulta-id="${consultaId}"]`);
    const botaoAvaliar = document.querySelector(`.btn-avaliar[data-consulta-id="${consultaId}"]`);

    if (card) {
        card.classList.add('avaliacao-ativa');
    }
    if (botaoAvaliar) {
        botaoAvaliar.setAttribute('aria-expanded', 'true');
    }
    if (secao) {
        secao.style.display = "flex";
        secao.setAttribute('aria-hidden', 'false');
        secao.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } else {
        console.error(`Seção de avaliação não encontrada: avaliacao-${consultaId}`);
    }
}

function ocultarEstrelas(consultaId) {
    const secao = document.getElementById(`avaliacao-${consultaId}`);
    const card = document.querySelector(`.card-agendamento[data-consulta-id="${consultaId}"]`);
    const botaoAvaliar = document.querySelector(`.btn-avaliar[data-consulta-id="${consultaId}"]`);

    if (card) {
        card.classList.remove('avaliacao-ativa');
    }
    if (botaoAvaliar) {
        botaoAvaliar.setAttribute('aria-expanded', 'false');
    }
    if (secao) {
        secao.style.display = "none";
        secao.setAttribute('aria-hidden', 'true');
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
        mostrarMensagem('Atenção', 'Por favor, selecione uma classificação em estrelas!', 'warning');
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
            mostrarMensagem('Sucesso', 'Avaliação enviada com sucesso!', 'success');
            ocultarEstrelas(consultaId);
            // Desabilitar botão de avaliação
            const btnAvaliar = document.querySelector(`.btn-avaliar[data-consulta-id="${consultaId}"]`);
            if (btnAvaliar) {
                btnAvaliar.disabled = true;
                btnAvaliar.textContent = "✅ Avaliado";
                btnAvaliar.style.opacity = "0.6";
                btnAvaliar.setAttribute('aria-expanded', 'false');
            }
        } else {
            mostrarMensagem('Erro', data.message || 'Erro ao enviar avaliação', 'error');
        }
    })
    .catch(err => {
        console.error("Erro na requisição:", err);
        mostrarMensagem('Erro', 'Erro ao enviar avaliação! Verifique o console.', 'error');
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

                    const medicoCard = document.createElement("div");
                    medicoCard.className = "card-medico";

                    const foto = medico.foto_url ? medico.foto_url : "/static/img/SemIcon.png";

                    // Buscar nomes das especialidades
                    const especialidadesNomes = [];
                    if (medico.especialidades && medico.especialidades.length > 0) {
                        medico.especialidades.forEach(espId => {
                            // Procurar a especialidade correspondente nos dados da clínica
                            if (data.especialidades) {
                                const esp = data.especialidades.find(e => e[0] === espId);
                                if (esp) {
                                    especialidadesNomes.push(esp[1]);
                                }
                            }
                        });
                    }

                    const especialidadesHtml = especialidadesNomes.length > 0 
                        ? `<p style="font-size: 12px; color: #666; margin-top: 5px;">${especialidadesNomes.join(", ")}</p>`
                        : '';

                    medicoCard.innerHTML = `
                        <img src="${foto}" 
                            style="width:80px;height:80px;border-radius:50%;object-fit:contain;margin-bottom:10px;" onerror="this.onerror=null;this.src='/static/img/SemIcon.png';">
                        <h4>${medico.nome}</h4>
                        ${especialidadesHtml}
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
            console.log('[carregarEspecialidadesEMedicos] data:', data);
            window.medicosClinica = data.medicos || [];

            // Preencher especialidades
            const selectEspecialidade = document.getElementById('selectEspecialidade');
            if (selectEspecialidade && data.especialidades) {
                selectEspecialidade.innerHTML = '<option value="">Selecione uma Especialidade</option>';
                data.especialidades.forEach(esp => {
                    const option = document.createElement('option');
                    option.value = esp[0]; // ID
                    const preco = Number(esp[2] || 0);
                    const precoFormatado = ` - R$ ${preco.toFixed(2).replace('.', ',')}`;
                    option.textContent = `${esp[1]}${precoFormatado}`; // Nome + Preço
                    selectEspecialidade.appendChild(option);
                });
                
                // Remover listener anterior para evitar duplicação
                selectEspecialidade.removeEventListener('change', atualizarMedicosPorEspecialidade);
                // Adicionar novo listener
                selectEspecialidade.addEventListener('change', atualizarMedicosPorEspecialidade);
            }
            
            // Limpar médicos inicialmente
            const selectProfissional = document.getElementById('selectProfissional');
            if (selectProfissional) {
                selectProfissional.innerHTML = '<option value="">Escolha uma especialidade primeiro</option>';
            }
        })
        .catch(error => {
            console.error('Erro ao carregar especialidades e médicos:', error);
            alert('Erro ao carregar dados. Tente novamente.');
        });
}

function atualizarMedicosPorEspecialidade() {
    const selectEspecialidade = document.getElementById('selectEspecialidade');
    const selectProfissional = document.getElementById('selectProfissional');
    if (!selectEspecialidade || !selectProfissional) return;

    const selectedEspecialidadeId = selectEspecialidade.value;
    const medicos = Array.isArray(window.medicosClinica) ? window.medicosClinica : [];
    
    console.log('[atualizarMedicosporEspecialidade] selectedId:', selectedEspecialidadeId, 'medicos:', medicos);
    
    let filtrados = [];
    if (selectedEspecialidadeId) {
        filtrados = medicos.filter(med => {
            const temEspecialidade = Array.isArray(med.especialidades) && 
                                     med.especialidades.map(String).includes(String(selectedEspecialidadeId));
            return temEspecialidade;
        });
    }

    selectProfissional.innerHTML = '<option value="">Escolha um Profissional</option>';
    if (filtrados.length > 0) {
        filtrados.forEach(medico => {
            const option = document.createElement('option');
            option.value = medico.id;
            option.textContent = medico.nome;
            selectProfissional.appendChild(option);
        });
    } else {
        const option = document.createElement('option');
        option.value = '';
        option.disabled = true;
        option.textContent = selectedEspecialidadeId ? 'Nenhum profissional disponível' : 'Escolha uma especialidade';
        selectProfissional.appendChild(option);
    }

    const precoDisplay = document.getElementById('valorEspecialidadeSelecionada');
    if (precoDisplay) {
        const especialidadeSelecionada = window.especialidadesClinica
            ? window.especialidadesClinica.find(e => String(e[0]) === String(selectedEspecialidadeId))
            : null;
        const preco = especialidadeSelecionada ? Number(especialidadeSelecionada[2] || 0) : 0;
        precoDisplay.textContent = `R$ ${preco.toFixed(2).replace('.', ',')}`;
    }
}

function carregarHorarios(clinicaId, data) {
    // Prevenir múltiplas requisições simultâneas
    if (carregarHorarios.isLoading) {
        console.log('[dashboard] Requisição já em andamento, ignorando...');
        return Promise.resolve([]);
    }
    carregarHorarios.isLoading = true;

    // Buscar horários disponíveis da clínica para a data selecionada
    return fetch(`/clinica/${clinicaId}/horarios/?data=${data}`)
        .then(response => response.json())
        .then(data => {
            const selectHorario = document.getElementById('selectHorario');
            if (!selectHorario) return Promise.reject('selectHorario não encontrado');
            
            selectHorario.innerHTML = '<option value="">Selecione o Horário</option>';
            
            if (data.horarios && data.horarios.length > 0) {
                data.horarios.forEach(horario => {
                    const option = document.createElement('option');
                    option.value = horario;
                    option.textContent = horario;
                    selectHorario.appendChild(option);
                });
                
                // IMPORTANTE: Sincronizar horários visíveis no modal com os horários reais do backend
                if (window.calendarSelector) {
                    console.log('[dashboard] Atualizando availableTimes com horários reais:', data.horarios);
                    window.calendarSelector.availableTimes = data.horarios;
                    window.calendarSelector.renderTimeSlots();
                }
                carregarHorarios.isLoading = false;
                return Promise.resolve(data.horarios);
            } else {
                const option = document.createElement('option');
                option.disabled = true;
                option.textContent = 'Nenhum horário disponível';
                selectHorario.appendChild(option);
                
                // Limpar disponibilidades se não houver horários
                if (window.calendarSelector) {
                    window.calendarSelector.availableTimes = [];
                    window.calendarSelector.renderTimeSlots();
                }
                carregarHorarios.isLoading = false;
                return Promise.resolve([]);
            }
        })
        .catch(error => {
            console.error('Erro ao carregar horários:', error);
            const selectHorario = document.getElementById('selectHorario');
            if (selectHorario) {
                selectHorario.innerHTML = '<option value="">Erro ao carregar horários</option>';
            }
            carregarHorarios.isLoading = false;
            return Promise.reject(error);
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
    
    // Se validação passou, prosseguir
    const modal1 = document.getElementById('modal-agendamento-1');
    const modal2 = document.getElementById('modal-agendamento-2');
    
    if (modal1) {
        modal1.classList.remove('mostrar');
        setTimeout(() => {
            modal1.style.display = 'none';
        }, 100);
    }
    
    if (modal2) {
        modal2.classList.add('mostrar');
        modal2.style.display = 'flex';
        
        // Adicionar event listener para o botão de fechar
        const btnFechar = document.getElementById('btn-fechar-agendamento');
        if (btnFechar) {
            btnFechar.addEventListener('click', fecharModalAgendamento);
        }
        
        // Reinicializar o calendário quando o modal é aberto
        setTimeout(() => {
            if (typeof initializeCalendarSelector === 'function') {
                console.log('Reinicializando calendário no segundo modal...');
                initializeCalendarSelector();
            }
        }, 300);
    }
    
    // Carregar especialidades e médicos da clínica selecionada
    carregarEspecialidadesEMedicos(clinicaSelecionada);
}

function voltarAoFormulario() {
    const modal1 = document.getElementById('modal-agendamento-1');
    const modal2 = document.getElementById('modal-agendamento-2');
    
    if (modal2) {
        modal2.classList.remove('mostrar');
        setTimeout(() => {
            modal2.style.display = 'none';
        }, 100);
    }
    
    if (modal1) {
        modal1.classList.add('mostrar');
        modal1.style.display = 'flex';
    }
}

/* ======== FUNÇÕES PARA ABRIR/FECHAR MODAIS DE DATA E HORA ======== */

function abrirModalCalendario() {
    const modal = document.getElementById('modal-calendario');
    const btnConfirm = document.getElementById('btn-confirmar-data');
    if (btnConfirm) {
        btnConfirm.style.display = 'inline-block';
        btnConfirm.disabled = true;
        btnConfirm.setAttribute('disabled', 'disabled');
        btnConfirm.style.pointerEvents = 'none';
        btnConfirm.textContent = 'Confirmar Data';
        btnConfirm.style.opacity = '0.5';
        btnConfirm.onclick = confirmarDataSelecionada;
    }

    if (modal) {
        modal.classList.add('mostrar');
        modal.style.display = 'flex';
        
        // Reinicializar calendário
        setTimeout(() => {
            if (typeof initializeCalendarSelector === 'function') {
                initializeCalendarSelector();
            }
        }, 100);
    }
}

function fecharModalCalendario() {
    const modal = document.getElementById('modal-calendario');
    if (modal) {
        modal.classList.remove('mostrar');
        modal.style.display = 'none';
    }
}

function abrirModalHorario() {
    const inputData = document.getElementById('inputData');
    
    if (!inputData || !inputData.value) {
        mostrarMensagem('Atenção', 'Por favor, selecione uma data primeiro.', 'warning');
        return;
    }
    
    const modal = document.getElementById('modal-horarios');
    if (modal) {
        modal.classList.add('mostrar');
        modal.style.display = 'flex';
    }
}

function fecharModalHorario() {
    const modal = document.getElementById('modal-horarios');
    if (modal) {
        modal.classList.remove('mostrar');
        modal.style.display = 'none';
    }
}

function vincularConfirmarDataBotao() {
    const btn = document.getElementById('btn-confirmar-data');
    if (!btn) return;

    btn.removeEventListener('click', window.__confirmarDataFallback);

    window.__confirmarDataFallback = (event) => {
        if (btn.disabled) {
            event.preventDefault();
            return;
        }
        console.log('[global] Confirmar Data fallback clicked');
        confirmarDataSelecionada();
    };

    btn.addEventListener('click', window.__confirmarDataFallback);
}

document.addEventListener('DOMContentLoaded', () => {
    vincularConfirmarDataBotao();
});

/**
 * Função para confirmar agendamento
 */

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
        mostrarMensagem('Erro', 'Erro ao acessar formulário. Recarregue a página.', 'error');
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
        mostrarMensagem('Atenção', 'Por favor, selecione uma especialidade.', 'warning');
        return;
    }
    
    if (!medico_id) {
        mostrarMensagem('Atenção', 'Por favor, selecione um profissional.', 'warning');
        return;
    }
    
    if (!data) {
        mostrarMensagem('Atenção', 'Por favor, selecione uma data.', 'warning');
        return;
    }
    
    if (!horario) {
        mostrarMensagem('Atenção', 'Por favor, selecione um horário.', 'warning');
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
    
    // include signed uid in case session cookie gets lost
    formData.append('uid', signedUid || document.getElementById('signedUidForAgendar')?.value || '');

    // Enviar para servidor
    fetch('/consulta/agendar/', {
        method: 'POST',
        credentials: 'same-origin',
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
    
    if (modal1) {
        modal1.classList.remove('mostrar');
        modal1.style.display = 'none';
    }
    if (modal2) {
        modal2.classList.remove('mostrar');
        modal2.style.display = 'none';
    }
    if (modalSucesso) {
        modalSucesso.classList.remove('mostrar');
        modalSucesso.style.display = 'none';
    }
    
    // Resetar formulário
    limparFormularioAgendamento();
}

/* Função para limpar o formulário de agendamento */
function limparFormularioAgendamento() {
    const campos = [
        'inputSintomas', 'selectEspecialidade', 'selectProfissional', 'inputData', 'selectHorario'
    ];
    
    campos.forEach(id => {
        const campo = document.getElementById(id);
        if (campo) campo.value = '';
    });
    
    // Recarregar informações do paciente para manter preenchimento automático
    preencherFormularioAgendamentoComDadosUsuario();
}

/* ================= IR PARA MEUS AGENDAMENTOS ================= */
function irParaMeusAgendamentos() {
    mostrarTela('consultas', document.querySelectorAll(".item-menu")[1]);
    fecharModalAgendamento();
}

function irParaAjustes() {
    mostrarTela('ajustes');
}

function abrirNotificacoes() {
    const modal = document.getElementById("modal-notificacoes");
    const ponto = document.querySelector(".ponto-alerta");
    const botao = document.querySelector(".botao-notificacao");

    modal.classList.add("mostrar");

    if (ponto) {
        ponto.style.display = "none";
    }

    if (botao) {
        botao.classList.remove("com-notificacao");
    }
}

function fecharNotificacoes() {
    document.getElementById("modal-notificacoes")
            .classList.remove("mostrar");
}

document.getElementById("modal-notificacoes")
    .addEventListener("click", function(e) {
        if (e.target.id === "modal-notificacoes") {
            fecharNotificacoes();
        }
});

// Event listeners para os botões de fechar modais
document.addEventListener('DOMContentLoaded', () => {
    // Botão fechar modal agendamento 1
    const btnFecharAgendamento1 = document.getElementById('btn-fechar-agendamento-1');
    if (btnFecharAgendamento1) {
        btnFecharAgendamento1.addEventListener('click', fecharModalAgendamento);
    }

    // Botão fechar modal agendamento 2
    const btnFecharAgendamento2 = document.getElementById('btn-fechar-agendamento');
    if (btnFecharAgendamento2) {
        btnFecharAgendamento2.addEventListener('click', fecharModalAgendamento);
    }

    // Event listeners para os selects de data e hora abrirem os modais
    const dataSelecionadaDisplay = document.getElementById('dataSelecionadaDisplay');
    const horaSelecionadaDisplay = document.getElementById('horaSelecionadaDisplay');

    if (dataSelecionadaDisplay) {
        dataSelecionadaDisplay.addEventListener('click', function(e) {
            e.preventDefault();
            abrirModalCalendario();
        });
        dataSelecionadaDisplay.addEventListener('mousedown', function(e) {
            e.preventDefault();
        });
    }

    if (horaSelecionadaDisplay) {
        horaSelecionadaDisplay.addEventListener('click', function(e) {
            e.preventDefault();
            abrirModalHorario();
        });
        horaSelecionadaDisplay.addEventListener('mousedown', function(e) {
            e.preventDefault();
        });
    }
});