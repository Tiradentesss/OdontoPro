document.addEventListener("DOMContentLoaded", function () {
    const selectEsp = document.getElementById("select-especialidade");
    const radios = document.querySelectorAll("input[name='filtro-estrelas']");
    const cards = document.querySelectorAll(".card");

    function aplicarFiltro() {
        const filtroEspecialidadeRaw = selectEsp.value || "";
        const filtroEspecialidade = filtroEspecialidadeRaw.toString().trim().toLowerCase();

        const filtroEstrelasRaw = document.querySelector("input[name='filtro-estrelas']:checked").value;
        const avaliacaoMin = filtroEstrelasRaw === "" ? 0 : parseInt(filtroEstrelasRaw, 10);

        cards.forEach(card => {
            // Especialidade normalizada
            const esp = (card.dataset.especialidade || "")
                .toString()
                .trim()
                .toLowerCase();

            // Avaliação convertida corretamente (igual clínicas)
            const cardStars = Math.floor(parseFloat(card.dataset.stars || 0));

            let mostrar = true;

            // filtro especialidade
            if (filtroEspecialidade !== "" && !esp.includes(filtroEspecialidade)) {
                mostrar = false;
            }

            // filtro estrelas (usando floor)
            if (avaliacaoMin > 0 && cardStars < avaliacaoMin) {
                mostrar = false;
            }

            card.style.display = mostrar ? "block" : "none";
        });
    }

    selectEsp.addEventListener("change", aplicarFiltro);
    radios.forEach(r => r.addEventListener("change", aplicarFiltro));

    aplicarFiltro(); // aplica no carregamento
});
