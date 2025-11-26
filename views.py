from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Paciente, Clinica

def lista_clinicas(request):
    clinicas = Clinica.objects.all()
    return render(request, 'clinicas.html', {'clinicas': clinicas})

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        try:
            paciente = Paciente.objects.get(email=email)
        except Paciente.DoesNotExist:
            messages.error(request, "Email não encontrado!")
            return render(request, "Login/login.html")

        if not check_password(senha, paciente.senha):
            messages.error(request, "Senha incorreta!")
            return render(request, "Login/login.html")

        return redirect("menuPrincipal")

    return render(request, "Login/login.html")

def criarConta(request):
    if request.method == "POST":

        nome = request.POST.get("nome")
        data_nascimento = request.POST.get("data_nascimento")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        senha = request.POST.get("senha")

        if not nome or not data_nascimento or not email or not telefone or not senha:
            messages.error(request, "Preencha todos os campos.")
            return render(request, "CriarConta/CriarConta.html")

        if Paciente.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está cadastrado.")
            return render(request, "CriarConta/CriarConta.html")

        Paciente.objects.create(
            nome=nome,
            data_nascimento=data_nascimento,
            email=email,
            telefone=telefone,
            senha=make_password(senha),
        )

        messages.success(request, "Conta criada com sucesso! Faça login.")
        return redirect("login")

    return render(request, "CriarConta/CriarConta.html")


def recuperarSenha(request):
    return render(request, "RecuperacaoSenha/tela_recuperacao_senha.html")


def menuPrincipal(request):
    clinicas = Clinica.objects.all()

    # PEGANDO MUNICÍPIO E BAIRRO CORRETOS
    municipios = clinicas.values_list('endereco__cidade', flat=True).distinct()
    bairros = clinicas.values_list('endereco__bairro', flat=True).distinct()

    # LIMPA ESPAÇOS E REMOVE NULLS
    municipios = [m.strip() for m in municipios if m]
    bairros = [b.strip() for b in bairros if b]

    context = {
        'clinicas': clinicas,
        'municipios': municipios,
        'bairros': bairros,
    }

    return render(request, "MenuPrincipal/tela_menu_principal.html", context)


def configuracoes(request):
    return render(request, "Configuracoes/Tela_configuracoes.html")


def novaSenha(request):
    return render(request, "NovaSenha/NovaSenha.html")


def perfil(request, clinica_id):
    clinica = get_object_or_404(Clinica, id=clinica_id)
    return render(request, 'perfil.html', {'clinica': clinica})


def perfilDoProfissional(request):
    return render(request, "PerfilDoProfissional/PerfilDoProfissional.html")


def profissionaisDisponiveis(request):
    return render(request, "ProfissionaisDisponiveis/ProfissionaisDisponiveis.html")


def verificarCodigo(request):
    return render(request, "VerificarCodigo/VerificarCodigo.html")
