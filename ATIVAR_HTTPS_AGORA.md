# 🔒 Ativar HTTPS AGORA - Guia Rápido

## ⚠️ Situação Atual

Seu sistema está rodando apenas em **HTTP** (porta 3000 e 8000).  
Para usar **HTTPS**, você precisa executar o script de configuração.

---

## 🚀 SOLUÇÃO RÁPIDA (5 minutos)

### Opção 1: HTTPS Local (Desenvolvimento)

**Melhor para**: Testes locais, desenvolvimento

**Passo 1**: Executar script
```powershell
.\setup-https.ps1 -SelfSigned
```

**Passo 2**: Aguardar configuração (1-2 minutos)

**Passo 3**: Acessar
```
https://localhost
```

**Passo 4**: Aceitar certificado
- Navegador mostrará: "Sua conexão não é particular"
- Clicar em "Avançado"
- Clicar em "Continuar para localhost (não seguro)"
- Pronto! Sistema funcionando em HTTPS

**Observação**: O aviso é normal para certificados auto-assinados em desenvolvimento.

---

## ❓ Por Que Não Está Funcionando Agora?

O sistema atual está configurado para HTTP:
- Frontend: http://localhost:3000
- API: http://localhost:8000

Para HTTPS funcionar, você precisa:
1. Gerar certificado SSL
2. Configurar Nginx
3. Redirecionar tráfego

O script `setup-https.ps1` faz tudo isso automaticamente!

---

## 🔧 Troubleshooting

### Erro: "Docker não está rodando"

**Solução**:
```powershell
# Iniciar Docker Desktop
# Aguardar inicialização completa
# Executar novamente
.\setup-https.ps1 -SelfSigned
```

### Erro: "Porta 443 já em uso"

**Solução**:
```powershell
# Parar containers atuais
docker-compose down

# Executar setup
.\setup-https.ps1 -SelfSigned
```

### Página não carrega em HTTPS

**Solução**:
```powershell
# Verificar se Nginx está rodando
docker ps | findstr nginx

# Ver logs
docker logs coruja-nginx

# Reiniciar se necessário
docker-compose -f docker-compose.yml -f docker-compose.https.yml restart nginx
```

---

## 📊 Verificar Status

Após executar o setup:

```powershell
# Ver containers rodando
docker-compose -f docker-compose.yml -f docker-compose.https.yml ps

# Deve mostrar:
# - coruja-nginx (porta 80 e 443)
# - coruja-certbot
# - coruja-frontend
# - coruja-api
# - coruja-postgres
# - coruja-redis
```

---

## 🎯 Resumo

**Situação Atual**: HTTP apenas  
**Solução**: Executar `.\setup-https.ps1 -SelfSigned`  
**Tempo**: 2-3 minutos  
**Resultado**: HTTPS funcionando em https://localhost  

---

## 💡 Próximos Passos (Opcional)

Depois que HTTPS local estiver funcionando, você pode:

1. **Usar em produção com domínio real**:
```powershell
.\setup-https.ps1 -Domain "monitor.seudominio.com" -Email "seu@email.com" -Production
```

2. **Usar DuckDNS (DNS gratuito)**:
- Criar conta em https://www.duckdns.org
- Criar subdomínio
- Executar setup com seu domínio DuckDNS

---

**Execute agora**: `.\setup-https.ps1 -SelfSigned`

🔒 **HTTPS em 2 minutos!**
