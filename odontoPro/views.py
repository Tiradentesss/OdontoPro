from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime

from .models import Paciente, Clinica, Consulta, Medico
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from .models import DiaSemanaDisponivel, HorarioAberto

@require_GET
def horarios_clinica(request, clinica_id):
    data = request.GET.get("data")  # yyyy-mm-dd
    if not data:
        return JsonResponse({"error": "Data não informada"}, status=400)

    try:
        data_dt = datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        return JsonResponse({"error": "Data inválida"}, status=400)

    dia_semana_map = {
        0: "segunda",
        1: "terca",
        2: "quarta",
        3: "quinta",
        4: "sexta",
        5: "sabado",
        6: "domingo",
    }

    dia_str = dia_semana_map[data_dt.weekday()]

    try:
        dia = DiaSemanaDisponivel.objects.get(
            clinica_id=clinica_id,
            dia=dia_str
        )
    except DiaSemanaDisponivel.DoesNotExist:
        return JsonResponse({"horarios": []})

    horarios = []
    for h in dia.horarios.all():
        hora = datetime.combine(data_dt, h.hora_inicio)
        while hora.time() < h.hora_fim:
            horarios.append(hora.strftime("%H:%M"))
            hora += timedelta(minutes=30)

    return JsonResponse({"horarios": horarios})


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


# -------- PERFIL CLÍNICA --------
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


# 🔹 RETORNA especialidades e médicos da clínica
@require_GET
def clinica_detalhes(request, clinica_id):
    try:
        clinica = Clinica.objects.get(id=clinica_id)
    except Clinica.DoesNotExist:
        return JsonResponse({"error": "Clínica não encontrada"}, status=404)

    especialidades = set()
    for medico in clinica.medico_set.all():
        for esp in medico.especialidades.all():
            especialidades.add((esp.id, esp.nome))

    medicos = [(m.id, m.nome) for m in clinica.medico_set.all()]

    return JsonResponse({
        "especialidades": list(especialidades),
        "medicos": medicos
    })


# 🔹 AGENDAR CONSULTA (via popup)
@csrf_exempt
@require_POST


def agendar_consulta(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método inválido"})

    clinica_id = request.POST.get("clinica_id")
    medico_id = request.POST.get("medico_id")
    especialidade = request.POST.get("especialidade")
    data_hora_str = request.POST.get("data_hora")
    observacoes = request.POST.get("observacoes", "")

    if not all([clinica_id, medico_id, data_hora_str]):
        return JsonResponse({"success": False, "error": "Dados incompletos"})

    data_hora = parse_datetime(data_hora_str)
    if not data_hora:
        return JsonResponse({"success": False, "error": "Data inválida"})

    clinica = Clinica.objects.get(id=clinica_id)
    medico = Medico.objects.get(id=medico_id)

    # 🔒 evita conflito de horário
    if Consulta.objects.filter(medico=medico, data_hora=data_hora).exists():
        return JsonResponse({"success": False, "error": "Horário indisponível"})

    paciente = None
    nome = email = telefone = ""

    # ✅ PACIENTE LOGADO (via sessão)
    paciente_id = request.session.get("paciente_id")
    if paciente_id:
        paciente = Paciente.objects.get(id=paciente_id)
        nome = paciente.nome
        email = paciente.email
        telefone = paciente.telefone
    else:
        # visitante (mantém compatibilidade)
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")

        if not all([nome, email, telefone]):
            return JsonResponse({"success": False, "error": "Dados do paciente ausentes"})

    Consulta.objects.create(
        paciente=paciente,
        nome=nome,
        email=email,
        telefone=telefone,
        clinica=clinica,
        medico=medico,
        especialidade=especialidade,
        data_hora=data_hora,
        observacoes=observacoes
    )

    return JsonResponse({"success": True})

def configuracoes_conta(request):
    paciente_id = request.session.get('paciente_id')

    if not paciente_id:
        return redirect('login')

    paciente = Paciente.objects.get(id=paciente_id)

    if request.method == 'POST':
        paciente.nome = request.POST.get('nome')
        paciente.email = request.POST.get('email')
        paciente.cpf = request.POST.get('cpf')
        paciente.telefone = request.POST.get('telefone')

        paciente.save()
        messages.success(request, 'Dados atualizados com sucesso!')
        return redirect('configuracoes_conta')

    return redirect('dashboard_paciente')


def alterar_senha_paciente(request):
    paciente_id = request.session.get('paciente_id')

    if not paciente_id:
        return redirect('login')

    paciente = Paciente.objects.get(id=paciente_id)

    if request.method == 'POST':
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not check_password(senha_atual, paciente.senha):
            messages.error(request, 'Senha atual incorreta.')
            return redirect('configuracoes_conta')

        if nova_senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('configuracoes_conta')

        paciente.senha = make_password(nova_senha)
        paciente.save()

        messages.success(request, 'Senha alterada com sucesso!')
        return redirect('configuracoes_conta')
