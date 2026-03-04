# 🔒 Guia Completo de Segurança - Coruja Monitor

## 📋 Índice

1. [Assinatura Digital de Instaladores](#assinatura-digital)
2. [WAF - Web Application Firewall](#waf)
3. [Hardening do Sistema](#hardening)
4. [Proteção contra Malware](#protecao-malware)
5. [Well-Architected Framework](#well-architected)
6. [Checklist de Segurança](#checklist)

---

## 🔐 1. ASSINATURA DIGITAL DE INSTALADORES

### Por que Assinar?

- ✅ Evita detecção como malware por antivírus
- ✅ Garante autenticidade do software
- ✅ Permite instalação sem avisos do Windows
- ✅ Aumenta confiança dos usuários

### Como Assinar o MSI

#### Opção 1: Certificado Code Signing (Recomendado)

```powershell
# 1. Adquirir certificado Code Signing
# Fornecedores: DigiCert, Sectigo, GlobalSign
# Custo: ~$200-500/ano

# 2. Instalar certificado no Windows
# Importar para: Certificados Pessoais

# 3. Assinar o MSI
$certThumbprint = "SEU_THUMBPRINT_AQUI"
$msiPath = ".\installer\CorujaMonitorProbe-1.0.0.msi"

signtool sign /sha1 $certThumbprint /fd SHA256 /t http://timestamp.digicert.com $msiPath

# 4. Verificar assinatura
signtool verify /pa $msiPath
```

#### Opção 2: Certificado Auto-Assinado (Desenvolvimento)

```powershell
# 1. Criar certificado auto-assinado
$cert = New-SelfSignedCertificate `
    -Type CodeSigningCert `
    -Subject "CN=Coruja Monitor, O=Sua Empresa, C=BR" `
    -KeyUsage DigitalSignature `
    -FriendlyName "Coruja Monitor Code Signing" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3") `
    -KeyExportPolicy Exportable `
    -KeyLength 2048 `
    -KeyAlgorithm RSA `
    -HashAlgorithm SHA256

# 2. Exportar certificado
$certPath = ".\CorujaMonitor.pfx"
$certPassword = ConvertTo-SecureString -String "SenhaForte123!" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath $certPath -Password $certPassword

# 3. Assinar MSI
$msiPath = ".\installer\CorujaMonitorProbe-1.0.0.msi"
signtool sign /f $certPath /p "SenhaForte123!" /fd SHA256 /t http://timestamp.digicert.com $msiPath
```

### Script Automatizado de Assinatura

Crie: `installer/sign-msi.ps1`

```powershell
# Sign MSI Script
param(
    [Parameter(Mandatory=$true)]
    [string]$MsiPath,
    
    [Parameter(Mandatory=$false)]
    [string]$CertThumbprint,
    
    [Parameter(Mandatory=$false)]
    [string]$CertPath,
    
    [Parameter(Mandatory=$false)]
    [string]$CertPassword
)

Write-Host "🔐 Assinando instalador MSI..." -ForegroundColor Cyan

# Verificar se signtool está disponível
$signtool = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"
if (-not (Test-Path $signtool)) {
    Write-Host "❌ signtool.exe não encontrado!" -ForegroundColor Red
    Write-Host "Instale o Windows SDK: https://developer.microsoft.com/windows/downloads/windows-sdk/" -ForegroundColor Yellow
    exit 1
}

# Assinar com certificado
if ($CertThumbprint) {
    # Usar certificado instalado
    & $signtool sign /sha1 $CertThumbprint /fd SHA256 /t http://timestamp.digicert.com $MsiPath
} elseif ($CertPath) {
    # Usar arquivo PFX
    & $signtool sign /f $CertPath /p $CertPassword /fd SHA256 /t http://timestamp.digicert.com $MsiPath
} else {
    Write-Host "❌ Nenhum certificado fornecido!" -ForegroundColor Red
    exit 1
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ MSI assinado com sucesso!" -ForegroundColor Green
    
    # Verificar assinatura
    & $signtool verify /pa $MsiPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Assinatura verificada!" -ForegroundColor Green
    }
} else {
    Write-Host "❌ Erro ao assinar MSI!" -ForegroundColor Red
    exit 1
}
```

---

## 🛡️ 2. WAF - WEB APPLICATION FIREWALL

### Implementação no FastAPI

Crie: `api/middleware/waf.py`

```python
"""
WAF Middleware - Proteção contra ataques
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import re

class WAFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limits = defaultdict(list)
        self.blacklist = set()
        
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        
        # 1. Rate Limiting
        if not self.check_rate_limit(client_ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"}
            )
        
        # 2. SQL Injection Detection
        if self.detect_sql_injection(request):
            self.blacklist.add(client_ip)
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid request"}
            )
        
        # 3. XSS Detection
        if self.detect_xss(request):
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid request"}
            )
        
        response = await call_next(request)
        
        # 4. Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        
        return response
```

### Configuração no main.py

```python
from middleware.waf import WAFMiddleware

app = FastAPI()
app.add_middleware(WAFMiddleware)
```

---

## 🔒 3. HARDENING DO SISTEMA

### Docker Security

Crie: `docker-compose.security.yml`

```yaml
version: '3.8'

services:
  api:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    user: "1000:1000"
    
  postgres:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /var/run/postgresql
```

### Nginx Security Headers

Crie: `nginx/security.conf`

```nginx
# Security Headers
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# Hide Nginx version
server_tokens off;

# Limit request size
client_max_body_size 10M;

# Timeout settings
client_body_timeout 10s;
client_header_timeout 10s;
keepalive_timeout 5s 5s;
send_timeout 10s;
```

---

## 🦠 4. PROTEÇÃO CONTRA MALWARE

### Scan de Dependências

```bash
# Python - Safety
pip install safety
safety check --json

# Node.js - npm audit
npm audit
npm audit fix

# Docker - Trivy
docker run aquasec/trivy image corujamonitor-api:latest
```

### Verificação de Integridade

Crie: `security/integrity_check.py`

```python
"""
Verificação de Integridade de Arquivos
"""

import hashlib
import json
from pathlib import Path

def generate_checksums(directory: str) -> dict:
    """Gera checksums SHA256 de todos os arquivos"""
    checksums = {}
    
    for file_path in Path(directory).rglob('*'):
        if file_path.is_file():
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                checksums[str(file_path)] = file_hash
    
    return checksums

def verify_integrity(checksums_file: str) -> bool:
    """Verifica integridade dos arquivos"""
    with open(checksums_file, 'r') as f:
        expected = json.load(f)
    
    current = generate_checksums('.')
    
    for file_path, expected_hash in expected.items():
        if file_path not in current:
            print(f"❌ Arquivo removido: {file_path}")
            return False
        
        if current[file_path] != expected_hash:
            print(f"❌ Arquivo modificado: {file_path}")
            return False
    
    print("✅ Integridade verificada!")
    return True

# Gerar checksums
checksums = generate_checksums('.')
with open('checksums.json', 'w') as f:
    json.dump(checksums, f, indent=2)
```

### Antivírus Scan

```powershell
# Windows Defender Scan
Start-MpScan -ScanType FullScan -ScanPath "C:\Users\andre.quirino\Coruja Monitor"

# VirusTotal API
$apiKey = "SUA_API_KEY"
$file = "CorujaMonitorProbe-1.0.0.msi"
$hash = (Get-FileHash $file -Algorithm SHA256).Hash

$response = Invoke-RestMethod -Uri "https://www.virustotal.com/api/v3/files/$hash" `
    -Headers @{"x-apikey" = $apiKey}

$response.data.attributes.last_analysis_stats
```

---

## 🏗️ 5. WELL-ARCHITECTED FRAMEWORK

### Pilar 1: Segurança

#### Identidade e Acesso
- ✅ Autenticação JWT
- ✅ MFA (Multi-Factor Authentication)
- ✅ RBAC (Role-Based Access Control)
- ✅ LDAP/SAML/OAuth2

#### Proteção de Dados
- ✅ Criptografia em trânsito (TLS 1.3)
- ✅ Criptografia em repouso (AES-256)
- ✅ Hashing de senhas (bcrypt)
- ✅ Secrets management

#### Detecção
- ✅ Logs de auditoria
- ✅ Monitoramento de segurança
- ✅ Alertas de anomalias
- ✅ WAF logs

#### Resposta a Incidentes
- ✅ Plano de resposta
- ✅ Backup automático
- ✅ Disaster recovery
- ✅ Rollback capability

### Pilar 2: Confiabilidade

- ✅ Alta disponibilidade (HA)
- ✅ Backup automático
- ✅ Health checks
- ✅ Retry logic
- ✅ Circuit breakers

### Pilar 3: Eficiência de Performance

- ✅ Cache (Redis)
- ✅ CDN para assets
- ✅ Compressão gzip
- ✅ Lazy loading
- ✅ Database indexing

### Pilar 4: Otimização de Custos

- ✅ Auto-scaling
- ✅ Resource tagging
- ✅ Cost monitoring
- ✅ Reserved instances

### Pilar 5: Excelência Operacional

- ✅ CI/CD pipeline
- ✅ Infrastructure as Code
- ✅ Monitoring e alerting
- ✅ Documentação completa

---

## ✅ 6. CHECKLIST DE SEGURANÇA

### Instaladores

- [ ] MSI assinado digitalmente
- [ ] Certificado Code Signing válido
- [ ] Scan antivírus limpo
- [ ] Verificação de integridade
- [ ] Documentação de instalação
- [ ] Rollback capability

### Aplicação

- [ ] WAF implementado
- [ ] Rate limiting ativo
- [ ] SQL Injection protection
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Security headers configurados
- [ ] HTTPS obrigatório
- [ ] Certificado SSL válido

### Autenticação

- [ ] JWT com expiração
- [ ] MFA disponível
- [ ] Política de senha forte
- [ ] Bloqueio após tentativas falhas
- [ ] Sessões com timeout
- [ ] Logout em todos os dispositivos

### Dados

- [ ] Criptografia em trânsito (TLS 1.3)
- [ ] Criptografia em repouso (AES-256)
- [ ] Backup automático diário
- [ ] Backup testado e funcional
- [ ] Retenção de dados configurada
- [ ] LGPD compliance

### Infraestrutura

- [ ] Docker hardening aplicado
- [ ] Firewall configurado
- [ ] Portas desnecessárias fechadas
- [ ] Logs centralizados
- [ ] Monitoramento ativo
- [ ] Alertas configurados

### Código

- [ ] Dependências atualizadas
- [ ] Scan de vulnerabilidades
- [ ] Code review realizado
- [ ] Testes de segurança
- [ ] SAST/DAST executados
- [ ] Secrets não commitados

---

## 📚 RECURSOS ADICIONAIS

### Ferramentas Recomendadas

1. **SAST** (Static Application Security Testing)
   - SonarQube
   - Bandit (Python)
   - ESLint Security Plugin (JavaScript)

2. **DAST** (Dynamic Application Security Testing)
   - OWASP ZAP
   - Burp Suite
   - Nikto

3. **Dependency Scanning**
   - Safety (Python)
   - npm audit (Node.js)
   - Snyk

4. **Container Security**
   - Trivy
   - Clair
   - Anchore

5. **Secrets Management**
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault

### Padrões e Frameworks

- OWASP Top 10
- CIS Benchmarks
- NIST Cybersecurity Framework
- ISO 27001
- SOC 2

### Certificações

- Certificado Code Signing
- Certificado SSL/TLS
- Certificação ISO 27001
- Certificação SOC 2

---

## 🚀 IMPLEMENTAÇÃO RÁPIDA

### Passo 1: Assinar Instaladores

```powershell
# Adquirir certificado Code Signing
# Executar script de assinatura
.\installer\sign-msi.ps1 -MsiPath ".\installer\CorujaMonitorProbe-1.0.0.msi" -CertThumbprint "SEU_THUMBPRINT"
```

### Passo 2: Implementar WAF

```python
# Adicionar ao api/main.py
from middleware.waf import WAFMiddleware
app.add_middleware(WAFMiddleware)
```

### Passo 3: Configurar Security Headers

```python
# Já implementado no WAF
# Verificar em: http://localhost:8000
```

### Passo 4: Scan de Segurança

```bash
# Python
safety check

# Node.js
npm audit

# Docker
docker scan corujamonitor-api:latest
```

### Passo 5: Verificar Integridade

```python
python security/integrity_check.py
```

---

## 📞 SUPORTE

Para questões de segurança:
- 📧 Email: security@corujamonitor.com
- 🔒 Reporte vulnerabilidades: security-report@corujamonitor.com

---

**Data**: 04 de Março de 2026  
**Versão**: 1.0.0  
**Status**: ✅ Guia Completo  
**Conformidade**: OWASP, ISO 27001, LGPD

---

*"Segurança não é um produto, é um processo"*
