document.addEventListener("DOMContentLoaded", function() {
    const btnFiltrar = document.getElementById("btnFiltrar");
    const selectMunicipio = document.getElementById("selectMunicipio");
    const selectBairro = document.getElementById("selectBairro");
    const selectAvaliacao = document.getElementById("selectAvaliacao");
    const clinicas = document.querySelectorAll(".opcoes .options");

    btnFiltrar.addEventListener("click", function() {
        const municipioSelecionado = selectMunicipio.value;
        const bairroSelecionado = selectBairro.value;
        const avaliacaoMinima = selectAvaliacao.value ? parseInt(selectAvaliacao.value) : 0;

        clinicas.forEach(clinica => {
            const clinicaMunicipio = clinica.getAttribute("data-municipio");
            const clinicaBairro = clinica.getAttribute("data-bairro");
            const clinicaAvaliacao = parseInt(clinica.getAttribute("data-avaliacao") || 0);

            let mostrar = true;

            if (municipioSelecionado && clinicaMunicipio !== municipioSelecionado) {
                mostrar = false;
            }
            if (bairroSelecionado && clinicaBairro !== bairroSelecionado) {
                mostrar = false;
            }
            if (avaliacaoMinima && clinicaAvaliacao < avaliacaoMinima) {
                mostrar = false;
            }

            clinica.style.display = mostrar ? "flex" : "none";
        });
    });
});
