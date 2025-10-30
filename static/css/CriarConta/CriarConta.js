// ELEMENTOS DO DOM
const inputs = {
    nome: document.getElementById('nome'),
    nascimento: document.getElementById('nascimento'),
    email: document.getElementById('email'),
    numero: document.getElementById('numero'),
    senha: document.getElementById('senha')
};

const erros = {
    nome: document.getElementById('erro-nome'),
    nascimento: document.getElementById('erro-nascimento'),
    email: document.getElementById('erro-email'),
    numero: document.getElementById('erro-numero'),
    senha: document.getElementById('erro-senha')
};

const formCadastro = document.getElementById('formCadastro');
const googleBtn = document.getElementById('googleBtn');
const facebookBtn = document.getElementById('facebookBtn');

// FUNÇÃO DE VALIDAÇÃO
function validarCampos() {
    let valido = true;

    // limpar erros anteriores
    for (let key in erros) {
        erros[key].textContent = "";
        inputs[key].classList.remove('input-erro');
    }

    if (inputs.nome.value.trim() === "") {
        erros.nome.textContent = "Por favor, preencha o Nome.";
        inputs.nome.classList.add('input-erro');
        valido = false;
    }

    if (inputs.nascimento.value.trim() === "") {
        erros.nascimento.textContent = "Por favor, preencha a Data de Nascimento.";
        inputs.nascimento.classList.add('input-erro');
        valido = false;
    }

    if (inputs.email.value.trim() === "") {
        erros.email.textContent = "Por favor, preencha o Email.";
        inputs.email.classList.add('input-erro');
        valido = false;
    }

    if (inputs.numero.value.trim() === "") {
        erros.numero.textContent = "Por favor, preencha o Número do Celular.";
        inputs.numero.classList.add('input-erro');
        valido = false;
    }

    if (inputs.senha.value.trim() === "") {
        erros.senha.textContent = "Por favor, preencha a Senha.";
        inputs.senha.classList.add('input-erro');
        valido = false;
    }

    return valido;
}

// EVENTO DO FORMULÁRIO
formCadastro.addEventListener('submit', function(event) {
    event.preventDefault();

    if (!validarCampos()) {
        return;
    }

    // captura os valores dos inputs
    const dados = {
        nome: inputs.nome.value,
        nascimento: inputs.nascimento.value,
        email: inputs.email.value,
        numero: inputs.numero.value,
        senha: inputs.senha.value
    };

    console.log("Cadastro:", dados);
    alert("Cadastro capturado com sucesso! Veja o console.");
});

// EVENTOS DOS BOTÕES SOCIAIS
googleBtn.addEventListener('click', function() {
    alert("Login com Google clicado!");
});

facebookBtn.addEventListener('click', function() {
    alert("Login com Facebook clicado!");
});
