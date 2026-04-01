# Implementation Plan

- [x] 1. Escrever testes de exploração do bug (Bug Condition)
  - **Property 1: Bug Condition** - HTTPS Stack Inoperante (SAN, WebSocket, Cron)
  - **CRITICAL**: Estes testes DEVEM FALHAR no código atual — a falha confirma que o bug existe
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: Os testes codificam o comportamento esperado — vão validar o fix quando passarem após a implementação
  - **GOAL**: Surfaçar contraexemplos que demonstram o bug
  - **Scoped PBT Approach**: Para bugs determinísticos, escopar a propriedade aos casos concretos de falha
  - Criar `tests/test_https_complete.py` com os seguintes casos:
    - `test_cert_has_san_ip`: Ler `nginx/ssl/coruja.crt` (se existir) ou parsear `scripts/generate-ssl-cert.sh` e verificar que `IP:192.168.31.161` está no SAN — FALHA no código atual (SAN atual: `DNS:coruja.empresaxpto.com.br, DNS:localhost, IP:127.0.0.1`)
    - `test_cert_has_san_domain`: Verificar que `DNS:coruja.empresaxpto.com.br` está no SAN do script — pode falhar se o cert foi gerado sem o domínio
    - `test_dashboard_ws_url_no_hardcoded_port`: Ler `frontend/src/components/Dashboard.js` e verificar que a constante `WS_URL` NÃO contém `:8000` hardcoded — FALHA no código atual (linha: `${proto}//${window.location.hostname}:8000/api/v1/ws/dashboard`)
    - `test_entrypoint_configures_cron`: Verificar que `nginx/docker-entrypoint-ssl.sh` existe e contém `crond` — FALHA no código atual (arquivo não existe)
    - `test_generate_ssl_script_has_server_ip`: Usar Hypothesis para gerar diferentes IPs e verificar que o script sempre inclui o IP do servidor no SAN
  - Contraexemplos esperados:
    - `test_cert_has_san_ip` falha: SAN atual não contém `IP:192.168.31.161`
    - `test_dashboard_ws_url_no_hardcoded_port` falha: código atual tem `:8000` hardcoded
    - `test_entrypoint_configures_cron` falha: `nginx/docker-entrypoint-ssl.sh` não existe
  - Executar: `pytest tests/test_https_complete.py -v` no código NÃO corrigido
  - **EXPECTED OUTCOME**: Testes FALHAM (isso é correto — prova que o bug existe)
  - Documentar os contraexemplos encontrados para entender o root cause
  - Marcar tarefa como completa quando os testes estiverem escritos, executados e as falhas documentadas
  - _Requirements: 1.1, 1.3, 1.4, 1.5_

- [x] 2. Escrever testes de preservação (ANTES de implementar o fix)
  - **Property 2: Preservation** - Comportamentos Existentes Não Devem Ser Alterados
  - **IMPORTANT**: Seguir metodologia observation-first
  - Observar no código NÃO corrigido:
    - `nginx/nginx.conf` tem `return 301 https://` no bloco porta 80
    - `frontend/src/config.js` usa `/api/v1` quando `port !== '3000'`
    - `nginx/nginx.conf` tem `ssl_certificate` configurado
    - `nginx/nginx.conf` tem headers `Upgrade` e `Connection` no bloco WebSocket
    - `config.js` usa `http://${hostname}:8000/api/v1` quando `port === '3000'`
  - Adicionar a `tests/test_https_complete.py` os seguintes casos de preservação:
    - `test_http_redirects_to_https`: Verificar que `nginx/nginx.conf` contém `return 301 https://` no bloco `listen 80`
    - `test_config_js_uses_relative_url`: Verificar que `frontend/src/config.js` usa `/api/v1` (URL relativa) quando não na porta 3000
    - `test_config_js_port_3000_uses_absolute_url`: Verificar que `config.js` usa `http://${hostname}:8000/api/v1` para porta 3000 (modo dev)
    - `test_nginx_conf_has_ssl`: Verificar que `nginx/nginx.conf` contém `ssl_certificate` e `ssl_certificate_key`
    - `test_nginx_conf_websocket_upgrade`: Verificar que `nginx/nginx.conf` contém `Upgrade` e `Connection "upgrade"` no bloco `/api/v1/ws/`
    - `test_nginx_conf_proxy_headers`: Verificar que `nginx/nginx.conf` contém `X-Forwarded-Proto`, `X-Real-IP`, `X-Forwarded-For` no bloco `/api/`
  - Executar: `pytest tests/test_https_complete.py -v -k "preservation or redirect or config_js or nginx_conf"` no código NÃO corrigido
  - **EXPECTED OUTCOME**: Testes de preservação PASSAM (confirma baseline a preservar)
  - Marcar tarefa como completa quando os testes estiverem escritos, executados e passando no código não corrigido
  - _Requirements: 3.1, 3.2, 3.4_

- [x] 3. Corrigir scripts/generate-ssl-cert.sh — adicionar IP:192.168.31.161 ao SAN

  - [x] 3.1 Implementar o fix no generate-ssl-cert.sh
    - Adicionar variável `SERVER_IP="${CORUJA_SERVER_IP:-192.168.31.161}"` antes do comando openssl
    - Alterar `-addext "subjectAltName=DNS:$DOMAIN,DNS:localhost,IP:127.0.0.1"` para `-addext "subjectAltName=DNS:$DOMAIN,DNS:localhost,IP:$SERVER_IP,IP:127.0.0.1"`
    - _Bug_Condition: isBugCondition(X) onde X.cert.san NOT CONTAINS "IP:192.168.31.161"_
    - _Expected_Behavior: certificado gerado contém IP:192.168.31.161 E DNS:coruja.empresaxpto.com.br no SAN_
    - _Preservation: script continua gerando certificado com DNS:$DOMAIN, DNS:localhost, IP:127.0.0.1_
    - _Requirements: 2.1, 2.2_

  - [x] 3.2 Verificar que test_cert_has_san_ip e test_cert_has_san_domain passam
    - **Property 1: Expected Behavior** - Certificado com SAN Completo
    - **IMPORTANT**: Re-executar os MESMOS testes da tarefa 1 — NÃO escrever novos testes
    - Executar: `pytest tests/test_https_complete.py::test_cert_has_san_ip tests/test_https_complete.py::test_cert_has_san_domain tests/test_https_complete.py::test_generate_ssl_script_has_server_ip -v`
    - **EXPECTED OUTCOME**: Testes PASSAM (confirma que o bug do certificado está corrigido)
    - _Requirements: 2.1, 2.2_

- [x] 4. Corrigir frontend/src/components/Dashboard.js — remover porta :8000 hardcoded do WebSocket URL

  - [x] 4.1 Implementar o fix na constante WS_URL
    - Localizar a constante `WS_URL` nas primeiras linhas do arquivo
    - Substituir:
      ```js
      const WS_URL = (() => {
        const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        return `${proto}//${window.location.hostname}:8000/api/v1/ws/dashboard`;
      })();
      ```
      Por:
      ```js
      const WS_URL = (() => {
        const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.protocol === 'https:'
          ? window.location.host          // usa host sem porta hardcoded (nginx proxy)
          : `${window.location.hostname}:8000`; // dev direto
        return `${proto}//${host}/api/v1/ws/dashboard`;
      })();
      ```
    - _Bug_Condition: isBugCondition(X) onde X.dashboard_ws_url CONTAINS ":8000" AND X.protocol = "https:"_
    - _Expected_Behavior: WS_URL usa window.location.host (sem :8000 hardcoded) em contexto HTTPS_
    - _Preservation: em contexto HTTP (dev direto), continua usando hostname:8000_
    - _Requirements: 2.4, 3.2_

  - [x] 4.2 Verificar que test_dashboard_ws_url_no_hardcoded_port passa
    - **Property 1: Expected Behavior** - WebSocket usa URL Relativa via Nginx
    - **IMPORTANT**: Re-executar o MESMO teste da tarefa 1 — NÃO escrever novo teste
    - Executar: `pytest tests/test_https_complete.py::test_dashboard_ws_url_no_hardcoded_port -v`
    - **EXPECTED OUTCOME**: Teste PASSA (confirma que o WebSocket URL está corrigido)
    - _Requirements: 2.4_

- [x] 5. Criar nginx/docker-entrypoint-ssl.sh — entrypoint com geração de cert + cron

  - [x] 5.1 Criar o arquivo nginx/docker-entrypoint-ssl.sh
    - Criar `nginx/docker-entrypoint-ssl.sh` com o seguinte conteúdo:
      ```sh
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
    - Tornar o arquivo executável: `chmod +x nginx/docker-entrypoint-ssl.sh`
    - _Bug_Condition: isBugCondition(X) onde X.nginx_container.cron_jobs NOT CONTAINS "renew-ssl-cert.sh"_
    - _Expected_Behavior: container nginx inicia com cron job ativo executando renew-ssl-cert.sh às 3h diariamente_
    - _Preservation: nginx continua iniciando em foreground com "daemon off;" — comportamento padrão preservado_
    - _Requirements: 2.5_

  - [x] 5.2 Verificar que test_entrypoint_configures_cron passa
    - **Property 1: Expected Behavior** - Renovação Automática Configurada
    - **IMPORTANT**: Re-executar o MESMO teste da tarefa 1 — NÃO escrever novo teste
    - Executar: `pytest tests/test_https_complete.py::test_entrypoint_configures_cron -v`
    - **EXPECTED OUTCOME**: Teste PASSA (confirma que o entrypoint configura o cron)
    - _Requirements: 2.5_

- [x] 6. Atualizar docker-compose.yml — serviço nginx usa entrypoint customizado

  - [x] 6.1 Atualizar o serviço nginx no docker-compose.yml
    - Adicionar `entrypoint: ["/docker-entrypoint-ssl.sh"]` ao serviço nginx
    - Alterar o volume `./nginx/ssl:/etc/nginx/ssl:ro` para `./nginx/ssl:/etc/nginx/ssl` (remover `:ro` para permitir escrita do certificado)
    - Adicionar volumes:
      - `./nginx/docker-entrypoint-ssl.sh:/docker-entrypoint-ssl.sh:ro`
      - `./scripts:/scripts:ro`
    - Adicionar variáveis de ambiente:
      - `CORUJA_SERVER_IP=192.168.31.161`
      - `CORUJA_DOMAIN=coruja.empresaxpto.com.br`
    - **NÃO reiniciar postgres ou redis**
    - **NÃO usar docker-compose --force-recreate** (bug no docker-compose 1.29.2)
    - _Requirements: 2.5, 3.5_

- [x] 7. Criar _fix_https_linux.sh — script de deploy completo para o servidor Linux

  - [x] 7.1 Criar o arquivo _fix_https_linux.sh na raiz do projeto
    - Criar `_fix_https_linux.sh` com o seguinte conteúdo:
      ```bash
      #!/bin/bash
      # Deploy do fix HTTPS no servidor Linux 192.168.31.161
      set -e

      echo "=== Fix HTTPS Coruja Monitor ==="

      # 1. Atualizar código
      git pull

      # 2. Recriar container nginx
      # NOTA: docker-compose 1.29.2 tem bug com --force-recreate, usar docker rm -f + up
      docker rm -f coruja-nginx
      docker-compose up -d nginx

      # 3. Aguardar nginx iniciar
      sleep 3

      # 4. Verificar que nginx está rodando
      docker ps | grep coruja-nginx

      # 5. Copiar config.js atualizado para o container frontend (sem rebuild)
      # O volume mount cobre o source, mas o container serve o arquivo compilado
      docker cp frontend/src/config.js coruja-frontend:/app/src/config.js

      # 6. Testar redirect HTTP→HTTPS
      curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "301" \
          && echo "✅ Redirect HTTP→HTTPS OK" \
          || echo "❌ Redirect HTTP→HTTPS FALHOU"

      # 7. Verificar SAN do certificado
      openssl x509 -in ./nginx/ssl/coruja.crt -text -noout 2>/dev/null \
          | grep -A1 "Subject Alternative Name" \
          && echo "✅ Certificado gerado" \
          || echo "⚠️  Certificado ainda não gerado (será gerado no próximo start)"

      echo "=== Deploy concluído ==="
      ```
    - Tornar o arquivo executável: `chmod +x _fix_https_linux.sh`
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.5_

- [x] 8. Executar testes de validação (fix checking + preservation checking)

  - [x] 8.1 Verificar todos os testes de bug condition passam (fix checking)
    - **Property 1: Expected Behavior** - Todos os Bug Conditions Corrigidos
    - **IMPORTANT**: Re-executar os MESMOS testes da tarefa 1 — NÃO escrever novos testes
    - Executar: `pytest tests/test_https_complete.py -v -k "not preservation and not redirect and not config_js and not nginx_conf"`
    - **EXPECTED OUTCOME**: Todos os testes de bug condition PASSAM
    - _Requirements: 2.1, 2.2, 2.4, 2.5_

  - [x] 8.2 Verificar todos os testes de preservação ainda passam (preservation checking)
    - **Property 2: Preservation** - Comportamentos Existentes Preservados
    - **IMPORTANT**: Re-executar os MESMOS testes da tarefa 2 — NÃO escrever novos testes
    - Executar: `pytest tests/test_https_complete.py -v -k "preservation or redirect or config_js or nginx_conf"`
    - **EXPECTED OUTCOME**: Todos os testes de preservação PASSAM (sem regressões)
    - _Requirements: 3.1, 3.2, 3.4_

  - [x] 8.3 Executar suite completa
    - Executar: `pytest tests/test_https_complete.py -v`
    - **EXPECTED OUTCOME**: Todos os testes PASSAM
    - Confirmar que nenhum teste de preservação regrediu após o fix

- [x] 9. Commit e push das correções
  - Verificar que todos os arquivos modificados/criados estão corretos:
    - `scripts/generate-ssl-cert.sh` — IP:192.168.31.161 no SAN
    - `frontend/src/components/Dashboard.js` — WS_URL sem :8000 hardcoded
    - `nginx/docker-entrypoint-ssl.sh` — entrypoint com cron (NOVO)
    - `docker-compose.yml` — serviço nginx com entrypoint customizado
    - `_fix_https_linux.sh` — script de deploy (NOVO)
    - `tests/test_https_complete.py` — testes de exploração e preservação (NOVO)
  - Executar: `git add scripts/generate-ssl-cert.sh frontend/src/components/Dashboard.js nginx/docker-entrypoint-ssl.sh docker-compose.yml _fix_https_linux.sh tests/test_https_complete.py`
  - Executar: `git commit -m "fix(https): add IP SAN, fix WS URL, add nginx entrypoint with cron"`
  - Executar: `git push`

- [x] 10. Checkpoint — Garantir que todos os testes passam
  - Executar suite completa: `pytest tests/test_https_complete.py -v`
  - Confirmar que todos os testes passam, perguntar ao usuário se surgirem dúvidas
  - Verificar que nenhum container postgres ou redis foi reiniciado durante o processo
