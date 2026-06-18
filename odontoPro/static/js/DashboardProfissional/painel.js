// Small helper to read cookies (CSRF)
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// 1. Função de Logout (Corrigida)
function fazerLogout() {
    const confirmar = confirm("Deseja realmente sair do sistema?");
    if (!confirmar) return;

    const csrftoken = getCookie('csrftoken');

    fetch('/logout/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
        },
    }).then(resp => {
        if (resp.redirected) {
            window.location.href = resp.url;
        } else if (resp.ok) {
            // fallback to clinic login if exists
            window.location.href = '/login-clinica/';
        } else {
            alert('Erro ao encerrar a sessão. Tente novamente.');
        }
    }).catch(() => {
        alert('Erro ao encerrar a sessão. Tente novamente.');
    });
}

// 2. Função para Abrir o Modal de Paciente
function openPreview(nome, horario) {
    const modal = document.getElementById('previewModal');
    document.getElementById('modalName').innerText = nome;
    document.getElementById('modalTime').innerText = horario;
    modal.classList.add('active'); // Certifique-se que o CSS usa .active para mostrar
    modal.style.display = "flex";
}

function closeModal() {
    document.getElementById('previewModal').style.display = "none";
}

// 3. Lógica de Troca de Abas (Tabs)
document.addEventListener('DOMContentLoaded', () => {
    // Inicializa ícones do Lucide
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    const links = document.querySelectorAll('.nav-link');
    const conteudos = document.querySelectorAll('.tab-content');

    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active de todos
            links.forEach(l => l.classList.remove('active'));
            conteudos.forEach(c => c.classList.remove('active'));

            // Adiciona active ao clicado
            link.classList.add('active');
            const target = link.getAttribute('data-target');
            const targetEl = document.getElementById(target);
            if (targetEl) {
                targetEl.classList.add('active');
                // se for a aba de agendamento, carregue horários
                if (target === 'agendamento') {
                    try { loadAgendamento(); } catch (err) { console.warn(err); }
                }
            } else {
                console.warn('Target tab not found:', target);
            }
        });
    });

    // Delegated click handler: handle buttons first, then appointment preview
    document.addEventListener('click', (e) => {
        const cancelarBtn = e.target.closest('.btn-cancelar-consulta');
        if (cancelarBtn) {
            const id = cancelarBtn.dataset.consultaId;
            if (id) confirmarCancelamento(id);
            return;
        }

        const confirmarBtn = e.target.closest('.btn-confirmar-consulta');
        if (confirmarBtn) {
            const id = confirmarBtn.dataset.consultaId;
            if (id) confirmarConsulta(id);
            return;
        }

        const item = e.target.closest('.appointment-item');
        if (item) {
            const nome = item.dataset.nome || '';
            const horario = item.dataset.horario || '';
            openPreview(nome, horario);
        }
    });

    // inicializar valor do input de data para hoje
    const dataInput = document.getElementById('agendamento-data');
    if (dataInput) {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        dataInput.value = `${yyyy}-${mm}-${dd}`;
    }

    // preview de imagens de upload antes do envio
    const bannerInput = document.getElementById('upload-banner');
    const logoInput = document.getElementById('upload-avatar');
    const bannerPreview = document.getElementById('previa-banner');
    const logoPreview = document.getElementById('previa-avatar');

    function filePreview(input, previewImage) {
        if (!input || !previewImage) return;
        input.addEventListener('change', () => {
            const file = input.files && input.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (event) => {
                previewImage.src = event.target.result;
            };
            reader.readAsDataURL(file);
        });
    }

    filePreview(bannerInput, bannerPreview);
    filePreview(logoInput, logoPreview);

    const specialtyInput = document.getElementById('especialidade_input');
    const addSpecialtyBtn = document.getElementById('add-specialty');
    const specialtyList = document.getElementById('specialty-list');

    function updateSpecialtyPlaceholder() {
        if (!specialtyList) return;
        const hasItems = specialtyList.querySelectorAll('.specialty-item').length > 0;
        const emptyMessage = specialtyList.querySelector('.specialty-empty');
        if (hasItems) {
            emptyMessage?.remove();
            return;
        }
        if (!emptyMessage) {
            const placeholder = document.createElement('p');
            placeholder.className = 'specialty-empty';
            placeholder.innerText = 'Nenhuma especialidade cadastrada.';
            specialtyList.appendChild(placeholder);
        }
    }

    function removeSpecialtyItem(button) {
        const item = button.closest('.specialty-item');
        if (!item) return;
        item.remove();
        updateSpecialtyPlaceholder();
    }

    function createSpecialtyItem(value) {
        if (!specialtyList || !value) return;
        const normalized = value.trim().toLowerCase();
        const exists = Array.from(specialtyList.querySelectorAll('.specialty-name')).some(el => el.innerText.trim().toLowerCase() === normalized);
        if (exists) return;

        const wrapper = document.createElement('div');
        wrapper.className = 'specialty-item';

        const span = document.createElement('span');
        span.className = 'specialty-name';
        span.innerText = value;

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'remove-specialty';
        removeBtn.innerText = '-';
        removeBtn.addEventListener('click', () => removeSpecialtyItem(removeBtn));

        const hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = 'especialidades[]';
        hidden.value = value;

        wrapper.appendChild(span);
        wrapper.appendChild(removeBtn);
        wrapper.appendChild(hidden);
        specialtyList.appendChild(wrapper);
        updateSpecialtyPlaceholder();
    }

    if (specialtyList) {
        specialtyList.querySelectorAll('.remove-specialty').forEach(btn => {
            btn.addEventListener('click', () => removeSpecialtyItem(btn));
        });
    }

    if (addSpecialtyBtn && specialtyInput) {
        addSpecialtyBtn.addEventListener('click', () => {
            const value = specialtyInput.value.trim();
            if (!value) return;
            createSpecialtyItem(value);
            specialtyInput.value = '';
            specialtyInput.focus();
        });

        specialtyInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addSpecialtyBtn.click();
            }
        });

        updateSpecialtyPlaceholder();
    }
});


// Carrega horários do endpoint existente `/clinica/<id>/horarios/?data=YYYY-MM-DD`
function carregarHorariosProfissional(clinicaId, data) {
    if (!clinicaId || !data) return Promise.resolve([]);
    return fetch(`/clinica/${clinicaId}/horarios/?data=${data}`)
        .then(resp => resp.json())
        .then(json => json.horarios || [])
        .catch(err => {
            console.error('Erro ao carregar horários', err);
            return [];
        });
}

function renderHorariosLista(horarios) {
    const container = document.getElementById('agendamento-list');
    if (!container) return;
    container.innerHTML = '';
    if (!horarios || horarios.length === 0) {
        container.innerHTML = '<p class="empty-message">Nenhum horário disponível.</p>';
        return;
    }
    const list = document.createElement('div');
    list.className = 'horarios-grid';
    horarios.forEach(h => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'horario-slot';
        btn.textContent = h;
        // comportamento futuro: agendar ao clicar
        list.appendChild(btn);
    });
    container.appendChild(list);
}

function loadAgendamento() {
    const section = document.getElementById('agendamento');
    if (!section) return;
    const clinicaId = section.getAttribute('data-clinica');
    const dataInput = document.getElementById('agendamento-data');
    const data = dataInput ? dataInput.value : '';
    const btn = document.getElementById('btnCarregarHorarios');
    if (btn) btn.disabled = true;
    carregarHorariosProfissional(clinicaId, data)
        .then(horarios => renderHorariosLista(horarios))
        .finally(() => { if (btn) btn.disabled = false; });
}

// Vincula botão de carregar horários
const btnCarregar = document.getElementById('btnCarregarHorarios');
if (btnCarregar) {
    btnCarregar.addEventListener('click', (e) => {
        e.preventDefault();
        loadAgendamento();
    });
}

// Garante que o botão de logout exista antes de anexar o evento
const btnLogout = document.getElementById("btnLogout");
if (btnLogout) {
    btnLogout.addEventListener("click", function(e) {
        e.preventDefault();
        fazerLogout();
    });
}

// Cancelar consulta (profissional)
function confirmarCancelamento(consultaId) {
    if (!confirm('Confirma o cancelamento desta consulta?')) return;
    const csrftoken = getCookie('csrftoken');
    fetch(`/consulta/${consultaId}/cancelar/`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
        },
    }).then(resp => resp.json())
      .then(json => {
          if (json && json.success) {
              // Atualiza UI: remove ou marca como cancelada
              const item = document.querySelector(`.appointment-item[data-consulta-id="${consultaId}"]`);
              if (item) {
                  const badge = item.querySelector('.badge-status');
                  if (badge) badge.innerText = 'Cancelada';
                  const actions = item.querySelector('.card-actions'); if (actions) actions.remove();
              }
              alert(json.message || 'Consulta cancelada');
          } else {
              alert((json && json.error) || 'Erro ao cancelar consulta');
          }
      }).catch(err => { console.error(err); alert('Erro ao cancelar consulta'); });
}

// Confirmar consulta (profissional)
function confirmarConsulta(consultaId) {
    if (!confirm('Confirma esta consulta?')) return;
    const csrftoken = getCookie('csrftoken');
    fetch(`/consulta/${consultaId}/confirmar/`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
        },
    }).then(resp => resp.json())
      .then(json => {
          if (json && json.success) {
              const item = document.querySelector(`.appointment-item[data-consulta-id="${consultaId}"]`);
              if (item) {
                  const badge = item.querySelector('.badge-status');
                  if (badge) badge.innerText = 'Confirmada';
                  // remove confirmar button
                  const btn = item.querySelector('.btn-confirmar-consulta'); if (btn) btn.remove();
              }
              alert(json.message || 'Consulta confirmada');
          } else {
              alert((json && json.error) || 'Erro ao confirmar consulta');
          }
      }).catch(err => { console.error(err); alert('Erro ao confirmar consulta'); });
}