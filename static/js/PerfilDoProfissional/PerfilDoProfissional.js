document.addEventListener("DOMContentLoaded", function () {

    /* -----------------------------------------------------
       ELEMENTOS
    ------------------------------------------------------*/
    const btnOpen = document.getElementById("btn-open-agenda");
    const modal = document.getElementById("agenda-modal");
    const fechar = document.getElementById("fechar-modal");
    const btnCancelar = document.getElementById("btn-cancelar");
    const horariosList = document.getElementById("horarios-list");
    const dataInput = document.getElementById("data");
    const btnSelecionar = document.getElementById("btn-selecionar");

    const dadosModal = document.getElementById("dados-consulta-modal");
    const fecharDados = document.getElementById("fechar-dados");
    const formDados = document.getElementById("formDadosConsulta");

    const sucessoModal = document.getElementById("sucesso-modal");
    const sucessoText = document.getElementById("sucesso-text");
    const voltarInicio = document.getElementById("voltarInicio");

    let selectedSlot = null;

    /* -----------------------------------------------------
       FUNÇÕES DE MODAL
    ------------------------------------------------------*/
    function abrirModal(m) {
        if (!m) return;
        m.style.display = "flex";
        m.setAttribute("aria-hidden", "false");
    }

    function fecharModal(m) {
        if (!m) return;
        m.style.display = "none";
        m.setAttribute("aria-hidden", "true");
    }

    /* -----------------------------------------------------
       ABERTURA / FECHAMENTO DO MODAL PRINCIPAL
    ------------------------------------------------------*/
    if (btnOpen) btnOpen.addEventListener("click", () => abrirModal(modal));
    if (fechar) fechar.addEventListener("click", () => fecharModal(modal));
    if (btnCancelar) btnCancelar.addEventListener("click", () => fecharModal(modal));

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            fecharModal(modal);
            fecharModal(dadosModal);
            fecharModal(sucessoModal);
        }
    });

    /* -----------------------------------------------------
       BUSCAR HORÁRIOS POR DATA
    ------------------------------------------------------*/
    if (dataInput) {
        dataInput.addEventListener("change", async (e) => {
            const date = e.target.value;
            horariosList.innerHTML = "<p class='muted'>Buscando horários...</p>";
            btnSelecionar.disabled = true;
            selectedSlot = null;

            if (!date) {
                horariosList.innerHTML = "<p class='muted'>Escolha uma data.</p>";
                return;
            }

            const resp = await fetch(`/api/medico/${window.PROFISSIONAL_ID}/horarios/?date=${date}`);
            const json = await resp.json();

            const slots = json.horarios || [];
            if (slots.length === 0) {
                horariosList.innerHTML = "<p class='muted'>Nenhum horário disponível.</p>";
                return;
            }

            horariosList.innerHTML = "";
            slots.forEach(s => {
                const btn = document.createElement("button");
                btn.type = "button";
                btn.textContent = s;
                btn.className = "horario-button";

                btn.addEventListener("click", () => {
                    document.querySelectorAll(".horario-button").forEach(b => b.classList.remove("ativo"));
                    btn.classList.add("ativo");
                    selectedSlot = s;
                    btnSelecionar.disabled = false;
                });

                horariosList.appendChild(btn);
            });
        });
    }

    /* -----------------------------------------------------
       CONTINUAR PARA AS INFORMAÇÕES DO PACIENTE
    ------------------------------------------------------*/
    if (btnSelecionar) {
        btnSelecionar.addEventListener("click", () => {
            const selectedDate = dataInput.value;
            const selectedTime = selectedSlot.split(" - ")[0];

            document.getElementById("selected_date").value = selectedDate;
            document.getElementById("selected_time").value = selectedTime;

            fecharModal(modal);
            abrirModal(dadosModal);
        });
    }

    if (fecharDados) fecharDados.addEventListener("click", () => fecharModal(dadosModal));

    /* -----------------------------------------------------
       ENVIAR AGENDAMENTO (única versão válida!)
    ------------------------------------------------------*/
    if (formDados) {
        formDados.addEventListener("submit", async (e) => {
            e.preventDefault();

            const payload = {
                nome: document.getElementById("nome").value.trim(),
                email: document.getElementById("email").value.trim(),
                telefone: document.getElementById("telefone").value.trim(),
                especialidade: document.getElementById("especialidade").value,
                observacoes: document.getElementById("observacoes").value,
                date: document.getElementById("selected_date").value,
                time: document.getElementById("selected_time").value,
            };

            const resp = await fetch(`/api/medico/${window.PROFISSIONAL_ID}/agendar/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.CSRF_TOKEN
                },
                body: JSON.stringify(payload)
            });

            const json = await resp.json();

            if (!resp.ok || !json.success) {
                alert(json.error || "Erro ao agendar.");
                return;
            }

            fecharModal(dadosModal);
            sucessoText.textContent = `Agendamento confirmado para ${payload.date} às ${payload.time}.`;
            abrirModal(sucessoModal);
        });
    }

    if (voltarInicio) {
        voltarInicio.addEventListener("click", () => fecharModal(sucessoModal));
    }

    /* -----------------------------------------------------
       ⭐ RESTANTE DA PÁGINA — TABS (NÃO PODE REMOVER!)
    ------------------------------------------------------*/
    document.querySelectorAll(".tab-button").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".tab-button").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const tab = btn.dataset.tab;

            document.querySelectorAll(".tab-content").forEach(c => c.style.display = "none");

            const content = document.getElementById(tab);
            if (content) content.style.display = "block";
        });
    });

});
