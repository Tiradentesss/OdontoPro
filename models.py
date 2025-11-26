from django.db import models


# -------------------------
# ENDERECO
# -------------------------
class Endereco(models.Model):
    cep = models.CharField(max_length=8)
    numero = models.CharField(max_length=60)
    quadra = models.CharField(max_length=60)
    rua = models.CharField(max_length=60)

    # ADICIONADO PARA COMPATIBILIDADE COM O HTML
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

    # ADICIONADOS PARA O HTML
    preco_consulta = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    avaliacao = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, default=5.0)
    num_avaliacoes = models.IntegerField(default=0)

    def __str__(self):
        return self.nome


# -------------------------
# Dias disponíveis da clínica
# -------------------------
class DiaDisponivel(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, related_name='dias_disponiveis')
    data = models.DateField()

    def __str__(self):
        return self.data.strftime("%d/%m/%Y")


# -------------------------
# Horários disponíveis
# -------------------------
class HorarioDisponivel(models.Model):
    dia = models.ForeignKey(DiaDisponivel, on_delete=models.CASCADE, related_name='horarios')
    hora = models.TimeField()

    def __str__(self):
        return self.hora.strftime("%H:%M")


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

    def __str__(self):
        return f"{self.nome} - {self.crm_cro}"


# -------------------------
# ESPECIALIDADES
# -------------------------
class Especialidade(models.Model):
    nome = models.CharField(max_length=45)
    descricao = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


# -------------------------
# SERVIÇO (AGENDA)
# -------------------------
class Servico(models.Model):
    STATUS = (
        ("agendado", "Agendado"),
        ("realizado", "Realizado"),
        ("cancelado", "Cancelado"),
    )

    data = models.DateField()
    hora = models.TimeField()
    tipo = models.CharField(max_length=45)
    motivo = models.CharField(max_length=45, null=True, blank=True)
    descricao = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS)

    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT)
    especialidade = models.ForeignKey(Especialidade, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.tipo} - {self.data}"


# -------------------------
# PRONTUÁRIO
# -------------------------
class Prontuario(models.Model):
    data = models.DateField()
    prescricao = models.CharField(max_length=100, null=True, blank=True)
    descricao_procedimento = models.CharField(max_length=100)
    data_modificacao = models.DateField()
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)

    def __str__(self):
        return f"Prontuário {self.id}"


# -------------------------
# SETOR
# -------------------------
class Setor(models.Model):
    nome_setor = models.CharField(max_length=45)
    descricao = models.CharField(max_length=45)

    def __str__(self):
        return self.nome_setor


# -------------------------
# CARGO
# -------------------------
class Cargo(models.Model):
    nome_cargo = models.CharField(max_length=45)
    descricao = models.CharField(max_length=100)
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT)

    def __str__(self):
        return self.nome_cargo


# -------------------------
# GESTOR
# -------------------------
class Gestor(models.Model):
    SEXO = (("f", "Feminino"), ("m", "Masculino"))

    nome = models.CharField(max_length=85)
    cpf = models.CharField(max_length=11, null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO)
    email = models.EmailField(max_length=45)
    data_nascimento = models.DateField(null=True, blank=True)
    senha = models.CharField(max_length=255)
    telefone = models.CharField(max_length=14)

    clinica = models.ForeignKey(Clinica, on_delete=models.PROTECT)
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT)

    def __str__(self):
        return self.nome


class ProntuarioMedico(models.Model):
    prontuario = models.ForeignKey(Prontuario, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)


class EspecialidadeMedico(models.Model):
    especialidade = models.ForeignKey(Especialidade, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)


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
