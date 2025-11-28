from django.db import models

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
    nome = models.CharField(max_length=45)
    descricao = models.CharField(max_length=300, null=True, blank=True)
    telefone = models.CharField(max_length=14)
    conta_bancaria_juridica = models.CharField(max_length=45)
    endereco = models.ForeignKey('Endereco', on_delete=models.PROTECT)

    imagem = models.ImageField(upload_to='clinicas/', null=True, blank=True)

    preco_consulta = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    avaliacao = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, default=5.0)
    num_avaliacoes = models.IntegerField(default=0)

    def __str__(self):
        return self.nome


# -------------------------
# Dias da semana disponíveis
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
# Horários de funcionamento
# -------------------------
class HorarioAberto(models.Model):
    dia = models.ForeignKey(DiaSemanaDisponivel, on_delete=models.CASCADE, related_name='horarios')
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    def __str__(self):
        return f"{self.dia.get_dia_display()} {self.hora_inicio.strftime('%H:%M')} - {self.hora_fim.strftime('%H:%M')}"


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

    def __str__(self):
        return self.nome


# -------------------------
# ESPECIALIDADE (NOVO)
# -------------------------
class Especialidade(models.Model):
    nome = models.CharField(max_length=80)

    def __str__(self):
        return self.nome


# -------------------------
# MÉDICO
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

    # 🔥 Especialidades ManyToMany
    especialidades = models.ManyToManyField(Especialidade, related_name="medicos")

    def __str__(self):
        return f"{self.nome} - {self.crm_cro}"


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
