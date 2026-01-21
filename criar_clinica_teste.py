import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from odontoPro.models import Endereco, Clinica, Medico, Especialidade

# Verificar se a clínica já existe
if Clinica.objects.filter(nome="Clínica Sorriso Perfeito").exists():
    print("⚠️  Clínica 'Clínica Sorriso Perfeito' já existe!")
    clinica = Clinica.objects.get(nome="Clínica Sorriso Perfeito")
    print(f"🎯 ID da clínica: {clinica.id}")
    print(f"Atualize-a no Django Admin se necessário.")
else:
    # Criar endereço
    endereco = Endereco.objects.create(
        cep="64000000",
        numero="123",
        quadra="A",
        rua="Rua das Flores",
        bairro="Centro",
        cidade="Teresina",
        estado="PI"
    )

    # Criar clínica
    clinica = Clinica.objects.create(
        cnpj="12.345.678/0001-99",
        nome="Clínica Sorriso Perfeito",
        descricao="Clínica odontológica moderna com atendimento completo",
        telefone="(86) 98888-7777",
        conta_bancaria_juridica="12345-6",
        endereco=endereco,
        preco_consulta=150.00,
        avaliacao=4.5,
        num_avaliacoes=24
    )

    # Criar especialidades
    especialidade_ortho, _ = Especialidade.objects.get_or_create(nome="Ortodontia")
    especialidade_perio, _ = Especialidade.objects.get_or_create(nome="Periodontia")
    especialidade_implanto, _ = Especialidade.objects.get_or_create(nome="Implantologia")

    # Criar médicos
    medico1 = Medico.objects.create(
        nome="Dr. Carlos Silva",
        crm_cro="123456",
        email="carlos@clinicasorriso.com",
        telefone="(86) 98888-1111",
        sexo="m",
        senha="senha123",
        clinica=clinica,
        cpf="12345678901",
        avaliacao=4.8,
        num_avaliacoes=18
    )
    medico1.especialidades.add(especialidade_ortho, especialidade_perio)

    medico2 = Medico.objects.create(
        nome="Dra. Maria Santos",
        crm_cro="654321",
        email="maria@clinicasorriso.com",
        telefone="(86) 98888-2222",
        sexo="f",
        senha="senha123",
        clinica=clinica,
        cpf="98765432101",
        avaliacao=4.9,
        num_avaliacoes=25
    )
    medico2.especialidades.add(especialidade_implanto)

    medico3 = Medico.objects.create(
        nome="Dr. João Oliveira",
        crm_cro="789012",
        email="joao@clinicasorriso.com",
        telefone="(86) 98888-3333",
        sexo="m",
        senha="senha123",
        clinica=clinica,
        cpf="11122233344",
        avaliacao=4.6,
        num_avaliacoes=12
    )
    medico3.especialidades.add(especialidade_ortho, especialidade_implanto)

    print("✅ Clínica de teste criada com sucesso!")
    print(f"📍 Clínica: {clinica.nome}")
    print(f"📞 Telefone: {clinica.telefone}")
    print(f"📍 Endereço: {endereco.rua}, {endereco.numero} - {endereco.cidade}, {endereco.estado}")
    print(f"⭐ Avaliação: {clinica.avaliacao}/5.0 ({clinica.num_avaliacoes} avaliações)")
    print(f"\n👨‍⚕️ Médicos criados:")
    print(f"  1. {medico1.nome} - {', '.join([e.nome for e in medico1.especialidades.all()])}")
    print(f"  2. {medico2.nome} - {', '.join([e.nome for e in medico2.especialidades.all()])}")
    print(f"  3. {medico3.nome} - {', '.join([e.nome for e in medico3.especialidades.all()])}")
    print(f"\n🎯 ID da clínica: {clinica.id}")
    print("\n💡 Para testar o botão 'Saiba Mais' na página inicial, você agora pode clicar na clínica!")
