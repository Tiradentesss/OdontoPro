from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password

from .models import Paciente


# ---------- LOGIN PACIENTE ----------
def login_paciente(request):
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        # tenta buscar o paciente
        try:
            paciente = Paciente.objects.get(email=email)
        except Paciente.DoesNotExist:
            messages.error(request, "Conta não encontrada. Cadastre-se primeiro.")
            return render(request, "LoginCadastro/login.html")

        # confere senha (HASH)
        if not check_password(senha, paciente.senha):
            messages.error(request, "Senha incorreta.")
            return render(request, "LoginCadastro/login.html")

        # cria sessão manual
        request.session["paciente_id"] = paciente.id

        return redirect("dashboard_paciente")

    return render(request, "LoginCadastro/login.html")


# ---------- LOGIN CLÍNICA ----------
# (mantém por enquanto — usa auth se você estiver usando para clínicas)
from django.contrib.auth import authenticate, login as auth_login

def login_clinica(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        user = authenticate(request, username=email, password=senha)

        if user and hasattr(user, "clinica"):
            auth_login(request, user)
            return redirect('dashboard_clinica')

        messages.error(request, "Login inválido para clínica.")
        return render(request, 'Login/login_clinica.html')

    return render(request, 'Login/login_clinica.html')


# ---------- DASHBOARD PACIENTE ----------
def dashboard_paciente(request):
    paciente_id = request.session.get("paciente_id")

    if not paciente_id:
        return redirect("login_paciente")

    paciente = Paciente.objects.get(id=paciente_id)

    return render(request, "DashboardPaciente/dashboard.html", {
        "paciente": paciente
    })


# ---------- DASHBOARD CLÍNICA ----------
def dashboard_clinica(request):
    return render(request, 'DashboardProfissional/painel.html')


# ---------- LOGOUT ----------
def logout_view(request):
    # limpa sessão do paciente
    request.session.flush()
    logout(request)
    return redirect('login_paciente')
