const btnAgendar = document.querySelector(".btn-agendar");
const popup1 = document.querySelector(".popup1");
const popup2 = document.querySelector(".popup2");
const btnNext = document.querySelector(".btn-next");
const btnBack = document.querySelector(".btn-back");
const btnConfirm = document.querySelector(".btn-confirm");
const inputData = document.querySelector(".input-data");
const inputHora = document.querySelector(".input-hora");
const confirmDataHora = document.querySelector(".confirm-data-hora");

let agendamento = { data: '', hora: '' };

// Abrir primeiro pop-up
btnAgendar.addEventListener("click", () => {
  popup1.classList.add("active");
});

// Avançar para segundo pop-up
btnNext.addEventListener("click", () => {
  if(inputData.value && inputHora.value) {
    agendamento.data = inputData.value;
    agendamento.hora = inputHora.value;
    confirmDataHora.textContent = `${agendamento.data} às ${agendamento.hora}`;
    popup1.classList.remove("active");
    popup2.classList.add("active");
  } else {
    alert("Escolha data e hora antes de continuar.");
  }
});

// Voltar para o primeiro pop-up
btnBack.addEventListener("click", () => {
  popup2.classList.remove("active");
  popup1.classList.add("active");
  // Preencher novamente os inputs com a escolha anterior
  inputData.value = agendamento.data;
  inputHora.value = agendamento.hora;
});

// Confirmar agendamento
btnConfirm.addEventListener("click", () => {
  alert(`Agendamento confirmado em ${agendamento.data} às ${agendamento.hora}`);
  popup2.classList.remove("active");
});
