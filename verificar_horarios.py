import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from odontoPro.models import MedicoHorario, Medico

# Verificar quantos horários existem
total_horarios = MedicoHorario.objects.count()
print(f"Total de horários no banco: {total_horarios}")

# Verificar por médico
medicos = Medico.objects.all()
for medico in medicos:
    horarios = MedicoHorario.objects.filter(medico=medico).count()
    print(f"{medico.nome}: {horarios} horários")

# Mostrar um exemplo de horário
exemplo = MedicoHorario.objects.first()
if exemplo:
    print(f"\nExemplo: {exemplo}")
else:
    print("\n❌ Nenhum horário encontrado!")
