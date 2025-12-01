document.addEventListener("DOMContentLoaded", function () {
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

  function abrirModal(m) {
      m.style.display = "flex";
      m.setAttribute("aria-hidden", "false");
  }
  function fecharModal(m) {
      m.style.display = "none";
      m.setAttribute("aria-hidden", "true");
  }

  btnOpen && btnOpen.addEventListener("click", () => {
      abrirModal(modal);
  });
  fechar && fechar.addEventListener("click", () => fecharModal(modal));
  btnCancelar && btnCancelar.addEventListener("click", () => fecharModal(modal));

  // fechar modais por ESC
  document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
          fecharModal(modal);
          fecharModal(dadosModal);
          fecharModal(sucessoModal);
      }
  });

  // Ao selecionar data, buscar horários via API
  dataInput && dataInput.addEventListener("change", async (e) => {
      const date = e.target.value;
      horariosList.innerHTML = "<p class='muted'>Buscando horários...</p>";
      btnSelecionar.disabled = true;
      selectedSlot = null;

      if (!date) {
          horariosList.innerHTML = "<p class='muted'>Escolha uma data para ver horários.</p>";
          return;
      }

      try {
          const resp = await fetch(`/api/medico/${window.PROFISSIONAL_ID}/horarios/?date=${date}`);
          const json = await resp.json();
          if (!resp.ok) {
              horariosList.innerHTML = "<p class='muted'>Erro ao buscar horários.</p>";
              return;
          }
          const slots = json.slots || [];
          if (slots.length === 0) {
              horariosList.innerHTML = "<p class='muted'>Sem horários disponíveis para essa data.</p>";
              return;
          }

          horariosList.innerHTML = "";
          slots.forEach(s => {
              const btn = document.createElement("button");
              btn.type = "button";
              btn.textContent = s;
              btn.className = "horario-button";
              btn.addEventListener("click", () => {
                  // desmarca todos
                  document.querySelectorAll(".horario-button").forEach(b => b.classList.remove("ativo"));
                  btn.classList.add("ativo");
                  selectedSlot = s;
                  btnSelecionar.disabled = false;
              });
              horariosList.appendChild(btn);
          });

      } catch (err) {
          console.error(err);
          horariosList.innerHTML = "<p class='muted'>Erro de rede ao buscar horários.</p>";
      }
  });

  // Continuar -> abrir modal de dados
  btnSelecionar && btnSelecionar.addEventListener("click", () => {
      if (!selectedSlot) return;
      document.getElementById("selected_time").value = selectedSlot;
      document.getElementById("selected_date").value = dataInput.value;
      fecharModal(modal);
      abrirModal(dadosModal);
  });

  fecharDados && fecharDados.addEventListener("click", () => fecharModal(dadosModal));

  // enviar agendamento via fetch
  formDados && formDados.addEventListener("submit", async (e) => {
      e.preventDefault();

      const nome = document.getElementById("nome").value.trim();
      const email = document.getElementById("email").value.trim();
      const telefone = document.getElementById("telefone").value.trim();
      const especialidade = document.getElementById("especialidade").value;
      const observacoes = document.getElementById("observacoes").value;
      const date = document.getElementById("selected_date").value;
      const time = document.getElementById("selected_time").value;

      if (!nome || !email || !telefone || !date || !time) {
          alert("Preencha todos os campos obrigatórios.");
          return;
      }

      const payload = {
          nome,
          email,
          telefone,
          date,
          time,
          especialidade,
          observacoes
      };

      try {
          const resp = await fetch(`/api/medico/${window.PROFISSIONAL_ID}/agendar/`, {
              method: "POST",
              headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": window.CSRF_TOKEN
              },
              body: JSON.stringify(payload)
          });
          const json = await resp.json();
          if (resp.ok && json.success) {
              fecharModal(dadosModal);
              sucessoText.textContent = `Agendamento confirmado para ${date} às ${time}. ID: ${json.consulta_id}`;
              abrirModal(sucessoModal);
          } else {
              const err = json.error || "Erro ao agendar";
              alert(err);
          }
      } catch (err) {
          console.error(err);
          alert("Erro de rede ao enviar agendamento.");
      }
  });

  voltarInicio && voltarInicio.addEventListener("click", () => {
      fecharModal(sucessoModal);
  });

  // TABS
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
