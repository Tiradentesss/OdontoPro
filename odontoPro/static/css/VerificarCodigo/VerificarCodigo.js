// ====================================
// TIMER E EMAIL DINÂMICO - VERIFICAÇÃO
// ====================================

// Tempo inicial em segundos (1 minuto)
let tempo = 60;
let contagem;

// Elementos principais
const timerContainer = document.querySelector('.timer');
const emailElemento = document.getElementById('emailDestino');

// ================================
// Atualiza o timer a cada segundo
// ================================
function atualizarTimer() {
  const minutos = String(Math.floor(tempo / 60)).padStart(2, '0');
  const segundos = String(tempo % 60).padStart(2, '0');

  const timerDisplay = timerContainer.querySelector('span');
  if (timerDisplay) timerDisplay.textContent = `${minutos}:${segundos}`;

  if (tempo <= 0) {
    clearInterval(contagem);
    mostrarBotaoReenviar();
  } else {
    tempo--;
  }
}

// ================================
// Mostra o botão "Enviar novamente"
// ================================
function mostrarBotaoReenviar() {
  timerContainer.innerHTML = ''; // limpa o timer

  const botao = document.createElement('button');
  botao.textContent = 'Enviar novamente';
  botao.classList.add('reenviar');

  botao.addEventListener('click', () => {
    alert('Novo código enviado para o seu e-mail!');
    reiniciarTimer();
  });

  timerContainer.appendChild(botao);
}

// ================================
// Reinicia o timer corretamente
// ================================
function reiniciarTimer() {
  clearInterval(contagem);
  tempo = 60;
  timerContainer.innerHTML = `
    <i class="fa-solid fa-clock"></i>
    <span>01:00</span>
  `;
  iniciarTimer();
}

// ================================
// Inicia o timer
// ================================
function iniciarTimer() {
  atualizarTimer();
  contagem = setInterval(atualizarTimer, 1000);
}

// ================================
// Define o e-mail dinamicamente
// ================================
function definirEmail(email) {
  emailElemento.textContent = email;
}

// ================================
// Inicialização
// ================================
iniciarTimer();

// Exemplo: definir o e-mail (pode vir do backend)
definirEmail('usuario@exemplo.com');
