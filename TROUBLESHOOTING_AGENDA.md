# 🔧 Guia de Troubleshooting - Agenda

## Se a Agenda AINDA ficar em "Carregando..." 

### Passo 1: Capture os Logs
```
Abra o terminal onde o app está rodando
Procure por "[Agenda]" nos logs
Copie TODOS os logs desde [Agenda] render() até onde travar
```

### Passo 2: Identifique o Ponto de Travamento

#### ❌ Se ficar em "Carregando consultas..."
Significa que os logs NÃO estão aparecendo. Isso indica:
- **Causa:** Código não está sendo executado
- **Solução:** Verifique se o arquivo foi salvo corretamente
- **Teste:** `grep -n "_load_data_thread" SistemaDesktop/views/agenda.py`

#### ⚠️ Se aparecer "TIMEOUT"
```
[Agenda] ⚠️ TIMEOUT: Carregamento preso por 31.5s (thread_id=2). Resetando...
```
Significa que as 4 chamadas do controller demoraram > 30s
- **Causa:** Banco de dados lento ou com problema
- **Solução:** Verifique conexão do banco em `config/database.py`

#### ❌ Se aparecer erro como "listar_por_clinica demorou 25.42s"
```
[Agenda] ⚠️ listar_por_clinica demorou 25.42s (>10s)
```
- **Causa:** Query SQL muito complexa ou sem índices
- **Solução:** Otimizar query ou adicionar índices no banco

#### ❌ Se aparecer "Erro na carga de dados:"
```
[Agenda] ❌ Erro na carga de dados: <mensagem de erro>
```
- **Causa:** Exceção em uma das chamadas do controller
- **Solução:** Leia a mensagem de erro para diagnosticar
- **Exemplos comuns:**
  - `No module named ...` → falta import
  - `AttributeError` → método não existe
  - `database connection refused` → banco offline
  - `UnicodeDecodeError` → problema com encoding

---

## Checklist de Diagnóstico

### ✓ Verificar Arquivo Salvo
```powershell
# Confirmar que mudanças foram salvas
Select-String -Path "SistemaDesktop\views\agenda.py" -Pattern "_trace_enabled" | Select-Object -First 1
```
Esperado: Deve encontrar a linha `self._trace_enabled = False`

### ✓ Verificar Sintaxe
```powershell
.\.venv\Scripts\python.exe -m py_compile SistemaDesktop/views/agenda.py
```
Se não retornar erro, sintaxe está OK.

### ✓ Testar Import
```powershell
# Abra Python interativo
.\.venv\Scripts\python.exe

# No Python:
>>> from SistemaDesktop.config.database import get_connection
>>> get_connection()
>>> # Deve retornar conexão, não erro

>>> from SistemaDesktop.controllers.consulta_controller import ConsultaController
>>> # Sem erro
```

### ✓ Testar Método do Controller
```powershell
.\.venv\Scripts\python.exe

>>> from SistemaDesktop.controllers.consulta_controller import ConsultaController
>>> result = ConsultaController.listar_por_clinica(1, pagina=0, limite=7)
>>> print(len(result), "consultas")
```
Se retornar número > 0, o método funciona.

---

## Logs Esperados vs Problemáticos

### ✅ Logs Normais (Sucesso)
```
[Agenda] __init__ concluído. Iniciando render()
[Agenda] render() iniciado
[Agenda] render: Thread #1 iniciando _load_data_thread
[Agenda] render thread #1 iniciada
[Agenda] _load_data_thread iniciada
[Agenda] Filtros: data=None, medico=None, status=None, especialidade=None
[Agenda] → Chamando listar_por_clinica...
[Agenda] ✓ listar_por_clinica OK (0.45s) - 7 consultas
[Agenda] → Chamando contar_por_clinica...
[Agenda] ✓ contar_por_clinica OK (0.12s) - total=42
[Agenda] → Chamando listar_opcoes_filtro...
[Agenda] ✓ listar_opcoes_filtro OK (0.08s)
[Agenda] → Chamando snapshot_por_clinica...
[Agenda] ✓ snapshot_por_clinica OK (0.05s)
[Agenda] ✅ Todos os dados carregados em 0.70s
[Agenda] → Chamando _render_after_load no thread principal
[Agenda] render thread #1 concluída
[Agenda] _render_after_load iniciada
[Agenda] ✅ renderização concluída em 0.15s
[Agenda] ✓ Estado de carregamento resetado (finally block)
```

### ⚠️ Logs com Problema - SQL Lento
```
[Agenda] → Chamando listar_por_clinica...
[Agenda] ⚠️ listar_por_clinica demorou 15.32s (>10s)  ← LENTO!
[Agenda] → Chamando contar_por_clinica...
[Agenda] ✓ contar_por_clinica OK (0.12s)
...
[Agenda] ⚠️ TIMEOUT: Carregamento preso por 25.5s...
```
**Solução:** Otimizar query SQL ou banco de dados.

### ❌ Logs com Erro - Método Não Existe
```
[Agenda] _load_data_thread iniciada
[Agenda] → Chamando listar_por_clinica...
[Agenda] ❌ _load_data_thread error: 'ConsultaController' object has no attribute 'listar_por_clinica'
```
**Solução:** Verificar se o método existe em `consulta_controller.py`.

### ❌ Logs com Erro - Banco Offline
```
[Agenda] → Chamando listar_por_clinica...
[Agenda] ❌ _load_data_thread error: (2003, "Can't connect to MySQL server...")
```
**Solução:** Verificar se banco de dados está ativo.

---

## Rollback (Se Quebrar Algo)

Se as mudanças causarem problemas graves, é possível voltar:

### Opção 1: Versão sem diagnóstico
Mantenha as correções principais (trace_enabled, timeout) mas remove logs excessivos.

### Opção 2: Voltar à versão original
```powershell
# Se você tiver git
git diff SistemaDesktop/views/agenda.py
git checkout SistemaDesktop/views/agenda.py
```

---

## Reporte o Problema

Se mesmo com essas correções a Agenda não funcionar, colete:

```
1. Screenshot da tela (mostrando "Carregando consultas...")
2. Logs do terminal completos até onde travar
3. Saída de:
   .\.venv\Scripts\python.exe -c "from SistemaDesktop.controllers.consulta_controller import ConsultaController; print('OK')"
4. Se possível, tente conectar ao banco manualmente
```

---

## Dicas de Performance

Se os métodos aparecem lentos (> 2s), tente:

### 1. Verificar Índices do Banco
```sql
SHOW INDEXES FROM odontoPro_consulta;
SHOW INDEXES FROM odontoPro_paciente;
SHOW INDEXES FROM odontoPro_medico;
```

### 2. Otimizar Query
Em `consulta_controller.py`, adicionar LIMIT para não carregar tudo.
```python
# Adicione LIMIT nos SELECTs
LIMIT 100  # Para não trazer milhares de registros
```

### 3. Adicionar Cache
Se as datas/médicos nunca mudam, cache em memória.
```python
self._cache_medicos = None
self._cache_timestamp = 0
```

### 4. Lazy Loading
Carregar detalhes apenas quando necessário.
```python
# Em vez de buscar tudo
apenas_ids = [...]  # Carrega rápido
# Depois buscar detalhes
```

---

## Contato

Se precisar de ajuda:
1. Capture todos os logs [Agenda] 
2. Identifique qual etapa é lenta
3. Comunique o tempo exato (ex: "listar_por_clinica demorou 50s")
4. Isso dirá exatamente qual parte otimizar
