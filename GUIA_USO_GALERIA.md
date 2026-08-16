# 📖 GUIA DE USO - GALERIA DA CLÍNICA

## 🚀 Como Usar

### 1. Abrir Configurações da Clínica

1. Acesse: **Configurações > Minha Clínica > Galeria da Clínica**
2. As 3 fotos já salvas (se houver) aparecerão automaticamente nos cards

### 2. Adicionar ou Trocar uma Foto

1. Clique no botão **"+ Adicionar foto"** do card desejado
2. Selecione uma imagem (PNG, JPG, JPEG, GIF) do seu computador
3. O preview será atualizado imediatamente
4. Repita para as outras fotos conforme necessário

### 3. Salvar as Alterações

1. Clique em **"SALVAR ALTERAÇÕES"** no final da tela
2. O sistema fará o upload de cada foto para o Cloudinary
3. Os dados serão salvos no banco de dados
4. Aguarde a mensagem de sucesso

### 4. Verificar Resultado no Site

1. Acesse o site da clínica
2. O carrossel da galeria (dashboard) exibirá as 3 fotos automaticamente
3. As imagens serão carregadas do Cloudinary

---

## ⚙️ Detalhes Técnicos

### Estrutura de Dados

```python
self.clinic_photos = [foto1_url, foto2_url, foto3_url]
```

- Índice 0 → Foto 1 (ordem 1 no banco)
- Índice 1 → Foto 2 (ordem 2 no banco)
- Índice 2 → Foto 3 (ordem 3 no banco)

### Banco de Dados

**Tabela:** `odontoPro_clinicaimagem`

```sql
SELECT id, clinica_id, imagem, ordem
FROM odontoPro_clinicaimagem
WHERE clinica_id = 1
ORDER BY ordem;
```

**Exemplo de Resultado:**
```
ID  | CLINICA_ID | IMAGEM (URL Cloudinary)              | ORDEM
1   | 1          | https://res.cloudinary.com/.../...   | 1
2   | 1          | https://res.cloudinary.com/.../...   | 2
3   | 1          | https://res.cloudinary.com/.../...   | 3
```

### Cloudinary

**Pasta:** `odontopro/clinicas/{clinica_id}/galeria`

**Public ID:** `clinica_{clinica_id}_foto_{ordem}_{timestamp}`

Exemplos:
- `clinica_1_foto_1_1786848109`
- `clinica_1_foto_2_1786848115`
- `clinica_1_foto_3_1786848113`

---

## ❓ Perguntas Comuns

### P: O que acontece se eu trocar apenas a Foto 2?

R: Apenas a Foto 2 será atualizada. As Fotos 1 e 3 permanecerão iguais. O banco continuará com apenas 3 registros (sem duplicatas).

### P: Posso deixar uma posição vazia?

R: Sim. Se você não selecionar uma foto para uma posição, ela será ignorada e nenhum registro será criado/deletado para essa posição.

### P: O que acontece se o upload falhar?

R: O sistema informará qual foto falhou. As outras fotos serão salvas normalmente. Você pode tentar novamente.

### P: As fotos antigas são apagadas?

R: Não. Quando você faz upload de uma nova foto na mesma posição, o registro anterior é atualizado (não apagado). A URL antiga será substituída pela nova.

### P: Quanto tempo leva para aparecer no site?

R: Imediatamente. O site lê diretamente da tabela `odontoPro_clinicaimagem` e exibe as URLs do Cloudinary.

### P: Preciso fazer algo no site?

R: Não. O site já está configurado para ler corretamente da tabela. Apenas preencha a galeria no desktop.

---

## 🔍 Verificar Status

### No Desktop
```python
# Abra as Configurações, e os cards da galeria mostrarão:
# - Foto 1: [preview ou "Sem imagem"]
# - Foto 2: [preview ou "Sem imagem"]
# - Foto 3: [preview ou "Sem imagem"]
```

### No Banco de Dados
```sql
-- Contar fotos cadastradas
SELECT COUNT(*) as total
FROM odontoPro_clinicaimagem
WHERE clinica_id = 1;

-- Ver detalhes
SELECT id, clinica_id, ordem, SUBSTRING(imagem, 1, 100) as url_preview
FROM odontoPro_clinicaimagem
WHERE clinica_id = 1
ORDER BY ordem;
```

### No Cloudinary
1. Acesse: https://cloudinary.com/console/media_library
2. Navegue até: `odontopro > clinicas > {seu_id_clinica} > galeria`
3. Você verá as 3 imagens uploads

---

## 📱 Interface Visual

### Cards da Galeria

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    Foto 1       │  │    Foto 2       │  │    Foto 3       │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│                 │  │                 │  │                 │
│   [Preview ou]  │  │   [Preview ou]  │  │   [Preview ou]  │
│   Sem imagem    │  │   Sem imagem    │  │   Sem imagem    │
│                 │  │                 │  │                 │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│+ Adicionar foto │  │+ Adicionar foto │  │+ Adicionar foto │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## ⚠️ Observações Importantes

1. **Tamanho da Imagem:** Recomenda-se usar imagens menores que 5MB
2. **Formatos Aceitos:** PNG, JPG, JPEG, GIF
3. **Resolução Ideal:** Mínimo 600x400px (16:9)
4. **Banner Principal:** Não confunda com a Galeria. O Banner é uma imagem principal (16:9)
5. **Logo:** A logo da clínica é diferente. Fica no topo do site.

---

## 🆘 Troubleshooting

### As fotos não aparecem no site
1. Verifique se foram salvas no desktop
2. Aguarde 30 segundos e atualize o site (F5)
3. Verifique se o Cloudinary está funcionar

### O preview mostra "Sem imagem"
1. A foto foi deletada do local original no computador?
   - Não importa, o sistema já salvou no Cloudinary
2. Clique em "SALVAR ALTERAÇÕES" novamente

### Erro ao fazer upload
1. Verifique se tem internet conectada
2. Verifique o tamanho da arquivo (máx 5MB)
3. Tente uma imagem diferente

---

**Pronto para usar! 🎉**
