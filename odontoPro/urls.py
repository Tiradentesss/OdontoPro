from django.urls import path
from . import views

urlpatterns = [
    path("", views.login, name="login"),
    path("criarConta/", views.criarConta, name="criarConta"),
    path("recuperarSenha/", views.recuperarSenha, name="recuperarSenha"),
    path("menuPrincipal/", views.menuPrincipal, name="menuPrincipal"),
    path("configuracoes/", views.configuracoes, name="configuracoes"),
    path("novaSenha/", views.novaSenha, name="novaSenha"),
    path("profissional/<int:id>/", views.perfilDoProfissional, name="perfilDoProfissional"),
    path('perfil/<int:clinica_id>/', views.perfil, name='perfil'),
    path("clinica/<int:clinica_id>/profissionais/", views.profissionaisDisponiveis, name="profissionaisDisponiveis"),
    path("clinica/<int:clinica_id>/profissionais/", views.profissionaisDisponiveis, name="profissionaisDisponiveis"),
    path("verificarCodigo/", views.verificarCodigo, name="verificarCodigo"),

    # AJAX / actions for perfil do profissional
    path("api/medico/<int:medico_id>/horarios/", views.get_horarios_medico, name="api_get_horarios_medico"),
    path("api/medico/<int:medico_id>/agendar/", views.agendar_profissional, name="agendarProfissional"),

    path("logout/", views.logout, name="logout"),

    path("pagamento/", views.pagamento, name="pagamento"),
    path("consultas/", views.consultas, name="consultas"),
    path("cadastroclinica/", views.cadastroclinica, name="cadastroclinica"),
]