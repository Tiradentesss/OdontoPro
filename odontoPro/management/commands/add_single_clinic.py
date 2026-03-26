from django.core.management.base import BaseCommand
from django.core.files import File
from pathlib import Path
from django.conf import settings
from odontoPro.models import Clinica, Endereco, DiaSemanaDisponivel, HorarioAberto, Especialidade, Medico, Gerenciamento, ClinicaImagem
from django.contrib.auth.hashers import make_password


def _carregar_imagens_clinica(clinica, dados):
    base_static = Path(settings.BASE_DIR) / 'odontoPro' / 'static'

    # Banner principal (imagem da clínica)
    imagem_local = dados.get('imagem_local')
    if imagem_local:
        caminho = base_static / imagem_local
        if caminho.exists():
            with caminho.open('rb') as f:
                clinica.imagem.save(Path(caminho).name, File(f), save=False)

    # Logo da clínica
    logo_local = dados.get('logo_local')
    if logo_local:
        caminho = base_static / logo_local
        if caminho.exists():
            with caminho.open('rb') as f:
                clinica.logo.save(Path(caminho).name, File(f), save=False)

    clinica.save()

    # Galeria de imagens (ClinicaImagem)
    for ordem, foto_local in enumerate(dados.get('fotos', []), start=1):
        caminho_foto = base_static / foto_local
        if caminho_foto.exists():
            with caminho_foto.open('rb') as f:
                ci = ClinicaImagem(clinica=clinica, ordem=ordem)
                ci.imagem.save(Path(caminho_foto).name, File(f), save=True)


def _criar_clinica(dados):
    # Verifica se a clínica já existe
    if Clinica.objects.filter(nome=dados["nome"]).exists():
        return Clinica.objects.get(nome=dados["nome"])
    
    endereco_data = dados["endereco"]
    endereco = Endereco.objects.create(
        cep=endereco_data["cep"],
        numero=endereco_data["numero"],
        quadra=endereco_data.get("quadra", ""),
        rua=endereco_data["rua"],
        bairro=endereco_data.get("bairro"),
        cidade=endereco_data.get("cidade"),
        estado=endereco_data.get("estado"),
    )

    clinica = Clinica.objects.create(
        cnpj=dados["cnpj"],
        nome=dados["nome"],
        descricao=dados.get("descricao", ""),
        telefone=dados.get("telefone", ""),
        conta_bancaria_juridica=dados.get("conta_bancaria_juridica", "0000000000"),
        endereco=endereco,
        email=dados.get("email", ""),
        senha=make_password(dados.get("senha", "123456")),
        preco_consulta=dados.get("preco_consulta"),
        avaliacao=dados.get("avaliacao", 5.0),
        num_avaliacoes=dados.get("num_avaliacoes", 0),
    )

    # Especialidades extras da clínica
    for esp_nome in dados.get("especialidades", []):
        esp, _ = Especialidade.objects.get_or_create(nome=esp_nome)

    # Dias e horários
    for dia in dados.get("dias", []):
        ds = DiaSemanaDisponivel.objects.create(clinica=clinica, dia=dia)
        for hora_inicio, hora_fim in dados.get("horarios", []):
            HorarioAberto.objects.create(dia=ds, hora_inicio=hora_inicio, hora_fim=hora_fim)

    # Médicos e especialidades médicas
    for medico_data in dados.get("medicos", []):
        medico = Medico.objects.create(
            nome=medico_data["nome"],
            cpf=medico_data.get("cpf", ""),
            sexo=medico_data.get("sexo", "m"),
            email=medico_data.get("email", ""),
            data_nascimento=medico_data.get("data_nascimento"),
            senha=make_password(medico_data.get("senha", "123456")),
            crm_cro=medico_data.get("crm_cro", ""),
            telefone=medico_data.get("telefone", ""),
            clinica=clinica,
        )
        for esp_nome in medico_data.get("especialidades", []):
            esp, _ = Especialidade.objects.get_or_create(nome=esp_nome)
            medico.especialidades.add(esp)

    # Gerentes
    for gerente_data in dados.get("gerentes", []):
        Gerenciamento.objects.create(
            nome=gerente_data["nome"],
            email=gerente_data["email"],
            senha=make_password(gerente_data.get("senha", "123456")),
            clinica=clinica,
        )

    _carregar_imagens_clinica(clinica, dados)

    return clinica


class Command(BaseCommand):
    help = "Adiciona OdontoPrime ao sistema sem deletar as outras clínicas"

    def handle(self, *args, **options):
        # Temos apenas os dados básicos, depois você completa via admin ou shell
        odontoprime = {
            "cnpj": "33333333000100",
            "nome": "OdontoPrime",
            "descricao": "Clínica OdontoPrime - Informações serão preenchidas depois.",
            "telefone": "(41) 90000-0001",
            "conta_bancaria_juridica": "9988776655",
            "email": "contato@odontoprime.com",
            "senha": "123456",
            "preco_consulta": "180.00",
            "avaliacao": "5.0",
            "num_avaliacoes": 0,
            "endereco": {
                "cep": "80000000",
                "numero": "0",
                "quadra": "",
                "rua": "Rua a ser preenchida",
                "bairro": "Bairro a ser preenchido",
                "cidade": "Curitiba",
                "estado": "PR",
            },
            "dias": ["segunda", "terca", "quarta", "quinta", "sexta"],
            "horarios": [("08:00", "12:00"), ("14:00", "18:00")],
            "especialidades": [],
            "medicos": [],
            "gerentes": [],
            "imagem_local": "",
            "logo_local": "",
            "fotos": [],
        }

        try:
            clinica = _criar_clinica(odontoprime)
            self.stdout.write(self.style.SUCCESS(f"✓ Clínica '{clinica.nome}' adicionada com sucesso!"))
            self.stdout.write(f"\nPróximas etapas:")
            self.stdout.write(f"1. Acesse /admin e edite a clínica para adicionar detalhes")
            self.stdout.write(f"2. Ou use o shell: python manage.py shell")
            self.stdout.write(f"   from odontoPro.models import Clinica")
            self.stdout.write(f"   c = Clinica.objects.get(nome='OdontoPrime')")
            self.stdout.write(f"   c.descricao = 'Nova descrição'")
            self.stdout.write(f"   c.save()")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Erro ao adicionar clínica: {str(e)}"))
