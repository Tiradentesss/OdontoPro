from django.core.management.base import BaseCommand
from django.core.files import File
from django.db import transaction
from pathlib import Path
from django.conf import settings
from odontoPro.models import Clinica, Endereco, DiaSemanaDisponivel, HorarioAberto, Especialidade, Medico, Gerenciamento, ClinicaImagem, Consulta, Avaliacao


def _sexo_por_titulo(nome):
    nome_lower = nome.lower()
    if "dra." in nome_lower or nome_lower.startswith("dra"):
        return "f"
    if "dr." in nome_lower or nome_lower.startswith("dr"):
        return "m"
    return "m"


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
    endereco_data = dados["endereco"]
    endereco = Endereco.objects.create(
        cep=endereco_data["cep"],
        numero=endereco_data["numero"],
        quadra=endereco_data["quadra"],
        rua=endereco_data["rua"],
        bairro=endereco_data.get("bairro"),
        cidade=endereco_data.get("cidade"),
        estado=endereco_data.get("estado"),
    )

    clinica = Clinica.objects.create(
        cnpj=dados["cnpj"],
        nome=dados["nome"],
        descricao=dados.get("descricao"),
        telefone=dados.get("telefone"),
        conta_bancaria_juridica=dados.get("conta_bancaria_juridica", "0000000000"),
        endereco=endereco,
        email=dados.get("email"),
        senha=dados.get("senha"),
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
        sexo = _sexo_por_titulo(medico_data["nome"])
        medico = Medico.objects.create(
            nome=medico_data["nome"],
            cpf=medico_data.get("cpf", ""),
            sexo=sexo,
            email=medico_data.get("email"),
            data_nascimento=medico_data.get("data_nascimento"),
            senha=medico_data.get("senha", "123456"),
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
            senha=gerente_data["senha"],
            clinica=clinica,
        )

    _carregar_imagens_clinica(clinica, dados)

    return clinica


class Command(BaseCommand):
    help = "Remove clínicas (por padrão OdontoPrime e Sorriso Leve). Use --reset-completo para recriar Clínica Villanova."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-completo",
            action="store_true",
            help="Apaga todos os dados e recria a Clínica Villanova (comportamento antigo).",
        )
        parser.add_argument(
            "--nomes",
            nargs="+",
            default=["OdontoPrime", "Sorriso Leve"],
            help="Lista de nomes de clínicas a remover (padrão OdontoPrime e Sorriso Leve).",
        )

    def _deletar_clinicas_por_nome(self, nomes):
        clinicas = Clinica.objects.filter(nome__in=nomes)
        if not clinicas.exists():
            self.stdout.write(self.style.WARNING(f"Nenhuma clínica encontrada para remoção: {', '.join(nomes)}"))
            return

        self.stdout.write(self.style.WARNING(f"Removendo clínicas: {', '.join(clinicas.values_list('nome', flat=True))}"))

        Gerenciamento.objects.filter(clinica__in=clinicas).delete()
        Consulta.objects.filter(clinica__in=clinicas).delete()
        Avaliacao.objects.filter(clinica__in=clinicas).delete()
        Medico.objects.filter(clinica__in=clinicas).delete()
        DiaSemanaDisponivel.objects.filter(clinica__in=clinicas).delete()
        HorarioAberto.objects.filter(dia__clinica__in=clinicas).delete()
        ClinicaImagem.objects.filter(clinica__in=clinicas).delete()

        enderecos = Endereco.objects.filter(clinica__in=clinicas)
        clinicas.delete()

        # Remove endereços órfãos
        Endereco.objects.filter(id__in=enderecos.values_list('id', flat=True)).delete()

        self.stdout.write(self.style.SUCCESS("Remoção de clínicas concluída."))

    def handle(self, *args, **options):
        with transaction.atomic():
            if not options.get("reset_completo"):
                nomes = options.get("nomes", ["OdontoPrime", "Sorriso Leve"])
                self.stdout.write(self.style.WARNING("Modo padrão: removendo clínicas especificadas sem recriar."))
                self._deletar_clinicas_por_nome(nomes)
                return

            self.stdout.write("Modo reset completo ativado: deletando todos os dados de clínicas e relacionados...")

            # Apaga primeiro as tabelas filhas que usam on_delete=PROTECT no Clinica
            Gerenciamento.objects.all().delete()
            Medico.objects.all().delete()
            DiaSemanaDisponivel.objects.all().delete()
            HorarioAberto.objects.all().delete()
            Consulta.objects.all().delete()
            Avaliacao.objects.all().delete()
            ClinicaImagem.objects.all().delete()
            # Em seguida, apaga as clínicas e endereços
            Clinica.objects.all().delete()
            Endereco.objects.all().delete()

            clinicas = [
                {
                    "cnpj": "55555555000100",
                    "nome": "Clínica Villanova",
                    "descricao": "A Clínica Villanova redefine a experiência odontológica com atendimento humanizado e tecnologia de ponta.",
                    "telefone": "(41) 90000-0010",
                    "conta_bancaria_juridica": "7766554433",
                    "email": "contato@villanova.com",
                    "senha": "123456",
                    "preco_consulta": "220.00",
                    "avaliacao": "5.0",
                    "num_avaliacoes": 5,
                    "endereco": {
                        "cep": "80420000",
                        "numero": "1042",
                        "quadra": "Edifício Platinum 12º Andar",
                        "rua": "Alameda das Orquídeas",
                        "bairro": "Batel",
                        "cidade": "Curitiba",
                        "estado": "PR",
                    },
                    "dias": ["domingo", "segunda", "terca", "quarta", "quinta", "sexta", "sabado"],
                    "horarios": [("08:00", "12:00"), ("14:00", "18:00")],
                    "especialidades": ["Periodontia", "Implantodontia", "Estética Orofacial", "Endodontia", "Reabilitação Oral"],
                    "imagem_local": "img/Clinicas/Vila Nova/Fotos/Foto_Villanova_fachada.png",
                    "logo_local": "img/Clinicas/Vila Nova/Fotos/Foto_Villanova_logo.png",
                    "fotos": [
                        "img/Clinicas/Vila Nova/Fotos/Foto_Villanova_fachada.png",
                    ],
                    "medicos": [
                        {"nome": "Dra. Heloísa Meirelles", "cpf": "22211133344", "email": "heloisa@villanova.com", "data_nascimento": "1986-05-18", "senha": "hash123", "crm_cro": "CRO-60001", "telefone": "(41)90000-0011", "especialidades": ["Periodontia", "Implantodontia"]},
                        {"nome": "Dr. Fabrício Lancellotti", "cpf": "33322244455", "email": "fabricio@villanova.com", "data_nascimento": "1983-09-07", "senha": "hash123", "crm_cro": "CRO-60002", "telefone": "(41)90000-0012", "especialidades": ["Estética Orofacial"]},
                    ],
                    "gerentes": [
                        {"nome": "Eduardo Pires", "email": "eduardo@villanova.com", "senha": "123456"},
                    ],
                },
            ]

            for cl in clinicas:
                _criar_clinica(cl)
                self.stdout.write(self.style.SUCCESS(f"Clínica criada: {cl['nome']}"))

            self.stdout.write(self.style.SUCCESS("Reset de clínicas concluído com sucesso."))
