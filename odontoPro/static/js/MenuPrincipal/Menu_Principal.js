document.addEventListener("DOMContentLoaded", function () {
    const filtros = document.querySelectorAll(".filtro");
    const clinicas = document.querySelectorAll(".opcoes .options");

    // aplica filtros sempre que qualquer select mudar (aplica automaticamente)
    filtros.forEach(filtro => {
        filtro.addEventListener("change", aplicarFiltros);
    });

    // também aplica no carregamento inicial (útil para debug/testes)
    aplicarFiltros();

    function aplicarFiltros() {
        // pega e normaliza (trim + lower) os valores selecionados
        const municipioRaw = document.getElementById("selectMunicipio").value || "";
        const bairroRaw = document.getElementById("selectBairro").value || "";
        const avaliacaoRaw = document.getElementById("selectAvaliacao").value || "";

        const municipio = municipioRaw.toString().trim().toLowerCase();
        const bairro = bairroRaw.toString().trim().toLowerCase();
        const avaliacaoMin = avaliacaoRaw === "" ? 0 : parseInt(avaliacaoRaw, 10);

        clinicas.forEach(clinica => {
            // dataset pode conter espaços — normalizamos tudo
            const clinicaMunicipio = (clinica.dataset.municipio || "").toString().trim().toLowerCase();
            const clinicaBairro = (clinica.dataset.bairro || "").toString().trim().toLowerCase();

            // avaliacao no data-* pode ser "5.0" ou "5" — usamos parseFloat e floor
            const clinicaAvaliacao = Math.floor(parseFloat(clinica.dataset.avaliacao || 0));

            let mostrar = true;

            // filtro de municipio (se houver)
            if (municipio !== "" && clinicaMunicipio !== municipio) {
                mostrar = false;
            }

            // filtro de bairro (se houver)
            if (bairro !== "" && clinicaBairro !== bairro) {
                mostrar = false;
            }

            // filtro de avaliacao (se houver)
            if (avaliacaoMin > 0 && clinicaAvaliacao < avaliacaoMin) {
                mostrar = false;
            }

            clinica.style.display = mostrar ? "flex" : "none";
        });

        // debug (descomente se quiser inspecionar valores no console)
        // console.log({ municipio, bairro, avaliacaoMin });
        // clinicas.forEach(c => console.log(c.dataset));
    }
});
