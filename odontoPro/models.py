from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# -------------------------
# ENDERECO
# -------------------------
class Endereco(models.Model):
    cep = models.CharField(max_length=8)
    numero = models.CharField(max_length=60)
    quadra = models.CharField(max_length=60)
    rua = models.CharField(max_length=60)

    bairro = models.CharField(max_length=80, null=True, blank=True)
    cidade = models.CharField(max_length=80, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)

    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.cep}"


# -------------------------
# CLINICA
# -------------------------
class Clinica(models.Model):
    cnpj = models.CharField(max_length=45)
    nome = models.CharField(max_length=85)
    descricao = models.TextField(null=True, blank=True)
    telefone = models.CharField(max_length=14)
    conta_bancaria_juridica = models.CharField(max_length=45)
    endereco = models.ForeignKey('Endereco', on_delete=models.PROTECT)

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True
    )
    senha = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    # 🔹 NOVO: logo da clínica (perfil)
    logo = models.ImageField(
        upload_to='clinicas/logo/',
        null=True,
        blank=True
    )

    # 🔹 EXISTENTE (mantido para compatibilidade)
    imagem = models.ImageField(
        upload_to='clinicas/',
        null=True,
        blank=True
    )

    preco_consulta = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    avaliacao = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, default=5.0)
    num_avaliacoes = models.IntegerField(default=0)

    def __str__(self):
        return self.nome



class ClinicaImagem(models.Model):
    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.CASCADE,
        related_name='imagens'
    )

    imagem = models.ImageField(
        upload_to='clinicas/capa/',
        null=False,
        blank=False
    )

    ordem = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['ordem']
        verbose_name = 'Imagem da Clínica'
        verbose_name_plural = 'Imagens da Clínica'

    def __str__(self):
        return f"{self.clinica.nome} - Imagem {self.ordem}"


# -------------------------
# Dias da semana disponíveis (para a clínica)
# -------------------------
class DiaSemanaDisponivel(models.Model):
    DIAS_SEMANA = (
        ("domingo", "Domingo"),
        ("segunda", "Segunda-feira"),
        ("terca", "Terça-feira"),
        ("quarta", "Quarta-feira"),
        ("quinta", "Quinta-feira"),
        ("sexta", "Sexta-feira"),
        ("sabado", "Sábado"),
    )

    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, related_name='dias_semana')
    dia = models.CharField(max_length=10, choices=DIAS_SEMANA)

    def __str__(self):
        return f"{self.clinica.nome} - {self.get_dia_display()}"


# -------------------------
# Horários de funcionamento (por dia da clínica)
# -------------------------
class HorarioAberto(models.Model):
    dia = models.ForeignKey(DiaSemanaDisponivel, on_delete=models.CASCADE, related_name='horarios')
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    def __str__(self):
        return f"{self.dia.get_dia_display()} {self.hora_inicio.strftime('%H:%M')} - {self.hora_fim.strftime('%H:%M')}"

# -------------------------
# GERENCIAMENTO
# -------------------------
class Permissao(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descricao = models.CharField(max_length=150)

    def __str__(self):
        return self.descricao


class Gerenciamento(models.Model):
    nome = models.CharField(max_length=85)
    email = models.EmailField(max_length=100, unique=True)
    senha = models.CharField(max_length=255)

    # 🔹 VINCULAÇÃO COM A CLÍNICA
    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.CASCADE,
        related_name="gerentes"
    )

    permissoes = models.ManyToManyField(
        Permissao,
        related_name="usuarios_gerenciamento",
        blank=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} - {self.clinica.nome}"



# -------------------------
# PACIENTE
# -------------------------
class Paciente(models.Model):
    nome = models.CharField(max_length=85)
    cpf = models.CharField(max_length=11, null=True, blank=True)
    sexo = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=45, unique=True)
    data_nascimento = models.DateField(null=True, blank=True)
    senha = models.CharField(max_length=255)  # hash
    telefone = models.CharField(max_length=14)

    foto = models.ImageField(upload_to='pacientes/', null=True, blank=True)

    def __str__(self):
        return self.nome

# -------------------------
# ESPECIALIDADE
# -------------------------
class Especialidade(models.Model):
    nome = models.CharField(max_length=80)

    def __str__(self):
        return self.nome


# -------------------------
# MÉDICO (PROFISSIONAL)
# -------------------------
class Medico(models.Model):
    SEXO = (("f", "Feminino"), ("m", "Masculino"))

    nome = models.CharField(max_length=85)
    cpf = models.CharField(max_length=11, null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO)
    email = models.EmailField(max_length=45)
    data_nascimento = models.DateField(null=True, blank=True)
    senha = models.CharField(max_length=255)
    crm_cro = models.CharField(max_length=60)
    telefone = models.CharField(max_length=14)
    clinica = models.ForeignKey(Clinica, on_delete=models.PROTECT)

    especialidades = models.ManyToManyField(Especialidade, related_name="medicos")

    avaliacao = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, default=5.0)
    num_avaliacoes = models.IntegerField(default=0)

    foto = models.ImageField(upload_to='medicos/', null=True, blank=True)  # opcional

    def __str__(self):
        return f"{self.nome} - {self.crm_cro}"


# -------------------------
# Horário do MÉDICO (cada médico tem seus horários por dia)
# -------------------------
class MedicoHorario(models.Model):
    DIAS_SEMANA = DiaSemanaDisponivel.DIAS_SEMANA

    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='horarios_medico')
    dia = models.CharField(max_length=10, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    class Meta:
        verbose_name = "Horário do Médico"
        verbose_name_plural = "Horários do Médico"

    def __str__(self):
        return f"{self.medico.nome} - {self.get_dia_display()} {self.hora_inicio.strftime('%H:%M')} - {self.hora_fim.strftime('%H:%M')}"


# -------------------------
# SERVIÇO
# -------------------------
class Servico(models.Model):
    tipo = models.CharField(max_length=45)
    descricao = models.CharField(max_length=200)

    def __str__(self):
        return self.tipo


# -------------------------
# CLINICA – SERVIÇO
# -------------------------
class ClinicaServico(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    preco = models.DecimalField(max_digits=7, decimal_places=2)
    forma_pagamento = models.CharField(max_length=45)

    def __str__(self):
        return f"{self.clinica.nome} - {self.servico.tipo}"


# -------------------------
# Consulta (agendamento)
# -------------------------
class Consulta(models.Model):
    STATUS = (
        ("agendada", "Agendada"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
        ("realizada", "Realizada"),
    )

    paciente = models.ForeignKey(Paciente, null=True, blank=True, on_delete=models.SET_NULL)
    nome = models.CharField(max_length=120)  # para caso de reserva sem login
    email = models.EmailField(max_length=120)
    telefone = models.CharField(max_length=20)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    especialidade = models.CharField(max_length=120, null=True, blank=True)
    data_hora = models.DateTimeField()
    observacoes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="agendada")
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.medico.nome} ({self.data_hora.strftime('%Y-%m-%d %H:%M')})"
    
    # -------------------------
# AVALIAÇÃO
# -------------------------


class Avaliacao(models.Model):
    nota = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    comentario = models.TextField(blank=True, null=True)

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="avaliacoes_paciente"
    )

    medico = models.ForeignKey(
        Medico,
        on_delete=models.CASCADE,
        related_name="avaliacoes_medico"
    )

    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.CASCADE,
        related_name="avaliacoes_clinica"
    )

    consulta = models.OneToOneField(
    Consulta,
    on_delete=models.CASCADE,
    related_name="avaliacao",
    null=True,
    blank=True,
    )

    data_postagem = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_postagem']

    def __str__(self):
        return f"{self.paciente.nome} - {self.nota}"

    # 🔹 Sempre que salvar ou deletar, atualiza médias
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.atualizar_medias()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.atualizar_medias()

    def atualizar_medias(self):
        # ===== MÉDICO =====
        aval_medico = Avaliacao.objects.filter(medico=self.medico)

        self.medico.num_avaliacoes = aval_medico.count()

        if aval_medico.exists():
            self.medico.avaliacao = sum(a.nota for a in aval_medico) / aval_medico.count()
        else:
            self.medico.avaliacao = 5.0

        self.medico.save()

        # ===== CLÍNICA =====
        aval_clinica = Avaliacao.objects.filter(clinica=self.clinica)

        self.clinica.num_avaliacoes = aval_clinica.count()

        if aval_clinica.exists():
            self.clinica.avaliacao = sum(a.nota for a in aval_clinica) / aval_clinica.count()
        else:
            self.clinica.avaliacao = 5.0

        self.clinica.save()