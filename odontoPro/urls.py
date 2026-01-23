from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    path("clinica/<int:clinica_id>/perfil/", views.clinica_perfil, name="clinica_perfil"),
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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)