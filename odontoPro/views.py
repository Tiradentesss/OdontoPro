from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.core import signing
from django.conf import settings
from django.core.management import call_command
from django.templatetags.static import static
from django.core.files.storage import default_storage

from .models import Paciente, Clinica, Consulta, Medico, Avaliacao, Endereco, Especialidade, Gerenciamento
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import make_aware
from .models import DiaSemanaDisponivel, HorarioAberto
from PIL import Image
from django.core.exceptions import ValidationError
from django.db import models

import logging
logger = logging.getLogger(__name__)

def _parse_especialidades(post_data):
    especialidades = []
    for nome_esp in post_data.getlist('especialidades') + post_data.getlist('especialidades[]'):
        nome_esp = (nome_esp or '').strip()
        if nome_esp:
            chave = nome_esp.lower()
            if chave not in {e.lower() for e in especialidades}:
                especialidades.append(nome_esp)
    return especialidades

@require_GET
def horarios_clinica(request, clinica_id):
    data = request.GET.get("data")
    
      # yyyy-mm-dd
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
        hora = make_aware(datetime.combine(data_dt, h.hora_inicio))
        hora_fim = h.hora_fim
        while hora.time() < hora_fim:
            horarios.append(hora.strftime("%H:%M"))
            hora += timedelta(minutes=30)

    return JsonResponse({"horarios": horarios})


# -------- CANCELAR CONSULTA --------
@require_POST
def cancelar_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)
    
    # Validar se pode cancelar (só agendada ou confirmada)
    if consulta.status not in ["agendada", "confirmada"]:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": f"Não é possível cancelar uma consulta {consulta.get_status_display().lower()}"})
        messages.error(request, f"Não é possível cancelar uma consulta {consulta.get_status_display().lower()}")
        return redirect("dashboard_paciente")
    
    consulta.status = "cancelada"
    consulta.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"success": True, "message": "Consulta cancelada com sucesso!"})
    
    messages.success(request, "Consulta cancelada com sucesso!")
    return redirect("dashboard_paciente")


@require_POST
def confirmar_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)

    # Só é possível confirmar se estiver agendada
    if consulta.status != 'agendada':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "Só é possível confirmar consultas agendadas."}, status=400)
        messages.error(request, "Só é possível confirmar consultas agendadas.")
        return redirect('painel_profissional')

    consulta.status = 'confirmada'
    consulta.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"success": True, "message": "Consulta confirmada com sucesso!"})

    messages.success(request, "Consulta confirmada com sucesso!")
    return redirect('painel_profissional')


# -------- REAGENDAR CONSULTA --------
def reagendar_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)

    if request.method == "POST":
        # Accept AJAX requests with an ISO datetime in `data_hora`
        data_hora_iso = request.POST.get("data_hora") or request.POST.get("data_hora_iso")
        if data_hora_iso:
            dt = parse_datetime(data_hora_iso)
            if not dt:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({"success": False, "error": "Data inválida"}, status=400)
                messages.error(request, "Data inválida")
            else:
                # make timezone-aware if necessary
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)
                if consulta.status == "perdida":
                    nova_consulta = Consulta.objects.create(
                        paciente=consulta.paciente,
                        nome=consulta.nome,
                        email=consulta.email,
                        telefone=consulta.telefone,
                        clinica=consulta.clinica,
                        medico=consulta.medico,
                        especialidade=consulta.especialidade,
                        observacoes=consulta.observacoes,
                        data_hora=dt,
                        status="agendada",
                    )
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            "success": True,
                            "message": "Consulta reagendada com sucesso!",
                            "data_hora": nova_consulta.data_hora.isoformat(),
                            "status": nova_consulta.status,
                            "new_consulta_id": nova_consulta.id,
                        })
                    messages.success(request, "Consulta reagendada com sucesso!")
                    return redirect("dashboard_paciente")
                consulta.data_hora = dt
                consulta.status = "agendada"
                consulta.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        "success": True,
                        "message": "Consulta reagendada com sucesso!",
                        "data_hora": consulta.data_hora.isoformat(),
                        "status": consulta.status,
                    })
                messages.success(request, "Consulta reagendada com sucesso!")
                return redirect("dashboard_paciente")

        # Fallback legacy POST (se vier em campos separados)
        nova_data = request.POST.get("data")
        novo_horario = request.POST.get("hora")

        if not nova_data or not novo_horario:
            messages.error(request, "Informe a nova data e horário.")
        else:
            dt = parse_datetime(f"{nova_data}T{novo_horario}:00")
            if dt and timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            if consulta.status == "perdida":
                Consulta.objects.create(
                    paciente=consulta.paciente,
                    nome=consulta.nome,
                    email=consulta.email,
                    telefone=consulta.telefone,
                    clinica=consulta.clinica,
                    medico=consulta.medico,
                    especialidade=consulta.especialidade,
                    observacoes=consulta.observacoes,
                    data_hora=dt or consulta.data_hora,
                    status="agendada",
                )
            else:
                consulta.data_hora = dt or consulta.data_hora
                consulta.status = "agendada"
                consulta.save()

            messages.success(request, "Consulta reagendada com sucesso!")
            return redirect("dashboard_paciente")

    return render(request, "DashboardPaciente/reagendar.html", {"consulta": consulta})


# -------- PERFIL CLÍNICA --------
def perfil_clinica(request, clinica_id):
    clinica = get_object_or_404(Clinica, id=clinica_id)
    medicos = Medico.objects.filter(clinica=clinica)
    consultas = Consulta.objects.filter(clinica=clinica).order_by("-data_hora")[:5]

    avaliacoes = Avaliacao.objects.filter(
        clinica=clinica
    ).select_related("paciente").order_by("-data_postagem")

    return render(request, "Clinica/perfil_clinica.html", {
        "clinica": clinica,
        "medicos": medicos,
        "consultas": consultas,
        "avaliacoes": avaliacoes,
    })


# ---------- LOGIN PACIENTE ----------
def login_paciente(request):
    if request.session.get("paciente_id"):
        return redirect("dashboard_paciente")
    if request.session.get("medico_id"):
        return redirect("painel_profissional")

    # unified login endpoint for pacientes and profissionais
    if request.method == "POST":
        raw_email = request.POST.get("email", "") or ""
        senha = request.POST.get("senha", "") or ""

        # normalize input to avoid accidental spaces/case issues
        email = raw_email.strip().lower()

        logger.info(f"login attempt email={email} from {request.META.get('REMOTE_ADDR')}")

        paciente = Paciente.objects.filter(email__iexact=email).first()
        if not paciente:
            messages.error(request, "Conta não encontrada. Cadastre-se primeiro.")
            logger.info("login failed - patient account not found %s", email)
            return render(request, "LoginCadastro/login.html", {"email": raw_email})

        if not check_password(senha, paciente.senha):
            messages.error(request, "Senha incorreta.")
            logger.info("login failed - wrong password for paciente %s", email)
            return render(request, "LoginCadastro/login.html", {"email": raw_email})

        request.session["paciente_id"] = paciente.id
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        try:
            request.session.save()
            logger.info("session saved successfully for paciente %s", email)
        except Exception as e:
            logger.error("error saving session: %s", e, exc_info=True)

        uid_signed = signing.dumps(paciente.id)
        response = redirect("dashboard_paciente")
        response.set_cookie(
            "uid_signed",
            uid_signed,
            max_age=getattr(settings, "SESSION_COOKIE_AGE", 1209600),
            path='/',
            httponly=True,
            samesite=getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax"),
            secure=getattr(settings, "SESSION_COOKIE_SECURE", False),
        )

        logger.info(
            "✓ Login success paciente %s | session_key=%s | uid_signed criado com sucesso",
            email,
            request.session.session_key
        )
        return response

    # GET
    return render(request, "LoginCadastro/login.html")


# ---------- DASHBOARD PACIENTE ----------
def _get_clinica_imagem_url(clinica):
    # prioriza assertiva e evita 404 se o arquivo físico estiver ausente
    if clinica.imagem and getattr(clinica.imagem, 'name', None):
        if default_storage.exists(clinica.imagem.name):
            return clinica.imagem.url

    if clinica.logo and getattr(clinica.logo, 'name', None):
        if default_storage.exists(clinica.logo.name):
            return clinica.logo.url

    primeira = clinica.imagens.order_by('ordem').first()
    if primeira and primeira.imagem and getattr(primeira.imagem, 'name', None):
        if default_storage.exists(primeira.imagem.name):
            return primeira.imagem.url

    return static('img/default-banner.jpg')


def _get_clinica_logo_url(clinica):
    if clinica.logo and getattr(clinica.logo, 'name', None):
        if default_storage.exists(clinica.logo.name):
            return clinica.logo.url

    if clinica.imagem and getattr(clinica.imagem, 'name', None):
        if default_storage.exists(clinica.imagem.name):
            return clinica.imagem.url

    primeira = clinica.imagens.order_by('ordem').first()
    if primeira and primeira.imagem and getattr(primeira.imagem, 'name', None):
        if default_storage.exists(primeira.imagem.name):
            return primeira.imagem.url

        return static('img/default-clinic-logo.svg')


def dashboard_paciente(request):
    paciente_id = request.session.get("paciente_id")

    # Tentar restaurar sessão a partir de UID assinado caso o cookie de sessão tenha sido perdido.
    if not paciente_id:
        signed = request.COOKIES.get("uid_signed")
        if signed:
            try:
                paciente_id = signing.loads(signed)
                if Paciente.objects.filter(id=paciente_id).exists():
                    request.session["paciente_id"] = paciente_id
                    request.session.save()
            except signing.BadSignature:
                paciente_id = None

    logger.debug("dashboard access session_key=%s paciente_id=%s cookies=%s",
                 request.session.session_key, paciente_id,
                 request.META.get('HTTP_COOKIE'))

    if not paciente_id:
        return redirect("login_paciente")

    paciente = Paciente.objects.get(id=paciente_id)
    clinicas = Clinica.objects.prefetch_related('imagens').all().order_by("nome")

    for c in clinicas:
        c.banner_url = _get_clinica_imagem_url(c)
        c.logo_url = _get_clinica_logo_url(c)

    # Se não houver clínica cadastrada, mantém lista vazia (evita criação automática de clínica de exemplo).
    if not clinicas.exists():
        messages.info(request, "Nenhuma clínica cadastrada foi encontrada. Não serão criadas clínicas automaticamente.")

    # prepare signed uid para settings forms so it is always disponível
    uid_signed = signing.dumps(paciente.id)

    filtro_status = request.GET.get("status")
    aba_ativa = request.GET.get("aba", "inicio")
    consultas = Consulta.objects.filter(paciente=paciente).order_by("-data_hora")
    agora = timezone.now()

    consultas_futuras = Consulta.objects.filter(
        paciente=paciente,
        data_hora__gte=agora,
        status__in=["agendada", "confirmada"]
    ).order_by("data_hora")

    # Notificações: consultas próximas (1 dia antes, mesmo dia, 1 hora antes) ou canceladas recentemente
    notificacoes = Consulta.objects.filter(
        (
            models.Q(
                data_hora__gte=agora - timedelta(days=1),
                data_hora__lte=agora + timedelta(days=1),
                status__in=["agendada", "confirmada"]
            ) |
            models.Q(
                status="cancelada",
                criado_em__gte=agora - timedelta(days=7)  # canceladas nos últimos 7 dias
            )
        ),
        paciente=paciente
    ).order_by("-data_hora")

    tem_notificacao = notificacoes.exists()

    if filtro_status and filtro_status != "todas" and filtro_status != "perdidas":
        consultas = consultas.filter(status=filtro_status)

    especialidades_consultas = Consulta.objects.filter(
        paciente=paciente
    ).exclude(especialidade__isnull=True).values_list(
        "especialidade__id",
        "especialidade__nome"
    ).distinct().order_by("especialidade__nome")

    context = {
        "paciente": paciente,
        "clinicas": clinicas,
        "consultas": consultas,
        "filtro_status": filtro_status or "todas",
        "consultas_futuras": consultas_futuras,
        "notificacoes": notificacoes,
        "tem_notificacao": tem_notificacao,
        "aba_ativa": aba_ativa,
        "uid_signed": uid_signed,
        "especialidades_consultas": especialidades_consultas,
        "debug_mode": settings.DEBUG,
        "debug_session_key": request.session.session_key,
        "debug_cookie_session": request.COOKIES.get(settings.SESSION_COOKIE_NAME),
        "debug_cookie_uid_signed": request.COOKIES.get("uid_signed"),
    }

    return render(request, "DashboardPaciente/dashboard.html", context)


def painel_profissional(request):
    medico_id = request.session.get('medico_id')
    gerente_id = request.session.get('gerente_id')
    clinica_id = request.session.get('clinica_id')

    if not (medico_id or gerente_id or clinica_id):
        messages.error(request, "Faça login como profissional para acessar o painel.")
        return redirect('login_clinica')

    if medico_id:
        profissional = Medico.objects.filter(id=medico_id).first()
        if not profissional:
            messages.error(request, "Profissional não encontrado.")
            return redirect('login_paciente')
        account_type = 'medico'
    elif gerente_id:
        profissional = Gerenciamento.objects.filter(id=gerente_id).select_related('clinica').first()
        if not profissional:
            messages.error(request, "Gerente não encontrado.")
            return redirect('login_paciente')
        account_type = 'gerente'
    else:
        profissional = Clinica.objects.filter(id=clinica_id).first()
        if not profissional:
            messages.error(request, "Clínica não encontrada.")
            return redirect('login_paciente')
        account_type = 'clinica'

    # determina a clínica associada ao usuário atual
    if account_type == 'medico':
        clinica_obj = profissional.clinica
    elif account_type == 'gerente':
        clinica_obj = profissional.clinica
    else:
        clinica_obj = profissional

    if request.method == 'POST' and request.POST.get('form_type') == 'clinica_config':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        cnpj = request.POST.get('cnpj', '').strip()
        conta_bancaria = request.POST.get('conta_bancaria', '').strip()
        preco_consulta = request.POST.get('preco_consulta', '').strip()
        rua = request.POST.get('endereco_rua', '').strip()
        numero = request.POST.get('endereco_numero', '').strip()
        bairro = request.POST.get('endereco_bairro', '').strip()
        cidade = request.POST.get('endereco_cidade', '').strip()
        estado = request.POST.get('endereco_estado', '').strip()
        cep = request.POST.get('endereco_cep', '').strip()

        if nome:
            clinica_obj.nome = nome
        if email:
            clinica_obj.email = email
        if telefone:
            clinica_obj.telefone = telefone
        clinica_obj.descricao = descricao
        clinica_obj.cnpj = cnpj
        clinica_obj.conta_bancaria_juridica = conta_bancaria
        if preco_consulta:
            try:
                clinica_obj.preco_consulta = float(preco_consulta.replace(',', '.'))
            except ValueError:
                pass

        if rua or numero or bairro or cidade or estado or cep:
            endereco = clinica_obj.endereco
            if not endereco:
                endereco = Endereco.objects.create(cep=cep or '', numero=numero or '', rua=rua or '')
                clinica_obj.endereco = endereco
            endereco.rua = rua or endereco.rua
            endereco.numero = numero or endereco.numero
            endereco.bairro = bairro or endereco.bairro
            endereco.cidade = cidade or endereco.cidade
            endereco.estado = estado or endereco.estado
            endereco.cep = cep or endereco.cep
            endereco.save()

        if request.POST.get('senha') or request.POST.get('confirmar_senha'):
            senha = request.POST.get('senha', '').strip()
            confirmar_senha = request.POST.get('confirmar_senha', '').strip()
            if senha or confirmar_senha:
                if senha != confirmar_senha:
                    messages.error(request, 'As senhas não coincidem.')
                    return redirect('painel_profissional')
                clinica_obj.senha = make_password(senha)

        especialidades_post = _parse_especialidades(request.POST)
        precos_post = request.POST.getlist('precos_especialidades[]')

        # Criar mapa de especialidades com seus preços
        esp_preco_map = {}
        for i, nome_esp in enumerate(especialidades_post):
            preco = precos_post[i] if i < len(precos_post) else '0'
            try:
                preco_float = float(preco.replace(',', '.')) if preco else 0
            except (ValueError, AttributeError):
                preco_float = 0
            esp_preco_map[nome_esp] = preco_float

        existing_especialidades = {esp.nome.strip().lower(): esp for esp in clinica_obj.especialidades.all()}
        
        # Atualizar e criar especialidades
        for nome_esp, preco in esp_preco_map.items():
            chave = nome_esp.strip().lower()
            if chave in existing_especialidades:
                # Atualizar preço se já existe
                esp_obj = existing_especialidades[chave]
                esp_obj.preco = preco
                esp_obj.save()
            else:
                # Criar nova especialidade com preço
                Especialidade.objects.create(clinica=clinica_obj, nome=nome_esp, preco=preco)

        # Remover especialidades não listadas
        remove_names = [nome for nome in existing_especialidades if nome not in {esp.lower() for esp in esp_preco_map.keys()}]
        if remove_names:
            Especialidade.objects.filter(clinica=clinica_obj, nome__in=remove_names).delete()

        if request.FILES.get('logo'):
            clinica_obj.logo = request.FILES['logo']
        if request.FILES.get('banner'):
            clinica_obj.imagem = request.FILES['banner']

        clinica_obj.save()
        messages.success(request, 'Dados da clínica atualizados com sucesso.')
        return redirect('painel_profissional')

    now = timezone.now()
    consultas = Consulta.objects.filter(
        clinica=clinica_obj,
        data_hora__gte=now
    ).select_related('paciente', 'medico', 'especialidade').order_by('data_hora')[:12]

    clinica_obj.logo_url = _get_clinica_logo_url(clinica_obj)
    clinica_obj.banner_url = _get_clinica_imagem_url(clinica_obj)
    clinica_obj.endereco_text = str(clinica_obj.endereco) if clinica_obj.endereco else ''

    return render(request, "DashboardProfissional/painel.html", {
        "profissional": profissional,
        "account_type": account_type,
        "consultas": consultas,
        "clinica": clinica_obj,
    })


# ---------- LOGOUT ----------
@require_POST
def logout_view(request):
    is_professional = bool(
        request.session.get('clinica_id')
        or request.session.get('medico_id')
        or request.session.get('gerente_id')
    )
    request.session.flush()
    logout(request)
    target = 'login_clinica' if is_professional else 'login_paciente'
    response = redirect(target)
    response.delete_cookie("uid_signed", path="/")
    return response


# kept for backwards compatibility, but the main login logic is now in login_paciente
# which handles both patients and professionals.
def login_clinica(request):
    if request.session.get("medico_id") or request.session.get("gerente_id") or request.session.get("clinica_id"):
        return redirect("painel_profissional")

    if request.method == "POST":
        raw_email = request.POST.get("email", "") or ""
        senha = request.POST.get("senha", "") or ""
        email = raw_email.strip().lower()

        logger.info(f"professional login attempt email={email} from {request.META.get('REMOTE_ADDR')}")

        clinica = Clinica.objects.filter(email__iexact=email).first()
        if clinica:
            if not check_password(senha, clinica.senha):
                messages.error(request, "Senha incorreta.")
                logger.info("login failed - wrong password for clinica %s", email)
                return render(request, "LoginCadastro/login_profissional.html", {"email": raw_email})

            request.session["clinica_id"] = clinica.id
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            try:
                request.session.save()
            except Exception as e:
                logger.error("error saving session: %s", e, exc_info=True)
            logger.info("login success clinica %s session_key=%s", email, request.session.session_key)
            return redirect("painel_profissional")

        gerente = Gerenciamento.objects.filter(email__iexact=email, ativo=True).select_related("clinica").first()
        if gerente:
            if not check_password(senha, gerente.senha):
                messages.error(request, "Senha incorreta.")
                logger.info("login failed - wrong password for gerente %s", email)
                return render(request, "LoginCadastro/login_profissional.html", {"email": raw_email})

            required_permission = "acesso_gerenciamento"
            if not gerente.permissoes.filter(codigo=required_permission).exists():
                messages.error(request, "Acesso negado. Gerente não tem permissão de gerenciamento.")
                logger.info("login failed - gerente without required permission %s", email)
                return render(request, "LoginCadastro/login_profissional.html", {"email": raw_email})

            request.session["gerente_id"] = gerente.id
            request.session["clinica_id"] = gerente.clinica.id
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            try:
                request.session.save()
            except Exception as e:
                logger.error("error saving session: %s", e, exc_info=True)
            logger.info("login success gerente %s session_key=%s", email, request.session.session_key)
            return redirect("painel_profissional")

        messages.error(request, "Conta profissional não encontrada.")
        logger.info("login failed - professional account not found %s", email)
        return render(request, "LoginCadastro/login_profissional.html", {"email": raw_email})

    return render(request, "LoginCadastro/login_profissional.html")


# 🔹 NOVO — RETORNA APENAS A LISTA FILTRADA (SEM RELOAD)
def filtrar_consultas(request):
    paciente_id = request.session.get("paciente_id")
    paciente = get_object_or_404(Paciente, id=paciente_id)

    status = request.GET.get("status", "todas")

    consultas = Consulta.objects.filter(paciente=paciente).order_by("-data_hora")
    if status != "todas" and status != "perdidas":
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
            especialidades.add((esp.id, esp.nome, float(esp.preco) if esp.preco else 0))

    medicos = [
        {
            "id": m.id,
            "nome": m.nome,
            "foto_url": m.foto.url if m.foto else None,
            "especialidades": [esp.id for esp in m.especialidades.all()]
        }
        for m in clinica.medico_set.all()
    ]


    # 🔹 BUSCAR AVALIAÇÕES APENAS DESSA CLÍNICA
    avaliacoes = Avaliacao.objects.filter(
        clinica=clinica
    ).select_related("paciente").order_by("-data_postagem")

    avaliacoes_json = [
        {
            "paciente": av.paciente.nome,
            "medico": av.medico.nome if av.medico else "",
            "nota": av.nota,
            "comentario": av.comentario,
            "data": av.data_postagem.strftime("%d/%m/%Y")
        }
        for av in avaliacoes
    ]

    # Prioridade lógica para imagem de banner
    banner_url = None
    imagens = []

    if clinica.imagens.exists():
        imagens = [img.imagem.url for img in clinica.imagens.all() if img.imagem]
        banner_url = imagens[0] if imagens else None
    elif clinica.imagem:
        imagens = [clinica.imagem.url]
        banner_url = clinica.imagem.url
    elif clinica.logo:
        imagens = [clinica.logo.url]
        banner_url = clinica.logo.url

    return JsonResponse({
    "nome": clinica.nome,
    "email": clinica.email,
    "telefone": clinica.telefone,
    "descricao": clinica.descricao,
    "logo_url": clinica.logo.url if clinica.logo else None,
    "imagem_url": clinica.imagem.url if clinica.imagem else None,
    "banner_url": banner_url,
    "images": imagens,
    "rua": clinica.endereco.rua,
    "numero": clinica.endereco.numero,
    "bairro": clinica.endereco.bairro,
    "cidade": clinica.endereco.cidade,
    "estado": clinica.endereco.estado,
    "cep": clinica.endereco.cep,
    "especialidades": list(especialidades),
    "medicos": medicos,
    "avaliacoes": avaliacoes_json
    })



def agendar_consulta(request):
    # --- diagnóstico e restauração de sessão semelhante ao que fazemos em configuracoes_conta ---
    logger.info("[AGENDAR] método=%s cookies=%s POST-keys=%s",
                request.method,
                request.META.get('HTTP_COOKIE'),
                list(request.POST.keys()))

    paciente_id = request.session.get('paciente_id')
    if request.method == 'POST' and not paciente_id:
        signed = request.POST.get('uid')
        logger.debug("[AGENDAR] signed uid from POST: %r", signed)
        if signed:
            try:
                restored = signing.loads(signed)
                paciente_id = restored
                request.session['paciente_id'] = paciente_id
                try:
                    request.session.save()
                except Exception as ex:
                    logger.error("[AGENDAR] erro salvando sessão restaurada: %s", ex, exc_info=True)
                logger.warning("[AGENDAR] sessão perdida, restaurada via uid assinada: %s", paciente_id)
            except signing.BadSignature:
                logger.warning("[AGENDAR] uid inválido fornecido: %r", signed)

    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método inválido"})

    clinica_id = request.POST.get("clinica_id")
    medico_id = request.POST.get("medico_id")
    especialidade_id = request.POST.get("especialidade")
    data_hora_str = request.POST.get("data_hora")
    observacoes = request.POST.get("observacoes", "")

    if not all([clinica_id, medico_id, data_hora_str, especialidade_id]):
        return JsonResponse({"success": False, "error": "Dados incompletos"})

    data_hora = parse_datetime(data_hora_str)
    if not data_hora:
        return JsonResponse({"success": False, "error": "Data inválida"})

    try:
        clinica = Clinica.objects.get(id=clinica_id)
        medico = Medico.objects.get(id=medico_id)
    except (Clinica.DoesNotExist, Medico.DoesNotExist):
        return JsonResponse({"success": False, "error": "Clínica ou médico não encontrado"}, status=404)

    try:
        especialidade = Especialidade.objects.get(id=especialidade_id, clinica=clinica)
    except Especialidade.DoesNotExist:
        return JsonResponse({"success": False, "error": "Especialidade não encontrada"}, status=404)

    if not medico.especialidades.filter(id=especialidade.id).exists():
        return JsonResponse({"success": False, "error": "Médico não atende à especialidade selecionada"}, status=400)

    # 🔒 evita conflito de horário
    if Consulta.objects.filter(medico=medico, data_hora=data_hora).exists():
        return JsonResponse({"success": False, "error": "Horário indisponível"})

    paciente = None
    nome = request.POST.get("nome", "")
    email = request.POST.get("email", "")
    telefone = request.POST.get("telefone", "")

    # ✅ PACIENTE LOGADO (via sessão)
    if paciente_id:
        try:
            paciente = Paciente.objects.get(id=paciente_id)
            if not nome:
                nome = paciente.nome
            if not email:
                email = paciente.email
            if not telefone:
                telefone = paciente.telefone
        except Paciente.DoesNotExist:
            return JsonResponse({"success": False, "error": "Paciente não encontrado"}, status=404)
    else:
        # visitante (mantém compatibilidade)
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
    """View para gerenciar as configurações da conta do paciente"""

    # ===== VERIFICAR AUTENTICAÇÃO =====
    paciente_id = request.session.get('paciente_id')

    # Durante POST, se existe uid assinado (mesmo com sessão corrente), devemos validar.
    if request.method == 'POST':
        signed_uid = request.POST.get('uid')
        if signed_uid:
            try:
                paciente_id_from_uid = signing.loads(signed_uid)
                if Paciente.objects.filter(id=paciente_id_from_uid).exists():
                    paciente_id = paciente_id_from_uid
                    request.session['paciente_id'] = paciente_id
                    request.session.save()
                else:
                    # uid inválido/inexistente: limpar sessão e exigir novo login
                    request.session.flush()
                    messages.error(request, "Sua sessão expirou. Faça login novamente.")
                    return redirect('login_paciente')
            except signing.BadSignature:
                logger.warning("uid inválido fornecido ao tentar restaurar sessão em configuracoes_conta: %s", signed_uid)
                request.session.flush()
                messages.error(request, "Sua sessão expirou. Faça login novamente.")
                return redirect('login_paciente')

    if not paciente_id:
        messages.error(request, "Sua sessão expirou. Faça login novamente.")
        return redirect('login_paciente')

    try:
        paciente = Paciente.objects.get(id=paciente_id)
    except Paciente.DoesNotExist:
        messages.error(request, "Paciente não encontrado.")
        request.session.flush()
        return redirect('login_paciente')

    # ===== PROCESSAR POST =====
    saved = False
    if request.method == 'POST':
        # Pegar todos os valores do formulário
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        cpf = request.POST.get('cpf', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        sexo = request.POST.get('sexo', '').strip()
        data_nascimento = request.POST.get('data_nascimento', '').strip()

        # Validar campos obrigatórios
        if not nome:
            messages.error(request, 'Nome é obrigatório.')
        elif not email:
            messages.error(request, 'Email é obrigatório.')
        else:
            # Email válido e preenchido
            try:
                # Verificar se email já existe (excluindo o próprio paciente)
                if email.lower() != paciente.email.lower():
                    if Paciente.objects.filter(email__iexact=email).exclude(id=paciente.id).exists():
                        messages.error(request, 'Este email já está registrado por outra conta.')
                    else:
                        # Email ok, atualizar dados
                        paciente.nome = nome
                        paciente.email = email.lower()
                        if cpf:
                            paciente.cpf = cpf
                        if telefone:
                            paciente.telefone = telefone
                        if sexo:
                            paciente.sexo = sexo
                        if data_nascimento:
                            paciente.data_nascimento = data_nascimento

                        # Processar foto
                        if 'foto' in request.FILES and request.FILES['foto'].size > 0:
                            arquivo = request.FILES['foto']
                            logger.info(f"[FOTO] Arquivo recebido: {arquivo.name}, tamanho: {arquivo.size} bytes")
                            if arquivo.size > 5 * 1024 * 1024:
                                messages.error(request, 'Foto muito grande (máximo 5MB).')
                            else:
                                try:
                                    # Verificar se é uma imagem válida
                                    img = Image.open(arquivo)
                                    img.verify()
                                    arquivo.seek(0)
                                    
                                    # Salvar a foto
                                    paciente.foto = arquivo
                                    paciente.save()
                                    
                                    # Verificar se o arquivo foi realmente salvo
                                    if paciente.foto and paciente.foto.url:
                                        logger.info(f"[FOTO] Foto salva com sucesso para paciente {paciente_id}: {paciente.foto.url}")
                                        messages.success(request, 'Dados atualizados com sucesso (com foto)!')
                                    else:
                                        logger.error(f"[FOTO] Foto não foi salva corretamente para paciente {paciente_id}")
                                        messages.error(request, 'Erro ao salvar a foto. Tente novamente.')
                                        return redirect('configuracoes_conta')
                                    
                                    request.session.save()
                                    saved = True
                                    
                                except Exception as e:
                                    logger.error(f"[FOTO] Erro ao processar imagem para paciente {paciente_id}: {str(e)}", exc_info=True)
                                    messages.error(request, f'Imagem inválida. Tente outra. Erro: {str(e)}')
                        else:
                            logger.info(f"[FOTO] Nenhum arquivo de foto enviado ou arquivo vazio")
                            # Salvar sem foto
                            paciente.save()
                            request.session.save()
                            saved = True
                            messages.success(request, 'Dados atualizados com sucesso!')
                else:
                    # Email não mudou, apenas atualizar outros dados
                    paciente.nome = nome
                    paciente.email = email.lower()
                    if cpf:
                        paciente.cpf = cpf
                    if telefone:
                        paciente.telefone = telefone
                    if sexo:
                        paciente.sexo = sexo
                    if data_nascimento:
                        paciente.data_nascimento = data_nascimento

                    # Processar foto
                    if 'foto' in request.FILES and request.FILES['foto'].size > 0:
                        arquivo = request.FILES['foto']
                        logger.info(f"[FOTO] Arquivo recebido: {arquivo.name}, tamanho: {arquivo.size} bytes")
                        if arquivo.size > 5 * 1024 * 1024:
                            messages.error(request, 'Foto muito grande (máximo 5MB).')
                        else:
                            try:
                                # Verificar se é uma imagem válida
                                img = Image.open(arquivo)
                                img.verify()
                                arquivo.seek(0)
                                
                                # Salvar a foto
                                paciente.foto = arquivo
                                paciente.save()
                                
                                # Verificar se o arquivo foi realmente salvo
                                if paciente.foto and paciente.foto.url:
                                    logger.info(f"[FOTO] Foto salva com sucesso para paciente {paciente_id}: {paciente.foto.url}")
                                    messages.success(request, 'Dados atualizados com sucesso (com foto)!')
                                else:
                                    logger.error(f"[FOTO] Foto não foi salva corretamente para paciente {paciente_id}")
                                    messages.error(request, 'Erro ao salvar a foto. Tente novamente.')
                                    return redirect('configuracoes_conta')
                                
                                request.session.save()
                                saved = True
                                
                            except Exception as e:
                                logger.error(f"[FOTO] Erro ao processar imagem para paciente {paciente_id}: {str(e)}", exc_info=True)
                                messages.error(request, f'Imagem inválida. Tente outra. Erro: {str(e)}')
                    else:
                        logger.info(f"[FOTO] Nenhum arquivo de foto enviado ou arquivo vazio")
                        # Salvar sem foto
                        paciente.save()
                        request.session.save()
                        saved = True
                        messages.success(request, 'Dados atualizados com sucesso!')
            except Exception as e:
                logger.error(f"Erro ao atualizar paciente {paciente_id}: {str(e)}", exc_info=True)
                messages.error(request, 'Erro ao salvar alterações. Tente novamente.')

        # Se salvou com sucesso, reemite o cookie de recuperação e redireciona para dashboard (aba ajustes)
        if saved:
            uid_signed = signing.dumps(paciente.id)
            redirect_url = reverse('dashboard_paciente') + '?open=ajustes'
            response = redirect(redirect_url)
            response.set_cookie(
                "uid_signed",
                uid_signed,
                max_age=getattr(settings, "SESSION_COOKIE_AGE", 1209600),
                path='/',
                httponly=True,
                samesite=getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax"),
                secure=getattr(settings, "SESSION_COOKIE_SECURE", False),
            )
            logger.info(
                "✓ Configurações salvas para paciente %s | uid_signed recriado com sucesso",
                paciente_id
            )
            return response

    # ===== PREPARAR CONTEXTO =====
    clinicas = Clinica.objects.all().order_by("nome")
    consultas = Consulta.objects.filter(paciente=paciente).order_by("-data_hora")
    agora = timezone.now()
    consultas_futuras = Consulta.objects.filter(
        paciente=paciente,
        data_hora__gte=agora,
        status__in=["agendada", "confirmada"]
    ).order_by("data_hora")

    tem_notificacao = consultas_futuras.exists()
    uid_signed = signing.dumps(paciente.id)

    context = {
        "paciente": paciente,
        "clinicas": clinicas,
        "consultas": consultas,
        "consultas_futuras": consultas_futuras,
        "tem_notificacao": tem_notificacao,
        "uid_signed": uid_signed,
        "aba_ativa": "ajustes",
        "debug_mode": settings.DEBUG,
        "debug_session_key": request.session.session_key,
        "debug_cookie_session": request.COOKIES.get(settings.SESSION_COOKIE_NAME),
        "debug_cookie_uid_signed": request.COOKIES.get("uid_signed"),
    }

    return render(request, "DashboardPaciente/dashboard.html", context)



def alterar_senha_paciente(request):
    paciente_id = request.session.get('paciente_id')

    if not paciente_id:
        messages.error(request, "Sua sessão expirou. Faça login novamente.")
        return redirect('login_paciente')

    try:
        paciente = Paciente.objects.get(id=paciente_id)
    except Paciente.DoesNotExist:
        messages.error(request, "Paciente não encontrado.")
        return redirect('login_paciente')

    if request.method == 'POST':
        senha_atual = request.POST.get('senha_atual', '').strip()
        nova_senha = request.POST.get('nova_senha', '').strip()
        confirmar_senha = request.POST.get('confirmar_senha', '').strip()

        senha_alterada = False

        # Validações
        try:
            if not senha_atual:
                messages.error(request, 'Informe sua senha atual.')
            elif not check_password(senha_atual, paciente.senha):
                messages.error(request, 'Senha atual incorreta.')
            elif not nova_senha:
                messages.error(request, 'Informe a nova senha.')
            elif nova_senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem.')
            elif len(nova_senha) < 6:
                messages.error(request, 'A senha deve ter no mínimo 6 caracteres.')
            else:
                # Tudo validado, salvar nova senha
                paciente.senha = make_password(nova_senha)
                paciente.save()
                # manter sessão viva explicita
                try:
                    request.session.save()
                except Exception as ex:
                    logger.error("[SENHA] erro salvando sessão após update: %s", ex, exc_info=True)
                messages.success(request, 'Senha alterada com sucesso!')
                logger.info(f"[SENHA] Senha do paciente {paciente_id} alterada")
                senha_alterada = True
        except Exception as e:
            logger.error(f"[SENHA] Erro: {str(e)}", exc_info=True)
            messages.error(request, f'Erro ao alterar senha: {str(e)}')

        if senha_alterada:
            return redirect('configuracoes_conta')

    # Preparar contexto para renderizar a página de configurações
    clinicas = Clinica.objects.all().order_by("nome")
    consultas = Consulta.objects.filter(paciente=paciente).order_by("-data_hora")
    agora = timezone.now()
    consultas_futuras = Consulta.objects.filter(
        paciente=paciente,
        data_hora__gte=agora,
        status__in=["agendada", "confirmada"]
    ).order_by("data_hora")

    # gerar UID assinado para possibilitar restauração de sessão caso ela se perca
    uid_signed = signing.dumps(paciente.id)

    tem_notificacao = consultas_futuras.exists()

    context = {
        "paciente": paciente,
        "clinicas": clinicas,
        "consultas": consultas,
        "consultas_futuras": consultas_futuras,
        "tem_notificacao": tem_notificacao,
        "uid_signed": uid_signed,
        "aba_ativa": "ajustes",
        "debug_mode": settings.DEBUG,
        "debug_session_key": request.session.session_key,
        "debug_cookie_session": request.COOKIES.get(settings.SESSION_COOKIE_NAME),
        "debug_cookie_uid_signed": request.COOKIES.get("uid_signed"),
    }
    return render(request, "DashboardPaciente/dashboard.html", context)


def home(request):
    """Simple home page layout (placeholder).

    This view renders a static marketing-like home screen. Functionality
    (downloads / redirects) can be wired later.
    """
    # Determine user type: patient vs professional/clinic
    is_patient = bool(request.session.get("paciente_id"))
    is_professional = bool(request.user.is_authenticated or request.session.get("medico_id"))
    logged_in = is_patient or is_professional

    featured_clinics = list(
        Clinica.objects.filter(ativo=True, avaliacao__gte=4.0)
        .select_related("endereco")
        .prefetch_related("imagens")
        .order_by("-avaliacao", "-num_avaliacoes", "nome")
    )

    for clinica in featured_clinics:
        first_image = clinica.imagens.first()

        if clinica.logo:
            clinica.display_image = clinica.logo.url
        elif clinica.imagem:
            clinica.display_image = clinica.imagem.url
        elif first_image:
            clinica.display_image = first_image.imagem.url
        else:
            clinica.display_image = static("img/default-banner.jpg")

        if clinica.endereco:
            location_parts = [part for part in [clinica.endereco.cidade, clinica.endereco.bairro] if part]
            clinica.location = ", ".join(location_parts) or "Localização não informada"
        else:
            clinica.location = "Localização não informada"

    display_featured_clinics = []
    if featured_clinics:
        while len(display_featured_clinics) < 4:
            display_featured_clinics.extend(featured_clinics)
        display_featured_clinics = display_featured_clinics[:4]

    return render(request, "home.html", {
        "logged_in": logged_in,
        "is_patient": is_patient,
        "is_professional": is_professional,
        "featured_clinics": display_featured_clinics,
    })


def download_desktop(request):
    return render(request, "download_desktop.html")


def gerenciar_clinicas(request):
    """Lista todas as clínicas para gerenciamento"""
    clinicas = Clinica.objects.all().order_by('nome')
    return render(request, 'Clinica/gerenciar_clinicas.html', {'clinicas': clinicas})


def editar_clinica(request, clinica_id):
    """Editar logo e imagens de uma clínica"""
    clinica = get_object_or_404(Clinica, id=clinica_id)
    
    if request.method == 'POST':
        # Atualizar logo
        if 'logo' in request.FILES:
            clinica.logo = request.FILES['logo']
        
        clinica.save()
        messages.success(request, f'Clínica {clinica.nome} atualizada com sucesso!')
        return redirect('editar_clinica', clinica_id=clinica_id)
    
    imagens = clinica.imagens.all().order_by('ordem')
    return render(request, 'Clinica/editar_clinica.html', {
        'clinica': clinica,
        'imagens': imagens,
    })


def adicionar_imagem_clinica(request, clinica_id):
    """Adicionar nova imagem à clínica"""
    clinica = get_object_or_404(Clinica, id=clinica_id)
    
    if request.method == 'POST' and 'imagem' in request.FILES:
        from .models import ClinicaImagem
        ordem = clinica.imagens.count() + 1
        ClinicaImagem.objects.create(
            clinica=clinica,
            imagem=request.FILES['imagem'],
            ordem=ordem
        )
        messages.success(request, 'Imagem adicionada com sucesso!')
        return redirect('editar_clinica', clinica_id=clinica_id)
    
    return redirect('editar_clinica', clinica_id=clinica_id)


def deletar_imagem_clinica(request, imagem_id):
    """Deletar imagem da clínica"""
    from .models import ClinicaImagem
    imagem = get_object_or_404(ClinicaImagem, id=imagem_id)
    clinica_id = imagem.clinica.id
    
    if request.method == 'POST':
        imagem.delete()
        messages.success(request, 'Imagem removida com sucesso!')
    
    return redirect('editar_clinica', clinica_id=clinica_id)


def cadastrar_paciente(request):
    if request.method != "POST":
        return redirect("login_paciente")

    nome = request.POST.get("nome")
    email = request.POST.get("email")
    senha = request.POST.get("senha")
    confirmar = request.POST.get("confirmar_senha")

    if not all([nome, email, senha, confirmar]):
        messages.error(request, "Preencha todos os campos.")
        return redirect("login_paciente")

    if senha != confirmar:
        messages.error(request, "As senhas não coincidem.")
        return redirect("login_paciente")

    if Paciente.objects.filter(email=email).exists():
        messages.error(request, "Este e-mail já está cadastrado.")
        return redirect("login_paciente")

    paciente = Paciente.objects.create(
        nome=nome,
        email=email,
        senha=make_password(senha),
        telefone=""  # pode ajustar depois
    )

    request.session["paciente_id"] = paciente.id
    messages.success(request, "Conta criada com sucesso!")
    return redirect("configuracoes_conta")


@require_POST
def criar_avaliacao(request):
    """
    Cria ou atualiza a avaliação de uma consulta.
    Espera: consulta_id, nota, comentario (opcional)
    """

    import logging
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from .models import Avaliacao, Consulta

    logger = logging.getLogger(__name__)

    try:
        consulta_id = request.POST.get("consulta_id")
        nota_str = request.POST.get("nota", "5")
        comentario = request.POST.get("comentario", "").strip()

        logger.info(f"Tentativa de avaliação - consulta={consulta_id}, nota={nota_str}")

        # =============================
        # Validação de sessão
        # =============================
        paciente_id = request.session.get("paciente_id")
        if not paciente_id:
            return JsonResponse({
                "success": False,
                "message": "Você precisa estar logado."
            }, status=401)

        # =============================
        # Validar nota
        # =============================
        try:
            nota = int(nota_str)
        except ValueError:
            return JsonResponse({
                "success": False,
                "message": "Nota inválida."
            }, status=400)

        if nota < 1 or nota > 5:
            return JsonResponse({
                "success": False,
                "message": "A nota deve ser entre 1 e 5."
            }, status=400)

        # =============================
        # Buscar consulta
        # =============================
        consulta = get_object_or_404(Consulta, id=consulta_id)

        # Segurança: garantir que a consulta pertence ao paciente logado
        if consulta.paciente.id != paciente_id:
            return JsonResponse({
                "success": False,
                "message": "Você não pode avaliar essa consulta."
            }, status=403)

        # Segurança extra: só pode avaliar consulta realizada
        if consulta.status != "realizada":
            return JsonResponse({
                "success": False,
                "message": "Só é possível avaliar consultas realizadas."
            }, status=400)

        # =============================
        # Criar ou atualizar avaliação
        # =============================
        avaliacao, created = Avaliacao.objects.update_or_create(
            consulta=consulta,
            defaults={
                "paciente": consulta.paciente,
                "clinica": consulta.clinica,
                "medico": consulta.medico,
                "nota": int(nota),
                "comentario": comentario
            }
        )

        logger.info(
            f"Avaliação {'criada' if created else 'atualizada'} "
            f"(ID={avaliacao.id}) para consulta {consulta.id}"
        )

        return JsonResponse({
            "success": True,
            "message": "Avaliação salva com sucesso!",
            "created": created
        })

    except Exception as e:
        logger.error("Erro ao criar avaliação", exc_info=True)
        return JsonResponse({
            "success": False,
            "message": "Erro interno ao processar avaliação."
        }, status=500)
    
def cadastro_clinica(request):

    if request.method == "POST":

        nome = request.POST.get("nome")
        descricao = request.POST.get("descricao")
        telefone = request.POST.get("telefone")
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        confirmar = request.POST.get("confirmar_senha")
        cnpj = request.POST.get("cnpj")

        cep = request.POST.get("cep")
        estado = request.POST.get("estado")
        cidade = request.POST.get("cidade")
        bairro = request.POST.get("bairro")
        rua = request.POST.get("rua")
        numero = request.POST.get("numero")

        logo = request.FILES.get("logo")
        imagem = request.FILES.get("imagem")  # suporte para imagem/banner além do logo

        if senha != confirmar:
            messages.error(request, "As senhas não coincidem")
            return render(request, "CadastroWeb/cadastro.html", status=400)

        if Clinica.objects.filter(email=email).exists():
            messages.error(request, "Este email já está cadastrado")
            return render(request, "CadastroWeb/cadastro.html", status=400)

        try:
            # criar endereço
            endereco = Endereco.objects.create(
                cep=cep,
                numero=numero,
                rua=rua,
                bairro=bairro,
                cidade=cidade,
                estado=estado,
                quadra=""
            )

            # Se o usuário enviou apenas logo, manter a imagem/banner como logo (fallback)
            if not imagem and logo:
                imagem = logo

            # criar clínica
            clinica_obj = Clinica.objects.create(
                nome=nome,
                descricao=descricao,
                telefone=telefone,
                email=email,
                senha=make_password(senha),
                cnpj=cnpj,
                endereco=endereco,
                logo=logo,
                imagem=imagem,
                conta_bancaria_juridica=""
            )

            # criar especialidades cadastradas na tela de registro
            for nome_esp in _parse_especialidades(request.POST):
                Especialidade.objects.create(clinica=clinica_obj, nome=nome_esp)

        except Exception as e:
            logger.exception("Erro ao cadastrar clínica")
            messages.error(request, f"Erro ao cadastrar clínica: {str(e)}")
            return render(request, "CadastroWeb/cadastro.html", status=500)

        messages.success(request, "Clínica cadastrada com sucesso!")
        return redirect("login_clinica")

    return render(request, "CadastroWeb/cadastro.html")