import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','setup.settings')
django.setup()
from odontoPro.models import Clinica
for c in Clinica.objects.all():
    print(c.id, c.nome, 'imagem:', c.imagem.name, 'logo:', c.logo.name)
