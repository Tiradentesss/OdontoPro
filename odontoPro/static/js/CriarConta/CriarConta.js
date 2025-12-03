document.addEventListener("DOMContentLoaded", function() {

    const inputs = {
        nome: document.getElementById('nome'),
        nascimento: document.getElementById('nascimento'),
        email: document.getElementById('email'),
        numero: document.getElementById('numero'),
        senha: document.getElementById('senha')
    };

    function validarCampos() {
        if (
            inputs.nome.value.trim() === "" ||
            !inputs.nascimento.value ||
            inputs.email.value.trim() === "" ||
            inputs.numero.value.trim() === "" ||
            inputs.senha.value.trim() === ""
        ) {
            return false;
        }
        return true;
    }

    document.getElementById("formCadastro").addEventListener("submit", e => {

        // APENAS impede se faltar algo
        if (!validarCampos()) {
            alert("Preencha todos os campos!");
            e.preventDefault();
        }

        // ⚠️ REMOVA QUALQUER OUTRO CÓDIGO AQUI
    });

});
