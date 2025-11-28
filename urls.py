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
    path("profissionaisDisponiveis/", views.profissionaisDisponiveis, name="profissionaisDisponiveis"),
    path("verificarCodigo/", views.verificarCodigo, name="verificarCodigo"),
]
