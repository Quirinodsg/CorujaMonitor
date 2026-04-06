# Documento de Requisitos — Escalação Contínua de Alarmes

## Introdução

O Coruja Monitor atualmente dispara uma única ligação de emergência via Twilio quando alertas críticos de datacenter são detectados (nobreak/gerador, ar-condicionado/HVAC). Após essa ligação, o sistema entra em cooldown de 30 minutos e não tenta novamente, mesmo que ninguém tenha atendido ou reconhecido o alarme.

Esta feature implementa um sistema de escalação contínua: o sistema continuará ligando repetidamente para os números configurados até que um analista reconheça o alarme através de um botão na interface. Além disso, será criada uma página de configuração do dashboard de escalação, permitindo ajustar modo de chamada (simultâneo ou sequencial), intervalo entre tentativas, número máximo de retentativas, e visualizar alarmes ativos e seu status de escalação.

## Glossário

- **Sistema_Escalacao**: Módulo responsável por gerenciar o loop contínuo de ligações de emergência via Celery, controlando retentativas, intervalos e estado de escalação no Redis.
- **Painel_Configuracao**: Página do frontend que exibe e permite editar as configurações de escalação (modo de chamada, intervalo, retentativas, cadeia de números).
- **Alarme_Ativo**: Incidente crítico de datacenter (nobreak/gerador ou ar-condicionado/HVAC) que está em estado de escalação contínua, aguardando reconhecimento.
- **Reconhecimento**: Ação explícita de um analista na interface que confirma ciência do alarme e interrompe o loop de ligações.
- **Cadeia_Escalacao**: Lista ordenada de números de telefone que serão chamados durante a escalação, conforme configuração do tenant.
- **Modo_Simultaneo**: Modo de chamada onde todos os números da Cadeia_Escalacao são chamados ao mesmo tempo em cada ciclo.
- **Modo_Sequencial**: Modo de chamada onde os números da Cadeia_Escalacao são chamados um por um, avançando para o próximo se o anterior não atender.
- **Ciclo_Escalacao**: Uma rodada completa de tentativas de ligação para todos os números da Cadeia_Escalacao.
- **Configuracao_Escalacao**: Objeto JSON armazenado dentro do `notification_config` do Tenant, contendo parâmetros de escalação (modo, intervalo, max_retentativas, números).
- **Celery_Worker**: Processo background que executa as tasks assíncronas de ligação e controle de escalação.
- **Redis**: Armazenamento em memória usado para controlar estado de escalação ativa, cooldowns e locks de concorrência.

## Requisitos

### Requisito 1: Loop Contínuo de Ligações

**User Story:** Como analista de NOC, eu quero que o sistema continue ligando repetidamente quando um alerta crítico de datacenter ocorrer, para que eu tenha certeza de que alguém será notificado mesmo se a primeira ligação não for atendida.

#### Critérios de Aceitação

1. WHEN um alerta crítico de datacenter é detectado (nobreak/gerador ou ar-condicionado/HVAC), THE Sistema_Escalacao SHALL iniciar um loop de ligações para todos os números da Cadeia_Escalacao.
2. WHILE um Alarme_Ativo não tiver sido reconhecido, THE Sistema_Escalacao SHALL repetir as ligações a cada intervalo configurado na Configuracao_Escalacao.
3. WHEN o número máximo de retentativas configurado for atingido, THE Sistema_Escalacao SHALL parar o loop de ligações e registrar o evento como "escalação expirada" no log do incidente.
4. THE Sistema_Escalacao SHALL registrar cada tentativa de ligação (número chamado, horário, resultado) no histórico do Alarme_Ativo.
5. IF o Celery_Worker falhar durante uma tentativa de ligação, THEN THE Sistema_Escalacao SHALL agendar uma nova tentativa no próximo intervalo sem perder o estado de escalação.
6. WHEN um novo alerta crítico de datacenter ocorrer para um sensor que já possui um Alarme_Ativo em escalação, THE Sistema_Escalacao SHALL ignorar o novo alerta e manter a escalação existente.

### Requisito 2: Reconhecimento de Alarme para Parar Escalação

**User Story:** Como analista de NOC, eu quero poder reconhecer um alarme ativo para parar as ligações contínuas, para que o sistema pare de ligar depois que eu já estiver ciente do problema.

#### Critérios de Aceitação

1. WHEN um analista clicar no botão de reconhecimento de um Alarme_Ativo, THE Sistema_Escalacao SHALL interromper imediatamente o loop de ligações para aquele alarme.
2. THE Sistema_Escalacao SHALL registrar o reconhecimento com o identificador do analista, data/hora e notas opcionais.
3. WHEN o reconhecimento for registrado, THE Sistema_Escalacao SHALL atualizar o status do incidente para "acknowledged" e remover o estado de escalação ativa do Redis.
4. IF uma ligação estiver em andamento no momento do reconhecimento, THEN THE Sistema_Escalacao SHALL permitir que a ligação em curso termine, mas não iniciar novas ligações.
5. WHEN um Alarme_Ativo for reconhecido, THE Painel_Configuracao SHALL refletir a mudança de status em tempo real (via polling ou WebSocket).

### Requisito 3: Modos de Chamada (Simultâneo e Sequencial)

**User Story:** Como administrador do sistema, eu quero configurar se as ligações devem ser feitas para todos os números ao mesmo tempo ou um por um, para adaptar o comportamento ao fluxo de trabalho da minha equipe.

#### Critérios de Aceitação

1. WHERE o Modo_Simultaneo estiver configurado, THE Sistema_Escalacao SHALL ligar para todos os números da Cadeia_Escalacao ao mesmo tempo em cada Ciclo_Escalacao.
2. WHERE o Modo_Sequencial estiver configurado, THE Sistema_Escalacao SHALL ligar para o primeiro número da Cadeia_Escalacao e aguardar o tempo de duração da chamada antes de avançar para o próximo número.
3. WHERE o Modo_Sequencial estiver configurado, WHEN todos os números da Cadeia_Escalacao tiverem sido chamados sem reconhecimento, THE Sistema_Escalacao SHALL reiniciar a sequência a partir do primeiro número no próximo Ciclo_Escalacao.
4. THE Painel_Configuracao SHALL permitir alternar entre Modo_Simultaneo e Modo_Sequencial.
5. THE Sistema_Escalacao SHALL aplicar a configuração de modo de chamada vigente no momento do início de cada Ciclo_Escalacao.

### Requisito 4: Configuração de Parâmetros de Escalação

**User Story:** Como administrador do sistema, eu quero configurar o intervalo entre ligações, o número máximo de retentativas e a duração de cada chamada, para ajustar o comportamento de escalação às necessidades do meu datacenter.

#### Critérios de Aceitação

1. THE Painel_Configuracao SHALL permitir configurar o intervalo entre Ciclos_Escalacao em minutos (valor padrão: 5 minutos, mínimo: 1 minuto, máximo: 60 minutos).
2. THE Painel_Configuracao SHALL permitir configurar o número máximo de retentativas (valor padrão: 10, mínimo: 1, máximo: 100).
3. THE Painel_Configuracao SHALL permitir configurar a duração máxima de cada chamada em segundos (valor padrão: 30 segundos, mínimo: 10 segundos, máximo: 120 segundos).
4. THE Painel_Configuracao SHALL salvar as configurações de escalação dentro do campo `notification_config` do Tenant como um objeto `escalation` no JSON.
5. WHEN as configurações de escalação forem salvas, THE Painel_Configuracao SHALL validar que os valores estão dentro dos limites permitidos antes de persistir.
6. IF valores fora dos limites forem submetidos, THEN THE Painel_Configuracao SHALL exibir mensagem de erro indicando o campo e os limites válidos.

### Requisito 5: Gerenciamento da Cadeia de Escalação

**User Story:** Como administrador do sistema, eu quero gerenciar a lista de números de telefone na cadeia de escalação e sua ordem, para controlar quem será chamado e em que sequência.

#### Critérios de Aceitação

1. THE Painel_Configuracao SHALL exibir a lista de números da Cadeia_Escalacao com nome do contato e número de telefone.
2. THE Painel_Configuracao SHALL permitir adicionar, remover e reordenar números na Cadeia_Escalacao.
3. WHEN um número for adicionado à Cadeia_Escalacao, THE Painel_Configuracao SHALL validar o formato do número de telefone (formato E.164 internacional).
4. THE Painel_Configuracao SHALL sincronizar a Cadeia_Escalacao com a lista `to_numbers` existente na configuração Twilio do tenant.
5. WHEN a Cadeia_Escalacao estiver vazia, THE Sistema_Escalacao SHALL registrar um log de erro e não iniciar o loop de ligações.

### Requisito 6: Dashboard de Alarmes Ativos e Status de Escalação

**User Story:** Como analista de NOC, eu quero visualizar todos os alarmes ativos e seu status de escalação em tempo real, para saber quais alarmes estão em escalação, quantas tentativas já foram feitas e quem já foi chamado.

#### Critérios de Aceitação

1. THE Painel_Configuracao SHALL exibir uma seção de "Alarmes Ativos" listando todos os Alarmes_Ativos em escalação.
2. THE Painel_Configuracao SHALL exibir para cada Alarme_Ativo: nome do sensor, tipo de dispositivo, descrição do problema, horário de início, número de tentativas realizadas, próxima tentativa agendada e status atual.
3. WHEN um Alarme_Ativo for reconhecido ou a escalação expirar, THE Painel_Configuracao SHALL mover o alarme para uma seção de "Histórico Recente".
4. THE Painel_Configuracao SHALL atualizar a lista de Alarmes_Ativos a cada 10 segundos via polling.
5. THE Painel_Configuracao SHALL exibir o botão de reconhecimento ao lado de cada Alarme_Ativo, permitindo reconhecimento direto da lista.

### Requisito 7: Controle de Concorrência e Resiliência

**User Story:** Como administrador do sistema, eu quero que o sistema de escalação seja resiliente a falhas e evite ligações duplicadas, para garantir operação confiável mesmo em cenários de falha.

#### Critérios de Aceitação

1. THE Sistema_Escalacao SHALL usar locks distribuídos no Redis para garantir que apenas um Celery_Worker processe a escalação de cada Alarme_Ativo por vez.
2. IF o Redis estiver indisponível, THEN THE Sistema_Escalacao SHALL operar em modo degradado, disparando uma única ligação (comportamento atual) e registrando log de aviso.
3. WHEN o Celery_Worker reiniciar, THE Sistema_Escalacao SHALL recuperar o estado de escalações ativas do Redis e retomar os loops pendentes.
4. THE Sistema_Escalacao SHALL impedir que dois Ciclos_Escalacao do mesmo Alarme_Ativo executem simultaneamente.
5. IF a API do Twilio retornar erro de rate-limit, THEN THE Sistema_Escalacao SHALL aguardar 60 segundos antes da próxima tentativa e registrar o evento no log.

### Requisito 8: Integração com Sistema de Incidentes Existente

**User Story:** Como analista de NOC, eu quero que o sistema de escalação contínua se integre com o fluxo de incidentes existente, para que reconhecimentos e resoluções de incidentes interajam corretamente com a escalação.

#### Critérios de Aceitação

1. WHEN um incidente for resolvido automaticamente (sensor voltou ao normal), THE Sistema_Escalacao SHALL interromper a escalação ativa para aquele sensor.
2. WHEN um incidente for reconhecido via endpoint existente (`POST /incidents/{id}/acknowledge`), THE Sistema_Escalacao SHALL interromper a escalação ativa para aquele sensor.
3. THE Sistema_Escalacao SHALL respeitar o campo `is_acknowledged` do sensor: sensores já reconhecidos não devem iniciar nova escalação.
4. WHEN a escalação for iniciada, THE Sistema_Escalacao SHALL criar uma entrada no histórico do incidente registrando o início da escalação.
5. WHEN a escalação for encerrada (por reconhecimento, resolução ou expiração), THE Sistema_Escalacao SHALL criar uma entrada no histórico do incidente registrando o motivo do encerramento.

### Requisito 9: Serialização e Persistência do Estado de Escalação

**User Story:** Como desenvolvedor, eu quero que o estado de escalação seja serializado de forma consistente entre Redis e a API, para garantir integridade dos dados e facilitar debugging.

#### Critérios de Aceitação

1. THE Sistema_Escalacao SHALL serializar o estado de escalação como JSON no Redis, contendo: sensor_id, incident_id, tentativas_realizadas, max_tentativas, próxima_tentativa, números_chamados, modo, status.
2. THE Sistema_Escalacao SHALL deserializar o estado de escalação do Redis e produzir um objeto equivalente ao original (propriedade round-trip: serializar → deserializar → serializar produz JSON idêntico).
3. THE API SHALL expor um endpoint `GET /api/v1/escalation/active` que retorna a lista de escalações ativas com seus estados atuais.
4. THE API SHALL expor um endpoint `POST /api/v1/escalation/{sensor_id}/acknowledge` que reconhece um alarme e interrompe a escalação.
5. FOR ALL estados de escalação válidos, serializar e depois deserializar SHALL produzir um objeto equivalente ao original (propriedade round-trip).

### Requisito 10: Seleção de Recursos Monitorados para Escalação

**User Story:** Como administrador do sistema, eu quero selecionar quais recursos específicos (servidores, sensores, dispositivos standalone) devem acionar a escalação contínua, para ter controle granular sobre quais ativos disparam o loop de ligações, similar a ferramentas como PRTG, Zabbix e SolarWinds.

#### Critérios de Aceitação

1. THE Painel_Configuracao SHALL exibir uma seção "Recursos Monitorados para Escalação" na página de configuração de escalação, listando todos os recursos atualmente configurados para acionar escalação contínua.
2. THE Painel_Configuracao SHALL permitir adicionar servidores, sensores e dispositivos standalone à lista de recursos monitorados para escalação, através de um seletor com busca por nome ou tipo.
3. THE Painel_Configuracao SHALL exibir para cada recurso configurado: nome do recurso, tipo (servidor, sensor ou dispositivo standalone), status atual e data de inclusão na lista de escalação.
4. THE Painel_Configuracao SHALL permitir remover recursos individuais da lista de escalação monitorada.
5. WHEN um recurso presente na lista de escalação monitorada entrar em estado crítico, THE Sistema_Escalacao SHALL iniciar o loop de ligações contínuas para aquele recurso, seguindo as mesmas regras de escalação dos alarmes de nobreak/gerador e ar-condicionado/HVAC.
6. WHEN um recurso que não está na lista de escalação monitorada entrar em estado crítico, THE Sistema_Escalacao SHALL processar o alerta conforme o fluxo padrão de notificação, sem iniciar escalação contínua.
7. THE Painel_Configuracao SHALL persistir a lista de recursos monitorados dentro do campo `notification_config` do Tenant como um array `escalation_resources` no objeto `escalation` do JSON.
8. WHEN a lista de recursos monitorados for alterada, THE Painel_Configuracao SHALL validar que cada recurso adicionado existe e está ativo no sistema antes de persistir.
9. IF um recurso configurado para escalação for removido do sistema (servidor descomissionado, sensor excluído), THEN THE Sistema_Escalacao SHALL remover automaticamente o recurso da lista de escalação monitorada e registrar o evento no log.
10. THE Painel_Configuracao SHALL manter a compatibilidade com os recursos padrão de escalação (nobreak/gerador e ar-condicionado/HVAC), que continuam acionando escalação contínua independentemente da lista de recursos monitorados.
