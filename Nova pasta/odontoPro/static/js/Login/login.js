// Login.js — Validação simples no cliente (não impede o envio real)

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");

  if (!form) return;

  form.addEventListener("submit", (e) => {
      const email = form.email.value.trim();
      const senha = form.senha.value.trim();

      if (email === "" || senha === "") {
          alert("Preencha todos os campos!");
          e.preventDefault();
      }
  });
});
