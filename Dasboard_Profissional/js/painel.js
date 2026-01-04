// 1. Função de Logout (Corrigida)
function fazerLogout() {
    const confirmar = confirm("Deseja realmente sair do sistema?");
    if (confirmar) {
        // Caminho para voltar: sai de html, sai de Dasboard_Profissional, entra em Login_e_Cadastro
        window.location.href = "../../Login_e_Cadastro/html/clinica.html";
    }
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
            document.getElementById(target).classList.add('active');
        });
    });
});

document.getElementById("btnLogout").addEventListener("click", function(e) {
    e.preventDefault();
    window.location.href = "../../Login_e_Cadastro/html/clinica.html";
});