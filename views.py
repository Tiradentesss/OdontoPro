from django.shortcuts import render

# Create your views here.
def login(request):
    return render(request, "Login/login.html")

def criarConta(request):
    return render(request, "CriarConta/CriarConta.html")

def recuperarSenha(request):
    return render(request, "RecuperacaoSenha/tela_recuperacao_senha.html")

def menuPrincipal(request):
    return render(request, "MenuPrincipal/tela_menu_principal.html")

def configuracoes(request):
    return render(request, "Configuracoes/Tela_configuracoes.html")

def novaSenha(request):
    return render(request, "NovaSenha/NovaSenha.html")

def perfil(request):
    return render(request, "Perfil/Perfil.html")

def perfilDoProfissional(request):
    return render(request, "PerfilDoProfissional/PerfilDoProfissional.html")

def profissionaisDisponiveis(request):
    return render(request, "ProfissionaisDisponiveis/ProfissionaisDisponiveis.html")

def verificarCodigo(request):
    return render(request, "VerificarCodigo/VerificarCodigo.html")