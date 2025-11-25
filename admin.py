from django.contrib import admin
from .models import Clinica, Endereco, Servico, DiaDisponivel, HorarioDisponivel

class HorarioInline(admin.TabularInline):
    model = HorarioDisponivel
    extra = 3

class DiaInline(admin.TabularInline):
    model = DiaDisponivel
    extra = 2
    inlines = [HorarioInline]

@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'telefone', 'avaliacao']
    inlines = [DiaInline]

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ['clinica', 'rua', 'numero', 'bairro']

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'clinica']

@admin.register(DiaDisponivel)
class DiaDisponivelAdmin(admin.ModelAdmin):
    list_display = ['clinica', 'data']

@admin.register(HorarioDisponivel)
class HorarioDisponivelAdmin(admin.ModelAdmin):
    list_display = ['dia', 'hora']
