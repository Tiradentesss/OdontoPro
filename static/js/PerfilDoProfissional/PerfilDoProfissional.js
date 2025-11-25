// -------- SELETORES -------- //
const btnAgendar = document.querySelector(".btn-agendar");

// MODAL 1
const modal1 = document.querySelector("#agenda-modal");
const fecharModal1 = document.querySelector("#fechar-modal");
const inputData = document.querySelector("#data");
const botoesHora = document.querySelectorAll(".horarios button");
let horaSelecionada = null;

const btnAvancar = document.querySelector("#abrirDadosConsulta");

// MODAL 2
const modal2 = document.querySelector("#dados-consulta-modal");
const fecharModal2 = document.querySelector("#fechar-dados");
const inputDataHoraFinal = document.querySelector("#dataHoraSelecionada");

// MODAL 3
const modalSucesso = document.querySelector("#sucesso-modal");
const btnVoltarInicio = document.querySelector("#voltarInicio");


// -------- ABRIR PRIMEIRO MODAL -------- //
btnAgendar.addEventListener("click", () => {
  modal1.classList.add("active");
});


// -------- SELECIONAR HORÁRIO -------- //
botoesHora.forEach(btn => {
  btn.addEventListener("click", () => {
    // tirar seleção anterior
    botoesHora.forEach(b => b.classList.remove("selecionado"));

    // marcar o clicado
    horaSelecionada = btn.textContent;
    btn.classList.add("selecionado");
  });
});


// -------- AVANÇAR PARA MODAL 2 -------- //
btnAvancar.addEventListener("click", () => {
  if (!inputData.value || !horaSelecionada) {
    alert("Escolha uma data e um horário.");
    return;
  }

  // Preencher campo no segundo modal
  inputDataHoraFinal.value = `${inputData.value} às ${horaSelecionada}`;

  // Abrir modal 2
  modal1.classList.remove("active");
  modal2.classList.add("active");
});


// -------- VOLTAR DO MODAL 2 PARA O 1 -------- //
fecharModal2.addEventListener("click", () => {
  modal2.classList.remove("active");
  modal1.classList.add("active");
});


// -------- FECHAR MODAL 1 -------- //
fecharModal1.addEventListener("click", () => {
  modal1.classList.remove("active");
  horaSelecionada = null;
  botoesHora.forEach(b => b.classList.remove("selecionado"));
});


// -------- FORM DE CONFIRMAÇÃO -------- //
document.querySelector("#formDadosConsulta").addEventListener("submit", (e) => {
  e.preventDefault();

  modal2.classList.remove("active");
  modalSucesso.classList.add("active");
});


// -------- VOLTAR AO INÍCIO -------- //
btnVoltarInicio.addEventListener("click", () => {
  modalSucesso.classList.remove("active");
});
