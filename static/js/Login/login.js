const loginForm = document.getElementById("login-form");
const loginErrorMsg = document.getElementById("login-error-msg");

loginForm.addEventListener("submit", (e) => {
  e.preventDefault();

  const username = loginForm.username.value.trim();
  const password = loginForm.password.value.trim();

  
  loginErrorMsg.style.opacity = 0;


  if (username === "nome@gmail.com" && password === "123456") {
    alert("Você fez login com sucesso.");
    window.location.href = "'../MenuPrincipal/tela_menu_principal.html'";
  } 
  else {
    loginErrorMsg.style.opacity = 1;
  }
});