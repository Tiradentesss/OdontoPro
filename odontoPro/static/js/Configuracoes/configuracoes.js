document.addEventListener("DOMContentLoaded", () => {

    // ====== TABS ======
    const buttons = document.querySelectorAll(".tab-button");
    const sections = document.querySelectorAll(".tab-section");

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            buttons.forEach(b => b.classList.remove("active"));
            sections.forEach(s => s.style.display = "none");

            btn.classList.add("active");
            const target = btn.dataset.tab;
            document.querySelector(`[data-tab-section="${target}"], #${target}`).style.display =
                target === "perfil-content" ? "grid" : "block";
        });
    });

    // ====== PERFIL ======
    const formPerfil = document.getElementById("form-perfil");
    if (formPerfil) {
        formPerfil.addEventListener("submit", async e => {
            e.preventDefault();

            const response = await fetch("", {
                method: "POST",
                body: new FormData(formPerfil),
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const data = await response.json();
            alert(data.mensagem || "Perfil atualizado");
        });
    }

    // ====== SEGURANÇA ======
    const formSeguranca = document.getElementById("form-seguranca");
    if (formSeguranca) {
        formSeguranca.addEventListener("submit", async e => {
            e.preventDefault();

            const response = await fetch("", {
                method: "POST",
                body: new FormData(formSeguranca),
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const data = await response.json();
            alert(data.mensagem || "Senha alterada");
            formSeguranca.reset();
        });
    }

});
