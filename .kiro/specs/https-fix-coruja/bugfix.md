# Bugfix Requirements Document

## Introduction

O HTTPS do Coruja Monitor (servidor 192.168.31.161, domínio coruja.techbiz.com.br) está completamente inoperante. O certificado SSL self-signed foi gerado sem `subjectAltName` (SAN) incluindo o IP do servidor, fazendo browsers modernos (Chrome 58+) rejeitarem a conexão com `ERR_CERT_AUTHORITY_INVALID`. Como consequência, o login falha, o dashboard não carrega dados, a seção "Empresa" não aparece e as conexões WebSocket (wss://) não se estabelecem. Adicionalmente, o `config.js` do frontend com a URL relativa correta não foi propagado para o container, e o script de renovação automática do certificado não está configurado como cron job.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN o browser acessa `https://192.168.31.161` THEN o sistema exibe `ERR_CERT_AUTHORITY_INVALID` porque o certificado não possui SAN para o IP `192.168.31.161`

1.2 WHEN o browser acessa `https://coruja.techbiz.com.br` THEN o sistema exibe aviso de certificado não confiável porque o certificado não possui SAN para o domínio `coruja.techbiz.com.br`

1.3 WHEN o usuário tenta fazer login via HTTPS THEN o sistema falha na autenticação porque o container frontend ainda usa a versão antiga do `config.js` com URL absoluta em vez de URL relativa `/api/v1`

1.4 WHEN o frontend carregado via HTTPS tenta conectar ao WebSocket THEN o sistema falha na conexão porque o protocolo `ws://` é bloqueado em contexto HTTPS (mixed content), exigindo `wss://`

1.5 WHEN o certificado SSL se aproxima da data de expiração THEN o sistema não renova automaticamente porque o script `renew-ssl-cert.sh` não está configurado como cron job no container nginx

### Expected Behavior (Correct)

2.1 WHEN o browser acessa `https://192.168.31.161` THEN o sistema SHALL estabelecer conexão TLS sem erros de certificado, pois o certificado contém SAN com `IP:192.168.31.161`

2.2 WHEN o browser acessa `https://coruja.techbiz.com.br` THEN o sistema SHALL estabelecer conexão TLS sem erros de certificado, pois o certificado contém SAN com `DNS:coruja.techbiz.com.br`

2.3 WHEN o usuário submete credenciais de login via HTTPS THEN o sistema SHALL autenticar com sucesso e retornar JWT token, pois o frontend usa URL relativa `/api/v1` que é roteada corretamente pelo nginx

2.4 WHEN o frontend carregado via HTTPS tenta conectar ao WebSocket THEN o sistema SHALL estabelecer conexão `wss://` com sucesso através do proxy nginx configurado para upgrade de protocolo

2.5 WHEN o certificado SSL possui menos de 30 dias até a expiração THEN o sistema SHALL renovar automaticamente o certificado e recarregar o nginx via cron job configurado no container

### Unchanged Behavior (Regression Prevention)

3.1 WHEN o browser acessa `http://192.168.31.161` THEN o sistema SHALL CONTINUE TO redirecionar para `https://192.168.31.161` com status 301

3.2 WHEN o frontend é acessado diretamente na porta 3000 (modo dev) THEN o sistema SHALL CONTINUE TO usar `http://{hostname}:8000/api/v1` como URL da API

3.3 WHEN requisições autenticadas são feitas à API via HTTPS THEN o sistema SHALL CONTINUE TO processar e retornar dados corretamente (sensores, servidores, alertas, etc.)

3.4 WHEN o nginx processa requisições para `/api/` THEN o sistema SHALL CONTINUE TO fazer proxy para `http://api:8000/api/` com os headers corretos (`X-Forwarded-Proto`, `X-Real-IP`, etc.)

3.5 WHEN os containers postgres e redis estão em execução THEN o sistema SHALL CONTINUE TO manter os dados persistidos sem reinicialização desses serviços durante o processo de correção

---

## Bug Condition (Pseudocódigo)

```pascal
FUNCTION isBugCondition(X)
  INPUT: X of type HttpsRequest
  OUTPUT: boolean

  RETURN (X.cert.san.includes(X.target_ip) = FALSE)
      OR (X.frontend_config_js.api_url = absolute_url)
      OR (X.websocket_protocol = "ws://" AND X.context = HTTPS)
      OR (X.cron_job.renew_ssl = NOT_CONFIGURED)
END FUNCTION

// Property: Fix Checking
FOR ALL X WHERE isBugCondition(X) DO
  result ← httpsStack'(X)
  ASSERT tls_handshake_success(result)
    AND login_returns_jwt(result)
    AND websocket_connects_wss(result)
    AND cert_auto_renews(result)
END FOR

// Property: Preservation Checking
FOR ALL X WHERE NOT isBugCondition(X) DO
  ASSERT httpsStack(X) = httpsStack'(X)
END FOR
```
