# 📋 Diagnóstico: Carregamento Infinito da Agenda

## ❌ PROBLEMAS IDENTIFICADOS

### 1. **Loop infinito de trace_add (CRÍTICO)**
**Localização:** `__init__()` linhas 61-67

**Problema:**
```python
self.data_var.trace_add('write', self.aplicar_filtros)
self.medico_var.trace_add('write', self.aplicar_filtros)
# ...
self.render()
```

Os `trace_add` eram configurados ANTES da inicialização estar completa. Se qualquer callback modificasse as variáveis durante o render, acionaria `aplicar_filtros()` → `refresh_data()` → `render()` novamente, criando um loop.

**Solução:** Flag `_trace_enabled` desabilitada durante `__init__` e ativada apenas após inicialização.

---

### 2. **Falta de timeout em chamadas do controller (CRÍTICO)**
**Localização:** `_load_data_thread()` linhas 245-290

**Problema:**
```python
# SEM timeout - se a query der hang, thread fica presa eternamente
consultas = ConsultaController.listar_por_clinica(...)
```

Se alguma query SQL demorar ou travar no banco de dados, o programa inteiro fica congelado.

**Solução:** 
- Adicionado monitoramento de tempo para cada chamada
- Alerta se demorar > 10 segundos
- Timeout geral de 35 segundos (força reset se não completar)

---

### 3. **Sem proteção contra múltiplas threads simultâneas**
**Problema:**
```python
def render(self):
    if self._loading: return
    self._loading = True
    thread = threading.Thread(...)  # Thread 1
```

Se `render()` e `refresh_data()` fossem chamadas simultaneamente, apenas uma checaria `_loading`. A outra iniciaria uma segunda thread concorrente, causando inconsistências.

**Solução:** Adicionado `_thread_count` para rastrear e identificar cada thread com ID único.

---

### 4. **Sem logs diagnósticos detalhados**
**Problema:**
Impossível saber onde o travamento estava ocorrendo. Logs vago como "Carregando..." não ajudam.

**Solução:** Logs estruturados em CADA ponto crítico:
```
[Agenda] render() iniciado
[Agenda] render: Thread #1 iniciando _load_data_thread
[Agenda] _load_data_thread iniciada
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
[Agenda] _render_after_load iniciada
[Agenda] ✅ renderização concluída em 0.15s
```

---

### 5. **Flag _loading não era garantida ser False em todas as exceções**
**Problema:**
```python
finally:
    self._loading = False  # Pode não executar em certos casos
```

Em algumas situações (exceções aninhadas, threads daemons), o finally pode não executar ou `_loading` pode já estar False, deixando a interface travada.

**Solução:** 
- Dupla proteção em `_render_after_load()` (reseta ANTES de renderizar)
- Proteção em `_render_error()` (reseta imediatamente)
- Logs no finally para confirmar reset
- Verificação se já está False antes de resetar

---

## ✅ CORREÇÕES IMPLEMENTADAS

### 1. Imports adicionado
```python
import time  # Para monitoramento de timeout
```

### 2. Variáveis de rastreamento adicionadas em `__init__`
```python
self._trace_enabled = False          # Previne loop de trace_add
self._thread_count = 0              # ID de cada thread
self._render_start_time = None      # Para timeout
```

### 3. `aplicar_filtros()` protegido
```python
def aplicar_filtros(self, *_):
    if not self._trace_enabled:
        return  # Ignora durante init
    # ... resto do código
```

### 4. `refresh_data()` com logs
```python
def refresh_data(self):
    if self._loading:
        print(f"[Agenda] refresh_data: já em carregamento, ignorando")
        return
    print(f"[Agenda] refresh_data iniciado")
    # ... código
```

### 5. `render()` com timeout
```python
def render(self):
    print(f"[Agenda] render() iniciado")
    # ... código
    self.after(35000, lambda: self._reset_loading_if_stuck(thread_id))
```

### 6. `_load_data_thread()` completamente reescrito
- ✅ 4 blocos de log separados (um para cada chamada do controller)
- ✅ Monitoramento de tempo individual (alerta se > 10s)
- ✅ Verificação de exceções completas
- ✅ Traceback completo em caso de erro
- ✅ Finally block com dupla proteção

### 7. `_reset_loading_if_stuck()` implementado
```python
def _reset_loading_if_stuck(self, thread_id=None):
    elapsed = time.time() - (self._render_start_time or time.time())
    if self._loading and elapsed > 30:
        print(f"[Agenda] ⚠️ TIMEOUT: Carregamento preso...")
        self._loading = False
        self._render_error(f"Timeout: Carregamento demorou >{elapsed:.0f}s")
```

### 8. `_render_error()` melhorado
- ✅ Logs de erro
- ✅ Card com border vermelha
- ✅ Mensagem amigável em `wraplength=300`
- ✅ Botão "Tentar Novamente"
- ✅ Reset garantido de `_loading = False`

### 9. `_render_after_load()` protegido
- ✅ Reset de `_loading` ANTES de renderizar
- ✅ Logs de sucesso
- ✅ Tempo total de renderização
- ✅ Try/except abrangente

---

## 🔍 COMO DIAGNOSTICAR SE FUNCIONA

Abra o terminal e observe os logs quando entrar na aba Agenda:

### ✅ Funcionando corretamente:
```
[Agenda] __init__ concluído. Iniciando render()
[Agenda] render() iniciado
[Agenda] render: Thread #1 iniciando _load_data_thread
[Agenda] render thread #1 iniciada
[Agenda] _load_data_thread iniciada
[Agenda] → Chamando listar_por_clinica...
[Agenda] ✓ listar_por_clinica OK (0.45s) - 7 consultas
[Agenda] → Chamando contar_por_clinica...
[Agenda] ✓ contar_por_clinica OK (0.12s) - total=42
[Agenda] → Chamando listar_opcoes_filtro...
[Agenda] ✓ listar_opcoes_filtro OK (0.08s)
[Agenda] → Chamando snapshot_por_clinica...
[Agenda] ✓ snapshot_por_clinica OK (0.05s)
[Agenda] ✅ Todos os dados carregados em 0.70s
[Agenda] _render_after_load iniciada
[Agenda] ✅ renderização concluída em 0.15s
```

### ❌ Problema no banco de dados:
```
[Agenda] → Chamando listar_por_clinica...
[Agenda] ⚠️ listar_por_clinica demorou 15.32s (>10s)
[Agenda] ❌ Erro na carga de dados: Conexão ao BD perdida
[Agenda] _render_error: Erro na carga de dados: Conexão ao BD perdida
```

### ⏱️ Timeout:
```
[Agenda] ⚠️ TIMEOUT: Carregamento preso por 31.5s (thread_id=2). Resetando...
```

---

## 📊 Resumo das Correções

| # | Problema | Solução | Linha |
|---|----------|---------|-------|
| 1 | Loop trace_add | Flag `_trace_enabled` | 61 |
| 2 | Sem timeout | Monitoramento + `after(35s)` | 245-290 |
| 3 | Threads concorrentes | `_thread_count` com ID | 60 |
| 4 | Sem logs | Logs detalhados em cada etapa | 245-290 |
| 5 | _loading não reset | Dupla proteção + Finally | 315-340 |
| 6 | Erro confuso | Card vermelho com mensagem clara | 300+ |

---

## 🚀 Próximos Passos

1. **Testar:** Abra a aba Agenda e observe os logs do terminal
2. **Se funcionar:** Todas as consultas devem aparecer em < 2 segundos
3. **Se falhar:** Analise qual log aparece último para identificar o gargalo

Se o problema persistir, capture os logs do terminal até ao ponto onde trava e comunique qual método está demorando > 10s (listar_por_clinica, contar_por_clinica, etc).
