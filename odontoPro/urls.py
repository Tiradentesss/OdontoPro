from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # LOGIN
    path('', views.login_paciente, name='login_paciente'),
    path('login/', views.login_paciente, name='login_paciente'),
    path("login-clinica/", views.login_clinica, name="login_clinica"),

    # DASHBOARD
    path('dashboard-paciente/', views.dashboard_paciente, name='dashboard_paciente'),

    # LOGOUT
    path('logout/', views.logout_view, name='logout'),

    # CLÍNICA
    path("clinica/<int:clinica_id>/", views.perfil_clinica, name="perfilClinica"),

    # CONSULTAS
    path("consulta/<int:consulta_id>/cancelar/", views.cancelar_consulta, name="cancelar_consulta"),
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
]
