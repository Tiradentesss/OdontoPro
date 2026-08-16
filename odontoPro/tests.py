from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.core import signing
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.templatetags.static import static
from .models import (
    Paciente, Medico, Clinica, Consulta, Endereco, Especialidade, Gerenciamento,
    Permissao, Financeiro, ClinicaImagem, DiaSemanaDisponivel, HorarioAberto
)


class FinanceiroDashboardTests(TestCase):
    def setUp(self):
        self.endereco = Endereco.objects.create(
            cep="00000000",
            numero="1",
            quadra="",
            rua="Rua X",
            bairro="Centro",
            cidade="Belém",
            estado="PA"
        )
        self.clinica = Clinica.objects.create(
            nome="Clinica Financeira",
            cnpj="00000000",
            endereco=self.endereco,
            telefone="999999999",
            conta_bancaria_juridica="0000-0",
            email="financeiro@example.com",
            senha=make_password("clinica123")
        )
        self.paciente = Paciente.objects.create(
            nome="Paciente Teste",
            email="paciente@example.com",
            senha=make_password("123456"),
            telefone="999999999",
            clinica=self.clinica,
        )
        self.medico = Medico.objects.create(
            nome="Dr. Financeiro",
            email="medico-financeiro@example.com",
            senha=make_password("medsenha"),
            telefone="988888888",
            crm_cro="9999",
            clinica=self.clinica,
        )
        Consulta.objects.create(
            paciente=self.paciente,
            nome=self.paciente.nome,
            email=self.paciente.email,
            telefone=self.paciente.telefone,
            clinica=self.clinica,
            medico=self.medico,
            data_hora=timezone.now() + timezone.timedelta(days=1),
            status='agendada',
        )
        Consulta.objects.create(
            paciente=self.paciente,
            nome=self.paciente.nome,
            email=self.paciente.email,
            telefone=self.paciente.telefone,
            clinica=self.clinica,
            medico=self.medico,
            data_hora=timezone.now(),
            status='realizada',
        )
        Financeiro.objects.create(
            clinica=self.clinica,
            tipo='receita',
            descricao='Consulta de retorno',
            valor='150.00',
            categoria='consulta'
        )
        Financeiro.objects.create(
            clinica=self.clinica,
            tipo='despesa',
            descricao='Aluguel',
            valor='80.00',
            categoria='aluguel'
        )

    def test_finance_dashboard_uses_database_entries(self):
        session = self.client.session
        session['clinica_id'] = self.clinica.id
        session.save()

        response = self.client.get(reverse('painel_profissional'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-target="relatorio"')
        self.assertContains(response, 'Relatório')
        self.assertContains(response, '100%')

    def test_painel_profissional_shows_new_reports_center(self):
        session = self.client.session
        session['clinica_id'] = self.clinica.id
        session.save()

        response = self.client.get(reverse('painel_profissional'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Centro de Relatórios')
        self.assertContains(response, 'Exportar para Excel (CSV)')
        self.assertContains(response, 'Relatório Gerencial Odontológico')


class ClinicBusinessHoursApiTests(TestCase):
    def setUp(self):
        self.endereco = Endereco.objects.create(
            cep="00000000",
            numero="1",
            quadra="",
            rua="Rua X",
            bairro="Centro",
            cidade="Belém",
            estado="PA"
        )
        self.clinica = Clinica.objects.create(
            nome="Clinica Horarios",
            cnpj="12345678000199",
            endereco=self.endereco,
            telefone="999999999",
            conta_bancaria_juridica="0000-0",
            email="horarios@example.com",
            senha=make_password("clinica123")
        )

    def test_clinica_detalhes_includes_all_week_days_business_hours(self):
        dias = {
            'segunda': '08:00',
            'terca': '08:00',
            'quarta': '08:00',
            'quinta': '08:00',
            'sexta': '08:00',
            'sabado': '08:00',
            'domingo': None,
        }

        for dia, hora_inicio in dias.items():
            dia_registro = DiaSemanaDisponivel.objects.create(clinica=self.clinica, dia=dia)
            if hora_inicio:
                HorarioAberto.objects.create(
                    dia=dia_registro,
                    hora_inicio=hora_inicio,
                    hora_fim='18:00' if dia != 'sabado' else '15:00'
                )

        resp = self.client.get(reverse('clinica_detalhes', args=[self.clinica.id]))
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertIn('horarios_funcionamento', payload)
        horarios = payload['horarios_funcionamento']
        self.assertEqual(len(horarios), 7)
        self.assertEqual(horarios[0]['dia'], 'segunda')
        self.assertEqual(horarios[0]['hora_inicio'], '08:00')
        self.assertEqual(horarios[0]['hora_fim'], '18:00')
        self.assertFalse(horarios[0]['fechado'])
        self.assertEqual(horarios[5]['dia'], 'sabado')
        self.assertEqual(horarios[5]['hora_inicio'], '08:00')
        self.assertEqual(horarios[5]['hora_fim'], '15:00')
        self.assertFalse(horarios[5]['fechado'])
        self.assertEqual(horarios[6]['dia'], 'domingo')
        self.assertTrue(horarios[6]['fechado'])
        self.assertIsNone(horarios[6]['hora_inicio'])
        self.assertIsNone(horarios[6]['hora_fim'])


class DashboardHomeImageRegressionTests(TestCase):
    def setUp(self):
        self.endereco = Endereco.objects.create(
            cep="00000000",
            numero="1",
            quadra="",
            rua="Rua X",
            bairro="Centro",
            cidade="Belém",
            estado="PA"
        )
        self.clinica = Clinica.objects.create(
            nome="Clinica Image Test",
            cnpj="00000000",
            endereco=self.endereco,
            telefone="999999999",
            conta_bancaria_juridica="0000-0",
            email="clinica-image@example.com",
            senha=make_password("clinica123"),
            ativo=True,
            avaliacao=5.0,
        )
        self.paciente = Paciente.objects.create(
            nome="Paciente Teste",
            email="paciente-image@example.com",
            senha=make_password("123456"),
            telefone="999999999",
            clinica=self.clinica,
        )

    @patch('odontoPro.views._url_responds', side_effect=lambda url: False)
    def test_dashboard_does_not_push_broken_gallery_urls_to_banner_images(self, _mock_responds):
        with open('odontoPro/static/img/sem-foto.jpg', 'rb') as handle:
            data = handle.read()
        uploaded = SimpleUploadedFile('banner.jpg', data, content_type='image/jpeg')
        ClinicaImagem.objects.create(clinica=self.clinica, imagem=uploaded)

        session = self.client.session
        session['paciente_id'] = self.paciente.id
        session.save()

        response = self.client.get(reverse('dashboard_paciente'))
        self.assertEqual(response.status_code, 200)
        context_clinicas = list(response.context['clinicas'])
        self.assertTrue(context_clinicas)
        first_clinica = context_clinicas[0]
        self.assertEqual(first_clinica.banner_images, [static('img/sem-foto.jpg')])


class LoginViewTests(TestCase):
    def setUp(self):
        # create a sample paciente and medico
        self.paciente = Paciente.objects.create(
            nome="Usuário Teste",
            email="user@example.com",
            senha=make_password("senha123"),
            telefone="123456789"
        )
        self.endereco = Endereco.objects.create(
            cep="00000000",
            numero="1",
            quadra="",
            rua="Rua X",
            bairro="Centro",
            cidade="Belém",
            estado="PA"
        )
        self.clinica = Clinica.objects.create(
            nome="Clinica X",
            cnpj="00000000",
            endereco=self.endereco,
            telefone="999999999",
            conta_bancaria_juridica="0000-0",
            email="clinica@example.com",
            senha=make_password("clinica123")
        )
        self.medico = Medico.objects.create(
            nome="Dr. Teste",
            email="medico@example.com",
            senha=make_password("medsenha"),
            telefone="987654321",
            crm_cro="1234",
            clinica=self.clinica
        )
        self.permissao_gerenciamento = Permissao.objects.create(
            codigo="acesso_gerenciamento",
            descricao="Acesso ao painel de gestão"
        )
        self.gerente = Gerenciamento.objects.create(
            nome="Gerente Autorizado",
            email="gerente@example.com",
            senha=make_password("gerente123"),
            clinica=self.clinica
        )
        self.gerente.permissoes.add(self.permissao_gerenciamento)

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
        resp = self.client.post(reverse('login_clinica'), {'email': 'medico@example.com', 'senha': 'medsenha'})
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('painel_profissional'))
        self.assertEqual(self.client.session.get('medico_id'), self.medico.id)

    def test_login_clinica_page_renders(self):
        resp = self.client.get(reverse('login_clinica'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'LoginCadastro/login_profissional.html')

    def test_login_clinica_with_clinica_success(self):
        resp = self.client.post(reverse('login_clinica'), {'email': 'clinica@example.com', 'senha': 'clinica123'})
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('painel_profissional'))
        self.assertEqual(self.client.session.get('clinica_id'), self.clinica.id)

    def test_login_clinica_with_gerente_success(self):
        resp = self.client.post(reverse('login_clinica'), {'email': 'gerente@example.com', 'senha': 'gerente123'})
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('painel_profissional'))
        self.assertEqual(self.client.session.get('gerente_id'), self.gerente.id)
        self.assertEqual(self.client.session.get('clinica_id'), self.clinica.id)

    def test_login_clinica_gerente_without_permission(self):
        gerente_sem_permissao = Gerenciamento.objects.create(
            nome="Gerente Sem Acesso",
            email="gerente-nao@example.com",
            senha=make_password("gerente123"),
            clinica=self.clinica
        )
        resp = self.client.post(reverse('login_clinica'), {'email': 'gerente-nao@example.com', 'senha': 'gerente123'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Acesso negado. Gerente não tem permissão de gerenciamento.')

    def test_login_clinica_wrong_password(self):
        resp = self.client.post(reverse('login_clinica'), {'email': 'medico@example.com', 'senha': 'wrong'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Senha incorreta.')

    def test_logout_clears_session_and_uid_cookie(self):
        resp = self.client.post(reverse('login_paciente'), {'email': 'user@example.com', 'senha': 'senha123'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.client.session.get('paciente_id'), self.paciente.id)
        self.assertIn('uid_signed', resp.cookies)

        logout_resp = self.client.post(reverse('logout'))
        self.assertEqual(logout_resp.status_code, 302)
        self.assertRedirects(logout_resp, reverse('login_paciente'))
        self.assertIsNone(self.client.session.get('paciente_id'))
        self.assertEqual(logout_resp.cookies['uid_signed']['max-age'], 0)

        login_page = self.client.get(reverse('login_paciente'))
        self.assertEqual(login_page.status_code, 200)
        self.assertTemplateUsed(login_page, 'LoginCadastro/login.html')

    def test_logout_redirects_to_login_clinica_for_professional(self):
        resp = self.client.post(reverse('login_clinica'), {'email': 'clinica@example.com', 'senha': 'clinica123'})
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('painel_profissional'))
        self.assertEqual(self.client.session.get('clinica_id'), self.clinica.id)

        logout_resp = self.client.post(reverse('logout'))
        self.assertEqual(logout_resp.status_code, 302)
        self.assertRedirects(logout_resp, reverse('login_clinica'))
        self.assertIsNone(self.client.session.get('clinica_id'))
        self.assertEqual(logout_resp.cookies['uid_signed']['max-age'], 0)

    def test_cadastro_clinica_salva_especialidades(self):
        logo = SimpleUploadedFile('logo3.png', b'\x89PNG\r\n\x1a\n', content_type='image/png')

        response = self.client.post(
            reverse('cadastro_clinica'),
            {
                'nome': 'Clinica Especialidades',
                'descricao': 'Descrição teste',
                'telefone': '123456789',
                'email': 'especialidades@clinica.com',
                'senha': '123456',
                'confirmar_senha': '123456',
                'cnpj': '123456789',
                'cep': '12345678',
                'estado': 'PA',
                'cidade': 'Belém',
                'bairro': 'Centro',
                'rua': 'Rua Teste',
                'numero': '100',
                'especialidades': ['Ortodontia', 'Implantodontia'],
                'logo': logo,
            },
            format='multipart'
        )

        self.assertEqual(response.status_code, 302)
        clinica = Clinica.objects.filter(email='especialidades@clinica.com').first()
        self.assertIsNotNone(clinica)
        self.assertEqual(clinica.especialidades.count(), 2)
        self.assertSetEqual(
            set(clinica.especialidades.values_list('nome', flat=True)),
            {'Ortodontia', 'Implantodontia'}
        )

    def test_login_wrong_password(self):
        resp = self.client.post(reverse('login_paciente'), {'email': 'user@example.com', 'senha': 'wrong'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Senha incorreta.")

    def test_login_not_found(self):
        resp = self.client.post(reverse('login_paciente'), {'email': 'noone@example.com', 'senha': 'whatever'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Conta não encontrada")

    def test_download_desktop_page_is_available(self):
        resp = self.client.get(reverse('download_desktop'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'download_desktop.html')
        self.assertContains(resp, 'Baixe o aplicativo Desktop')

    def test_login_page_has_home_link(self):
        resp = self.client.get(reverse('login_paciente'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Voltar para a Home')
        self.assertContains(resp, 'href="/"')

    def test_home_download_button_points_to_professional_login(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'href="/login-clinica/"')

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
        # should redirect to dashboard settings tab
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('dashboard_paciente') + '?open=ajustes')
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
        resp = self.client.post(reverse('configuracoes_conta'), {
            'nome': 'X',
            'email': 'user@example.com',
            'uid': 'not-a-valid-signature',
        }, follow=True)
        # should be sent back to login because we could not restore session
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'LoginCadastro/login.html')
        self.assertContains(resp, 'Sua sessão expirou')

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

    def helper_create_clinic_and_doctor(self):
        endereco = Endereco.objects.create(
            cep="11111111",
            numero="10",
            quadra="",
            rua="Rua Y",
            bairro="Centro",
            cidade="Belém",
            estado="PA"
        )
        clinica = Clinica.objects.create(
            nome="Clinica Y",
            cnpj="11111111",
            endereco=endereco,
            telefone="43211234",
            conta_bancaria_juridica="0000-0",
            email="clinicay@example.com",
            senha=make_password("clave")
        )
        medico = Medico.objects.create(
            nome="Dr. Agendar",
            email="dia@example.com",
            senha=make_password("pwd"),
            telefone="000",
            crm_cro="999",
            clinica=clinica
        )
        return clinica, medico

    def test_agendar_consulta_assigns_patient_and_keeps_session(self):
        # prepare clinic and doctor
        clinica, medico = self.helper_create_clinic_and_doctor()
        # login
        self.client.post(reverse('login_paciente'), {'email': 'user@example.com', 'senha': 'senha123'})
        key_before = self.client.session.session_key
        # schedule appointment via POST
        resp = self.client.post(reverse('agendar_consulta'), {
            'clinica_id': clinica.id,
            'medico_id': medico.id,
            'especialidade': '',
            'data_hora': '2025-01-01T10:00:00',
            'nome': 'Usuário Teste',
            'email': 'user@example.com',
            'telefone': '123456789',
            'uid': signing.dumps(self.paciente.id),
        })
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(resp.content, {'success': True})
        # appointment should exist with paciente foreign key set
        cons = Consulta.objects.get(clinica=clinica, medico=medico)
        self.assertEqual(cons.paciente, self.paciente)
        # session key remains unchanged
        self.assertEqual(self.client.session.session_key, key_before)

    def test_clinica_detalhes_retains_only_clinic_specialties(self):
        clinica, medico = self.helper_create_clinic_and_doctor()
        outra_endereco = Endereco.objects.create(
            cep='22222222',
            numero='20',
            quadra='',
            rua='Rua Z',
            bairro='Bairro Norte',
            cidade='Belém',
            estado='PA'
        )
        outra_clinica = Clinica.objects.create(
            nome='Outra Clínica',
            cnpj='22222222',
            endereco=outra_endereco,
            telefone='55555555',
            conta_bancaria_juridica='1111-1',
            email='outraclinica@example.com',
            senha=make_password('senhaoutra')
        )
        especialidade_clinica = Especialidade.objects.create(
            clinica=clinica,
            nome='Ortodontia',
            preco='150.00'
        )
        especialidade_outra = Especialidade.objects.create(
            clinica=outra_clinica,
            nome='Periodontia',
            preco='200.00'
        )
        medico.especialidades.add(especialidade_clinica, especialidade_outra)

        resp = self.client.get(reverse('clinica_detalhes', args=[clinica.id]))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        ids = [esp[0] for esp in data.get('especialidades', [])]
        self.assertIn(especialidade_clinica.id, ids)
        self.assertNotIn(especialidade_outra.id, ids)

    def test_agendar_consulta_with_lost_session_and_signed_uid(self):
        clinica, medico = self.helper_create_clinic_and_doctor()
        # login normally
        self.client.post(reverse('login_paciente'), {'email': 'user@example.com', 'senha': 'senha123'})
        # fetch dashboard and get signed uid hidden value
        resp_page = self.client.get(reverse('dashboard_paciente'))
        import re
        page_text = resp_page.content.decode()
        m = re.search(r'id="signedUidForAgendar"[^>]*value="([^"]+)"', page_text)
        if not m:
            # fallback legacy order
            m = re.search(r'value="([^"]+)"[^>]*id="signedUidForAgendar"', page_text)
        self.assertIsNotNone(m, "Hidden signedUidForAgendar input not found")
        uid_from_page = m.group(1)
        # simulate session expiration
        self.client.session.flush()
        # send schedule with uid
        resp = self.client.post(reverse('agendar_consulta'), {
            'clinica_id': clinica.id,
            'medico_id': medico.id,
            'especialidade': '',
            'data_hora': '2025-01-02T11:00:00',
            'nome': 'Outro Nome',
            'email': 'user@example.com',
            'telefone': '123456789',
            'uid': uid_from_page,
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        cons = Consulta.objects.filter(clinica=clinica, medico=medico, nome='Outro Nome').first()
        self.assertIsNotNone(cons)
        self.assertEqual(cons.paciente, self.paciente)

    def test_cadastro_clinica_fallback_imagem_para_logo(self):
        logo = SimpleUploadedFile('logo.png', b'\x89PNG\r\n\x1a\n', content_type='image/png')

        response = self.client.post(
            reverse('cadastro_clinica'),
            {
                'nome': 'Clinica Fallback',
                'descricao': 'Descrição teste',
                'telefone': '123456789',
                'email': 'fallback@clinica.com',
                'senha': '123456',
                'confirmar_senha': '123456',
                'cnpj': '123456789',
                'cep': '12345678',
                'estado': 'PA',
                'cidade': 'Belém',
                'bairro': 'Centro',
                'rua': 'Rua Teste',
                'numero': '100',
                'logo': logo,
            },
            format='multipart'
        )

        self.assertEqual(response.status_code, 302)
        clinica = Clinica.objects.filter(email='fallback@clinica.com').first()
        self.assertIsNotNone(clinica)
        self.assertIsNotNone(clinica.logo)
        self.assertIsNotNone(clinica.imagem)
        self.assertTrue(clinica.imagem.name.endswith('.png'))

    def test_cadastro_clinica_com_imagem_e_logo(self):
        logo = SimpleUploadedFile('logo2.png', b'\x89PNG\r\n\x1a\n', content_type='image/png')
        imagem = SimpleUploadedFile('banner2.png', b'\x89PNG\r\n\x1a\n', content_type='image/png')

        response = self.client.post(
            reverse('cadastro_clinica'),
            {
                'nome': 'Clinica Com Imagem',
                'descricao': 'Descrição teste',
                'telefone': '123456789',
                'email': 'comimagem@clinica.com',
                'senha': '123456',
                'confirmar_senha': '123456',
                'cnpj': '123456789',
                'cep': '12345678',
                'estado': 'PA',
                'cidade': 'Belém',
                'bairro': 'Centro',
                'rua': 'Rua Teste',
                'numero': '100',
                'logo': logo,
                'imagem': imagem,
            },
            format='multipart'
        )

        self.assertEqual(response.status_code, 302)
        clinica = Clinica.objects.filter(email='comimagem@clinica.com').first()
        self.assertIsNotNone(clinica)
        self.assertIsNotNone(clinica.logo)
        self.assertIsNotNone(clinica.imagem)
        self.assertNotEqual(clinica.imagem.name, '')

