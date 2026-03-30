#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from odontoPro.models import Clinica, Medico, Gerenciamento, DiaSemanaDisponivel, HorarioAberto, ClinicaImagem, Endereco

# Deletar em ordem de dependência
print("Deletando dados relacionados às clínicas...")

# 1. Delete médicos (relacionam-se com clínicas via PROTECT)
medicos = Medico.objects.all().delete()
print(f"✓ Removidos {medicos[0]} médicos")

# 2. Delete gerentes
gerentes = Gerenciamento.objects.all().delete()
print(f"✓ Removidos {gerentes[0]} gerentes")

# 3. Delete dias/horários
dias = DiaSemanaDisponivel.objects.all().delete()
print(f"✓ Removidos {dias[0]} dias de semana")

# 4. Delete imagens de clínicas
imagens = ClinicaImagem.objects.all().delete()
print(f"✓ Removidas {imagens[0]} imagens")

# 5. Agora delete as clínicas
clinicas = Clinica.objects.all().delete()
print(f"✓ Removidas {clinicas[0]} clínicas")

# 6. Delete endereços órfãos
enderecos = Endereco.objects.all().delete()
print(f"✓ Removidos {enderecos[0]} endereços")

# Confirmar
qt = Clinica.objects.count()
print(f"\n✓ Total de clínicas agora: {qt}")
print("✓ Sistema limpo!")
