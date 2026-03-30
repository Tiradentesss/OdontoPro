# 🔒 Configuração de SECRET_KEY no Railway

## Problema
A tela de configuração não está salvando dados e redireciona para login porque o `SECRET_KEY` do Django está mudando a cada deploy no Railway.

### Por quê isso acontece?
1. Ao fazer login, um cookie `uid_signed` é criado e assinado com a `SECRET_KEY`
2. Ao fazer uma requisição POST (como "Salvar alterações"), um worker diferente processa a requisição
3. Se a `SECRET_KEY` for aleatória (como era), o novo worker gera uma chave **diferente**
4. Quando tenta validar o cookie `uid_signed`, falha porque foi assinado com uma chave diferente
5. Usuário é redirecionado para login ❌

## Solução

### Passo 1: Gerar uma SECRET_KEY segura para produção

No seu terminal local, execute:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Você receberá uma string como:
```
abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

### Passo 2: Adicionar a SECRET_KEY no Railway

1. Acesse seu projeto no Railway: https://railway.app
2. Vá para a aba **Variables** (Variáveis)
3. Clique em **Add Variable**
4. **Name**: `SECRET_KEY`
5. **Value**: Cole a string gerada no Passo 1
6. Salve

### Passo 3: Deploy
Faça um novo deploy. Desta vez:
- O `SECRET_KEY` será **fixo** em todos os workers
- Os cookies `uid_signed` serão validados corretamente
- Salvar alterações funcionará! ✅

## Verificação

Nos logs do Railway, você deve ver agora:
```
✓ Login success paciente...
✓ Configurações salvas para paciente...
✓ Sessão restaurada via uid_signed para paciente...
```

Se ainda vir `BadSignature error`, significa que a `SECRET_KEY` ainda está mudando. Verifique se você adicionou corretamente nas variáveis de ambiente.

## Código Implementado

- **`setup/settings.py`**: Agora usa `SECRET_KEY` de variáveis de ambiente, com fallback seguro
- **`odontoPro/middleware.py`**: Restaura automaticamente a sessão via cookie `uid_signed`
- **Logs melhorados**: Avisos claros se houver problema com `SECRET_KEY`
