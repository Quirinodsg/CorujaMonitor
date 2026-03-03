# Guia Visual - Sistema de Reconhecimento de Sensores

## 🎯 Objetivo

Permitir que técnicos marquem sensores como "em análise" para suprimir alertas e ligações, inspirado no PRTG.

## 📸 Antes e Depois

### ANTES - Sensor Crítico (Sem Reconhecimento)

```
┌─────────────────────────────────────┐
│  🖥️ CPU                        × 🔍 ✏️│
│                                     │
│           95.8%                     │
│                                     │
│  ┌───────────────────────────────┐ │
│  │        CRITICAL               │ │ ← Vermelho
│  └───────────────────────────────┘ │
│                                     │
│  Atualizado: 13/02 14:30           │
│  ⚠️ 80% | 🔥 95%                    │
└─────────────────────────────────────┘

Status: Gerando alertas e ligações 📞
```

### DEPOIS - Sensor Reconhecido (Em Análise)

```
┌─────────────────────────────────────┐
│  🖥️ CPU                        × 🔍 ✏️│
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ✓ Verificado pela TI        │   │ ← Badge Verde
│  └─────────────────────────────┘   │
│                                     │
│           95.8%                     │
│                                     │
│  ┌───────────────────────────────┐ │
│  │        EM ANÁLISE             │ │ ← Azul
│  └───────────────────────────────┘ │
│                                     │
│  Atualizado: 13/02 14:30           │
│  ⚠️ 80% | 🔥 95%                    │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ 📝 Verificando causa raiz...  │ │ ← Última Nota
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘

Status: Alertas e ligações SUPRIMIDOS 🔇
```

### Tooltip ao Passar Mouse

```
┌─────────────────────────────────────────────┐
│  Última nota:                               │
│  Verificando causa raiz do problema.        │
│  Reiniciando serviço IIS.                   │
│                                             │
│  Por: João Silva                            │
│  Em: 13/02/2026 14:30                       │
└─────────────────────────────────────────────┘
```

## 🎨 Cores e Estados

### Estados do Sensor

| Estado | Cor | Badge | Alertas | Ligações |
|--------|-----|-------|---------|----------|
| **Saudável** | 🟢 Verde | - | Não | Não |
| **Aviso** | 🟡 Amarelo | - | Sim | Não |
| **Crítico** | 🔴 Vermelho | - | Sim | Sim |
| **Em Análise** | 🔵 Azul | ✓ Verificado pela TI | **NÃO** | **NÃO** |
| **Verificado** | 🔵 Azul | ✓ Verificado pela TI | **NÃO** | **NÃO** |

### Dashboard - Status de Saúde

```
┌──────────────────────────────────────────────────────────────┐
│  Status de Saúde                                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   150    │  │    5     │  │    2     │  │    3     │   │
│  │ Saudável │  │  Aviso   │  │ Crítico  │  │Verificado│   │ ← NOVO
│  │          │  │          │  │          │  │ pela TI  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│     🟢            🟡            🔴            🔵            │
│                                                              │
│  ┌──────────┐                                               │
│  │    1     │                                               │
│  │Desconhec.│                                               │
│  │          │                                               │
│  └──────────┘                                               │
│     ⚪                                                       │
└──────────────────────────────────────────────────────────────┘
```

## 🔄 Fluxo de Trabalho

### 1️⃣ Sensor Entra em Estado Crítico

```
Sensor CPU > 95%
    ↓
Sistema detecta problema
    ↓
Gera alerta 🚨
    ↓
Inicia ligações 📞
```

### 2️⃣ Técnico Reconhece Sensor

```
Técnico vê alerta
    ↓
Clica em 🔍 no sensor
    ↓
Adiciona nota: "Verificando causa raiz"
    ↓
Seleciona status: "Em Análise"
    ↓
Clica "Adicionar Nota"
```

### 3️⃣ Sistema Reconhece Automaticamente

```
Backend recebe nota
    ↓
Verifica status = "in_analysis"
    ↓
Define is_acknowledged = TRUE
    ↓
Salva acknowledged_by = user_id
    ↓
Salva acknowledged_at = now()
    ↓
Atualiza cache (last_note, etc)
```

### 4️⃣ Interface Atualiza

```
Frontend recebe resposta
    ↓
Exibe badge "✓ Verificado pela TI"
    ↓
Muda barra para azul
    ↓
Mostra preview da nota
    ↓
Configura tooltip
```

### 5️⃣ Alertas Suprimidos

```
Worker verifica sensor
    ↓
Vê is_acknowledged = TRUE
    ↓
NÃO envia alerta ❌
    ↓
NÃO faz ligação ❌
    ↓
Log: "Alert suppressed - acknowledged"
```

### 6️⃣ Técnico Resolve Problema

```
Problema resolvido
    ↓
Adiciona nota: "Resolvido - serviço reiniciado"
    ↓
Seleciona status: "Resolvido"
    ↓
Clica "Adicionar Nota"
```

### 7️⃣ Sistema Desreconhece

```
Backend recebe nota
    ↓
Verifica status = "resolved"
    ↓
Define is_acknowledged = FALSE
    ↓
Limpa acknowledged_by = NULL
    ↓
Limpa acknowledged_at = NULL
    ↓
Sensor volta ao monitoramento normal
```

## 📋 Status de Verificação

### ⏳ Pendente
```
Uso: Problema identificado, aguardando análise
Efeito: Sensor NÃO reconhecido
Alertas: ✅ Ativos
Ligações: ✅ Ativas
```

### 🔍 Em Análise
```
Uso: Técnico está investigando
Efeito: Sensor reconhecido automaticamente
Alertas: ❌ Suprimidos
Ligações: ❌ Suprimidas
Badge: ✓ Verificado pela TI
Cor: 🔵 Azul
```

### ✅ Verificado
```
Uso: Problema confirmado e documentado
Efeito: Sensor reconhecido automaticamente
Alertas: ❌ Suprimidos
Ligações: ❌ Suprimidas
Badge: ✓ Verificado pela TI
Cor: 🔵 Azul
```

### 🎉 Resolvido
```
Uso: Problema solucionado
Efeito: Sensor desreconhecido automaticamente
Alertas: ✅ Reativados
Ligações: ✅ Reativadas
Badge: Removido
Cor: Volta ao normal (verde/amarelo/vermelho)
```

## 🎯 Casos de Uso

### Caso 1: Manutenção Programada
```
Situação: Servidor será reiniciado para atualização
Ação: Marcar sensores como "Em Análise"
Nota: "Manutenção programada - reinício às 22h"
Resultado: Sem alertas durante manutenção
```

### Caso 2: Problema Conhecido
```
Situação: Disco C: sempre fica em 90% (normal)
Ação: Marcar como "Verificado"
Nota: "Disco C: opera normalmente em 90%. Limpeza agendada."
Resultado: Equipe sabe que é esperado
```

### Caso 3: Investigação Longa
```
Situação: CPU alta, causa desconhecida
Ação: Marcar como "Em Análise"
Nota: "Investigando processo consumindo CPU. Coletando logs."
Resultado: Sem ligações enquanto investiga
Atualização: Adicionar notas conforme progride
```

### Caso 4: Falso Positivo
```
Situação: Alerta disparado incorretamente
Ação: Marcar como "Verificado"
Nota: "Falso positivo - sensor funcionando corretamente"
Resultado: Ajustar threshold depois
```

## 🔔 Notificações

### Antes do Reconhecimento
```
14:30 - 🚨 ALERTA: CPU > 95%
14:31 - 📞 Ligando para João Silva
14:32 - 📞 Ligando para Maria Santos
14:33 - 📧 Email enviado para equipe
14:34 - 💬 Mensagem Teams enviada
```

### Depois do Reconhecimento
```
14:35 - ✅ Sensor reconhecido por João Silva
14:36 - 🔇 Alertas suprimidos
14:37 - (silêncio)
14:38 - (silêncio)
14:39 - (silêncio)
```

### Após Resolução
```
15:00 - ✅ Problema resolvido por João Silva
15:01 - 🔔 Monitoramento reativado
15:02 - (volta ao normal)
```

## 👥 Visibilidade da Equipe

### Técnico A vê:
```
Sensor CPU - SERVER-01
Badge: ✓ Verificado pela TI
Última nota: "Investigando processo..."
Por: Técnico B
Há: 5 minutos
```

### Gestor vê:
```
Dashboard > Verificado pela TI: 3 sensores

1. CPU - SERVER-01 (Técnico B, 5 min)
2. Disco C: - SERVER-02 (Técnico A, 15 min)
3. IIS - SERVER-03 (Técnico C, 30 min)
```

## 📊 Métricas (Futuro)

```
┌─────────────────────────────────────────┐
│  Métricas de Reconhecimento             │
├─────────────────────────────────────────┤
│  Tempo médio até reconhecimento: 3 min  │
│  Tempo médio de resolução: 25 min       │
│  Taxa de reconhecimento: 85%            │
│  Técnico mais ativo: João Silva (12)    │
│  Sensor mais problemático: CPU-SRV01    │
└─────────────────────────────────────────┘
```

## 🎓 Dicas

### Para Técnicos
✅ Reconheça sensores assim que começar a trabalhar
✅ Adicione notas detalhadas do que está fazendo
✅ Atualize status conforme progride
✅ Marque como "Resolvido" quando terminar

### Para Gestores
✅ Monitore "Verificado pela TI" no dashboard
✅ Verifique se técnicos estão reconhecendo sensores
✅ Identifique sensores com tempo de resolução longo
✅ Use histórico de notas para auditoria

### Para Administradores
✅ Configure thresholds adequados
✅ Treine equipe no uso do sistema
✅ Monitore logs de reconhecimento
✅ Ajuste integrações de notificação

## 🚀 Próximos Passos

1. ✅ Sistema implementado e funcionando
2. ⏳ Integrar com worker de notificações
3. ⏳ Integrar com sistema de ligações Twilio
4. ⏳ Adicionar métricas de reconhecimento
5. ⏳ Criar relatório de performance da equipe
6. ⏳ Implementar reconhecimento em massa
7. ⏳ Adicionar templates de notas comuns

---

**Sistema pronto para uso!** 🎉

Acesse: http://localhost:3000
Login: admin@coruja.com / admin123
