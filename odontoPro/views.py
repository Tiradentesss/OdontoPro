from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.template.loader import render_to_string

from .models import Paciente, Clinica, Consulta, Medico


# -------- CANCELAR CONSULTA --------
def cancelar_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)
    consulta.status = "cancelada"
    consulta.save()
    messages.success(request, "Consulta cancelada com sucesso!")
    return redirect("dashboard_paciente")


# -------- REAGENDAR CONSULTA --------
def reagendar_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)

    if request.method == "POST":
        nova_data = request.POST.get("data")
        novo_horario = request.POST.get("hora")

        if not nova_data or not novo_horario:
            messages.error(request, "Informe a nova data e horário.")
        else:
            consulta.data_hora = f"{nova_data} {novo_horario}"
            consulta.status = "agendada"
            consulta.save()

            messages.success(request, "Consulta reagendada com sucesso!")
            return redirect("dashboard_paciente")

    return render(request, "DashboardPaciente/reagendar.html", {"consulta": consulta})


def perfil_clinica(request, clinica_id):
    clinica = get_object_or_404(Clinica, id=clinica_id)
    medicos = clinica.medico_set.all() if hasattr(clinica, "medico_set") else []
    consultas = Consulta.objects.filter(clinica=clinica).order_by("-data_hora")[:5]

    return render(request, "Clinica/perfil_clinica.html", {
        "clinica": clinica,
        "medicos": medicos,
        "consultas": consultas,
    })


# ---------- LOGIN PACIENTE ----------
def login_paciente(request):
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        try:
            paciente = Paciente.objects.get(email=email)
        except Paciente.DoesNotExist:
            messages.error(request, "Conta não encontrada. Cadastre-se primeiro.")
            return render(request, "LoginCadastro/login.html")

        if not check_password(senha, paciente.senha):
            messages.error(request, "Senha incorreta.")
            return render(request, "LoginCadastro/login.html")

        request.session["paciente_id"] = paciente.id
        return redirect("dashboard_paciente")

    return render(request, "LoginCadastro/login.html")


# ---------- DASHBOARD PACIENTE ----------
def dashboard_paciente(request):
    paciente_id = request.session.get("paciente_id")
    if not paciente_id:
        return redirect("login_paciente")

    paciente = Paciente.objects.get(id=paciente_id)

    clinicas = Clinica.objects.all().order_by("nome")

    filtro_status = request.GET.get("status")
    consultas = Consulta.objects.filter(paciente=paciente).order_by("-data_hora")

    if filtro_status and filtro_status != "todas":
        consultas = consultas.filter(status=filtro_status)

    context = {
        "paciente": paciente,
        "clinicas": clinicas,
        "consultas": consultas,
        "filtro_status": filtro_status or "todas",
    }

    return render(request, "DashboardPaciente/dashboard.html", context)


# ---------- LOGOUT ----------
def logout_view(request):
    request.session.flush()
    logout(request)
    return redirect("login_paciente")


def login_clinica(request):
    request.session.flush()
    logout(request)
    return redirect("login_paciente")


# 🔹 NOVO — RETORNA APENAS A LISTA FILTRADA (SEM RELOAD)
def filtrar_consultas(request):
    paciente_id = request.session.get("paciente_id")
    paciente = get_object_or_404(Paciente, id=paciente_id)

    status = request.GET.get("status", "todas")

    consultas = Consulta.objects.filter(paciente=paciente).order_by("-data_hora")
    if status != "todas":
        consultas = consultas.filter(status=status)

    html = render_to_string(
        "DashboardPaciente/partials/lista_consultas.html",
        {"consultas": consultas},
        request=request
    )

    return JsonResponse({"html": html})
