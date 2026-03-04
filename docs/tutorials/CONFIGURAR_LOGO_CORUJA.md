# Configurar Logo da Coruja nas Notificações

## Opção 1: Usar Imgur (Recomendado - Mais Fácil)

### Passo 1: Upload no Imgur
1. Acesse https://imgur.com/upload
2. Faça upload da imagem da coruja
3. Após o upload, clique com botão direito na imagem
4. Selecione "Copiar endereço da imagem"
5. A URL será algo como: `https://i.imgur.com/ABC123.png`

### Passo 2: Atualizar o Código
1. Abra o arquivo `api/routers/notifications.py`
2. Procure por: `"activityImage": "https://i.imgur.com/YourImageID.png"`
3. Substitua pela URL que você copiou do Imgur
4. Salve o arquivo
5. Reinicie a API: `docker restart coruja-api`

---

## Opção 2: Hospedar Localmente

### Passo 1: Salvar a Imagem
1. Salve a imagem da coruja como `coruja-logo.png`
2. Coloque em: `frontend/public/assets/coruja-logo.png`

### Passo 2: Atualizar o Código
1. Abra o arquivo `api/routers/notifications.py`
2. Procure por: `"activityImage": "https://i.imgur.com/YourImageID.png"`
3. Substitua por: `"activityImage": "http://192.168.30.189:3000/assets/coruja-logo.png"`
4. Salve o arquivo
5. Reinicie a API: `docker restart coruja-api`

**Nota:** O Teams precisa conseguir acessar a URL da imagem. Se usar localhost, só funcionará na sua máquina.

---

## Opção 3: Usar Base64 (Não Recomendado)

O Teams não suporta imagens em Base64 diretamente nos Adaptive Cards.

---

## Recomendação

Use o **Imgur** (Opção 1) porque:
- ✅ Gratuito
- ✅ Rápido
- ✅ Funciona de qualquer lugar
- ✅ Não precisa configurar servidor
- ✅ URL pública e permanente

---

## Testando

Após configurar:
1. Vá em Configurações → Notificações → Microsoft Teams
2. Clique em "Testar Mensagem"
3. Verifique no Teams se a imagem da coruja aparece

---

## Sua Imagem

A imagem que você enviou é perfeita! Ela tem:
- ✅ Fundo escuro/transparente
- ✅ Logo moderno e profissional
- ✅ Cores azul/ciano que combinam com o tema
- ✅ Tamanho adequado

---

## Próximos Passos

1. Faça upload no Imgur
2. Copie a URL
3. Atualize o código
4. Reinicie a API
5. Teste no Teams

A imagem vai aparecer ao lado de cada notificação, deixando muito mais profissional! 🦉
