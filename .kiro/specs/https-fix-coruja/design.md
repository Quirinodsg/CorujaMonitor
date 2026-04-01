# HTTPS Fix Coruja — Bugfix Design

## Overview

O stack HTTPS do Coruja Monitor (servidor 192.168.31.161) está inoperante por quatro causas
independentes mas relacionadas:

1. O certificado SSL self-signed é gerado sem `subjectAltName` (SAN) incluindo o IP do servidor,
   fazendo browsers Chrome 58+ rejeitarem com `ERR_CERT_AUTHORITY_INVALID`.
2. O `config.js` do frontend com URL relativa correta não foi propagado para o container em execução.
3. O WebSocket em `Dashboard.js` constrói a URL com porta hardcoded `:8000` em vez de usar o proxy
   nginx, quebrando `wss://` em contexto HTTPS.
4. O script `renew-ssl-cert.sh` existe mas não está configurado como cron job no container nginx.

A estratégia de correção é mínima e cirúrgica: corrigir `generate-ssl-cert.sh` para incluir o IP
no SAN, criar `nginx/docker-entrypoint-ssl.sh` que inicializa o cron no container, corrigir a URL
do WebSocket no `Dashboard.js`, e criar `_fix_https_linux.sh` para deploy no servidor.

## Glossary

- **Bug_Condition (C)**: Conjunto de condições que tornam o HTTPS inoperante — certificado sem SAN
  para IP/domínio, config.js desatualizado no container, WebSocket com porta hardcoded, ou cron
  de renovação ausente.
- **Property (P)**: Comportamento correto esperado quando a condição de bug é satisfeita — TLS
  handshake bem-sucedido, login retorna JWT, WebSocket conecta via `wss://`, certificado renova
  automaticamente.
- **Preservation**: Comportamentos existentes que NÃO devem ser alterados pela correção — redirect
  HTTP→HTTPS, proxy da API com headers corretos, acesso direto na porta 3000, dados persistidos.
- **isBugCondition**: Função pseudocódigo que identifica entradas que ativam o bug.
- **httpsStack**: Função original (com bug) que processa requisições HTTPS.
- **httpsStack'**: Função corrigida após o fix.
- **SAN**: Subject Alternative Name — extensão X.509 obrigatória para browsers modernos validarem
  certificados por IP ou domínio.
- **generate-ssl-cert.sh**: Script em `scripts/generate-ssl-cert.sh` que gera o certificado
  self-signed. Atualmente omite `IP:192.168.31.161` no SAN.
- **docker-entrypoint-ssl.sh**: Script NOVO em `nginx/docker-entrypoint-ssl.sh` que inicializa
  o container nginx gerando o certificado se ausente e configurando o cron de renovação.
- **WS_URL**: Constante em `frontend/src/components/Dashboard.js` que constrói a URL do WebSocket.
  Atualmente hardcoda `:8000` em vez de usar URL relativa via nginx.

## Bug Details

### Bug Condition

O bug se manifesta quando qualquer uma das quatro condições abaixo é verdadeira. Cada condição
é independente mas todas contribuem para o HTTPS estar inoperante.

**Formal Specification:**
```
FUNCTION isBugCondition(X)
  INPUT: X of type HttpsStackState
  OUTPUT: boolean

  cert_missing_san_ip     ← X.cert.san NOT CONTAINS "IP:192.168.31.161"
  cert_missing_san_domain ← X.cert.san NOT CONTAINS "DNS:coruja.empresaxpto.com.br"
  config_js_stale         ← X.frontend_container.config_js.api_url IS absolute_url
                            AND X.access_port != 3000
  ws_hardcoded_port       ← X.dashboard_ws_url CONTAINS ":8000"
                            AND X.protocol = "https:"
  cron_not_configured     ← X.nginx_container.cron_jobs NOT CONTAINS "renew-ssl-cert.sh"

  RETURN cert_missing_san_ip
      OR cert_missing_san_domain
      OR config_js_stale
      OR ws_hardcoded_port
      OR cron_not_configured
END FUNCTION
```

### Examples

- **Certificado sem SAN IP**: Browser acessa `https://192.168.31.161` → Chrome exibe
  `ERR_CERT_AUTHORITY_INVALID` porque o certificado atual tem apenas `DNS:coruja.empresaxpto.com.br`
  no SAN, sem `IP:192.168.31.161`.

- **Certificado sem SAN domínio**: Browser acessa `https://coruja.empresaxpto.com.br` → aviso de
  certificado não confiável porque o SAN não inclui o domínio (ou o certificado foi gerado sem
  `-addext subjectAltName`).

- **config.js desatualizado**: Login via HTTPS falha com CORS/network error porque o container
  frontend ainda serve o `config.js` antigo com `API_URL = "http://192.168.31.161:8000/api/v1"`,
  que é bloqueado como mixed content em contexto HTTPS.

- **WebSocket com porta hardcoded**: `Dashboard.js` constrói
  `wss://192.168.31.161:8000/api/v1/ws/dashboard` — a porta 8000 não está exposta via HTTPS,
  causando falha de conexão. O correto é usar URL relativa via nginx: `/api/v1/ws/dashboard`.

- **Cron ausente**: Certificado expira após 365 dias sem renovação automática porque o container
  nginx:alpine não tem cron configurado por padrão.

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Requisições HTTP para `http://192.168.31.161` devem continuar redirecionando para HTTPS com 301
- Acesso direto ao frontend na porta 3000 (modo dev) deve continuar usando
  `http://{hostname}:8000/api/v1` como URL da API
- O nginx deve continuar fazendo proxy de `/api/` para `http://api:8000/api/` com todos os
  headers corretos (`X-Forwarded-Proto`, `X-Real-IP`, `X-Forwarded-For`, `Host`)
- O bloco WebSocket no nginx.conf (`/api/v1/ws/`) com headers `Upgrade` e `Connection` deve
  permanecer inalterado
- Os containers postgres e redis não devem ser reiniciados durante o processo de correção
- Requisições autenticadas à API devem continuar retornando dados corretamente

**Scope:**
Todos os inputs que NÃO envolvem o stack HTTPS (certificado, config.js, WebSocket URL, cron)
devem ser completamente inalterados por este fix. Isso inclui:
- Lógica de negócio da API (sensores, servidores, alertas, incidentes)
- Autenticação JWT (geração e validação de tokens)
- Coleta de métricas pelo worker e probe
- Dados persistidos no postgres e redis

## Hypothesized Root Cause

Com base na análise dos arquivos existentes:

1. **SAN ausente no generate-ssl-cert.sh**: O script atual usa `-addext "subjectAltName=DNS:$DOMAIN,DNS:localhost,IP:127.0.0.1"` mas omite `IP:192.168.31.161`. O IP do servidor de rede interna não está incluído, causando rejeição pelo browser ao acessar por IP.

2. **config.js não propagado para o container**: O `frontend/src/config.js` já está correto (usa URL relativa quando não na porta 3000), mas o container em execução ainda serve a versão antiga porque o volume mount do docker-compose não cobre o arquivo compilado/servido. É necessário `docker cp` ou rebuild do container.

3. **WebSocket URL hardcoda porta 8000**: Em `Dashboard.js`, a constante `WS_URL` é:
   ```js
   const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
   return `${proto}//${window.location.hostname}:8000/api/v1/ws/dashboard`;
   ```
   Isso bypassa o nginx e tenta conectar diretamente na porta 8000, que não está exposta via TLS.
   A correção é usar URL relativa: `${proto}//${window.location.host}/api/v1/ws/dashboard`
   (sem porta hardcoded, usando `window.location.host` que inclui a porta correta se necessário).

4. **Entrypoint nginx não configura cron**: A imagem `nginx:alpine` não tem cron ativo por padrão.
   O `docker-compose.yml` atual não define `entrypoint` para o serviço nginx, então o container
   inicia com o entrypoint padrão do nginx sem configurar o cron de renovação.

## Correctness Properties

Property 1: Bug Condition — Certificado com SAN Completo

_For any_ certificado gerado pelo `generate-ssl-cert.sh` corrigido, o certificado SHALL conter
`IP:192.168.31.161` E `DNS:coruja.empresaxpto.com.br` E `DNS:localhost` no campo
`subjectAltName`, e SHALL ter validade mínima de 365 dias a partir da data de geração.

**Validates: Requirements 2.1, 2.2**

Property 2: Bug Condition — WebSocket usa URL Relativa via Nginx

_For any_ acesso ao Dashboard via HTTPS (`window.location.protocol === 'https:'`), a constante
`WS_URL` em `Dashboard.js` SHALL construir uma URL `wss://` usando `window.location.host`
(sem porta hardcoded `:8000`), permitindo que o nginx faça o proxy do WebSocket corretamente.

**Validates: Requirements 2.4**

Property 3: Bug Condition — Renovação Automática Configurada

_For any_ estado do container nginx iniciado via `docker-entrypoint-ssl.sh`, o container SHALL
ter um cron job ativo executando `renew-ssl-cert.sh` às 3h diariamente, e o script SHALL
renovar o certificado quando restar menos de 30 dias para expiração.

**Validates: Requirements 2.5**

Property 4: Preservation — Redirect HTTP→HTTPS

_For any_ requisição HTTP na porta 80, o nginx SHALL retornar status 301 redirecionando para
`https://`, preservando o comportamento existente inalterado pelo fix.

**Validates: Requirements 3.1**

Property 5: Preservation — config.js Porta 3000

_For any_ acesso ao frontend com `window.location.port === '3000'`, o `config.js` SHALL
retornar `API_URL = http://{hostname}:8000/api/v1`, preservando o comportamento de
desenvolvimento direto sem nginx.

**Validates: Requirements 3.2**

## Fix Implementation

### Changes Required

**Arquivo 1**: `scripts/generate-ssl-cert.sh`

**Mudança**: Adicionar `IP:192.168.31.161` ao SAN e tornar o IP configurável via variável de ambiente.

```bash
# Antes:
-addext "subjectAltName=DNS:$DOMAIN,DNS:localhost,IP:127.0.0.1"

# Depois:
SERVER_IP="${CORUJA_SERVER_IP:-192.168.31.161}"
-addext "subjectAltName=DNS:$DOMAIN,DNS:localhost,IP:$SERVER_IP,IP:127.0.0.1"
```

---

**Arquivo 2**: `frontend/src/components/Dashboard.js`

**Mudança**: Corrigir `WS_URL` para usar `window.location.host` em vez de hostname + porta hardcoded.

```js
// Antes:
const WS_URL = (() => {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${window.location.hostname}:8000/api/v1/ws/dashboard`;
})();

// Depois:
const WS_URL = (() => {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.protocol === 'https:'
    ? window.location.host          // usa host sem porta (nginx proxy)
    : `${window.location.hostname}:8000`; // dev direto
  return `${proto}//${host}/api/v1/ws/dashboard`;
})();
```

---

**Arquivo 3**: `nginx/docker-entrypoint-ssl.sh` (NOVO)

**Mudança**: Criar script de entrypoint que gera certificado se ausente e configura cron.

```bash
#!/bin/sh
# Entrypoint customizado para nginx com SSL e cron de renovação

# Gerar certificado se não existir
if [ ! -f /etc/nginx/ssl/coruja.crt ]; then
    echo "[entrypoint] Gerando certificado SSL..."
    /scripts/generate-ssl-cert.sh
fi

# Instalar e configurar cron (alpine usa busybox crond)
echo "0 3 * * * /scripts/renew-ssl-cert.sh >> /var/log/ssl-renew.log 2>&1" \
    > /etc/crontabs/root
crond -b -l 8

# Iniciar nginx em foreground
exec nginx -g "daemon off;"
```

---

**Arquivo 4**: `docker-compose.yml`

**Mudança**: Atualizar serviço nginx para usar entrypoint customizado e montar scripts.

```yaml
nginx:
  image: nginx:alpine
  container_name: coruja-nginx
  restart: always
  entrypoint: ["/docker-entrypoint-ssl.sh"]
  ports:
    - "80:80"
    - "443:443"
  depends_on:
    - api
    - frontend
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - ./nginx/ssl:/etc/nginx/ssl          # rw para geração do cert
    - ./nginx/docker-entrypoint-ssl.sh:/docker-entrypoint-ssl.sh:ro
    - ./scripts:/scripts:ro
  environment:
    - TZ=America/Sao_Paulo
    - CORUJA_SERVER_IP=192.168.31.161
    - CORUJA_DOMAIN=coruja.empresaxpto.com.br
```

---

**Arquivo 5**: `_fix_https_linux.sh` (NOVO)

**Mudança**: Script de deploy completo para executar no servidor Linux.

```bash
#!/bin/bash
# Deploy do fix HTTPS no servidor Linux 192.168.31.161
set -e

echo "=== Fix HTTPS Coruja Monitor ==="

# 1. Atualizar código
git pull

# 2. Recriar container nginx (docker-compose 1.29.2 tem bug com --force-recreate)
docker rm -f coruja-nginx
docker-compose up -d nginx

# 3. Aguardar nginx iniciar
sleep 3

# 4. Verificar que nginx está rodando
docker ps | grep coruja-nginx

# 5. Testar redirect HTTP→HTTPS
curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "301" \
    && echo "✅ Redirect HTTP→HTTPS OK" \
    || echo "❌ Redirect HTTP→HTTPS FALHOU"

# 6. Verificar SAN do certificado
openssl x509 -in ./nginx/ssl/coruja.crt -text -noout 2>/dev/null \
    | grep -A1 "Subject Alternative Name" \
    && echo "✅ Certificado gerado" \
    || echo "⚠️  Certificado ainda não gerado (será gerado no próximo start)"

echo "=== Deploy concluído ==="
```

## Testing Strategy

### Validation Approach

A estratégia segue duas fases: primeiro executar os testes no código NÃO corrigido para confirmar
o root cause, depois verificar que o fix resolve o bug e preserva os comportamentos existentes.

### Exploratory Bug Condition Checking

**Goal**: Confirmar as hipóteses de root cause executando testes no código atual (sem fix).

**Test Plan**: Executar `tests/v35/test_https_complete.py` no código atual e observar as falhas.

**Test Cases**:
1. **test_cert_has_san_ip**: Verifica que `coruja.crt` contém `IP:192.168.31.161` no SAN
   (vai falhar no código atual — certificado não tem esse IP)
2. **test_cert_has_san_domain**: Verifica que `coruja.crt` contém `DNS:coruja.empresaxpto.com.br`
   (pode falhar se o certificado foi gerado sem o domínio)
3. **test_dashboard_ws_url_no_hardcoded_port**: Verifica que `Dashboard.js` não usa `:8000`
   hardcoded na URL do WebSocket em contexto HTTPS (vai falhar no código atual)
4. **test_entrypoint_configures_cron**: Verifica que `docker-entrypoint-ssl.sh` existe e
   configura cron (vai falhar — arquivo não existe ainda)

**Expected Counterexamples**:
- `test_cert_has_san_ip` falha: SAN atual é `DNS:coruja.empresaxpto.com.br, DNS:localhost, IP:127.0.0.1`
- `test_dashboard_ws_url_no_hardcoded_port` falha: código atual tem `:8000` hardcoded
- `test_entrypoint_configures_cron` falha: arquivo não existe

### Fix Checking

**Goal**: Verificar que para todos os inputs onde `isBugCondition(X)` é verdadeiro, o stack
corrigido produz o comportamento esperado.

**Pseudocode:**
```
FOR ALL X WHERE isBugCondition(X) DO
  result ← httpsStack'(X)
  ASSERT cert_has_san_ip(result)
    AND cert_has_san_domain(result)
    AND ws_url_uses_relative_path(result)
    AND cron_job_configured(result)
    AND cert_validity_days(result) >= 365
END FOR
```

### Preservation Checking

**Goal**: Verificar que para todos os inputs onde `NOT isBugCondition(X)`, o stack corrigido
produz o mesmo resultado que o original.

**Pseudocode:**
```
FOR ALL X WHERE NOT isBugCondition(X) DO
  ASSERT httpsStack(X) = httpsStack'(X)
END FOR
```

**Testing Approach**: Property-based testing com Hypothesis para verificar que:
- Qualquer certificado gerado com o script corrigido sempre contém os SANs esperados
- A lógica do `config.js` para porta 3000 permanece inalterada
- O nginx.conf continua com redirect 301 e proxy headers corretos

**Test Cases**:
1. **test_http_redirects_to_https**: Verifica que nginx.conf tem `return 301 https://` no bloco
   porta 80 — comportamento de redirect deve ser preservado
2. **test_config_js_uses_relative_url**: Verifica que `config.js` usa `/api/v1` quando não na
   porta 3000 — comportamento existente deve ser preservado
3. **test_nginx_conf_has_ssl**: Verifica que nginx.conf tem `ssl_certificate` configurado
4. **test_nginx_conf_websocket_upgrade**: Verifica que nginx.conf tem `Upgrade` header no bloco
   WebSocket — configuração existente deve ser preservada

### Unit Tests

- Verificar que `generate-ssl-cert.sh` inclui `IP:192.168.31.161` no SAN após o fix
- Verificar que `Dashboard.js` não contém `:8000` hardcoded na URL do WebSocket
- Verificar que `docker-entrypoint-ssl.sh` contém configuração de cron (`crond`)
- Verificar que `renew-ssl-cert.sh` existe e é executável
- Verificar que `config.js` usa URL relativa quando `port !== '3000'`

### Property-Based Tests

- Gerar certificados com diferentes domínios e IPs via Hypothesis e verificar que o SAN sempre
  contém todos os valores esperados (IP do servidor + domínio + localhost)
- Gerar diferentes valores de `window.location.port` e verificar que `config.js` sempre retorna
  URL relativa para qualquer porta diferente de `'3000'`
- Gerar diferentes valores de `window.location.protocol` e verificar que `WS_URL` sempre usa
  `wss:` para `https:` e `ws:` para `http:`

### Integration Tests

- Verificar que o nginx redireciona HTTP→HTTPS (status 301)
- Verificar que o certificado gerado tem validade >= 30 dias
- Verificar que o script de renovação existe e é executável
- Verificar que o entrypoint configura o cron corretamente
