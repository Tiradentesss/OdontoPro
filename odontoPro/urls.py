from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # LOGIN PACIENTE (página inicial)
    path('', views.login_paciente, name='login_paciente'),
    path('login/', views.login_paciente, name='login_paciente'),

    # LOGIN CLÍNICA
    path('login-clinica/', views.login_clinica, name='login_clinica'),

    # DASHBOARDS
    path('dashboard-paciente/', views.dashboard_paciente, name='dashboard_paciente'),
    path('dashboard-clinica/', views.dashboard_clinica, name='dashboard_clinica'),

    # LOGOUT
    path('logout/', views.logout_view, name='logout'),
]
