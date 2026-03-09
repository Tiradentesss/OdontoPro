document.addEventListener('DOMContentLoaded', () => {
    console.log("Sistema OdontoPro carregado!");

    // --- 1. SELETORES DE SEÇÕES (TELAS) ---
    const secoes = {
        login: document.getElementById('secao-login'),
        cadastro: document.getElementById('secao-cadastro'),
        pagamento: document.getElementById('secao-pagamento'),
        sucesso: document.getElementById('secao-sucesso')
    };

    // --- 2. SELETORES DE BOTÕES E LINKS ---
    const linkCadastro = document.getElementById('link-cadastro');
    const linksVoltar = document.querySelectorAll('.link-voltar-login');
    const formLogin = document.getElementById('form-login');
    const formCadastro = document.getElementById('form-cadastro');
    const btnConfirmarPagamento = document.getElementById('btn-confirmar-pagamento');
    const btnGoogle = document.querySelector('.botao-google');

    // --- 3. SELETORES DO MODAL (ESQUECI SENHA) ---
    const linkEsqueci = document.querySelector('.link-esqueci');
    const modalEsqueci = document.getElementById('modal-esqueci');
    const btnFecharModal = document.querySelector('.fechar-modal');
    const etapaEmail = document.getElementById('etapa-email');
    const etapaCodigo = document.getElementById('etapa-codigo');
    const etapaNovaSenha = document.getElementById('etapa-nova-senha');
    const btnEnviarCodigo = document.getElementById('btn-enviar-codigo');
    const btnValidarCodigo = document.getElementById('btn-validar-codigo');
    const btnResetarSenha = document.getElementById('btn-resetar-senha');

    // --- 4. FUNÇÃO PARA TROCAR DE TELA ---
    function mostrarTela(nomeDaTela) {
        // Esconde todas
        Object.values(secoes).forEach(s => {
            if (s) s.classList.add('hidden');
        });
        // Mostra a desejada
        if (secoes[nomeDaTela]) {
            secoes[nomeDaTela].classList.remove('hidden');
        }
    }

    // --- 5. LÓGICA DE NAVEGAÇÃO ---

    // Abrir tela de cadastro
    if (linkCadastro) {
        linkCadastro.onclick = (e) => {
            e.preventDefault();
            mostrarTela('cadastro');
        };
    }

    // Voltar para login (todos os botões "Voltar")
    linksVoltar.forEach(link => {
        link.onclick = (e) => {
            e.preventDefault();
            mostrarTela('login');
        };
    });

    // Login -> Dashboard
    if (formLogin) {
        formLogin.onsubmit = (e) => {
            e.preventDefault();
            window.location.href = "../../Dasboard_Profissional/html/painel.html";
        };
    }

    // Cadastro -> Pagamento
    if (formCadastro) {
        formCadastro.onsubmit = (e) => {
            e.preventDefault();
            mostrarTela('pagamento');
        };
    }

    // Confirmar Pagamento -> Sucesso
    if (btnConfirmarPagamento) {
        btnConfirmarPagamento.onclick = () => {
            btnConfirmarPagamento.innerText = "Verificando...";
            setTimeout(() => {
                mostrarTela('sucesso');
            }, 2000);
        };
    }

    // Login com Google
    if (btnGoogle) {
        btnGoogle.onclick = (e) => {
            e.preventDefault();
            window.location.href = "../../Dasboard_Profissional/html/painel.html";
        };
    }

    // --- 6. LÓGICA DO MODAL (ESQUECI SENHA) ---

    function resetarEtapasModal() {
        if (etapaEmail) etapaEmail.classList.remove('hidden');
        if (etapaCodigo) etapaCodigo.classList.add('hidden');
        if (etapaNovaSenha) etapaNovaSenha.classList.add('hidden');
        if (btnEnviarCodigo) btnEnviarCodigo.innerText = "Enviar Código";
    }

    if (linkEsqueci) {
        linkEsqueci.onclick = (e) => {
            e.preventDefault();
            modalEsqueci.classList.remove('hidden');
        };
    }

    if (btnFecharModal) {
        btnFecharModal.onclick = () => {
            modalEsqueci.classList.add('hidden');
            resetarEtapasModal();
        };
    }

    if (btnEnviarCodigo) {
        btnEnviarCodigo.onclick = () => {
            const email = document.getElementById('recuperar-email').value;
            if (email) {
                btnEnviarCodigo.innerText = "Enviando...";
                setTimeout(() => {
                    etapaEmail.classList.add('hidden');
                    etapaCodigo.classList.remove('hidden');
                }, 1000);
            } else { alert("Digite um e-mail válido!"); }
        };
    }

    if (btnValidarCodigo) {
        btnValidarCodigo.onclick = () => {
            const codigo = document.getElementById('input-codigo').value;
            if (codigo.length === 6) {
                etapaCodigo.classList.add('hidden');
                etapaNovaSenha.classList.remove('hidden');
            } else { alert("O código deve ter 6 dígitos!"); }
        };
    }

    if (btnResetarSenha) {
        btnResetarSenha.onclick = () => {
            alert("Senha alterada com sucesso!");
            modalEsqueci.classList.add('hidden');
            resetarEtapasModal();
        };
    }
});