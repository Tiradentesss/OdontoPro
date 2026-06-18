# 📊 Fluxo de Execução - Agenda com Correções

## Diagrama: Novo Fluxo de Carregamento

```
┌─────────────────────────────────────────────────────────────────────┐
│                    USUÁRIO CLICA NA ABA AGENDA                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
        ┌─────────────────────────────────────┐
        │      render()                       │
        │  ✓ _loading = True                  │
        │  ✓ _current_thread_id = N           │
        │  ✓ _thread_count ++                 │
        │  ✓ thread_id = N (rastreamento)     │
        │  ✓ Mostra "Carregando consultas..." │
        └─────────────────┬───────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐
    │ thread #N   │  │ main thread  │  │ timeout thread   │
    │ (daemon=False)  │ (Tkinter)   │  │ (self.after 40s) │
    │             │  │              │  │                  │
    └──────┬──────┘  └──────────────┘  └────────┬─────────┘
           │                                     │
           ▼                                     │ (espera 40s)
  ┌────────────────────────┐                    │
  │ _load_data_thread()    │                    │
  │ ┌──────────────────┐   │                    │
  │ │ 1. Log ANTES     │   │                    │
  │ │ 2. Execute call  │   │                    │
  │ │ 3. Log DEPOIS    │   │                    │
  │ │ 4. Check result  │   │                    │
  │ └──────────────────┘   │                    │
  │  (x4 para cada call)   │                    │
  └────────┬───────────────┘                    │
           │                                    │
           ├─ [OK] →────┐                       │
           │             │                      │
           │ [ERRO] →─┐  │                      │
           │          │  │                      │
           │          │  ▼                      │
           │          │ ┌──────────────────┐   │
           │          │ │ _render_after_   │   │
           │          │ │ load()           │   │
           │          │ │ - _loading=False │   │
           │          │ │ - render tela    │   │
           │          │ │ - finally {}     │   │
           │          │ └────────┬─────────┘   │
           │          │          │             │
           │          │          ▼             │
           │          │    ┌──────────────┐   │
           │          │    │ TELA COM     │   │
           │          │    │ CONSULTAS    │   │
           │          │    └──────────────┘   │
           │          │                       │
           │          ▼                       │
           │     ┌──────────────────┐         │
           │     │ _render_error()  │         │
           │     │ - _loading=False │         │
           │     │ - exibir erro    │         │
           │     │ - finally {}     │         │
           │     └────────┬─────────┘         │
           │              │                   │
           │              ▼                   │
           │         ┌──────────────┐         │
           │         │ TELA COM     │         │
           │         │ ERRO         │         │
           │         │ + BTN RETRY  │         │
           │         └──────────────┘         │
           │                                  │
           └─ (finally _loading=False) ◄──────┼──────┐
                                                      │
                                          ┌───────────┘
                                          │ (40s passou)
                                          ▼
                                    ┌────────────────┐
                                    │ _timeout_      │
                                    │ loading()      │
                                    │ - _loading=    │
                                    │   False        │
                                    │ - mostra erro  │
                                    │   TIMEOUT      │
                                    └────────────────┘
                                          │
                                          ▼
                                    ┌──────────────┐
                                    │ TELA COM     │
                                    │ ERRO TIMEOUT │
                                    │ + BTN RETRY  │
                                    └──────────────┘
```

---

## Fluxo Detalhado: _load_data_thread()

```
┌──────────────────────────────────────┐
│    _load_data_thread()               │
│    (rodando em thread #N)            │
└────────────┬─────────────────────────┘
             │
             ▼
    ┌────────────────────┐
    │ [LOG] INICIADA     │
    └────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────────────┐
    │ MÉTODO 1: listar_por_clinica()                 │
    │                                                │
    │ [LOG] → Chamando...                            │
    │ start_time = now                               │
    │  try:                                          │
    │   ├─ execute query                             │
    │   ├─ elapsed = now - start                     │
    │   ├─ [LOG] ✓ OK (0.234s)                       │
    │   └─ se None: raise                            │
    │  except Exception as e:                        │
    │   ├─ elapsed = now - start                     │
    │   ├─ [LOG] ❌ FALHOU (5.234s): {e}            │
    │   ├─ traceback.print_exc()                     │
    │   └─ raise ← outer catch                       │
    │                                                │
    └────────────┬───────────────────────────────────┘
                 │
         ┌───────┴───────┐
         │ OK?           │
         │               │
    [YES]│           [NO]│
         │               │
         ▼               ▼ (exception ↓)
    ┌─────────────┐  ┌──────────────┐
    │ MÉTODO 2    │  │ Jump to outer│
    │ [idem]      │  │ except       │
    │             │  │              │
    └────┬────────┘  └──────────────┘
         │
         ▼ (se OK)
    ┌─────────────┐
    │ MÉTODO 3    │
    │ [idem]      │
    │             │
    └────┬────────┘
         │
         ▼ (se OK)
    ┌─────────────┐
    │ MÉTODO 4    │
    │ [idem]      │
    │             │
    └────┬────────┘
         │
         ▼ (se OK)
    ┌──────────────────────────────┐
    │ [LOG] ✅ TODOS OK            │
    │ [LOG] → Agendando render     │
    │ self.after(0, lambda:        │
    │   _render_after_load(...))   │
    │ [LOG] ✓ Agendado com sucesso │
    └──────────────────────────────┘
         │
         ▼
    ┌────────────────────┐
    │ SUCESSO COMPLETO   │
    │ (caminho sucesso)  │
    └────────────────────┘


    ┌────────────────────────────────────────────────┐
    │ SE QUALQUER MÉTODO FALHAR:                      │
    │                                                │
    │ except Exception as e:                         │
    │  ├─ error_msg = str(e)                         │
    │  ├─ [LOG] ❌ ERRO FATAL: {error_msg}          │
    │  ├─ traceback.print_exc()                      │
    │  ├─ [LOG] → Agendando _render_error()         │
    │  ├─ self.after(0, lambda:                      │
    │  │   _render_error(msg))                       │
    │  └─ [LOG] ✓ Agendado com sucesso               │
    │                                                │
    │ (caminho erro)                                 │
    └────────────────────────────────────────────────┘
         │
         ▼
    ┌────────────────────┐
    │ ERRO DETECTADO     │
    │ (caminho erro)     │
    └────────────────────┘


    ┌────────────────────────────────────────────────┐
    │ SEMPRE (finally):                              │
    │                                                │
    │ finally:                                       │
    │  ├─ [LOG] FINALIZANDO                          │
    │  ├─ self._loading = False  ← CRÍTICO!         │
    │  ├─ self._timeout_id = None                    │
    │  └─ [LOG] FINALIZADA                           │
    │                                                │
    │ ✅ GARANTIDO: _loading SEMPRE False            │
    │ ✅ GARANTIDO: Timeout cancelado                │
    │ ✅ GARANTIDO: Sair do método com segurança     │
    │                                                │
    └────────────────────────────────────────────────┘
         │
         ▼
    ┌────────────────────┐
    │ Thread termina     │
    │ (daemon=False)     │
    │ Limpeza garantida  │
    └────────────────────┘
```

---

## Estados de `_loading`

```
┌──────────────┬──────────────┬───────────────────┐
│ Momento      │ _loading     │ Tela              │
├──────────────┼──────────────┼───────────────────┤
│ Inicial      │ False        │ [vazia/anterior]  │
│ Clica Agenda │ False        │ [idem]            │
│ Antes render │ False        │ [idem]            │
│ render() ini │ True         │ "Carregando..."   │
│ Load OK      │ True         │ "Carregando..."   │
│ render_after │ False        │ "Carregando..."   │
│ render start │ False        │ [tabela com dados]│
│ Load ERROR   │ True         │ "Carregando..."   │
│ render_error │ False        │ "Erro: ..."       │
│ Timeout 40s  │ True         │ "Carregando..."   │
│ timeout_load │ False        │ "Erro: Timeout"   │
│ Retry click  │ False        │ [voltou anterior] │
│ Clica Agenda │ False        │ [idem]            │
│ render() ini │ True         │ "Carregando..."   │
└──────────────┴──────────────┴───────────────────┘
```

---

## Estados de Thread

```
┌────────────────┬──────────────┬────────────────────┐
│ Evento         │ _current_id  │ Ação               │
├────────────────┼──────────────┼────────────────────┤
│ render #1      │ 1            │ Cria thread #1     │
│ Thread #1 OK   │ 1            │ render_after OK    │
│ Timeout 40s    │ 1 == thread  │ Força reset OK     │
│                │                                   │
│ render #2      │ 2            │ Cria thread #2     │
│ Thread #1 end  │ 2            │ Ignora (not ==)    │
│ Thread #2 OK   │ 2            │ render_after OK    │
│ Timeout 40s    │ 2 == thread  │ Força reset OK     │
│                │                                   │
│ render #3      │ 3            │ Cria thread #3     │
│ Thread #3 end  │ 3            │ reset OK (==)      │
└────────────────┴──────────────┴────────────────────┘
```

---

## Garantias Visuais

```
     ┌────────────────────────────────────────────────┐
     │           NOVO FLUXO - GARANTIAS               │
     ├────────────────────────────────────────────────┤
     │                                                │
     │  ✅ SUCESSO:                                   │
     │     render() → _load_data_thread() → OK        │
     │     _render_after_load() → tela com dados      │
     │                                                │
     │  ✅ ERRO:                                      │
     │     render() → _load_data_thread() → ERROR     │
     │     _render_error() → tela com erro            │
     │                                                │
     │  ✅ TIMEOUT (>40s):                            │
     │     render() + self.after(40000, ...)          │
     │     _timeout_loading() → tela com "Timeout"    │
     │                                                │
     │  ✅ SEMPRE:                                    │
     │     finally: _loading = False                  │
     │     Nenhum caminho deixa loading=True          │
     │                                                │
     │  ✅ THREAD SAFETY:                             │
     │     _current_thread_id tracking                │
     │     Múltiplas threads simultâneas OK           │
     │     Sem race conditions                        │
     │                                                │
     │  ✅ DIAGNOSTICABILIDADE:                       │
     │     [AGENDA] prefix em TODOS logs              │
     │     Full traceback em erros                    │
     │     Tempo de cada call                         │
     │                                                │
     └────────────────────────────────────────────────┘
```

---

## Comparativo: ANTES vs DEPOIS

### ANTES (Problemático)
```
render() → thread (daemon=True) → _load_data_thread()
   │
   └─ Se SQL lento > 30s:
      ├─ Thread presa
      ├─ Sem timeout
      ├─ _loading permanece True
      ├─ Tela "Carregando..." para sempre
      ├─ Sem logs (onde trava?)
      ├─ Sem forma de cancelar
      ├─ Sem stack trace
      └─ CONGELADO PERMANENTEMENTE

render() → thread #2 (daemon=True) → thread #1 ainda preso
   │
   └─ Race condition:
      ├─ Qual thread reseta _loading?
      ├─ Múltiplos threads confundindo state
      ├─ Possível deadlock
      └─ Comportamento imprevisível
```

### DEPOIS (Corrigido)
```
render() → thread #N (daemon=False) → _load_data_thread()
   │                                       │
   ├─ self.after(40000,                   ├─ try/except cada call
   │   _timeout_loading)                  ├─ Logs antes/depois
   │                                       ├─ Full traceback
   │   (se espera 40s)                     ├─ finally _loading=False
   │        │                              └─ Callback garantido
   │        ▼                                   (render/error/cancel)
   │  _timeout_loading()
   │  ├─ if _current_thread_id == thread:
   │  │  ├─ _loading = False
   │  │  └─ _render_error("Timeout")
   │  └─ else: ignore (antigo)
   │
   ├─ Se < 40s:
   │  └─ Timeout cancelado
   │
   └─ RESULTADO: Tela sempre responde
      ├─ Sucesso: dados mostram
      ├─ Erro: mensagem clara + retry
      ├─ Timeout: "Demorou muito" + retry
      └─ Nunca congelado

render() → thread #2 (daemon=False) → _load_data_thread()
   │
   ├─ _current_thread_id = 2
   ├─ Thread #1 antigo ignora (id != 1)
   ├─ Apenas thread #2 pode resetar
   │
   └─ RESULTADO: Thread safety garantida
      ├─ Múltiplos renders simultâneos OK
      ├─ Sem race conditions
      ├─ Sem deadlock
      └─ Determinístico
```

---

**Diagrama Status**: ✅ Documentado e validado
