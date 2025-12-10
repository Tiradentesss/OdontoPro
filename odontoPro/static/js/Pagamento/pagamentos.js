document.getElementById("copyBtn").addEventListener("click", function () {
    const text = document.getElementById("pixCode");

    text.select();
    text.setSelectionRange(0, 99999); // compatibilidade mobile

    navigator.clipboard.writeText(text.value).then(() => {
        document.getElementById("msg").textContent = "Código Pix copiado!";
    });
});


// BOTÃO CONFIRMAR PAGAMENTO → ABRE POPUP
document.getElementById("confirmBtn").addEventListener("click", function () {
    document.getElementById("popup").classList.add("show");
});

// FECHAR POPUP + REDIRECIONAR PARA A TELA DE CADASTRO
document.getElementById("closePopup").addEventListener("click", function () {
    document.getElementById("popup").classList.remove("show");

    // Redireciona após fechar o popup
    setTimeout(() => {
        window.location.href = "clinica-cadastro.html";
    }, 300); // tempo suave para fechar o popup antes do redirecionamento
});

// Pré-visualização da imagem
document.getElementById("fotoInput").addEventListener("change", function (event) {
    const file = event.target.files[0];
    if (file) {
        document.getElementById("preview").src = URL.createObjectURL(file);
    }
});

// Botão salvar
document.getElementById("submitBtn").addEventListener("click", function () {
    const nome = document.getElementById("nomeClinica").value.trim();
    const desc = document.getElementById("descricaoClinica").value.trim();

    if (!nome || !desc) {
        document.getElementById("msg").style.color = "red";
        document.getElementById("msg").textContent = "Preencha todos os campos!";
        return;
    }

    document.getElementById("msg").style.color = "green";
    document.getElementById("msg").textContent = "Informações salvas com sucesso!";
});

// Voltar ao início
document.getElementById("backBtn").addEventListener("click", function () {
    window.location.href = "/";
});
