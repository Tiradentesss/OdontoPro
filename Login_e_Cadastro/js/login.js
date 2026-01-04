 const modal = document.getElementById("modalCadastro");
    const btnOpen = document.getElementById("openModal");
    const btnClose = document.querySelector(".close-btn");

    // Abre o modal
    btnOpen.onclick = function(e) {
      e.preventDefault();
      modal.style.display = "block";
    }

    // Fecha no botão X
    btnClose.onclick = function() {
      modal.style.display = "none";
    }

    // Fecha se clicar fora da caixa
    window.onclick = function(event) {
      if (event.target == modal) {
        modal.style.display = "none";
      }
    }

const modalForgot = document.getElementById("modalEsqueciSenha");
const linkForgot = document.querySelector(".forgot-password");
const closeForgot = document.querySelector(".close-forgot-btn");

linkForgot.onclick = (e) => {
    e.preventDefault();
    modalForgot.style.display = "block";
    goToStep(1); // Garante que comece na etapa 1
}

closeForgot.onclick = () => modalForgot.style.display = "none";

// Função para mudar de etapa
function goToStep(stepNumber) {
    // Esconde todas
    document.querySelectorAll('.forgot-step').forEach(step => {
        step.classList.remove('active');
    });
    // Mostra a desejada
    document.getElementById('step' + stepNumber).classList.add('active');
}

function finishReset() {
    alert("Senha alterada com sucesso!");
    modalForgot.style.display = "none";
}

document.getElementById("btnEntrarDashboard").addEventListener("click", function() {
    // Caminho baseado na sua estrutura: Nova_OdontoPro > Dasboard_paciente > html > dasboard.html
    window.location.href = "../../Dasboard_paciente/html/dasboard.html";
});