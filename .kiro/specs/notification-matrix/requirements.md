# Documento de Requisitos — Matriz de Notificação Inteligente

## Introdução

O Coruja Monitor atualmente depende do pipeline AIOps (`execute_aiops_analysis` → `send_incident_notifications_with_aiops`) para despachar notificações. Se o AIOps falhar, **nenhuma notificação é enviada**. Além disso, canais como SMS, WhatsApp e ligação telefônica nunca são disparados automaticamente, e a lógica de despacho não diferencia o tipo de sensor para decidir quais canais acionar.

Este documento especifica uma **Matriz de Notificação Inteligente** que mapeia cada `sensor_type` a um conjunto determinístico de canais de notificação, operando de forma **independente** do AIOps. O AIOps pode enriquecer a notificação, mas jamais bloquear o envio.

## Glossário

- **Dispatcher**: Módulo responsável por resolver a matriz de notificação e despachar para os canais corretos, independente do AIOps.
- **Matriz_de_Notificação**: Tabela de mapeamento `sensor_type → conjunto de canais` que define quais canais devem ser acionados para cada tipo de sensor.
- **Canal**: Meio de envio de notificação (email, teams, sms, whatsapp, ticket, phone_call).
- **Ticket**: Abertura de chamado em sistema externo (TOPdesk, Conecta, GLPI, Dynamics 365).
- **Phone_Call**: Ligação telefônica via Twilio como parte do ciclo de escalação.
- **AIOps_Enrichment**: Dados opcionais de análise de causa raiz e plano de ação gerados pelo pipeline AIOps, anexados à notificação quando disponíveis.
- **Sensor_Type**: Classificação do sensor no banco de dados (ping, disk, service, http, system, network_in, network_out, printer, conflex, engetron, snmp).
- **Priority**: Nível de prioridade do sensor (1-5 estrelas). Sensores PING devem ter priority=5.
- **Metric_Only**: Modo de alerta onde métricas são coletadas mas nenhum incidente ou notificação é gerado.
- **Tenant**: Organização/cliente no sistema multi-tenant, com configuração de notificação própria (`notification_config`).

## Requisitos

### Requisito 1: Despacho Independente do AIOps

**User Story:** Como operador NOC, eu quero que as notificações sejam enviadas mesmo quando o pipeline AIOps estiver indisponível, para que nenhum incidente crítico passe despercebido.

#### Critérios de Aceitação

1. WHEN um incidente é criado, THE Dispatcher SHALL enviar notificações para os canais definidos na Matriz_de_Notificação dentro de 30 segundos, sem aguardar resposta do AIOps.
2. WHEN o pipeline AIOps retorna análise com sucesso, THE Dispatcher SHALL anexar o AIOps_Enrichment à notificação já enviada ou enviar atualização complementar.
3. IF o pipeline AIOps falhar ou não responder em 15 segundos, THEN THE Dispatcher SHALL manter as notificações já enviadas sem alteração e registrar o erro em log.
4. THE Dispatcher SHALL executar o despacho de notificações em processo separado do pipeline AIOps, sem dependência de chamada síncrona.

### Requisito 2: Matriz de Notificação por Sensor Type

**User Story:** Como administrador do sistema, eu quero que cada tipo de sensor tenha canais de notificação pré-definidos, para que a resposta a incidentes seja adequada à criticidade de cada cenário.

#### Critérios de Aceitação

1. WHEN um incidente é criado para um sensor com sensor_type='ping', THE Dispatcher SHALL enviar notificações via email, ticket e teams.
2. WHEN um incidente é criado para um sensor com sensor_type='disk', THE Dispatcher SHALL enviar notificações via email, teams e ticket.
3. WHEN um incidente é criado para um sensor com sensor_type='service', THE Dispatcher SHALL enviar notificações via email e teams.
4. WHEN um incidente é criado para um sensor com sensor_type='http', THE Dispatcher SHALL enviar notificações via email, teams, ticket, sms e whatsapp.
5. WHEN um incidente é criado para um sensor com sensor_type='printer', THE Dispatcher SHALL enviar notificações via email, teams e ticket.
6. WHEN um incidente é criado para um sensor com sensor_type='conflex' ou sensor_type='engetron', THE Dispatcher SHALL enviar notificações via phone_call, email, ticket, teams, sms e whatsapp.
7. WHEN um incidente é criado para um sensor com sensor_type='snmp', THE Dispatcher SHALL enviar notificações via email, teams e sms.
8. THE Dispatcher SHALL resolver os canais de notificação consultando a Matriz_de_Notificação antes de iniciar qualquer envio.


### Requisito 3: Reboot — Notificação Informativa por Email

**User Story:** Como operador NOC, eu quero receber um email informativo quando um servidor reiniciar, para que eu tenha registro do evento sem gerar incidente aberto ou chamado.

#### Critérios de Aceitação

1. WHEN um sensor com sensor_type='system' detecta reboot, THE Dispatcher SHALL enviar apenas email informativo.
2. WHEN um sensor com sensor_type='system' detecta reboot, THE Dispatcher SHALL criar um incidente com status 'resolved' (informativo) e registrar o evento.
3. THE Dispatcher SHALL limitar o envio de email de reboot a no máximo um por hora por sensor, utilizando cooldown.

### Requisito 4: Network IN/OUT — Somente Métrica

**User Story:** Como administrador do sistema, eu quero que sensores de rede (network_in, network_out) coletem métricas sem gerar incidentes ou notificações, para evitar ruído operacional.

#### Critérios de Aceitação

1. THE Dispatcher SHALL tratar sensores com sensor_type='network_in' e sensor_type='network_out' como metric_only, independente da configuração do sensor.
2. WHEN um sensor com sensor_type='network_in' ou sensor_type='network_out' ultrapassa threshold, THE Dispatcher SHALL registrar a métrica sem criar incidente e sem enviar notificação.

### Requisito 5: Prioridade Obrigatória para Sensores PING

**User Story:** Como administrador do sistema, eu quero que todos os sensores PING tenham prioridade máxima (5 estrelas), para garantir que indisponibilidade de servidor sempre acione todos os canais de notificação.

#### Critérios de Aceitação

1. THE Dispatcher SHALL forçar priority=5 para todo sensor com sensor_type='ping', independente do valor configurado no banco de dados.
2. WHEN um sensor com sensor_type='ping' é avaliado, THE Dispatcher SHALL aplicar priority=5 antes de resolver a Matriz_de_Notificação.

### Requisito 6: Infraestrutura Crítica — Escalação com Ligação Telefônica

**User Story:** Como gestor de datacenter, eu quero que falhas em HVAC (Conflex) e Nobreak (Engetron) disparem ligação telefônica automática além de todos os outros canais, para que a equipe seja alertada imediatamente sobre riscos à infraestrutura física.

#### Critérios de Aceitação

1. WHEN um incidente é criado para sensor com sensor_type='conflex' ou sensor_type='engetron', THE Dispatcher SHALL iniciar o ciclo de escalação com phone_call automaticamente.
2. WHEN um incidente é criado para sensor com sensor_type='conflex' ou sensor_type='engetron', THE Dispatcher SHALL enviar simultaneamente email, ticket, teams, sms e whatsapp.
3. IF a ligação telefônica não for atendida, THEN THE Dispatcher SHALL seguir o ciclo de escalação configurado (sequencial ou simultâneo) até max_attempts.

### Requisito 7: Canais SMS e WhatsApp Automáticos

**User Story:** Como operador NOC, eu quero que SMS e WhatsApp sejam enviados automaticamente para os tipos de sensor definidos na matriz, para que a equipe de campo receba alertas mesmo sem acesso ao email ou Teams.

#### Critérios de Aceitação

1. WHEN a Matriz_de_Notificação inclui o canal 'sms' para um sensor_type, THE Dispatcher SHALL enviar SMS via Twilio para os números configurados no Tenant.
2. WHEN a Matriz_de_Notificação inclui o canal 'whatsapp' para um sensor_type, THE Dispatcher SHALL enviar mensagem WhatsApp via Twilio para os números configurados no Tenant.
3. IF o envio de SMS ou WhatsApp falhar, THEN THE Dispatcher SHALL registrar o erro em log e continuar o envio nos demais canais sem interrupção.

### Requisito 8: Email Obrigatório para Todo Incidente

**User Story:** Como operador NOC, eu quero que todo incidente criado gere pelo menos um email de notificação, para que exista sempre um registro formal do evento.

#### Critérios de Aceitação

1. WHEN qualquer incidente é criado (independente do sensor_type), THE Dispatcher SHALL enviar email de notificação para os destinatários configurados no Tenant.
2. IF o envio de email falhar, THEN THE Dispatcher SHALL registrar o erro em log e continuar o envio nos demais canais.

### Requisito 9: Resiliência e Isolamento de Falhas por Canal

**User Story:** Como administrador do sistema, eu quero que a falha de um canal de notificação não impeça o envio pelos demais canais, para garantir máxima confiabilidade.

#### Critérios de Aceitação

1. THE Dispatcher SHALL executar o envio para cada canal de forma isolada, capturando exceções individualmente.
2. IF um canal falhar, THEN THE Dispatcher SHALL registrar o erro com detalhes (canal, erro, incident_id) e prosseguir com os canais restantes.
3. THE Dispatcher SHALL retornar um resumo contendo a lista de canais enviados com sucesso e a lista de canais que falharam.
4. WHEN todos os canais falharem, THE Dispatcher SHALL registrar alerta crítico em log indicando falha total de notificação para o incidente.

### Requisito 10: Resolução Determinística da Matriz

**User Story:** Como desenvolvedor, eu quero que a resolução da matriz de notificação seja uma função pura (sensor_type → canais), para que seja testável com property-based tests e previsível em produção.

#### Critérios de Aceitação

1. THE Dispatcher SHALL implementar a resolução da Matriz_de_Notificação como função pura que recebe sensor_type e retorna o conjunto de canais.
2. FOR ALL sensor_types válidos, a função de resolução SHALL retornar o mesmo conjunto de canais para o mesmo sensor_type (determinismo).
3. FOR ALL sensor_types válidos, a função de resolução SHALL retornar um conjunto não-vazio de canais (completude).
4. FOR ALL sensor_types não mapeados na matriz, a função de resolução SHALL retornar o conjunto padrão contendo pelo menos email (fallback seguro).
5. THE Dispatcher SHALL implementar a Matriz_de_Notificação como estrutura de dados declarativa (dicionário/mapa), separada da lógica de envio.

### Requisito 11: Interface de Configuração da Matriz de Notificação

**User Story:** Como administrador do sistema, eu quero uma página em Configurações onde eu possa visualizar e editar a matriz de notificação (sensor_type × canais) com checkboxes, para que eu possa adicionar ou remover canais por categoria sem alterar código.

#### Critérios de Aceitação

1. THE frontend SHALL exibir uma tabela/grid com linhas representando sensor_types (PING, Disco, Serviço, HTTP, Impressora, Ar-condicionado, Nobreak, Ativos de Rede, Reboot) e colunas representando canais (Email, Teams, Chamado, SMS, WhatsApp, Ligação).
2. EACH célula da tabela SHALL conter um checkbox (toggle) indicando se o canal está ativo para aquele sensor_type.
3. WHEN o administrador marca ou desmarca um checkbox, THE frontend SHALL atualizar o estado local imediatamente (feedback visual).
4. WHEN o administrador clica em "Salvar", THE frontend SHALL enviar a matriz atualizada para a API, que persiste no campo `notification_matrix` do Tenant.
5. THE API SHALL expor endpoints GET e PUT para `/notifications/matrix` que leem e gravam a matriz de notificação do Tenant.
6. THE Dispatcher SHALL ler a matriz de notificação do Tenant ao resolver canais, usando a matriz salva no banco como fonte de verdade (em vez de hardcoded).
7. IF a matriz do Tenant estiver vazia ou ausente, THE Dispatcher SHALL usar a matriz padrão (hardcoded) como fallback.
8. THE frontend SHALL permitir adicionar novas linhas (sensor_types customizados) à matriz via botão "Adicionar Categoria".
9. THE frontend SHALL exibir a página de Matriz de Notificação como uma seção dentro de Configurações > Notificações, acessível apenas para administradores.
