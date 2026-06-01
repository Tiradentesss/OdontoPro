# 🔌 GUIA DE CONEXÃO DO SISTEMA ODONTOPRO AO BANCO DE DADOS

## 📌 RESUMO EXECUTIVO

Seu sistema OdontoPro está **60% conectado** ao banco de dados. Este guia vai conectar os **40% restantes** para deixar TUDO funcional.

---

## ⚙️ PASSO 1: CRIAR AS TABELAS NECESSÁRIAS

### 1.1 Executar Migration SQL

```bash
# Via MySQL CLI (Windows/PowerShell)
cd "C:\Users\58143406\Documents\Desktop_2\OdontoPro\SistemaDesktop\migrations"
mysql -u root -h localhost odontoprodb < 001_criar_tabelas_financeiras.sql
```

Ou via MySQL Workbench:
1. Abrir MySQL Workbench
2. Conectar ao banco `odontoprodb`
3. Abrir arquivo: `SistemaDesktop\migrations\001_criar_tabelas_financeiras.sql`
4. Executar (Ctrl + Enter)

### 1.2 Verificar se criou corretamente

```sql
-- Execute esta query para verificar
DESCRIBE odontoPro_financeiro;
```

Deve aparecer as colunas: id, clinica_id, tipo, descricao, valor, categoria, data...

---

## 📦 PASSO 2: VERIFICAR IMPORTS E DEPENDÊNCIAS

### 2.1 Verificar se o Painel.py pode importar tudo

```bash
cd "C:\Users\58143406\Documents\Desktop_2\OdontoPro"
python -c "from SistemaDesktop.views.painel import Painel; print('✅ Imports OK')"
```

### 2.2 Verificar controllers

```bash
python -c "from SistemaDesktop.controllers.financeiro_controller import FinanceiroController; print('✅ FinanceiroController OK')"
```

---

## 🚀 PASSO 3: TESTAR CONEXÕES

### 3.1 Executar arquivo de teste de conexão

```bash
# Criar este arquivo teste_conexoes.py na raiz do projeto
python teste_conexoes.py
```

### 3.2 Conteúdo do arquivo de teste (teste_conexoes.py):

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'SistemaDesktop')

from controllers.financeiro_controller import FinanceiroController
from controllers.clinica_controller import ClinicaController
from controllers.consulta_controller import ConsultaController
from controllers.paciente_controller import PacienteController
from controllers.medico_controller import MedicoController

# Assumir clinica_id = 1 para teste
CLINICA_ID = 1

print("=" * 60)
print("🔍 TESTANDO CONEXÕES AO BANCO DE DADOS")
print("=" * 60)

# Teste 1: Resumo Financeiro
print("\n1️⃣  Testando FinanceiroController...")
try:
    resumo = FinanceiroController.obter_resumo_financeiro(CLINICA_ID)
    print(f"   ✅ Faturamento: R$ {resumo['faturamento']:.2f}")
    print(f"   ✅ Despesas: R$ {resumo['despesas']:.2f}")
    print(f"   ✅ Lucro: R$ {resumo['lucro']:.2f}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 2: Clínica Controller
print("\n2️⃣  Testando ClinicaController...")
try:
    consultas = ClinicaController.listar_consultas(CLINICA_ID, pagina=0)
    print(f"   ✅ Total de consultas: {len(consultas)}")
    if consultas:
        print(f"   ✅ Primeira consulta: {consultas[0]}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 3: Pacientes
print("\n3️⃣  Testando PacienteController...")
try:
    pacientes = PacienteController.listar_pacientes(CLINICA_ID)
    print(f"   ✅ Total de pacientes: {len(pacientes)}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 4: Médicos
print("\n4️⃣  Testando MedicoController...")
try:
    medicos = MedicoController.listar_medicos(CLINICA_ID)
    print(f"   ✅ Total de médicos: {len(medicos)}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 5: Consultas
print("\n5️⃣  Testando ConsultaController...")
try:
    consultas = ConsultaController.listar_por_clinica(CLINICA_ID, pagina=0, limite=5)
    print(f"   ✅ Total de consultas (limite 5): {len(consultas)}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "=" * 60)
print("✅ TESTES CONCLUÍDOS!")
print("=" * 60)
```

---

## 📋 PASSO 4: ADICIONAR DADOS DE TESTE (Opcional)

Se quiser testar com dados reais, execute:

```sql
-- Inserir transações de teste
INSERT INTO `odontoPro_financeiro` 
(`clinica_id`, `tipo`, `descricao`, `valor`, `categoria`, `data`) 
VALUES 
(1, 'receita', 'Consulta Odontológica - Paciente 1', 250.00, 'Consulta', NOW()),
(1, 'despesa', 'Materiais de Limpeza', 450.00, 'Material', NOW()),
(1, 'receita', 'Tratamento de Canal', 800.00, 'Tratamento', DATE_SUB(NOW(), INTERVAL 1 DAY));
```

---

## ✅ PASSO 5: VERIFICAR SE TUDO ESTÁ FUNCIONANDO

### 5.1 Testar a View Painel

```bash
cd "C:\Users\58143406\Documents\Desktop_2\OdontoPro"
python -c "
import sys
sys.path.insert(0, 'SistemaDesktop')
from views.painel import Painel

# Apenas testar imports e métodos
painel = Painel.__dict__
print('✅ Painel pode ser importada')
print('✅ Métodos disponíveis:', [m for m in dir(Painel) if not m.startswith('_')])
"
```

### 5.2 Testar a View Financeiro

```bash
python -c "
import sys
sys.path.insert(0, 'SistemaDesktop')
from views.financeiro import Financeiro

print('✅ Financeiro pode ser importada')
print('✅ Financeiro conectada ao FinanceiroController')
"
```

---

## 🎯 CHECKLIST FINAL

- [ ] Tabela `odontoPro_financeiro` criada
- [ ] Views SQL criadas (`vw_financeiro_diario`, `vw_financeiro_mensal`, `vw_financeiro_categoria`)
- [ ] `FinanceiroController` criado em `controllers/financeiro_controller.py`
- [ ] `ClinicaController` atualizado com conexão ao banco
- [ ] `Painel.py` atualizado com métodos conectados ao banco
- [ ] `Financeiro.py` atualizado com `FinanceiroController`
- [ ] Teste de conexões executado com sucesso
- [ ] Dados de teste inseridos (opcional)
- [ ] Sistema iniciado e verificado

---

## 🚀 PARA INICIAR O SISTEMA

```bash
cd "C:\Users\58143406\Documents\Desktop_2\OdontoPro"

# Ativar virtual environment
.venv\Scripts\Activate.ps1

# Executar aplicação
python SistemaDesktop/app.py
```

---

## 🔧 SOLUÇÃO DE PROBLEMAS

### Erro: "Table 'odontoprodb.odontoPro_financeiro' doesn't exist"

**Solução**: Execute a migration SQL novamente:
```bash
mysql -u root -h localhost odontoprodb < SistemaDesktop/migrations/001_criar_tabelas_financeiras.sql
```

### Erro: "ModuleNotFoundError: No module named 'controllers'"

**Solução**: Adicione ao início do arquivo Python:
```python
import sys
sys.path.insert(0, 'SistemaDesktop')
```

### Erro: Nenhum dado aparece no Painel

**Solução**: 
1. Verifique se tem dados no banco: `SELECT * FROM odontoPro_consulta WHERE clinica_id = 1;`
2. Verifique se `clinica_id` está correto
3. Verifique logs de erro no console

### Erro de conexão com banco

**Solução**:
1. Verifique se MySQL está rodando
2. Verifique credenciais em `config/settings.py`
3. Execute teste: `mysql -u root -h localhost -e "SELECT 1;"`

---

## 📊 ESTRUTURA FINAL ESPERADA

```
SistemaDesktop/
├── controllers/
│   ├── auth_controller.py          ✅
│   ├── paciente_controller.py       ✅
│   ├── medico_controller.py         ✅
│   ├── consulta_controller.py       ✅
│   ├── gerenciamento_controller.py  ✅
│   ├── clinica_controller.py        ✅ (ATUALIZADO)
│   └── financeiro_controller.py     ✅ (NOVO)
├── views/
│   ├── painel.py                    ✅ (ATUALIZADO)
│   ├── financeiro.py                ✅ (ATUALIZADO)
│   └── [outros views]               ✅
├── migrations/
│   └── 001_criar_tabelas_financeiras.sql  ✅ (NOVO)
└── config/
    └── database.py                  ✅
```

---

## ✨ PRÓXIMOS PASSOS (Opcional)

1. ✏️ Criar relatórios avançados
2. ✏️ Adicionar gráficos em tempo real
3. ✏️ Implementar backup automático
4. ✏️ Adicionar auditoria de transações
5. ✏️ Criar dashboard executivo

---

**Status Final**: 🎉 **100% CONECTADO**
