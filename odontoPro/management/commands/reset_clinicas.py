from django.core.management.base import BaseCommand
from django.core.files import File
from django.db import transaction
from pathlib import Path
from django.conf import settings
from odontoPro.models import Clinica, Endereco, DiaSemanaDisponivel, HorarioAberto, Especialidade, Medico, Gerenciamento, ClinicaImagem


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
    help = "Remove todas as clínicas antigas e cria OdontoPrime, Sorriso Leve e Clínica Villanova com dados completos"

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write("Deletando dados existentes de clínicas e relacionados...")

            # Apaga primeiro as tabelas filhas que usam on_delete=PROTECT no Clinica
            Gerenciamento.objects.all().delete()
            Medico.objects.all().delete()
            DiaSemanaDisponivel.objects.all().delete()
            HorarioAberto.objects.all().delete()
            # Em seguida, apaga as clínicas e endereços
            Clinica.objects.all().delete()
            Endereco.objects.all().delete()

            clinicas = [
                {
                    "cnpj": "33333333000100",
                    "nome": "OdontoPrime",
                    "descricao": "A OdontoPrime é referência em tratamentos odontológicos de alta tecnologia e atendimento humanizado para toda a família. Nossa missão é transformar sorrisos através de procedimentos inovadores em estética, implantes e ortodontia. Contamos com uma infraestrutura moderna e profissionais altamente qualificados para garantir o máximo de conforto e segurança aos nossos pacientes.",
                    "telefone": "(41) 90000-0001",
                    "conta_bancaria_juridica": "9988776655",
                    "email": "contato@odontoprime.com",
                    "senha": "123456",
                    "preco_consulta": "180.00",
                    "avaliacao": "4.8",
                    "num_avaliacoes": 5,
                    "endereco": {
                        "cep": "80210390",
                        "numero": "1024",
                        "quadra": "Bloco B Sala 502",
                        "rua": "Avenida das Esmeraldas",
                        "bairro": "Jardim Botânico",
                        "cidade": "Curitiba",
                        "estado": "PR",
                    },
                    "dias": ["domingo", "segunda", "terca", "quarta", "quinta", "sexta", "sabado"],
                    "horarios": [("08:00", "12:00"), ("14:00", "18:00")],
                    "especialidades": ["Harmonização Orofacial", "Implantodontia", "Ortodontia", "Endodontia", "Odontopediatria"],
                    "imagem_local": "img/Clinicas/Odontoprime/Fotos/OdontoPrime_fachada.png",
                    "logo_local": "img/Clinicas/Odontoprime/Fotos/OdontoPrime_logo.png",
                    "fotos": [
                        "img/Clinicas/Odontoprime/Fotos/OdontoPrime_fachada.png",
                        "img/Clinicas/Odontoprime/Fotos/OdontoPrime_interior_1.png",
                        "img/Clinicas/Odontoprime/Fotos/OdontoPrime_interior_2.png",
                        "img/Clinicas/Odontoprime/Fotos/OdontoPrime_interior_3.png",
                        "img/Clinicas/Odontoprime/Fotos/OdontoPrime_interior_4.png",
                        "img/Clinicas/Odontoprime/Fotos/OdontoPrime_interior_5.png",
                    ],
                    "medicos": [
                        {"nome": "Dr. Ricardo Almeida", "cpf": "11122233344", "email": "ricardo@odontoprime.com", "data_nascimento": "1982-03-12", "senha": "hash123", "crm_cro": "CRO-77777", "telefone": "(41)90000-0002", "especialidades": ["Implantodontia"]},
                        {"nome": "Dra. Fernanda Souza", "cpf": "22233344455", "email": "fernanda@odontoprime.com", "data_nascimento": "1988-06-25", "senha": "hash123", "crm_cro": "CRO-88888", "telefone": "(41)90000-0003", "especialidades": ["Ortodontia"]},
                        {"nome": "Dr. Marcelo Guimarães", "cpf": "33344455566", "email": "marcelo@odontoprime.com", "data_nascimento": "1980-11-10", "senha": "hash123", "crm_cro": "CRO-99991", "telefone": "(41)90000-0004", "especialidades": ["Endodontia"]},
                        {"nome": "Dra. Camila Bittencourt", "cpf": "44455566677", "email": "camila@odontoprime.com", "data_nascimento": "1991-09-18", "senha": "hash123", "crm_cro": "CRO-99992", "telefone": "(41)90000-0005", "especialidades": ["Odontopediatria"]},
                        {"nome": "Dra. Juliana Mendes", "cpf": "55566677788", "email": "juliana@odontoprime.com", "data_nascimento": "1989-02-14", "senha": "hash123", "crm_cro": "CRO-99993", "telefone": "(41)90000-0006", "especialidades": ["Harmonização Orofacial"]},
                    ],
                    "gerentes": [
                        {"nome": "Paulo Martins", "email": "paulo@odontoprime.com", "senha": "123456"},
                        {"nome": "Carla Ribeiro", "email": "carla@odontoprime.com", "senha": "123456"},
                    ],
                },

                {
                    "cnpj": "44444444000100",
                    "nome": "Sorriso Leve",
                    "descricao": "A Sorriso Leve redefine o conceito de bem-estar bucal ao integrar tecnologias de ponta com um atendimento humanizado e acolhedor. Nossa missão é proporcionar transformações estéticas e funcionais que elevam a autoestima através de protocolos personalizados e minimamente invasivos. Aqui, cada detalhe foi planejado para que sua visita seja marcada pelo conforto e pela segurança de um sorriso saudável.",
                    "telefone": "(62) 90000-0001",
                    "conta_bancaria_juridica": "3344556677",
                    "email": "contato@sorrisoleve.com",
                    "senha": "123456",
                    "preco_consulta": "170.00",
                    "avaliacao": "4.8",
                    "num_avaliacoes": 5,
                    "endereco": {
                        "cep": "74210010",
                        "numero": "842",
                        "quadra": "Edifício Platinum Sala 504",
                        "rua": "Alameda das Orquídeas",
                        "bairro": "Setor Bueno",
                        "cidade": "Goiânia",
                        "estado": "GO",
                    },
                    "dias": ["domingo", "segunda", "terca", "quarta", "quinta", "sexta", "sabado"],
                    "horarios": [("08:00", "12:00"), ("14:00", "18:00")],
                    "especialidades": ["Implantodontia Avançada", "Odontopediatria Lúdica", "Ortodontia Digital", "Harmonização Orofacial", "Endodontia Microscópica"],
                    "imagem_local": "img/Clinicas/Sorriso Leve/Fotos/ChatGPT_Image_11_de_mar._de_2026_16_04_02.png",
                    "logo_local": "img/Clinicas/Sorriso Leve/Fotos/ChatGPT_Image_11_de_mar._de_2026_16_23_58.png",
                    "fotos": [
                        "img/Clinicas/Sorriso Leve/Fotos/ChatGPT_Image_11_de_mar._de_2026_16_04_02.png",
                        "img/Clinicas/Sorriso Leve/Fotos/ChatGPT_Image_11_de_mar._de_2026_16_14_20.png",
                        "img/Clinicas/Sorriso Leve/Fotos/ChatGPT_Image_11_de_mar._de_2026_16_15_34.png",
                        "img/Clinicas/Sorriso Leve/Fotos/ChatGPT_Image_11_de_mar._de_2026_16_17_30.png",
                        "img/Clinicas/Sorriso Leve/Fotos/ChatGPT_Image_11_de_mar._de_2026_16_19_53.png",
                        "img/Clinicas/Sorriso Leve/Fotos/ChatGPT_Image_11_de_mar._de_2026_16_22_41.png",
                        "img/Clinicas/Sorriso Leve/Fotos/ChatGPT_Image_11_de_mar._de_2026_16_23_58.png",
                    ],
                    "medicos": [
                        {"nome": "Dr. Renato Alencar", "cpf": "66677788899", "email": "renato@sorrisoleve.com", "data_nascimento": "1981-04-15", "senha": "hash123", "crm_cro": "CRO-11111", "telefone": "(62)90000-0002", "especialidades": ["Implantodontia Avançada"]},
                        {"nome": "Dra. Beatriz Valente", "cpf": "77788899900", "email": "beatriz@sorrisoleve.com", "data_nascimento": "1990-08-11", "senha": "hash123", "crm_cro": "CRO-22223", "telefone": "(62)90000-0003", "especialidades": ["Odontopediatria Lúdica"]},
                        {"nome": "Dr. Hugo Fontana", "cpf": "88899900011", "email": "hugo@sorrisoleve.com", "data_nascimento": "1987-01-22", "senha": "hash123", "crm_cro": "CRO-33334", "telefone": "(62)90000-0004", "especialidades": ["Ortodontia Digital"]},
                        {"nome": "Dra. Clarice Mendes", "cpf": "99900011122", "email": "clarice@sorrisoleve.com", "data_nascimento": "1992-06-09", "senha": "hash123", "crm_cro": "CRO-44445", "telefone": "(62)90000-0005", "especialidades": ["Harmonização Orofacial"]},
                        {"nome": "Dr. Samuel Porto", "cpf": "11100022233", "email": "samuel@sorrisoleve.com", "data_nascimento": "1984-12-03", "senha": "hash123", "crm_cro": "CRO-55556", "telefone": "(62)90000-0006", "especialidades": ["Endodontia Microscópica"]},
                    ],
                    "gerentes": [
                        {"nome": "Gabriel Nogueira", "email": "gabriel@sorrisoleve.com", "senha": "123456"},
                        {"nome": "Larissa Duarte", "email": "larissa@sorrisoleve.com", "senha": "123456"},
                    ],
                },

                {
                    "cnpj": "55555555000100",
                    "nome": "Clínica Villanova",
                    "descricao": "A Clínica Villanova redefine a experiência odontológica ao integrar protocolos de biotecnologia avançada com um atendimento humanizado e exclusivo. Localizada em um ambiente planejado para o máximo de conforto sensorial, nossa unidade foca na precisão diagnóstica através de escaneamento digital e planejamento 3D. Nossa missão é elevar a saúde sistêmica e a autoestima de nossos pacientes através de reabilitações que unem funcionalidade biológica e estética de alto padrão.",
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
                    "especialidades": ["Periodontia", "Implantodontia", "Estética Orofacial", "Endodontia Microscópica", "Reabilitação Oral de Alta Complexidade"],
                    "imagem_local": "img/Clinicas/Vila Nova/Fotos/Foto_Villanova_fachada.png",
                    "logo_local": "img/Clinicas/Vila Nova/Fotos/Foto_Villanova_logo.png",
                    "fotos": [
                        "img/Clinicas/Vila Nova/Fotos/Foto_Villanova_fachada.png",
                        "img/Clinicas/Vila Nova/Fotos/Foto_Villanova_interior_1.png",
                        "img/Clinicas/Vila Nova/Fotos/Foto_Villanova_interior_2.png",
                        "img/Clinicas/Vila Nova/Fotos/Foto_Villanova_interior_3.png",
                        "img/Clinicas/Vila Nova/Fotos/Foto_Villanova_interior_4.png",
                    ],
                    "medicos": [
                        {"nome": "Dra. Heloísa Meirelles", "cpf": "22211133344", "email": "heloisa@villanova.com", "data_nascimento": "1986-05-18", "senha": "hash123", "crm_cro": "CRO-60001", "telefone": "(41)90000-0011", "especialidades": ["Periodontia", "Implantodontia"]},
                        {"nome": "Dr. Fabrício Lancellotti", "cpf": "33322244455", "email": "fabricio@villanova.com", "data_nascimento": "1983-09-07", "senha": "hash123", "crm_cro": "CRO-60002", "telefone": "(41)90000-0012", "especialidades": ["Estética Orofacial"]},
                        {"nome": "Dr. Tiago Arantes", "cpf": "44433355566", "email": "tiago@villanova.com", "data_nascimento": "1988-01-29", "senha": "hash123", "crm_cro": "CRO-60003", "telefone": "(41)90000-0013", "especialidades": ["Endodontia Microscópica"]},
                        {"nome": "Dra. Camila Siqueira", "cpf": "55544466677", "email": "camila@villanova.com", "data_nascimento": "1990-11-14", "senha": "hash123", "crm_cro": "CRO-60004", "telefone": "(41)90000-0014", "especialidades": ["Reabilitação Oral de Alta Complexidade"]},
                    ],
                    "gerentes": [
                        {"nome": "Eduardo Pires", "email": "eduardo@villanova.com", "senha": "123456"},
                        {"nome": "Marina Tavares", "email": "marina@villanova.com", "senha": "123456"},
                    ],
                },
            ]

            for cl in clinicas:
                _criar_clinica(cl)
                self.stdout.write(self.style.SUCCESS(f"Clínica criada: {cl['nome']}"))

            self.stdout.write(self.style.SUCCESS("Reset de clínicas concluído com sucesso."))
