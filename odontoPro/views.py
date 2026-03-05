from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime

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
    }

    return render(request, "DashboardPaciente/dashboard.html", context)


# ---------- LOGOUT ----------
def logout_view(request):
    request.session.flush()
    logout(request)
    return redirect("login_paciente")


def login_clinica(request):
    """Login para clínicas/profissionais"""
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        try:
            medico = Medico.objects.get(email=email)
        except Medico.DoesNotExist:
            messages.error(request, "Conta não encontrada.")
            return render(request, "LoginCadastro/login.html")

        if not check_password(senha, medico.senha):
            messages.error(request, "Senha incorreta.")
            return render(request, "LoginCadastro/login.html")

        request.session["medico_id"] = medico.id
        request.session["clinica_id"] = medico.clinica.id
        return redirect("painel_profissional")

    return render(request, "LoginCadastro/login.html")


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
    paciente_id = request.session.get("paciente_id")
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
    paciente_id = request.session.get('paciente_id')

    if not paciente_id:
        return redirect('login_paciente')

    try:
        paciente = Paciente.objects.get(id=paciente_id)
    except Paciente.DoesNotExist:
        request.session.flush()
        messages.error(request, 'Sua conta foi removida.')
        return redirect('login_paciente')

    if request.method == 'POST':
        try:
            paciente.nome = request.POST.get('nome', paciente.nome)
            paciente.email = request.POST.get('email', paciente.email)
            paciente.cpf = request.POST.get('cpf', paciente.cpf)
            paciente.telefone = request.POST.get('telefone', paciente.telefone)

            # 🔥 SALVAR FOTO
            if 'foto' in request.FILES:
                arquivo = request.FILES['foto']
                # Validar tamanho (máx 5MB)
                if arquivo.size > 5 * 1024 * 1024:
                    messages.error(request, 'Arquivo muito grande. Máximo 5MB.')
                    return redirect('/dashboard-paciente/?open=ajustes&tab=aba-perfil')
                
                # Validar tipo
                try:
                    img = Image.open(arquivo)
                    img.verify()
                except Exception:
                    messages.error(request, 'Arquivo de imagem inválido.')
                    return redirect('/dashboard-paciente/?open=ajustes&tab=aba-perfil')
                
                paciente.foto = arquivo

            paciente.save()
            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('/dashboard-paciente/?open=ajustes&tab=aba-perfil')
        except Exception as e:
            messages.error(request, f'Erro ao salvar: {str(e)}')
            return redirect('/dashboard-paciente/?open=ajustes&tab=aba-perfil')

    return redirect('/dashboard-paciente/?open=ajustes&tab=aba-perfil')



def alterar_senha_paciente(request):
    paciente_id = request.session.get('paciente_id')

    if not paciente_id:
        return redirect('login_paciente')

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

    return redirect('configuracoes_conta')

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

        if senha != confirmar:
            messages.error(request, "As senhas não coincidem")
            return redirect("cadastro_clinica")

        if Clinica.objects.filter(email=email).exists():
            messages.error(request, "Este email já está cadastrado")
            return redirect("cadastro_clinica")

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
            conta_bancaria_juridica=""
        )

        messages.success(request, "Clínica cadastrada com sucesso!")
        return redirect("login_clinica")

    return render(request, "CadastroWeb/cadastro.html")