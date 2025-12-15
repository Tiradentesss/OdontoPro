function openModal(btn) {
    document.getElementById("m-paciente").textContent = btn.dataset.paciente;
    document.getElementById("m-data").textContent = btn.dataset.data;
    document.getElementById("m-hora").textContent = btn.dataset.hora;
    document.getElementById("m-status").textContent = btn.dataset.status;
    document.getElementById("m-especialidade").textContent = btn.dataset.especialidade;
    document.getElementById("m-medico").textContent = btn.dataset.medico;
    document.getElementById("m-clinica").textContent = btn.dataset.clinica;
    document.getElementById("m-endereco").textContent = btn.dataset.endereco;
    document.getElementById("m-observacoes").textContent = btn.dataset.observacoes;

    document.getElementById("modal-detalhes").style.display = "flex";
}

function closeModal() {
    document.getElementById("modal-detalhes").style.display = "none";
}

function cancelarConsulta(id) {
    if (!confirm("Tem certeza que deseja cancelar esta consulta?")) return;

    fetch(`/consulta/${id}/cancelar/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
        },
    })
    .then(res => res.json())
    .then(data => {
        alert(data.mensagem);
        if (data.success) {
            location.reload();
        }
    })
    .catch(() => {
        alert("Erro ao cancelar a consulta.");
    });
}

function getCSRFToken() {
    return document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];
}
