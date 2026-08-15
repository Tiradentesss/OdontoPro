# Generated manually to add 'descricao' field to Especialidade
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('odontoPro', '0010_alter_clinica_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='especialidade',
            name='descricao',
            field=models.TextField(blank=True, null=True),
        ),
    ]
