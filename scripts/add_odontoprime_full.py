import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from odontoPro.models import Endereco, Clinica, DiaSemanaDisponivel, HorarioAberto, Especialidade, Medico, Gerenciamento
from django.contrib.auth.hashers import make_password

# Deletar qualquer OdontoPrime existente para evitar duplicação
Clinica.objects.filter(nome='OdontoPrime').delete()

# Endereço
endereco = Endereco.objects.create(
    cep='80210390',
    numero='1024',
    quadra='Bloco B Sala 502',
    rua='Avenida das Esmeraldas',
    bairro='Jardim Botânico',
    cidade='Curitiba',
    estado='PR'
)

# Clínica
clinica = Clinica.objects.create(
    cnpj='33333333000100',
    nome='OdontoPrime',
    descricao=('A OdontoPrime é referência em tratamentos odontológicos de alta tecnologia e atendimento ' 
               'humanizado para toda a família. Nossa missão é transformar sorrisos através de procedimentos ' 
               'inovadores em estética, implantes e ortodontia. Contamos com uma infraestrutura moderna e profissionais ' 
               'altamente qualificados para garantir o máximo de conforto e segurança aos nossos pacientes.'),
    telefone='(41) 90000-0001',
    conta_bancaria_juridica='9988776655',
    endereco=endereco,
    email='contato@odontoprime.com',
    senha=make_password('123456'),
    preco_consulta='180.00',
    avaliacao=4.8,
    num_avaliacoes=5
)

# Dias da semana
dias = ['domingo', 'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado']
for dia in dias:
    ds = DiaSemanaDisponivel.objects.create(clinica=clinica, dia=dia)
    HorarioAberto.objects.create(dia=ds, hora_inicio='08:00', hora_fim='12:00')
    HorarioAberto.objects.create(dia=ds, hora_inicio='14:00', hora_fim='18:00')

# Especialidade adicional
esp_harmonizacao, _ = Especialidade.objects.get_or_create(nome='Harmonização Orofacial')

# Médicos
medicos_data = [
    ('Dr. Ricardo Almeida', '11122233344', 'm', 'ricardo@odontoprime.com', '1982-03-12', 'CRO-77777', '(41)90000-0002', ['Implantodontia']),
    ('Dra. Fernanda Souza', '22233344455', 'f', 'fernanda@odontoprime.com', '1988-06-25', 'CRO-88888', '(41)90000-0003', ['Ortodontia']),
    ('Dr. Marcelo Guimarães', '33344455566', 'm', 'marcelo@odontoprime.com', '1980-11-10', 'CRO-99991', '(41)90000-0004', ['Endodontia']),
    ('Dra. Camila Bittencourt', '44455566677', 'f', 'camila@odontoprime.com', '1991-09-18', 'CRO-99992', '(41)90000-0005', ['Odontopediatria']),
    ('Dra. Juliana Mendes', '55566677788', 'f', 'juliana@odontoprime.com', '1989-02-14', 'CRO-99993', '(41)90000-0006', ['Harmonização Orofacial'])
]

for nome, cpf, sexo, email, data_nascimento, crm, telefone, especialidades in medicos_data:
    med = Medico.objects.create(
        nome=nome,
        cpf=cpf,
        sexo=sexo,
        email=email,
        data_nascimento=data_nascimento,
        senha=make_password('hash123'),
        crm_cro=crm,
        telefone=telefone,
        clinica=clinica
    )
    for esp_nome in especialidades:
        esp, _ = Especialidade.objects.get_or_create(nome=esp_nome)
        med.especialidades.add(esp)

# Gerentes
Gerenciamento.objects.create(nome='Paulo Martins', email='paulo@odontoprime.com', senha=make_password('123456'), clinica=clinica)
Gerenciamento.objects.create(nome='Carla Ribeiro', email='carla@odontoprime.com', senha=make_password('123456'), clinica=clinica)

print('✓ OdontoPrime adicionada ao sistema com detalhes completos!')
print('Clínica ID:', clinica.id)
