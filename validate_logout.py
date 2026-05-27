from django.test import Client
from django.urls import reverse
from odontoPro.models import Paciente

c = Client()
paciente = Paciente.objects.filter(email='user@example.com').first()
print('paciente_exists', bool(paciente))
if not paciente:
    raise SystemExit('no seed user')

login_resp = c.post(reverse('login_paciente'), {'email': 'user@example.com', 'senha': 'senha123'})
print('login_status', login_resp.status_code, 'redirect', login_resp['Location'])
print('session_paciente_id', c.session.get('paciente_id'))
print('uid_signed_cookie', login_resp.cookies.get('uid_signed').value if 'uid_signed' in login_resp.cookies else None)

logout_resp = c.post(reverse('logout'))
print('logout_status', logout_resp.status_code, 'redirect', logout_resp['Location'])
print('post_logout_session_paciente_id', c.session.get('paciente_id'))
print('post_logout_uid_signed_max_age', logout_resp.cookies['uid_signed']['max-age'])

login_page = c.get(reverse('login_paciente'))
print('login_page_status', login_page.status_code)
print('template_used', getattr(login_page, 'template_name', None))
