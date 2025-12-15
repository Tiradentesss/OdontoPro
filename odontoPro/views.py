from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse  # CORREÇÃO: sem espaço
from django.contrib.auth.hashers import make_password, check_password
from .models import Paciente, Clinica, Medico, Especialidade, HorarioAberto, DiaSemanaDisponivel, ClinicaServico, Consulta
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.utils.dateparse import parse_datetime
from datetime import date, datetime

def agendar_profissional(request, medico_id):
    medico = get_object_or_404(Medico, id=medico_id)
    clinica = medico.clinica

    if request.method != "POST":
        return JsonResponse({"error": "Método inválido"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))

        data = payload.get("date")
        hora = payload.get("time")
        especialidade = payload.get("especialidade")
        observacoes = payload.get("observacoes", "")

        if not data or not hora:
            return JsonResponse(
                {"success": False, "error": "Data e horário são obrigatórios."},
                status=400
            )

        try:
            data_hora = datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
        except ValueError:
            return JsonResponse(
                {"success": False, "error": "Formato de data/hora inválido."},
                status=400
            )

        # ==========================
        # PACIENTE DA SESSÃO
        # ==========================
        paciente_id = paciente_logado(request)
        if not paciente_id:
            return JsonResponse(
                {"success": False, "error": "Usuário não autenticado."},
                status=401
            )

        paciente = get_object_or_404(Paciente, id=paciente_id)

        consulta = Consulta.objects.create(
            paciente=paciente,
            nome=paciente.nome,
            email=paciente.email,
            telefone=paciente.telefone,
            clinica=clinica,
            medico=medico,
            especialidade=especialidade,
            data_hora=data_hora,
            observacoes=observacoes
        )

        return JsonResponse({
            "success": True,
            "consulta_id": consulta.id,
            "data": data,
            "hora": hora
        })

    except Exception as e:
        return JsonResponse(
            {"success": False, "error": str(e)},
            status=400
        )

def get_horarios_medico(request, medico_id):
    medico = get_object_or_404(Medico, id=medico_id)

    horarios = []

    for dia in medico.clinica.dias_semana.prefetch_related("horarios").all():
        for h in dia.horarios.all():
            horarios.append(
                f"{h.hora_inicio.strftime('%H:%M')} - {h.hora_fim.strftime('%H:%M')}"
            )

    return JsonResponse({"horarios": horarios})

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

        # =========================
        # CRIA A SESSÃO
        # =========================
        request.session["paciente_id"] = paciente.id
        request.session["paciente_nome"] = paciente.nome
        request.session["paciente_email"] = paciente.email

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
    if not paciente_logado(request):
        return redirect("login")

    clinicas = Clinica.objects.all()

    municipios = clinicas.values_list('endereco__cidade', flat=True).distinct()
    bairros = clinicas.values_list('endereco__bairro', flat=True).distinct()

    municipios = [m.strip() for m in municipios if m]
    bairros = [b.strip() for b in bairros if b]

    context = {
        'clinicas': clinicas,
        'municipios': municipios,
        'bairros': bairros,
    }

    return render(request, "MenuPrincipal/tela_menu_principal.html", context)

def configuracoes(request):
    paciente_id = request.session.get("paciente_id")
    if not paciente_id:
        return redirect("login")

    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == "POST":
        tipo = request.POST.get("tipo")

        # ======================
        # PERFIL
        # ======================
        if tipo == "perfil":
            paciente.nome = request.POST.get("nome")
            paciente.cpf = request.POST.get("cpf")
            paciente.email = request.POST.get("email")
            paciente.telefone = request.POST.get("telefone")

            data_nascimento = request.POST.get("data_nascimento")
            if data_nascimento:
                paciente.data_nascimento = data_nascimento

            paciente.save()
            return JsonResponse({"success": True, "mensagem": "Perfil atualizado com sucesso"})

        # ======================
        # SEGURANÇA
        # ======================
        if tipo == "senha":
            nova = request.POST.get("nova_senha")
            confirmar = request.POST.get("confirmar")

            if nova != confirmar:
                return JsonResponse({"success": False, "mensagem": "As senhas não coincidem"})

            paciente.senha = make_password(nova)
            paciente.save()

            return JsonResponse({"success": True, "mensagem": "Senha alterada com sucesso"})

    return render(request, "Configuracoes/Tela_configuracoes.html", {
        "paciente": paciente
    })


def novaSenha(request):
    return render(request, "NovaSenha/NovaSenha.html")

def perfil(request, clinica_id):
    if not paciente_logado(request):
        return redirect("login")

    clinica = get_object_or_404(Clinica, id=clinica_id)
    
    # Pega todos os dias da semana que a clínica funciona
    dias_disponiveis = clinica.dias_semana.prefetch_related('horarios').all()

    # Pega os serviços da clínicalogado
    servicos = ClinicaServico.objects.filter(clinica=clinica)

    context = {
        'clinica': clinica,
        'dias_disponiveis': dias_disponiveis,
        'servicos': servicos,
    }
    return render(request, 'Perfil/perfil.html', context)

def perfilDoProfissional(request, id):
    paciente_id = paciente_logado(request)
    if not paciente_id:
        return redirect("login")

    paciente = get_object_or_404(Paciente, id=paciente_id)
    profissional = get_object_or_404(Medico, id=id)

    especialidades = Especialidade.objects.filter(
        medicos=profissional
    ).distinct()

    context = {
        "paciente": paciente,
        "profissional": profissional,
        "clinica": profissional.clinica,
        "especialidades": especialidades,
        "today": date.today()
    }

    return render(
        request,
        "PerfilDoProfissional/PerfilDoProfissional.html",
        context
    )


def profissionaisDisponiveis(request, clinica_id):
    paciente_id = paciente_logado(request)
    if not paciente_id:
        return redirect("login")
    
    clinica = get_object_or_404(Clinica, id=clinica_id)

    profissionais = Medico.objects.filter(clinica=clinica).prefetch_related("especialidades")

    # especialidades da clínica
    especialidades = Especialidade.objects.filter(
        medicos__in=profissionais
    ).distinct()

    context = {
        "clinica": clinica,
        "profissionais": profissionais,
        "especialidades": especialidades
    }

    return render(request, "ProfissionaisDisponiveis/ProfissionaisDisponiveis.html", context)

def logout(request):
    request.session.flush()
    return redirect("login")

def paciente_logado(request):
    return request.session.get("paciente_id")

def verificarCodigo(request):
    return render(request, "VerificarCodigo/VerificarCodigo.html")

def pagamento(request):
    return render(request, "pagamento/pagamentos.html")

def consultas(request):
    paciente_id = paciente_logado(request)
    if not paciente_id:
        return redirect("login")

    consultas = Consulta.objects.filter(
        paciente_id=paciente_id
    ).order_by("-data_hora")

    return render(request, "Consultas/consultas.html", {
        "consultas": consultas
    })

def cadastroclinica(request):
    return render(request, "Cadastroclinica/clinica-cadastro.html")

@require_POST
def cancelar_consulta(request, consulta_id):
    paciente_id = paciente_logado(request)
    if not paciente_id:
        return JsonResponse({"success": False, "mensagem": "Não autorizado"}, status=403)

    consulta = get_object_or_404(
        Consulta,
        id=consulta_id,
        paciente_id=paciente_id
    )

    # regra simples: só cancelar se ainda não passou
    if consulta.data_hora < timezone.now():
        return JsonResponse({
            "success": False,
            "mensagem": "Não é possível cancelar consultas passadas."
        })

    consulta.status = "cancelada"
    consulta.save()

    return JsonResponse({
        "success": True,
        "mensagem": "Consulta cancelada com sucesso."
    })