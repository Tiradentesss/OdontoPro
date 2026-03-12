from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.core import signing
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
        # session key should exist and persist across follow-up GET
        key = self.client.session.session_key
        self.assertIsNotNone(key)
        # follow redirect to dashboard
        resp2 = self.client.get(reverse('dashboard_paciente'))
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(self.client.session.session_key, key)

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

    def test_config_update_keeps_session(self):
        # login first
        self.client.post(reverse('login_paciente'), {'email': 'user@example.com', 'senha': 'senha123'})
        # session should now contain paciente_id
        self.assertEqual(self.client.session.get('paciente_id'), self.paciente.id)
        # perform POST to config
        resp = self.client.post(reverse('configuracoes_conta'), {
            'nome': 'Novo Nome',
            'email': 'user@example.com',
            'cpf': '12345678901',
            'telefone': '999888777',
        })
        # should redirect to dashboard
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('dashboard_paciente'))
        # ensure paciente updated
        self.paciente.refresh_from_db()
        self.assertEqual(self.paciente.nome, 'Novo Nome')
        self.assertEqual(self.paciente.cpf, '12345678901')
        self.assertEqual(self.paciente.telefone, '999888777')

    def test_config_requires_login(self):
        # no login
        resp = self.client.post(reverse('configuracoes_conta'), {
            'nome': 'x',
            'email': 'x',
        })
        # should redirect to login page
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('login_paciente'))

    def test_config_restores_session_from_signed_uid(self):
        # login normally first to generate signed uid
        self.client.post(reverse('login_paciente'), {'email': 'user@example.com', 'senha': 'senha123'})
        # fetch dashboard to obtain generated uid in the page
        resp_page = self.client.get(reverse('dashboard_paciente'))
        self.assertEqual(resp_page.status_code, 200)
        self.assertIn('name="uid"', resp_page.content.decode())
        # extract the value from hidden field
        import re
        m = re.search(r'name="uid" value="([^"]+)"', resp_page.content.decode())
        self.assertIsNotNone(m, "UID hidden input missing")
        uid_from_page = m.group(1)

        # clear session as if expired
        self.client.session.flush()
        self.assertIsNone(self.client.session.get('paciente_id'))

        # post with signed uid obtained from dashboard
        resp = self.client.post(reverse('configuracoes_conta'), {
            'nome': 'Outra Coisa',
            'email': 'user@example.com',
            'cpf': '',
            'telefone': '',
            'uid': uid_from_page,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('dashboard_paciente') + '?open=ajustes')
        self.paciente.refresh_from_db()
        self.assertEqual(self.paciente.nome, 'Outra Coisa')

    def test_config_invalid_uid_redirects_and_logs(self):
        # login and then clear session to simulate expiration
        self.client.post(reverse('login_paciente'), {'email': 'user@example.com', 'senha': 'senha123'})
        self.client.session.flush()
        # post with a deliberately bad signature
        with self.assertLogs('odontoPro.views', level='WARNING') as cm:
            resp = self.client.post(reverse('configuracoes_conta'), {
                'nome': 'X',
                'email': 'user@example.com',
                'uid': 'not-a-valid-signature',
            }, follow=True)
        # should be sent back to login because we could not restore session
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'LoginCadastro/login.html')
        self.assertContains(resp, 'Sua sessão expirou')
        # logger should contain our warning about invalid uid
        self.assertTrue(any('uid inválido' in msg for msg in cm.output),
                        f"Expected invalid uid warning in logs but got {cm.output}")

    def test_change_password_with_fallback(self):
        # login and flush session to simulate expiration
        self.client.post(reverse('login_paciente'), {'email': 'user@example.com', 'senha': 'senha123'})
        uid = signing.dumps(self.paciente.id)
        self.client.session.flush()
        resp = self.client.post(reverse('alterar_senha_paciente'), {
            'senha_atual': 'senha123',
            'nova_senha': 'novasenha',
            'confirmar_senha': 'novasenha',
            'uid': uid,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('configuracoes_conta'))
        self.paciente.refresh_from_db()
        from django.contrib.auth.hashers import check_password
        self.assertTrue(check_password('novasenha', self.paciente.senha))

