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

from .models import Paciente, Clinica, Consulta, Medico, Avaliacao, Endereco
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from .models import DiaSemanaDisponivel, HorarioAberto
from PIL import Image
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

import logging
logger = logging.getLogger(__name__)

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
    # unified login endpoint for pacientes and profissionais
    if request.method == "POST":
        raw_email = request.POST.get("email", "") or ""
        senha = request.POST.get("senha", "") or ""

        # normalize input to avoid accidental spaces/case issues
        email = raw_email.strip().lower()

        logger.info(f"login attempt email={email} from {request.META.get('REMOTE_ADDR')}")

        # first try paciente
        paciente = Paciente.objects.filter(email__iexact=email).first()
        if paciente:
            if not check_password(senha, paciente.senha):
                messages.error(request, "Senha incorreta.")
                logger.info("login failed - wrong password for paciente %s", email)
                return render(request, "LoginCadastro/login.html", {"email": raw_email})

            # successful paciente login
            request.session["paciente_id"] = paciente.id
            # explicitly save session before redirect and debug
            try:
                request.session.save()
                logger.info("session saved successfully for paciente %s", email)
            except Exception as e:
                logger.error("error saving session: %s", e, exc_info=True)
            logger.info("login success paciente %s session_key=%s cookies=%s", email,
                        request.session.session_key,
                        request.META.get('HTTP_COOKIE'))
            messages.success(request, f"Bem-vindo, {paciente.nome}!")
            return redirect("dashboard_paciente")

        # if no paciente found, attempt to authenticate a medico
        medico = Medico.objects.filter(email__iexact=email).first()
        if medico:
            if not check_password(senha, medico.senha):
                messages.error(request, "Senha incorreta.")
                logger.info("login failed - wrong password for medico %s", email)
                return render(request, "LoginCadastro/login.html", {"email": raw_email})

            request.session["medico_id"] = medico.id
            request.session["clinica_id"] = medico.clinica.id
            try:
                request.session.save()
            except Exception as e:
                logger.error("error saving session: %s", e, exc_info=True)
            logger.info("login success medico %s session_key=%s cookies=%s", email,
                        request.session.session_key,
                        request.META.get('HTTP_COOKIE'))
            return redirect("painel_profissional")

        # no account found at all
        messages.error(request, "Conta não encontrada. Cadastre-se primeiro.")
        logger.info("login failed - account not found %s", email)
        return render(request, "LoginCadastro/login.html", {"email": raw_email})

    # GET
    return render(request, "LoginCadastro/login.html")


# ---------- DASHBOARD PACIENTE ----------
def dashboard_paciente(request):
    paciente_id = request.session.get("paciente_id")
    logger.debug("dashboard access session_key=%s paciente_id=%s cookies=%s",
                 request.session.session_key, paciente_id,
                 request.META.get('HTTP_COOKIE'))
    if not paciente_id:
        return redirect("login_paciente")

    paciente = Paciente.objects.get(id=paciente_id)
    clinicas = Clinica.objects.all().order_by("nome")

    # prepare signed uid for settings forms so it is always available
    uid_signed = signing.dumps(paciente.id)

    filtro_status = request.GET.get("status")
    aba_ativa = request.GET.get("aba", "principal")
    consultas = Consulta.objects.filter(paciente=paciente).order_by("-data_hora")
    agora = timezone.now()

    consultas_futuras = Consulta.objects.filter(
        paciente=paciente,
        data_hora__gte=agora,
        status__in=["agendada", "confirmada"]
    ).order_by("data_hora")

    tem_notificacao = consultas_futuras.exists()

    if filtro_status and filtro_status != "todas":
        consultas = consultas.filter(status=filtro_status)

    context = {
        "paciente": paciente,
        "clinicas": clinicas,
        "consultas": consultas,
        "filtro_status": filtro_status or "todas",
        "consultas_futuras": consultas_futuras,
        "tem_notificacao": tem_notificacao,
        "aba_ativa": aba_ativa,
        "uid_signed": uid_signed,
    }

    return render(request, "DashboardPaciente/dashboard.html", context)


# ---------- LOGOUT ----------
def logout_view(request):
    request.session.flush()
    logout(request)
    return redirect("login_paciente")


# kept for backwards compatibility, but the main login logic is now in login_paciente
# which handles both patients and professionals.
def login_clinica(request):
    # redirect all requests to the unified view
    return login_paciente(request)


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

    medicos = [
        {
            "id": m.id,
            "nome": m.nome,
            "foto_url": m.foto.url if m.foto else None
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

    return JsonResponse({
    "nome": clinica.nome,
    "email": clinica.email,
    "telefone": clinica.telefone,
    "descricao": clinica.descricao,
    "logo_url": clinica.logo.url if clinica.logo else None,
    "imagem_url": clinica.imagem.url if clinica.imagem else None,
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
    especialidade = request.POST.get("especialidade")
    data_hora_str = request.POST.get("data_hora")
    observacoes = request.POST.get("observacoes", "")

    if not all([clinica_id, medico_id, data_hora_str]):
        return JsonResponse({"success": False, "error": "Dados incompletos"})

    data_hora = parse_datetime(data_hora_str)
    if not data_hora:
        return JsonResponse({"success": False, "error": "Data inválida"})

    try:
        clinica = Clinica.objects.get(id=clinica_id)
        medico = Medico.objects.get(id=medico_id)
    except (Clinica.DoesNotExist, Medico.DoesNotExist):
        return JsonResponse({"success": False, "error": "Clínica ou médico não encontrado"}, status=404)

    # 🔒 evita conflito de horário
    if Consulta.objects.filter(medico=medico, data_hora=data_hora).exists():
        return JsonResponse({"success": False, "error": "Horário indisponível"})

    paciente = None
    nome = email = telefone = ""

    # ✅ PACIENTE LOGADO (via sessão)
    if paciente_id:
        try:
            paciente = Paciente.objects.get(id=paciente_id)
            nome = paciente.nome
            email = paciente.email
            telefone = paciente.telefone
        except Paciente.DoesNotExist:
            return JsonResponse({"success": False, "error": "Paciente não encontrado"}, status=404)
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
    """View para gerenciar as configurações da conta do paciente"""

    # ===== VERIFICAR AUTENTICAÇÃO =====
    paciente_id = request.session.get('paciente_id')

    # Se sessão perdida, tentar recuperar via UID assinado
    if request.method == 'POST' and not paciente_id:
        signed = request.POST.get('uid')
        if signed:
            try:
                paciente_id = signing.loads(signed)
                if Paciente.objects.filter(id=paciente_id).exists():
                    request.session['paciente_id'] = paciente_id
                    request.session.save()
                else:
                    paciente_id = None
            except signing.BadSignature:
                paciente_id = None

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
    if request.method == 'POST':
        # Pegar todos os valores do formulário
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        cpf = request.POST.get('cpf', '').strip()
        telefone = request.POST.get('telefone', '').strip()

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

                        # Processar foto
                        if 'foto' in request.FILES and request.FILES['foto'].size > 0:
                            arquivo = request.FILES['foto']
                            if arquivo.size > 5 * 1024 * 1024:
                                messages.error(request, 'Foto muito grande (máximo 5MB).')
                            else:
                                try:
                                    img = Image.open(arquivo)
                                    img.verify()
                                    arquivo.seek(0)
                                    paciente.foto = arquivo
                                    paciente.save()
                                    request.session.save()
                                    messages.success(request, 'Dados atualizados com sucesso (com foto)!')
                                except Exception:
                                    messages.error(request, 'Imagem inválida. Tente outra.')
                        else:
                            # Salvar sem foto
                            paciente.save()
                            request.session.save()
                            messages.success(request, 'Dados atualizados com sucesso!')
                else:
                    # Email não mudou, apenas atualizar outros dados
                    paciente.nome = nome
                    paciente.email = email.lower()
                    if cpf:
                        paciente.cpf = cpf
                    if telefone:
                        paciente.telefone = telefone

                    # Processar foto
                    if 'foto' in request.FILES and request.FILES['foto'].size > 0:
                        arquivo = request.FILES['foto']
                        if arquivo.size > 5 * 1024 * 1024:
                            messages.error(request, 'Foto muito grande (máximo 5MB).')
                        else:
                            try:
                                img = Image.open(arquivo)
                                img.verify()
                                arquivo.seek(0)
                                paciente.foto = arquivo
                                paciente.save()
                                request.session.save()
                                messages.success(request, 'Dados atualizados com sucesso (com foto)!')
                            except Exception:
                                messages.error(request, 'Imagem inválida. Tente outra.')
                    else:
                        # Salvar sem foto
                        paciente.save()
                        request.session.save()
                        messages.success(request, 'Dados atualizados com sucesso!')
            except Exception as e:
                logger.error(f"Erro ao atualizar paciente {paciente_id}: {str(e)}", exc_info=True)
                messages.error(request, 'Erro ao salvar alterações. Tente novamente.')

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
    }

    return render(request, "DashboardPaciente/dashboard.html", context)

    # Aplicar filtro de status se recebido
    tem_notificacao = consultas_futuras.exists()

    context = {
        "paciente": paciente,
        "clinicas": clinicas,
        "consultas": consultas,
        "consultas_futuras": consultas_futuras,
        "tem_notificacao": tem_notificacao,
        "uid_signed": uid_signed,
    }
    return render(request, "DashboardPaciente/dashboard.html", context)



def alterar_senha_paciente(request):
    paciente_id = request.session.get('paciente_id')

    # tentar recuperar sessão a partir de uid assinado se POST
    if request.method == 'POST' and not paciente_id:
        signed = request.POST.get('uid')
        logger.debug("[SENHA] signed uid from POST: %r", signed)
        if signed:
            try:
                restored = signing.loads(signed)
                paciente_id = restored
                request.session['paciente_id'] = paciente_id
                try:
                    request.session.save()
                except Exception as ex:
                    logger.error("[SENHA] erro salvando sessão restaurada: %s", ex, exc_info=True)
                logger.warning("[SENHA] sessão perdida, restaurada via uid: %s", paciente_id)
            except signing.BadSignature:
                logger.warning("[SENHA] uid inválido fornecido: %r", signed)

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
        except Exception as e:
            logger.error(f"[SENHA] Erro: {str(e)}", exc_info=True)
            messages.error(request, f'Erro ao alterar senha: {str(e)}')

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
    }
    return render(request, "DashboardPaciente/dashboard.html", context)

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

            # criar clínica
            Clinica.objects.create(
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

        except Exception as e:
            logger.exception("Erro ao cadastrar clínica")
            messages.error(request, f"Erro ao cadastrar clínica: {str(e)}")
            return render(request, "CadastroWeb/cadastro.html", status=500)

        messages.success(request, "Clínica cadastrada com sucesso!")
        return redirect("login_clinica")

    return render(request, "CadastroWeb/cadastro.html")