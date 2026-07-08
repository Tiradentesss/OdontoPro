import os
import sys

# Adicionar path do SistemaDesktop
projeto_dir = os.path.dirname(os.path.abspath(__file__))
sistema_dir = os.path.join(projeto_dir, 'SistemaDesktop')
sys.path.insert(0, sistema_dir)

from config.database import get_connection

conn = get_connection()
cursor = conn.cursor(dictionary=True)

print('=' * 60)
print('VERIFICANDO USUÁRIOS NO BANCO')
print('=' * 60)
print()

print('--- CLÍNICAS CADASTRADAS ---')
cursor.execute('SELECT id, nome, email FROM odontoPro_clinica')
clinicas = cursor.fetchall()
print(f'Total de clínicas: {len(clinicas)}')
if clinicas:
    for c in clinicas:
        print(f'  ID: {c["id"]}, Nome: {c["nome"]}, Email: {c["email"]}')
else:
    print('  ⚠️  Nenhuma clínica cadastrada!')
print()

print('--- GERENCIAMENTO (ADMINISTRADORES) ---')
cursor.execute('SELECT id, nome, email, ativo FROM odontoPro_gerenciamento')
gerenc = cursor.fetchall()
print(f'Total de gerentes: {len(gerenc)}')
if gerenc:
    for g in gerenc:
        status = '✅ ATIVO' if g["ativo"] else '❌ INATIVO'
        print(f'  ID: {g["id"]}, Nome: {g["nome"]}, Email: {g["email"]} ({status})')
else:
    print('  ⚠️  Nenhum gerente cadastrado!')
print()

print('--- PACIENTES CADASTRADOS ---')
cursor.execute('SELECT id, nome, email FROM odontoPro_paciente LIMIT 5')
pacientes = cursor.fetchall()
cursor.execute('SELECT COUNT(*) as total FROM odontoPro_paciente')
total_pac = cursor.fetchone()
print(f'Total de pacientes: {total_pac["total"]}')
if pacientes:
    print('Primeiros 5:')
    for p in pacientes:
        print(f'  ID: {p["id"]}, Nome: {p["nome"]}, Email: {p["email"]}')
print()

print('--- MÉDICOS CADASTRADOS ---')
cursor.execute('SELECT id, nome, email FROM odontoPro_medico LIMIT 5')
medicos = cursor.fetchall()
cursor.execute('SELECT COUNT(*) as total FROM odontoPro_medico')
total_med = cursor.fetchone()
print(f'Total de médicos: {total_med["total"]}')
if medicos:
    print('Primeiros 5:')
    for m in medicos:
        print(f'  ID: {m["id"]}, Nome: {m["nome"]}, Email: {m["email"]}')
print()

print('=' * 60)
print('✅ BANCO DE DADOS CONECTADO E FUNCIONAL')
print('=' * 60)

cursor.close()
conn.close()
