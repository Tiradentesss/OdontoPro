// TROCA DE ABAS
const tabButtons = document.querySelectorAll(".tab-button");
const tabContents = document.querySelectorAll(".tab-content");

tabButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    tabButtons.forEach(b => b.classList.remove("active"));
    tabContents.forEach(c => c.style.display = "none");
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).style.display = "block";
  });
});

// MODAIS
const modal = document.getElementById("agenda-modal");
const modalDados = document.getElementById("dados-consulta-modal");
const modalSucesso = document.getElementById("sucesso-modal");

document.querySelector(".btn-agendar").onclick = () => modal.style.display = "flex";
document.getElementById("fechar-modal").onclick = () => modal.style.display = "none";
document.getElementById("fechar-dados").onclick = () => modalDados.style.display = "none";

document.getElementById("abrirDadosConsulta").onclick = () => {
  modal.style.display = "none";
  modalDados.style.display = "flex";
};

document.getElementById("formDadosConsulta").onsubmit = e => {
  e.preventDefault();
  modalDados.style.display = "none";
  modalSucesso.style.display = "flex";
};

document.getElementById("voltarInicio").onclick = () => {
  modalSucesso.style.display = "none";
  window.scrollTo({ top: 0, behavior: "smooth" });
};

// COMENTÁRIOS
const btnAdicionar = document.getElementById("btnAdicionar");
const novoComentario = document.getElementById("novoComentario");
const listaComentarios = document.getElementById("listaComentarios");

btnAdicionar.addEventListener("click", () => {
  const texto = novoComentario.value.trim();
  if (!texto) {
    alert("Por favor, escreva um comentário antes de adicionar!");
    return;
  }
  const novo = document.createElement("div");
  novo.className = "comentario";
  novo.innerHTML = `<p>${texto}</p><span class="tempo">Comentado agora mesmo</span>`;
  listaComentarios.prepend(novo);
  novoComentario.value = "";
});
