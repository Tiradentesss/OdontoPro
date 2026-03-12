from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from .models import Paciente, Medico, Clinica


class LoginViewTests(TestCase):
    def setUp(self):
        # create a sample paciente and medico
        self.paciente = Paciente.objects.create(
            nome="Usuário Teste",
            email="user@example.com",
            senha=make_password("senha123"),
            telefone="123456789"
        )
        self.clinica = Clinica.objects.create(nome="Clinica X", cnpj="00000000", endereco="Rua X")
        self.medico = Medico.objects.create(
            nome="Dr. Teste",
            email="medico@example.com",
            senha=make_password("medsenha"),
            telefone="987654321",
            crm_cro="1234",
            clinica=self.clinica
        )

    def test_login_patient_success(self):
        resp = self.client.post(reverse('login_paciente'), {'email': 'user@example.com', 'senha': 'senha123'})
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('dashboard_paciente'))
        self.assertEqual(self.client.session.get('paciente_id'), self.paciente.id)

    def test_login_patient_normalization(self):
        # uppercase and surrounding spaces
        resp = self.client.post(reverse('login_paciente'), {'email': ' User@Example.COM ', 'senha': 'senha123'})
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('dashboard_paciente'))

    def test_login_medico_success(self):
        resp = self.client.post(reverse('login_paciente'), {'email': 'medico@example.com', 'senha': 'medsenha'})
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('painel_profissional'))
        self.assertEqual(self.client.session.get('medico_id'), self.medico.id)

    def test_login_wrong_password(self):
        resp = self.client.post(reverse('login_paciente'), {'email': 'user@example.com', 'senha': 'wrong'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Senha incorreta.")

    def test_login_not_found(self):
        resp = self.client.post(reverse('login_paciente'), {'email': 'noone@example.com', 'senha': 'whatever'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Conta não encontrada")

