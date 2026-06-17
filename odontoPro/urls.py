from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # HOME / LOGIN
    path('', views.home, name='home'),
    path('login/', views.login_paciente, name='login_paciente'),
    path("cadastro-clinica/", views.cadastro_clinica, name="cadastro_clinica"),
    path("login-clinica/", views.login_clinica, name="login_clinica"),

    # DASHBOARD
    path('dashboard-paciente/', views.dashboard_paciente, name='dashboard_paciente'),
    path('painel-profissional/', views.painel_profissional, name='painel_profissional'),
    path('home/', views.home, name='home'),
    path('download-desktop/', views.download_desktop, name='download_desktop'),

    # LOGOUT
    path('logout/', views.logout_view, name='logout'),

    # CLÍNICA
    path("clinica/<int:clinica_id>/", views.perfil_clinica, name="perfilClinica"),
    path("clinicas/gerenciar/", views.gerenciar_clinicas, name="gerenciar_clinicas"),
    path("clinica/<int:clinica_id>/editar/", views.editar_clinica, name="editar_clinica"),
    path("clinica/<int:clinica_id>/imagem/adicionar/", views.adicionar_imagem_clinica, name="adicionar_imagem_clinica"),
    path("imagem/<int:imagem_id>/deletar/", views.deletar_imagem_clinica, name="deletar_imagem_clinica"),

    # CONSULTAS
    path("consulta/<int:consulta_id>/cancelar/", views.cancelar_consulta, name="cancelar_consulta"),
    path("consulta/<int:consulta_id>/confirmar/", views.confirmar_consulta, name="confirmar_consulta"),
    path("consulta/<int:consulta_id>/reagendar/", views.reagendar_consulta, name="reagendar_consulta"),

    # 🔹 NOVO — FILTRO SEM RECARREGAR PÁGINA
    path("consultas/filtrar/", views.filtrar_consultas, name="filtrar_consultas"),

    # 🔹 Retorna especialidades e médicos da clínica
    path("clinica/<int:clinica_id>/detalhes/", views.clinica_detalhes, name="clinica_detalhes"),

    # 🔹 Agendar consulta
    path("consulta/agendar/", views.agendar_consulta, name="agendar_consulta"),

    path("clinica/<int:clinica_id>/horarios/",views.horarios_clinica,name="horarios_clinica"),

    path('configuracoes/', views.configuracoes_conta, name='configuracoes_conta'),
    path('alterar-senha/', views.alterar_senha_paciente, name='alterar_senha_paciente'),

    path('cadastrar/', views.cadastrar_paciente, name='cadastrar_paciente'),
    
    # 🔹 AVALIAÇÃO
    path('avaliacao/criar/', views.criar_avaliacao, name='criar_avaliacao'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)