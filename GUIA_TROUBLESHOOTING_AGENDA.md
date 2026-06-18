# 📋 GUIA DE TROUBLESHOOTING - Agenda com Logs Esperados

## Se "Carregando consultas..." AINDA aparecer infinito

Siga este guia para identificar exatamente onde o carregamento trava.

---

## 🔴 PASSO 1: Coletar Logs

### 1.1 - Abrir console/terminal
```bash
# Windows PowerShell
cd "c:\Users\58143406\Documents\Desktop_2\OdontoPro"
python SistemaDesktop/main.py

# Ou no VS Code:
# Ctrl+` para abrir terminal integrado
# cd SistemaDesktop
# python main.py
```

### 1.2 - Reproduzir o problema
1. Aplicação abre
2. Vai para aba "Agenda"
3. Tela mostra "Carregando consultas..."
4. Deixa por 10+ segundos SEM fazer nada
5. Continua mostrando "Carregando consultas..."

### 1.3 - Salvar os logs
```
Copiar TODO o output do console (Ctrl+A, Ctrl+C)
Salvar em arquivo: logs_agenda.txt
```

---

## 📊 PASSO 2: Analisar Logs

### Cenário A: ✅ Funcionando Corretamente

Se ver esta sequência, o sistema está OK:

```
[AGENDA] ========== RENDER INICIADO ==========
[AGENDA] render: ativando _loading
[AGENDA] render: limpando widgets
[AGENDA] render: iniciando thread #1 para carregar dados
[AGENDA] render: agendando timeout de 40s para thread #1

[AGENDA] thread render #1: INICIADA
[AGENDA] _load_data_thread: INICIADA
[AGENDA] _load_data_thread: analisando filtros
[AGENDA]   - data=None
[AGENDA]   - medico=None
[AGENDA]   - status=None
[AGENDA]   - especialidade=None

[AGENDA] → Chamando ConsultaController.listar_por_clinica()
[AGENDA] ✓ listar_por_clinica OK (0.234s) - retornou 15 registros

[AGENDA] → Chamando ConsultaController.contar_por_clinica()
[AGENDA] ✓ contar_por_clinica OK (0.123s) - total=15

[AGENDA] → Chamando ConsultaController.listar_opcoes_filtro()
[AGENDA] ✓ listar_opcoes_filtro OK (0.089s)

[AGENDA] → Chamando ConsultaController.snapshot_por_clinica()
[AGENDA] ✓ snapshot_por_clinica OK (0.045s)

[AGENDA] ✅ TODOS OS DADOS CARREGADOS COM SUCESSO
[AGENDA] → Agendando _render_after_load() no thread principal
[AGENDA] ✓ _render_after_load agendado com sucesso
[AGENDA] thread render #1: TERMINADA

[AGENDA] ========== _RENDER_AFTER_LOAD INICIADA ==========
[AGENDA] _render_after_load: resetando _loading IMEDIATAMENTE
[AGENDA] _render_after_load: destruindo widgets antigos
[AGENDA] _render_after_load: criando frames esquerdo e direito
[AGENDA] _render_after_load: renderizando filtros
[AGENDA] _render_after_load: renderizando info
[AGENDA] _render_after_load: criando tabela
[AGENDA] _render_after_load: renderizando 15 linhas
[AGENDA] _render_after_load: renderizando paginação
[AGENDA] _render_after_load: renderizando painel de detalhes
[AGENDA] ✅ _render_after_load CONCLUÍDA em 0.456s
```

✅ **Resultado**: Tela mostra lista de consultas

---

### Cenário B: ❌ Tranca em listar_por_clinica

Se ver isto:

```
[AGENDA] ========== RENDER INICIADO ==========
[AGENDA] render: ativando _loading
[AGENDA] thread render #1: INICIADA
[AGENDA] _load_data_thread: INICIADA
[AGENDA] → Chamando ConsultaController.listar_por_clinica()
(preso aqui por > 40 segundos)
```

❌ **Diagnóstico**: 
- `listar_por_clinica()` está pendurado
- Pode ser:
  - ✋ MySQL offline
  - 🔒 Query muito lenta (> 10s)
  - 📡 Conexão de rede lenta
  - 🐌 Dados muito grandes

✅ **Solução**:
1. Verificar MySQL: `test_aiven_connection.py`
2. Aumentar timeout para 60s: Mudar `40000` para `60000` em `render()`
3. Chamar DBA se query > 30s em produção

---

### Cenário C: ❌ Timeout Disparado

Se ver isto:

```
[AGENDA] → Chamando ConsultaController.listar_por_clinica()
(espera 40 segundos)

[AGENDA] ⏱️  TIMEOUT: carregamento da thread #1 demorou > 40s
[AGENDA] ⏱️  TIMEOUT: ressetando _loading (era thread atual)

[AGENDA] _render_error: ⏱️ Timeout: O carregamento demorou muito. Tente novamente...
```

❌ **Diagnóstico**: 
- Timeout de 40s foi atingido
- Uma ou mais queries MySQL demoraram muito

✅ **Resultado**: 
- Tela mostra "❌ Falha ao carregar Agenda" com mensagem de timeout
- Botão "↻ Tentar Novamente" aparece

✅ **Solução**:
- Clicar "Tentar Novamente"
- Se continuar, aumentar timeout ou otimizar queries

---

### Cenário D: ❌ Erro de Conexão

Se ver isto:

```
[AGENDA] → Chamando ConsultaController.listar_por_clinica()
[AGENDA] ❌ listar_por_clinica FALHOU (0.234s): ConnectionError: Lost connection to MySQL server

Traceback (most recent call last):
  File "c:\Users\...\SistemaDesktop\views\agenda.py", line 304, in _load_data_thread
    consultas = ConsultaController.listar_por_clinica(...)
  File "c:\Users\...\SistemaDesktop\controllers\consulta_controller.py", line 123, in listar_por_clinica
    cursor.execute(query)
  File "c:\...\mysql\connector\abstracts\cursor.py", line 267, in execute
    self._handle_errors()
  ...
ConnectionError: Lost connection to MySQL server during query

[AGENDA] ❌ ERRO FATAL em _load_data_thread: ConnectionError: Lost connection...
```

❌ **Diagnóstico**: 
- MySQL desconectou
- Pool de conexões pode estar exaurido
- Rede caiu

✅ **Resultado**: 
- Tela mostra "❌ Falha ao carregar Agenda: Lost connection to MySQL server"
- Botão "↻ Tentar Novamente" aparece

✅ **Solução**:
1. Executar `test_aiven_connection.py` para verificar conectividade
2. Reiniciar aplicação
3. Verificar status de MySQL

---

### Cenário E: ❌ Nenhum Log Aparece

Se você abrir a aplicação e não ver NENHUM log `[AGENDA]`:

❌ **Diagnóstico**: 
- Aba "Agenda" não foi clicada
- Ou `render()` não foi chamado

✅ **Solução**:
1. Clicar explicitamente na aba "Agenda"
2. Clicar botão de atualizar (refresh)
3. Se ainda nada, problema está em outra parte (views não está sendo renderizada)

---

### Cenário F: ❌ Erro ao Renderizar

Se ver isto:

```
[AGENDA] ========== _RENDER_AFTER_LOAD INICIADA ==========
[AGENDA] _render_after_load: resetando _loading IMEDIATAMENTE
[AGENDA] _render_after_load: destruindo widgets antigos
[AGENDA] ❌ _render_after_load ERROR: invalid literal for int() with base 10: 'abc'

Traceback (most recent call last):
  File "c:\Users\...\views\agenda.py", line 460, in _render_after_load
    self._render_filtros(...)
  File "c:\Users\...\views\agenda.py", line 620, in _render_filtros
    value = int(data_row[0])
ValueError: invalid literal for int() with base 10: 'abc'
```

❌ **Diagnóstico**: 
- Dados retornados por ConsultaController estão com formato errado
- `listar_opcoes_filtro()` retornou dados inválidos

✅ **Resultado**: 
- Tela mostra "❌ Falha ao carregar Agenda: invalid literal for int()..."
- Botão "↻ Tentar Novamente" aparece

✅ **Solução**:
1. Verificar dados em banco de dados
2. Rodar `gerar_relatorio_bd.py` para verificar integridade
3. Restaurar backup se necessário

---

## 🔧 PASSO 3: Se Após 40 Segundos AINDA Mostrar "Carregando..."

Se o timeout NÃO disparar:

### Verificação A: Verificar se `_timeout_loading()` é chamado

```python
# Em agenda.py, linhas 231-238, verificar se função existe:

def _timeout_loading(self, thread_id):
    """Força reset se carregamento demorar muito"""
    print(f"\n[AGENDA] ⏱️  TIMEOUT: carregamento da thread #{thread_id} demorou > 40s")
    
    if self._current_thread_id == thread_id:
        print(f"[AGENDA] ⏱️  TIMEOUT: ressetando _loading (era thread atual)")
        self._loading = False
        self._render_error("...")
```

✅ Se função existe: OK
❌ Se função não existe: Executar novamente os `replace_string_in_file` commands

### Verificação B: Timeout foi agendado?

Procurar por log:
```
[AGENDA] render: agendando timeout de 40s para thread #1
```

✅ Se aparecer: Timeout foi agendado
❌ Se não aparecer: Problema em `render()`, linha ~267

### Verificação C: Verificar `self._timeout_id`

Adicionar debug em `render()`:
```python
print(f"[AGENDA] render: self._timeout_id ANTES = {self._timeout_id}")
if self._timeout_id is not None:
    try:
        self.after_cancel(self._timeout_id)
        print(f"[AGENDA] render: timeout anterior cancelado")
    except:
        pass
print(f"[AGENDA] render: self._timeout_id DEPOIS de cancelar = {self._timeout_id}")

self._timeout_id = self.after(40000, lambda: self._timeout_loading(thread_id))
print(f"[AGENDA] render: self._timeout_id NOVO = {self._timeout_id}")
```

Se `self._timeout_id` sempre é None: OK (comportamento esperado)
Se `self._timeout_id` é sempre o mesmo: PROBLEMA (timeout não está sendo cancelado)

---

## 🧠 PASSO 4: Análise Manual de Problema

Se todos os logs aparecem MAS a tela não renderiza:

### 4.1 - Verificar se `_render_after_load()` É chamado

Procurar por:
```
[AGENDA] ========== _RENDER_AFTER_LOAD INICIADA ==========
```

✅ Se aparecer: Renderização foi iniciada
❌ Se não aparecer: Problema entre `_load_data_thread()` e chamada de `_render_after_load()`

### 4.2 - Se `_render_after_load()` É chamado, ver onde trava

```
[AGENDA] _render_after_load: resetando _loading IMEDIATAMENTE      ← OK até aqui?
[AGENDA] _render_after_load: destruindo widgets antigos              ← OK até aqui?
[AGENDA] _render_after_load: criando frames esquerdo e direito       ← OK até aqui?
[AGENDA] _render_after_load: renderizando filtros                    ← OK até aqui?
[AGENDA] _render_after_load: renderizando info                       ← OK até aqui?
```

Se um dos logs não aparecer, é ali que trava.

Por exemplo, se só aparecer até "renderizando filtros", o problema está em `_render_info_top()`.

### 4.3 - Se `_render_after_load()` completa mas tela não muda

Verificar:
```
[AGENDA] ✅ _render_after_load CONCLUÍDA em 0.456s
```

Se este log aparece:
- ✅ Tudo funcionou
- ✅ `_loading` foi setado para False
- Problema está em outra aba ou refresh visual

Tentar:
1. Clicar em outra aba
2. Clicar de volta em Agenda
3. Se tela aparecer: OK (foi cache do display)

---

## 📞 Se Nenhum dos Cenários Acima Resolver

Coletar:

1. **Arquivo `logs_agenda.txt`** - Todos os logs do console
2. **Verificar `test_aiven_connection.py`**:
   ```bash
   cd "c:\Users\58143406\Documents\Desktop_2\OdontoPro"
   python test_aiven_connection.py
   ```
3. **Rodar diagnóstico de banco de dados**:
   ```bash
   python gerar_relatorio_bd.py
   ```
4. **Verificar se `agenda.py` foi salvo corretamente**:
   ```bash
   python -m py_compile SistemaDesktop/views/agenda.py
   ```
5. **Compartilhar**:
   - logs_agenda.txt (os primeiros 100 linhas, OK para compartilhar)
   - Resultado de `test_aiven_connection.py`
   - Se há erro no console do Python (traceback de ImportError, etc)

---

## 📝 Checklist Rápido

- [ ] Sintaxe do `agenda.py` OK? `py_compile` rodou sem erros?
- [ ] Aba "Agenda" foi clicada?
- [ ] Logs `[AGENDA]` aparecem no console?
- [ ] MySQL está online? `test_aiven_connection.py` passou?
- [ ] Timeout apareceu após 40 segundos?
- [ ] `_render_error()` foi chamado com mensagem clara?
- [ ] Botão "↻ Tentar Novamente" aparece?
- [ ] Segundo attempt funciona?

Se TUDO passar: ✅ Sistema funcionando
Se algum FALHAR: 🔧 Use logs acima para diagnosticar

---

## 🎯 Resumo

| Sintoma | Diagnóstico | Solução |
|---------|-------------|---------|
| "Carregando..." infinito | Ver logs de qual método trava | Verificar MySQL / aumentar timeout |
| Timeout após 40s | Esperado se query > 40s | Otimizar query ou aumentar timeout |
| "❌ Falha ao carregar" | Erro em ConsultaController | Ver error message no card |
| Nenhum log aparece | `render()` não foi chamado | Clicar em aba "Agenda" |
| Carrega mas tela não muda | Cache de display | Clicar em outra aba e voltar |

---
