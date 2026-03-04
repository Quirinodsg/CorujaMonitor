# Correções Imediatas - Coruja Monitor

## Data: 19/02/2026

## 1. Busca de Serviços Windows

### Problema
Ao clicar para buscar serviços do Windows, mostra apenas alguns serviços e não carrega a lista completa da máquina.

### Diagnóstico
- Endpoint `/api/v1/probe-commands/services/{server_id}` está implementado
- Usa PowerShell para servidor local
- Fallback para lista comum se falhar

### Solução
Verificar logs da API e melhorar tratamento de erros no frontend.

## 2. Página Empresas - Título Desalinhado

### Problema
O título "Empresas" está no meio da tela ao invés de alinhado como outras páginas.

### Solução
Ajustar CSS para seguir padrão das outras páginas.

## 3. Modo Escuro - Botão Sobrepondo Texto

### Problema
Botão de ativar/desativar modo escuro está em cima do texto.

### Solução
Ajustar posicionamento do toggle no Settings.

## 4. Texto Sobreposto em Configurações

### Problema
Texto "Monitoramento sem agente", "Expansão SNMP", etc. está sobreposto.

### Solução
Revisar layout da página de Configurações.
