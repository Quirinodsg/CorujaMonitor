# Solução Rápida - Coruja Monitor

## Problema Atual
O frontend está com cache e o token não está sendo enviado corretamente.

## Solução Imediata

### 1. Limpar LocalStorage

Abra o Console do navegador (F12) e execute:

```javascript
localStorage.clear()
location.reload()
```

### 2. Testar com diagnose.html

Abra o arquivo `diagnose.html` no navegador e:
1. Clique em "Testar Health" - deve mostrar `{"status":"healthy"}`
2. Clique em "Login" - deve mostrar o token
3. Clique em "Testar Dashboard" - deve mostrar os dados

Se o diagnose.html funcionar, o problema é apenas cache do React.

### 3. Forçar Rebuild Completo

```cmd
docker compose down -v
docker system prune -af
docker compose build --no-cache
docker compose up -d
```

Aguarde 30 segundos e crie o usuário:

```cmd
docker exec -it coruja-api pip install bcrypt==4.0.1
docker exec -it coruja-api python init_admin.py
```

### 4. Acessar em Modo Anônimo

- Chrome: Ctrl+Shift+N
- Firefox: Ctrl+Shift+P
- Edge: Ctrl+Shift+N

Acesse: http://localhost:3000

Login:
- Email: admin@coruja.com
- Senha: admin123

## Se Ainda Não Funcionar

O problema pode ser que o token JWT está sendo gerado mas não está sendo validado corretamente.

Teste manualmente:

1. Faça login via diagnose.html
2. Copie o token que aparece
3. No Console, teste:

```javascript
fetch('http://localhost:8000/api/v1/dashboard/overview', {
  headers: { 'Authorization': 'Bearer SEU_TOKEN_AQUI' }
}).then(r => r.json()).then(console.log)
```

Se retornar 401, o problema é na API (validação do JWT).
Se retornar os dados, o problema é no frontend (não está enviando o token).

## Verificar Logs da API

```cmd
docker logs coruja-api --tail 50
```

Procure por erros de JWT ou autenticação.

## Última Opção: Desabilitar Autenticação Temporariamente

Se nada funcionar, podemos temporariamente desabilitar a autenticação apenas para testar se o resto funciona.

Me avise qual dos testes acima funcionou ou não funcionou!
