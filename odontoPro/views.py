from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse  # CORREÇÃO: sem espaço
from django.contrib.auth.hashers import make_password, check_password
from .models import Paciente, Clinica, Medico, Especialidade, HorarioAberto, DiaSemanaDisponivel, ClinicaServico, Consulta
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.dateparse import parse_datetime
from datetime import date, datetime

def agendar_profissional(request, medico_id):
    medico = get_object_or_404(Medico, id=medico_id)
    clinica = medico.clinica

    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8"))

            nome = payload.get("nome")
            email = payload.get("email")
            telefone = payload.get("telefone")
            especialidade = payload.get("especialidade")
            data = payload.get("date")      # YYYY-MM-DD
            hora = payload.get("time")      # HH:MM
            observacoes = payload.get("observacoes", "")

            # validação
            if not all([nome, email, telefone, data, hora]):
                return JsonResponse(
                    {"success": False, "error": "Campos obrigatórios faltando."},
                    status=400
                )

            # juntar data + hora (correção principal)
            try:
                data_hora = datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
            except ValueError:
                return JsonResponse(
                    {"success": False, "error": "Formato de data/hora inválido."},
                    status=400
                )

            # criar consulta
            consulta = Consulta.objects.create(
                nome=nome,
                email=email,
                telefone=telefone,
                clinica=clinica,
                medico=medico,
                especialidade=especialidade,
                data_hora=data_hora,
                observacoes=observacoes
            )

            return JsonResponse({
                "success": True,
                "consulta_id": consulta.id,
                "mensagem": "Consulta agendada com sucesso!",
                "data": data,
                "hora": hora
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    # GET — apenas informações básicas
    return JsonResponse({
        "medico": medico.nome,
        "clinica": clinica.nome,
        "status": "ok"
    })

def get_horarios_medico(request, medico_id):
    medico = get_object_or_404(Medico, id=medico_id)
    requested_date = request.GET.get("date")

    horarios = []

    # Exemplo simples: coletar horários da clínica (ajuste conforme seu modelo real)
    # Aqui eu assumo que clinica.dias_semana é um relacionamento para os dias com horários
    for dia in medico.clinica.dias_semana.prefetch_related("horarios").all():
        for h in dia.horarios.all():
            horarios.append(f"{h.hora_inicio.strftime('%H:%M')} - {h.hora_fim.strftime('%H:%M')}")

    # Se desejar filtrar por requested_date, implemente a lógica aqui (ex.: checar reservas já feitas)
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
    
    # Pega todos os dias da semana que a clínica funciona
    dias_disponiveis = clinica.dias_semana.prefetch_related('horarios').all()

    # Pega os serviços da clínica
    servicos = ClinicaServico.objects.filter(clinica=clinica)

    context = {
        'clinica': clinica,
        'dias_disponiveis': dias_disponiveis,
        'servicos': servicos,
    }
    return render(request, 'Perfil/perfil.html', context)

def perfilDoProfissional(request, id):
    profissional = get_object_or_404(Medico, id=id)
    clinica = profissional.clinica
    # especialidades para dropdown no form (ou apenas as do profissional)
    especialidades = Especialidade.objects.filter(medicos=profissional).distinct()

    context = {
        "profissional": profissional,
        "clinica": clinica,
        "especialidades": especialidades,
        "today": date.today()
    }
    return render(request, "PerfilDoProfissional/PerfilDoProfissional.html", context)



def profissionaisDisponiveis(request, clinica_id):
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



def verificarCodigo(request):
    return render(request, "VerificarCodigo/VerificarCodigo.html")

def pagamento(request):
    return render(request, "pagamento/pagamentos.html")

def consultas(request):
    return render(request, "Consultas/consultas.html")

def cadastroclinica(request):
    return render(request, "Cadastroclinica/clinica-cadastro.html")
