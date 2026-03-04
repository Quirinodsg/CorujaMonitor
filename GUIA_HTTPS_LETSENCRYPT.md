# 🔒 Guia Completo - HTTPS com Let's Encrypt

## ✅ Solução Implementada

**Let's Encrypt** - Certificados SSL/TLS gratuitos e automáticos

### Características

✅ **Gratuito** - 100% grátis, sem custos  
✅ **Automático** - Renovação automática a cada 12 horas  
✅ **Confiável** - Reconhecido por todos os navegadores  
✅ **Válido** - 90 dias (renovado automaticamente aos 60 dias)  
✅ **Fácil** - Configuração em 1 comando  

---

## 🚀 Opções de Uso

### Opção 1: Certificado Auto-Assinado (Desenvolvimento)

**Quando usar**: Desenvolvimento local, testes internos

**Vantagens**:
- ✅ Funciona sem domínio público
- ✅ Funciona com localhost
- ✅ Configuração instantânea
- ✅ Válido por 365 dias

**Desvantagens**:
- ⚠️ Navegador mostra aviso de segurança
- ⚠️ Não é confiável publicamente
- ⚠️ Renovação manual

**Como usar**:
```powershell
.\setup-https.ps1 -SelfSigned
```

---

### Opção 2: Let's Encrypt (Produção)

**Quando usar**: Produção, acesso público

**Vantagens**:
- ✅ Certificado confiável
- ✅ Sem avisos no navegador
- ✅ Renovação AUTOMÁTICA
- ✅ Gratuito para sempre

**Requisitos**:
1. Domínio público (ex: monitor.seudominio.com)
2. Domínio apontando para o IP do servidor
3. Porta 80 acessível externamente

**Como usar**:
```powershell
.\setup-https.ps1 -Domain "monitor.seudominio.com" -Email "seu@email.com" -Production
```

---

## 📋 Passo a Passo Completo

### Para Desenvolvimento Local (Auto-Assinado)

#### 1. Executar Setup

```powershell
.\setup-https.ps1 -SelfSigned
```

#### 2. Acessar Sistema

```
https://localhost
```

#### 3. Aceitar Certificado no Navegador

1. Navegador mostrará: "Sua conexão não é particular"
2. Clicar em "Avançado"
3. Clicar em "Continuar para localhost (não seguro)"
4. Pronto! Sistema funcionando com HTTPS

#### 4. Renovação (após 365 dias)

```powershell
# Executar novamente
.\setup-https.ps1 -SelfSigned
```

---

### Para Produção (Let's Encrypt)

#### 1. Configurar Domínio

**Opção A: Domínio Próprio**
- Comprar domínio (ex: GoDaddy, Registro.br)
- Criar subdomínio: monitor.seudominio.com
- Apontar para IP do servidor

**Opção B: DuckDNS (Gratuito)**
- Acessar: https://www.duckdns.org
- Criar conta gratuita
- Criar subdomínio: corujamonitor.duckdns.org
- Apontar para seu IP público

#### 2. Verificar DNS

```powershell
# Verificar se domínio aponta para seu IP
nslookup monitor.seudominio.com

# Ou
ping monitor.seudominio.com
```

#### 3. Abrir Porta 80

**Windows Firewall**:
```powershell
# Abrir porta 80
New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow

# Abrir porta 443
New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow
```

**Router**:
- Acessar configurações do router
- Configurar Port Forwarding:
  - Porta 80 → IP do servidor
  - Porta 443 → IP do servidor

#### 4. Executar Setup (Teste)

```powershell
# Primeiro teste em staging (não conta no limite)
.\setup-https.ps1 -Domain "monitor.seudominio.com" -Email "seu@email.com"
```

#### 5. Executar Setup (Produção)

```powershell
# Depois em produção
.\setup-https.ps1 -Domain "monitor.seudominio.com" -Email "seu@email.com" -Production
```

#### 6. Acessar Sistema

```
https://monitor.seudominio.com
```

✅ Sem avisos de segurança!  
✅ Cadeado verde no navegador!

#### 7. Renovação Automática

**Não precisa fazer nada!**

O Certbot renova automaticamente:
- Verifica a cada 12 horas
- Renova aos 60 dias (antes de expirar aos 90)
- Reinicia Nginx automaticamente

---

## 🔧 Comandos Úteis

### Verificar Status

```powershell
# Ver containers rodando
docker-compose -f docker-compose.yml -f docker-compose.https.yml ps

# Ver logs do Nginx
docker logs coruja-nginx

# Ver logs do Certbot
docker logs coruja-certbot
```

### Verificar Certificado

```powershell
# Ver detalhes do certificado
openssl s_client -connect localhost:443 -servername localhost

# Ver data de expiração
openssl s_client -connect localhost:443 -servername localhost 2>/dev/null | openssl x509 -noout -dates
```

### Renovar Manualmente

```powershell
# Forçar renovação (Let's Encrypt)
docker-compose -f docker-compose.yml -f docker-compose.https.yml run --rm certbot renew --force-renewal

# Reiniciar Nginx
docker-compose -f docker-compose.yml -f docker-compose.https.yml restart nginx
```

### Parar HTTPS

```powershell
# Voltar para HTTP
docker-compose -f docker-compose.yml -f docker-compose.https.yml down
docker-compose up -d
```

---

## 📊 Arquitetura

```
Internet
   ↓
Porta 80/443
   ↓
Nginx (SSL Termination)
   ↓
┌─────────────┬─────────────┐
│             │             │
Frontend    API         Database
(React)   (FastAPI)   (PostgreSQL)
```

**Fluxo**:
1. Usuário acessa https://monitor.seudominio.com
2. Nginx recebe conexão HTTPS (porta 443)
3. Nginx descriptografa SSL
4. Nginx encaminha para Frontend/API (HTTP interno)
5. Resposta volta criptografada para usuário

---

## 🔐 Segurança

### Configurações Aplicadas

✅ **TLS 1.2 e 1.3** - Protocolos modernos  
✅ **Ciphers Seguros** - Mozilla Intermediate  
✅ **HSTS** - Force HTTPS por 1 ano  
✅ **OCSP Stapling** - Validação rápida  
✅ **Security Headers** - Proteção adicional  

### Teste de Segurança

Após configurar, teste em:
- https://www.ssllabs.com/ssltest/
- Deve obter nota A ou A+

---

## ❓ Troubleshooting

### Erro: "Domínio não aponta para este servidor"

**Solução**:
```powershell
# Verificar DNS
nslookup monitor.seudominio.com

# Deve retornar o IP do seu servidor
```

### Erro: "Porta 80 não acessível"

**Solução**:
1. Verificar firewall do Windows
2. Verificar port forwarding no router
3. Verificar se ISP não bloqueia porta 80

### Erro: "Rate limit exceeded"

**Solução**:
- Let's Encrypt tem limite de 5 certificados/semana por domínio
- Use modo staging para testes: `-Production` (sem flag)
- Aguarde 1 semana para tentar novamente

### Navegador ainda mostra aviso

**Solução**:
1. Limpar cache do navegador (Ctrl+Shift+Delete)
2. Fechar e reabrir navegador
3. Verificar se está acessando https:// (não http://)

---

## 📚 Recursos Adicionais

### Let's Encrypt

- Site: https://letsencrypt.org
- Documentação: https://letsencrypt.org/docs/
- Status: https://letsencrypt.status.io

### Certbot

- Site: https://certbot.eff.org
- Documentação: https://eff-certbot.readthedocs.io

### DuckDNS (DNS Gratuito)

- Site: https://www.duckdns.org
- Atualização automática de IP dinâmico

---

## 💡 Dicas

### Usar com IP Dinâmico

Se seu IP muda frequentemente:

1. Usar DuckDNS
2. Instalar cliente de atualização:
```powershell
# Atualizar IP no DuckDNS a cada 5 minutos
$token = "SEU_TOKEN_DUCKDNS"
$domain = "corujamonitor"

while ($true) {
    Invoke-WebRequest "https://www.duckdns.org/update?domains=$domain&token=$token"
    Start-Sleep -Seconds 300
}
```

### Múltiplos Domínios

```powershell
# Adicionar múltiplos domínios ao mesmo certificado
.\setup-https.ps1 -Domain "monitor.seudominio.com,monitor2.seudominio.com" -Email "seu@email.com" -Production
```

### Wildcard Certificate

```powershell
# Certificado para *.seudominio.com
# Requer validação DNS (mais complexo)
docker-compose run --rm certbot certonly --manual --preferred-challenges dns -d "*.seudominio.com"
```

---

## ✅ Checklist de Implementação

### Desenvolvimento

- [ ] Executar `.\setup-https.ps1 -SelfSigned`
- [ ] Acessar https://localhost
- [ ] Aceitar certificado no navegador
- [ ] Testar funcionalidades

### Produção

- [ ] Configurar domínio
- [ ] Verificar DNS aponta para servidor
- [ ] Abrir portas 80 e 443
- [ ] Executar setup em staging
- [ ] Executar setup em produção
- [ ] Testar acesso HTTPS
- [ ] Verificar renovação automática

---

## 🎉 Conclusão

Com Let's Encrypt você tem:

✅ **HTTPS gratuito** para sempre  
✅ **Renovação automática** - zero manutenção  
✅ **Certificado confiável** - sem avisos  
✅ **Fácil configuração** - 1 comando  

**Seu sistema está seguro e profissional!** 🔒

---

**Data**: 04 de Março de 2026  
**Versão**: 1.0.0  
**Status**: ✅ IMPLEMENTADO

🔒 **CORUJA MONITOR - HTTPS ENTERPRISE**
