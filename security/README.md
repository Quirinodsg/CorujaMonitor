# 🔒 Segurança - Coruja Monitor

Este diretório contém todos os componentes de segurança do Coruja Monitor.

## 📁 Arquivos

### Middleware e Proteções

- **`waf_middleware.py`** - Web Application Firewall
  - Proteção contra SQL Injection
  - Proteção contra XSS
  - Rate Limiting
  - Security Headers
  - Blacklist de IPs maliciosos

### Verificação de Integridade

- **`integrity_check.py`** - Verificação de integridade de arquivos
  - Gera checksums SHA256
  - Detecta modificações não autorizadas
  - Detecta arquivos removidos ou adicionados

### Scan de Vulnerabilidades

- **`scan_dependencies.py`** - Scanner de dependências
  - Scan de dependências Python (Safety)
  - Scan de dependências Node.js (npm audit)
  - Scan de imagens Docker (Trivy)

- **`run_security_scan.ps1`** - Script completo de segurança
  - Executa todos os scans
  - Verifica integridade
  - Scan de secrets expostos
  - Windows Defender scan
  - Docker security check

## 🚀 Uso Rápido

### 1. Executar Scan Completo

```powershell
# Windows PowerShell
.\security\run_security_scan.ps1
```

```bash
# Linux/Mac
python security/scan_dependencies.py
```

### 2. Verificar Integridade

```bash
# Gerar checksums (primeira vez)
python security/integrity_check.py generate

# Verificar integridade
python security/integrity_check.py verify
```

### 3. Ativar WAF

O WAF é ativado automaticamente quando a API inicia. Verifique os logs:

```
✅ WAF Middleware enabled
```

## 🛡️ Proteções Implementadas

### WAF (Web Application Firewall)

✅ **SQL Injection Protection**
- Detecta padrões de SQL injection em query params e body
- Bloqueia requisições maliciosas
- Adiciona IP à blacklist

✅ **XSS Protection**
- Detecta scripts maliciosos
- Valida headers
- Sanitiza inputs

✅ **Rate Limiting**
- 100 requisições por minuto por IP
- 1000 requisições por hora por IP
- Blacklist temporária para abusadores

✅ **Security Headers**
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security
- Content-Security-Policy
- Referrer-Policy
- Permissions-Policy

### Verificação de Integridade

✅ **Checksums SHA256**
- Detecta modificações em arquivos
- Detecta arquivos removidos
- Detecta arquivos adicionados
- Relatório detalhado

### Scan de Vulnerabilidades

✅ **Python Dependencies**
- Safety check para vulnerabilidades conhecidas
- Relatório de CVEs
- Sugestões de correção

✅ **Node.js Dependencies**
- npm audit para vulnerabilidades
- Severidade (low, moderate, high, critical)
- Auto-fix disponível

✅ **Docker Images**
- Trivy scan para vulnerabilidades
- Foco em HIGH e CRITICAL
- Scan de todas as imagens

## 📊 Configuração

### WAF Middleware

Edite `waf_middleware.py` para ajustar:

```python
# Rate limiting
self.max_requests_per_minute = 100
self.max_requests_per_hour = 1000

# Duração da blacklist
self.blacklist_duration = timedelta(hours=1)
```

### Integrity Check

Edite `integrity_check.py` para ajustar arquivos ignorados:

```python
self.ignore_patterns = [
    ".git",
    "__pycache__",
    "node_modules",
    "*.log",
    # Adicione mais padrões aqui
]
```

## 🔐 Assinatura de Instaladores

Para assinar o instalador MSI e evitar detecção como malware:

```powershell
# Com certificado auto-assinado (desenvolvimento)
.\installer\sign-msi.ps1 -MsiPath ".\installer\CorujaMonitorProbe-1.0.0.msi" -CreateSelfSigned

# Com certificado Code Signing (produção)
.\installer\sign-msi.ps1 -MsiPath ".\installer\CorujaMonitorProbe-1.0.0.msi" -CertThumbprint "SEU_THUMBPRINT"
```

## 🐳 Docker Security Hardening

Para aplicar hardening de segurança nos containers:

```bash
# Usar docker-compose com security
docker-compose -f docker-compose.yml -f docker-compose.security.yml up -d
```

Isso aplica:
- `no-new-privileges:true`
- Capabilities mínimas (cap_drop ALL)
- tmpfs com noexec
- Security options

## 📋 Checklist de Segurança

### Antes de Deploy

- [ ] Executar `run_security_scan.ps1`
- [ ] Gerar checksums com `integrity_check.py generate`
- [ ] Assinar instalador MSI
- [ ] Verificar que não há secrets no código
- [ ] Atualizar todas as dependências
- [ ] Executar testes de segurança

### Após Deploy

- [ ] Verificar WAF está ativo
- [ ] Monitorar logs de segurança
- [ ] Verificar integridade periodicamente
- [ ] Manter dependências atualizadas
- [ ] Revisar blacklist de IPs

## 🚨 Resposta a Incidentes

### Se Detectar Vulnerabilidade

1. **Avaliar severidade** (Low, Medium, High, Critical)
2. **Isolar sistema** se necessário
3. **Aplicar patch** ou atualização
4. **Verificar integridade** após correção
5. **Documentar incidente**

### Se Detectar Modificação Não Autorizada

1. **Parar sistema imediatamente**
2. **Verificar logs** de acesso
3. **Restaurar backup** se necessário
4. **Investigar causa raiz**
5. **Fortalecer segurança**

## 📚 Recursos Adicionais

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [ISO 27001](https://www.iso.org/isoiec-27001-information-security.html)

## 📞 Suporte

Para questões de segurança:
- 📧 Email: security@corujamonitor.com
- 🔒 Reporte vulnerabilidades: security-report@corujamonitor.com

---

**Última atualização**: 04 de Março de 2026  
**Versão**: 1.0.0
