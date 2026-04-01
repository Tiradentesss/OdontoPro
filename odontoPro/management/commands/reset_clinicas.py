from django.core.management.base import BaseCommand
from django.core.files import File
from django.db import transaction
from pathlib import Path
from django.conf import settings
from odontoPro.models import Clinica, Endereco, DiaSemanaDisponivel, HorarioAberto, Especialidade, Medico, Gerenciamento, ClinicaImagem, Consulta, Avaliacao, ClinicaServico


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
    help = "Remove clínicas e dados relacionados. Se --nomes for omitido, remove todas as clínicas."

    def add_arguments(self, parser):
        parser.add_argument(
            "--nomes",
            nargs="+",
            default=None,
            help="Lista de nomes de clínicas a remover. Se omitido, remove todas as clínicas.",
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
        ClinicaServico.objects.filter(clinica__in=clinicas).delete()

        enderecos = Endereco.objects.filter(clinica__in=clinicas)
        clinicas.delete()

        # Remove endereços órfãos
        Endereco.objects.filter(id__in=enderecos.values_list('id', flat=True)).delete()

        # Remove quaisquer endereços que não estejam mais vinculados a clínicas
        Endereco.objects.filter(clinica__isnull=True).delete()

        self.stdout.write(self.style.SUCCESS("Remoção de clínicas concluída."))

    def handle(self, *args, **options):
        with transaction.atomic():
            nomes = options.get("nomes")
            if nomes:
                self.stdout.write(self.style.WARNING("Removendo clínicas por nome: %s" % ", ".join(nomes)))
                self._deletar_clinicas_por_nome(nomes)
                return

            self.stdout.write(self.style.WARNING("Modo padrão: removendo todas as clínicas e dados relacionados."))
            nomes_todas = list(Clinica.objects.values_list("nome", flat=True))
            if not nomes_todas:
                self.stdout.write(self.style.WARNING("Não há clínicas cadastradas para remoção."))
                # Limpa endereços órfãos existentes, caso tenham sobrado processos anteriores
                orphan_delete_count, _ = Endereco.objects.filter(clinica__isnull=True).delete()
                self.stdout.write(self.style.SUCCESS(f"Endereços órfãos removidos: {orphan_delete_count}"))
                return

            self._deletar_clinicas_por_nome(nomes_todas)
            return

