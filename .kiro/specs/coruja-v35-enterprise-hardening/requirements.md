# Requirements Document

## Introduction

Este documento especifica os requisitos para o conjunto de melhorias enterprise do Coruja Monitor v3.5 (codename: **Enterprise Hardening**). O sistema é uma plataforma SaaS de monitoramento de infraestrutura composta por backend Python/FastAPI, worker Celery, frontend React, PostgreSQL/TimescaleDB e Redis, orquestrados via Docker Compose.

Os seis problemas a resolver são: (1) alertas inúteis de sensores de rede, (2) configuração de sensores padrão por tipo de ativo, (3) pause de sensor não funciona corretamente no worker, (4) redirect HTTP → HTTPS via Nginx, (5) consistência de alertas com cooldown e deduplicação, e (6) suite de testes SDD cobrindo todos os problemas.

---

## Glossary

- **Alert_Engine**: Módulo `alert_engine/engine.py` responsável por processar eventos e gerar alertas.
- **Cooldown_Filter**: Componente interno do Alert_Engine que suprime alertas repetidos dentro de uma janela de tempo configurável.
- **Default_Sensor_Profile**: Conjunto de sensores padrão associado a um tipo de ativo (VM, Servidor Físico, Network Device), persistido na tabela `default_sensor_profiles`.
- **Dependency_Engine**: Módulo `engine/dependency_engine.py` que gerencia o DAG de dependências entre sensores.
- **Discovery_Service**: Serviço de descoberta automática de ativos (`api/routers/discovery.py`).
- **Incident**: Registro de violação de threshold persistido na tabela `incidents`.
- **Metric_Only_Sensor**: Sensor com `alert_mode = 'metric_only'` — coleta métricas mas nunca gera Incident nem envia ao predictor.
- **Nginx_Proxy**: Serviço Nginx configurado como reverse proxy com terminação TLS.
- **Sensor**: Entidade persistida na tabela `sensors` com campos `enabled`, `alert_mode`, `priority`, `paused_until`.
- **Sensor_Controls_Router**: Módulo `api/routers/sensor_controls.py` com endpoints PATCH para controle de sensores.
- **Worker**: Serviço Celery (`worker/tasks.py`) responsável pela avaliação periódica de thresholds.

---

## Requirements

### Requirement 1: Sensores de Rede como Metric-Only por Padrão

**User Story:** Como operador de NOC, quero que sensores `network_in` e `network_out` não gerem incidentes por padrão, para que o painel de incidentes não seja poluído com alertas de tráfego de rede irrelevantes.

#### Acceptance Criteria

1. THE Sensor SHALL suportar o valor `'metric_only'` no campo `alert_mode`, distinto de `'normal'` e `'silent'`.
2. WHEN um Sensor com `sensor_type` igual a `'network_in'` ou `'network_out'` é criado sem `alert_mode` explícito, THE Sensor SHALL ter `alert_mode` definido como `'metric_only'`.
3. WHILE um Sensor possui `alert_mode = 'metric_only'`, THE Worker SHALL coletar e persistir métricas normalmente sem criar Incident.
4. WHILE um Sensor possui `alert_mode = 'metric_only'`, THE Worker SHALL não enviar dados do Sensor ao serviço de predição de falhas (failure predictor).
5. WHERE um Sensor possui a tag `'internet_link'` em seu campo `config`, THE Sensor SHALL ter `alert_mode` padrão igual a `'alert'` (comportamento normal com geração de Incident).
6. THE Sensor_Controls_Router SHALL aceitar o valor `'metric_only'` no endpoint `PATCH /sensors/{id}/alert-mode`.
7. IF um Sensor com `alert_mode = 'metric_only'` ultrapassa threshold, THEN THE Worker SHALL registrar o evento apenas como métrica com status `'warning'` ou `'critical'` sem criar Incident.

---

### Requirement 2: Configuração de Sensores Padrão por Tipo de Ativo

**User Story:** Como administrador do sistema, quero configurar quais sensores são criados automaticamente para cada tipo de ativo (VM, Servidor Físico, Network Device), para que novos servidores sejam monitorados com o conjunto correto de sensores desde o primeiro momento.

#### Acceptance Criteria

1. THE System SHALL persistir Default_Sensor_Profiles na tabela `default_sensor_profiles` com campos: `asset_type` (VM, physical_server, network_device), `sensor_type`, `enabled`, `alert_mode`, `threshold_warning`, `threshold_critical`.
2. WHEN um novo Server é criado via API, THE Discovery_Service SHALL aplicar o Default_Sensor_Profile correspondente ao `device_type` do Server, criando os Sensors definidos no perfil.
3. WHEN o Discovery_Service descobre um novo ativo, THE Discovery_Service SHALL aplicar o Default_Sensor_Profile correspondente ao tipo de ativo descoberto.
4. THE System SHALL expor endpoints REST `GET /default-sensor-profiles` e `PUT /default-sensor-profiles/{asset_type}` para leitura e atualização dos perfis.
5. WHEN um Default_Sensor_Profile define `alert_mode = 'metric_only'` para um `sensor_type`, THE System SHALL criar o Sensor correspondente com `alert_mode = 'metric_only'`.
6. THE Frontend SHALL exibir uma tela em Configurações → Sensores Padrão permitindo ao usuário ativar/desativar e configurar `alert_mode` para cada tipo de sensor por tipo de ativo.
7. IF nenhum Default_Sensor_Profile existe para um `asset_type`, THEN THE System SHALL aplicar o perfil padrão de fábrica definido em código (CPU, Memória, Disco habilitados; Network metric_only).

---

### Requirement 3: Pause de Sensor com Efeito Completo no Worker

**User Story:** Como operador, quero que ao pausar um sensor o Worker pare imediatamente de coletar métricas, gerar alertas e enviar dados ao predictor, para que janelas de manutenção não gerem ruído no sistema.

#### Acceptance Criteria

1. WHEN um Sensor tem `enabled = False`, THE Worker SHALL ignorar completamente o Sensor no ciclo de avaliação de thresholds, não coletando métricas, não criando Incidents e não enviando ao predictor.
2. WHEN um Sensor tem `paused_until` definido com valor futuro, THE Worker SHALL tratar o Sensor como desabilitado até que `paused_until` seja ultrapassado.
3. THE Worker SHALL verificar tanto `enabled` quanto `paused_until` antes de processar qualquer Sensor no ciclo `evaluate_all_thresholds`.
4. WHEN um Sensor é pausado via `PATCH /sensors/{id}/pause`, THE Sensor_Controls_Router SHALL retornar resposta imediata com `is_paused = True` e o `paused_until` calculado.
5. THE Frontend SHALL exibir badge visual "PAUSADO" em Sensors com `enabled = False` ou `paused_until` futuro, com atualização imediata após chamada à API.
6. WHEN um Sensor pausado tem Incidents abertos, THE Worker SHALL não criar novos Incidents para esse Sensor durante o período de pausa.
7. IF o campo `enabled` não existe na versão do container do Worker, THEN THE Worker SHALL ser atualizado para verificar `enabled` e `paused_until` antes de processar cada Sensor.

---

### Requirement 4: Redirect HTTP → HTTPS via Nginx

**User Story:** Como administrador de segurança, quero que todo acesso HTTP seja redirecionado para HTTPS com certificado válido, para que a comunicação com o Coruja Monitor seja sempre criptografada.

#### Acceptance Criteria

1. THE Nginx_Proxy SHALL redirecionar todas as requisições recebidas na porta 80 para HTTPS na porta 443 com código HTTP 301.
2. THE Nginx_Proxy SHALL fazer proxy reverso de requisições HTTPS para `frontend:3000` (rotas de UI) e `api:8000` (rotas `/api/`).
3. THE System SHALL incluir script de geração de certificado self-signed (`scripts/generate-ssl-cert.sh`) que cria certificado e chave em `/etc/nginx/ssl/`.
4. THE System SHALL incluir configuração de cron (`scripts/renew-ssl-cert.sh`) para renovação automática do certificado com antecedência mínima de 30 dias.
5. THE docker-compose.yml SHALL incluir serviço `nginx` com volumes para certificados SSL e dependência dos serviços `api` e `frontend`.
6. WHEN o certificado SSL está ausente no path configurado, THE Nginx_Proxy SHALL registrar erro no log e não iniciar, evitando exposição sem TLS.
7. THE Frontend SHALL ter `REACT_APP_API_URL` configurado para usar `https://` no ambiente de produção.

---

### Requirement 5: Consistência de Alertas com Cooldown, Deduplicação e Supressão por Dependência

**User Story:** Como operador de NOC, quero que o sistema não gere alertas duplicados, respeite cooldown por sensor e suprima alertas de filhos quando o sensor pai (ping) estiver em falha, para que o painel de incidentes reflita apenas problemas reais e únicos.

#### Acceptance Criteria

1. THE Alert_Engine SHALL aplicar cooldown por Sensor com valor padrão de 300 segundos (5 minutos), configurável por Sensor via campo `cooldown_seconds`.
2. WHEN já existe um Incident com `status = 'open'` para um Sensor, THE Worker SHALL não criar novo Incident para o mesmo Sensor até que o Incident existente seja resolvido.
3. THE Alert_Engine SHALL integrar com o Dependency_Engine para supressão por dependência: WHEN um Sensor do tipo `ping` está com status `CRITICAL` para um host, THE Alert_Engine SHALL suprimir Incidents de sensores `cpu`, `memory`, `disk` e `network` do mesmo host.
4. WHEN o Sensor pai (ping) retorna ao status `OK`, THE Alert_Engine SHALL reativar a geração de Incidents para os sensores filhos do mesmo host.
5. THE Alert_Engine SHALL registrar em log cada supressão por dependência com identificação do sensor pai e dos sensores filhos suprimidos.
6. THE Worker SHALL verificar existência de Incident aberto antes de criar novo Incident (deduplicação no nível do Worker, além da deduplicação no Alert_Engine).
7. IF o Dependency_Engine não possui estado de cache para um host, THEN THE Alert_Engine SHALL permitir a geração de Incidents normalmente (fail-open).

---

### Requirement 6: Suite de Testes SDD para Enterprise Hardening v3.5

**User Story:** Como desenvolvedor, quero uma suite de testes automatizados cobrindo todos os seis problemas do Enterprise Hardening, para que regressões sejam detectadas automaticamente em CI/CD.

#### Acceptance Criteria

1. THE System SHALL conter arquivo `tests/v35/test_network_alert_mode.py` com testes que verificam: sensor `network_in` não gera Incident com `alert_mode = 'metric_only'`; sensor com tag `internet_link` gera Incident normalmente.
2. THE System SHALL conter arquivo `tests/v35/test_sensor_pause.py` com testes que verificam: sensor com `enabled = False` é ignorado pelo Worker; sensor com `paused_until` futuro é ignorado; sensor retomado volta a ser processado.
3. THE System SHALL conter arquivo `tests/v35/test_default_profiles.py` com testes que verificam: novo Server do tipo VM recebe sensores do perfil VM; perfil com `metric_only` cria sensor com `alert_mode = 'metric_only'`.
4. THE System SHALL conter arquivo `tests/v35/test_https_redirect.py` com testes que verificam: configuração Nginx contém redirect 301 de porta 80 para 443; bloco SSL está presente na configuração.
5. THE System SHALL conter arquivo `tests/v35/test_alert_consistency.py` com testes que verificam: cooldown impede segundo Incident dentro da janela; deduplicação impede Incident duplicado com Incident aberto; ping CRITICAL suprime sensores filhos do mesmo host.
6. WHEN todos os testes em `tests/v35/` são executados, THE System SHALL reportar 0 falhas para o código implementado conforme este documento.
7. THE System SHALL conter arquivo `tests/v35/__init__.py` para que o diretório seja reconhecido como pacote Python pelo pytest.
