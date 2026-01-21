import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from odontoPro.models import Clinica, Medico, Endereco, Especialidade

# Criar endereço
endereco, created = Endereco.objects.get_or_create(
    rua='Avenida Paulista',
    numero='1000',
    defaults={
        'quadra': 'Q-01',
        'bairro': 'Bela Vista',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'cep': '01311-100'
    }
)

# Criar clínica
clinica, created = Clinica.objects.get_or_create(
    nome='Clínica Dental Excellence',
    defaults={
        'cnpj': '12345678901234',
        'descricao': 'Clínica de odontologia com os melhores profissionais e equipamentos',
        'telefone': '(11) 3456-7890',
        'endereco': endereco,
        'preco_consulta': 150.00,
        'avaliacao': 4.8,
        'num_avaliacoes': 125
    }
)

if created:
    print(f"✅ Clínica '{clinica.nome}' criada com sucesso! ID: {clinica.id}")
else:
    print(f"ℹ️ Clínica '{clinica.nome}' já existe! ID: {clinica.id}")

# Criar especialidades
esp_ortho = Especialidade.objects.filter(nome='Ortodontia').first() or Especialidade.objects.create(nome='Ortodontia')
esp_perio = Especialidade.objects.filter(nome='Periodontia').first() or Especialidade.objects.create(nome='Periodontia')
esp_implan = Especialidade.objects.filter(nome='Implantologia').first() or Especialidade.objects.create(nome='Implantologia')

# Criar médicos
medicos_data = [
    {
        'nome': 'Dr. Roberto Silva',
        'cpf': '12345678901',
        'crm_cro': 'CRO 12345',
        'email': 'roberto@clinica.com',
        'especialidades': [esp_ortho, esp_implan]
    },
    {
        'nome': 'Dra. Fernanda Costa',
        'cpf': '98765432101',
        'crm_cro': 'CRO 67890',
        'email': 'fernanda@clinica.com',
        'especialidades': [esp_perio]
    },
    {
        'nome': 'Dr. Marcelo Oliveira',
        'cpf': '55555555555',
        'crm_cro': 'CRO 11111',
        'email': 'marcelo@clinica.com',
        'especialidades': [esp_ortho, esp_perio]
    }
]

for med_data in medicos_data:
    especialidades = med_data.pop('especialidades')
    medico, created = Medico.objects.get_or_create(
        clinica=clinica,
        email=med_data['email'],
        defaults={
            **med_data,
            'sexo': 'M' if 'Dr.' in med_data['nome'] else 'F',
            'telefone': '(11) 98765-4321',
            'avaliacao': 4.7,
            'num_avaliacoes': 89
        }
    )
    
    if created:
        medico.especialidades.set(especialidades)
        print(f"   ✅ Médico '{medico.nome}' criado!")
    else:
        print(f"   ℹ️ Médico '{medico.nome}' já existe!")

print("\n✅ Clínica de teste criada com sucesso!")
print(f"   ID da Clínica: {clinica.id}")
print(f"   Nome: {clinica.nome}")
print(f"   Acesse: /clinica/{clinica.id}/")
