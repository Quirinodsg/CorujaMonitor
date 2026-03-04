# Guia de Teste - Sistema "Verificado pela TI"

## ✅ Status: Implementado e Funcionando

## Como Testar o Fluxo Completo

### 1. Acessar o Sistema
```
URL: http://localhost:3000
Login: admin@coruja.com
Senha: admin123
```

### 2. Verificar Sensor Crítico

**Passo a Passo:**
1. Acesse "Servidores" no menu lateral
2. Selecione um servidor com sensores
3. Localize um sensor com status CRÍTICO (vermelho) ou AVISO (amarelo)

**O que você deve ver:**
- Sensor com barra vermelha ou amarela
- Valor acima do threshold
- SEM badge "Verificado pela TI"

### 3. Reconhecer o Sensor (Marcar como "Em Análise")

**Passo a Passo:**
1. No sensor crítico, clique no ícone 🔍 (Ver detalhes)
2. Modal abre com "Detalhes do Sensor"
3. Role até "Notas do Técnico"
4. Preencha:
   - **Status:** Selecione "🔍 Em Análise"
   - **Nota:** Digite algo como "Verificando causa do problema. Servidor sob análise."
5. Clique em "Adicionar Nota"

**O que deve acontecer:**
- Modal fecha automaticamente
- Sensor agora mostra:
  - ✅ Badge verde "✓ Verificado pela TI" no topo
  - 🔵 Barra azul com texto "EM ANÁLISE"
  - 📝 Preview da nota no rodapé
- Sensor SAI da contagem de "Crítico"
- Sensor ENTRA na contagem de "Verificado pela TI"

### 4. Verificar na Página "Todos os Sensores"

**Passo a Passo:**
1. Clique em "Sensores" no menu lateral
2. Veja os cards de resumo no topo

**O que você deve ver:**
- Card "Verificado pela TI" com número > 0
- Card "Crítico" com número reduzido (sensor saiu de lá)
- Sensor reconhecido aparece na lista com:
  - Badge verde "✓ Verificado pela TI"
  - Barra azul "EM ANÁLISE"
  - Preview da nota

**Teste o Filtro:**
1. Clique no card "Verificado pela TI" (azul)
2. Lista mostra APENAS sensores reconhecidos
3. Todos devem ter badge verde e barra azul

### 5. Verificar no Dashboard

**Passo a Passo:**
1. Volte para "Dashboard" no menu
2. Veja a seção "Status de Saúde"

**O que você deve ver:**
- 5 cards agora (antes eram 4):
  - Saudável (verde)
  - Aviso (amarelo)
  - Crítico (vermelho)
  - **Verificado pela TI (azul)** ← NOVO
  - Desconhecido (cinza)
- Número em "Verificado pela TI" > 0
- Número em "Crítico" reduzido

### 6. Resolver o Problema

**Passo a Passo:**
1. Volte para "Servidores"
2. Localize o sensor reconhecido (com badge verde)
3. Clique em 🔍 novamente
4. Adicione nova nota:
   - **Status:** Selecione "🎉 Resolvido"
   - **Nota:** Digite "Problema resolvido. Serviço reiniciado com sucesso."
5. Clique em "Adicionar Nota"

**O que deve acontecer:**
- Badge "Verificado pela TI" DESAPARECE
- Barra volta para cor normal (verde/amarelo/vermelho conforme métrica)
- Sensor SAI da contagem "Verificado pela TI"
- Sensor volta para contagem normal (OK/Aviso/Crítico)
- Alertas e ligações REATIVADOS

## Fluxo Visual Completo

```
┌─────────────────────────────────────────────────────────────┐
│ ESTADO 1: Sensor Crítico (Inicial)                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────┐                     │
│  │  🖥️ CPU                      × 🔍 ✏️│                     │
│  │                                   │                     │
│  │           95.8%                   │                     │
│  │                                   │                     │
│  │  ┌─────────────────────────────┐ │                     │
│  │  │      CRITICAL               │ │ ← Vermelho          │
│  │  └─────────────────────────────┘ │                     │
│  │                                   │                     │
│  │  Atualizado: 13/02 14:30         │                     │
│  │  ⚠️ 80% | 🔥 95%                  │                     │
│  └───────────────────────────────────┘                     │
│                                                             │
│  Dashboard: Crítico = 1                                    │
│  Sensores: Crítico = 1                                     │
│  Alertas: ✅ ATIVOS                                         │
│  Ligações: ✅ ATIVAS                                        │
└─────────────────────────────────────────────────────────────┘

                         ↓
              Técnico adiciona nota
              Status: "Em Análise"
                         ↓

┌─────────────────────────────────────────────────────────────┐
│ ESTADO 2: Sensor Reconhecido (Em Análise)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────┐                     │
│  │  🖥️ CPU                      × 🔍 ✏️│                     │
│  │                                   │                     │
│  │  ┌───────────────────────────┐   │                     │
│  │  │ ✓ Verificado pela TI      │   │ ← Badge Verde       │
│  │  └───────────────────────────┘   │                     │
│  │                                   │                     │
│  │           95.8%                   │                     │
│  │                                   │                     │
│  │  ┌─────────────────────────────┐ │                     │
│  │  │      EM ANÁLISE             │ │ ← Azul              │
│  │  └─────────────────────────────┘ │                     │
│  │                                   │                     │
│  │  Atualizado: 13/02 14:30         │                     │
│  │  ⚠️ 80% | 🔥 95%                  │                     │
│  │                                   │                     │
│  │  ┌─────────────────────────────┐ │                     │
│  │  │ 📝 Verificando causa...     │ │ ← Nota              │
│  │  └─────────────────────────────┘ │                     │
│  └───────────────────────────────────┘                     │
│                                                             │
│  Dashboard: Crítico = 0, Verificado TI = 1                 │
│  Sensores: Crítico = 0, Verificado TI = 1                  │
│  Alertas: ❌ SUPRIMIDOS                                     │
│  Ligações: ❌ SUPRIMIDAS                                    │
└─────────────────────────────────────────────────────────────┘

                         ↓
              Técnico resolve problema
              Status: "Resolvido"
                         ↓

┌─────────────────────────────────────────────────────────────┐
│ ESTADO 3: Sensor Resolvido (Volta ao Normal)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────┐                     │
│  │  🖥️ CPU                      × 🔍 ✏️│                     │
│  │                                   │                     │
│  │           45.2%                   │                     │
│  │                                   │                     │
│  │  ┌─────────────────────────────┐ │                     │
│  │  │      OK                     │ │ ← Verde             │
│  │  └─────────────────────────────┘ │                     │
│  │                                   │                     │
│  │  Atualizado: 13/02 15:00         │                     │
│  │  ⚠️ 80% | 🔥 95%                  │                     │
│  └───────────────────────────────────┘                     │
│                                                             │
│  Dashboard: OK = 1, Verificado TI = 0                      │
│  Sensores: OK = 1, Verificado TI = 0                       │
│  Alertas: ✅ REATIVADOS                                     │
│  Ligações: ✅ REATIVADAS                                    │
└─────────────────────────────────────────────────────────────┘
```

## Verificações Importantes

### ✅ Checklist de Funcionamento

- [ ] Sensor crítico aparece com barra vermelha
- [ ] Ao adicionar nota "Em Análise", badge verde aparece
- [ ] Barra muda para azul com texto "EM ANÁLISE"
- [ ] Preview da nota aparece no rodapé do card
- [ ] Tooltip mostra nota completa ao passar mouse
- [ ] Card "Verificado pela TI" mostra contagem correta
- [ ] Filtro "Verificado pela TI" funciona
- [ ] Dashboard mostra 5 cards (incluindo "Verificado pela TI")
- [ ] Sensor SAI de "Crítico" e VAI para "Verificado pela TI"
- [ ] Ao resolver, badge desaparece
- [ ] Sensor volta para status normal (OK/Aviso/Crítico)

### ❌ Problemas Comuns

**1. Badge não aparece**
- Solução: Limpe cache do navegador (Ctrl+Shift+R)
- Verifique se migração foi executada
- Reinicie frontend: `docker compose restart frontend`

**2. Contagem não atualiza**
- Solução: Aguarde 10 segundos (auto-refresh)
- Ou recarregue a página (F5)

**3. Filtro não funciona**
- Solução: Verifique se `is_acknowledged` está no banco
- Execute: `docker exec -it coruja-postgres psql -U coruja -d coruja -c "SELECT id, name, is_acknowledged FROM sensors LIMIT 5;"`

**4. Sensor continua em "Crítico"**
- Problema: Lógica de contagem não exclui reconhecidos
- Solução: Já corrigido no código - sensores reconhecidos não contam em critical/warning

## Comandos de Verificação

### Ver sensores reconhecidos no banco
```bash
docker exec -it coruja-postgres psql -U coruja -d coruja -c "
SELECT 
  s.id, 
  s.name, 
  s.is_acknowledged, 
  s.last_note,
  u.full_name as acknowledged_by_name
FROM sensors s
LEFT JOIN users u ON s.acknowledged_by = u.id
WHERE s.is_acknowledged = true;
"
```

### Ver logs do frontend
```bash
docker logs coruja-frontend --tail 50
```

### Ver logs da API
```bash
docker logs coruja-api --tail 50
```

### Reiniciar serviços
```bash
docker compose restart frontend api
```

## Comportamento Esperado por Status

| Status da Nota | Badge | Cor Barra | Conta em | Alertas | Ligações |
|----------------|-------|-----------|----------|---------|----------|
| Pendente | ❌ Não | Normal | Critical/Warning/OK | ✅ Sim | ✅ Sim |
| Em Análise | ✅ Sim | 🔵 Azul | Verificado TI | ❌ Não | ❌ Não |
| Verificado | ✅ Sim | 🔵 Azul | Verificado TI | ❌ Não | ❌ Não |
| Resolvido | ❌ Não | Normal | Critical/Warning/OK | ✅ Sim | ✅ Sim |

## Integração com Incidentes

Quando um sensor é reconhecido:
1. Incidentes relacionados devem ser marcados como "acknowledged"
2. Não devem gerar novos incidentes enquanto reconhecido
3. Ao resolver, incidentes podem ser auto-resolvidos

## Próximos Passos

1. ✅ Sistema implementado e funcionando
2. ⏳ Integrar com worker de notificações (suprimir alertas)
3. ⏳ Integrar com sistema de ligações Twilio (suprimir calls)
4. ⏳ Adicionar métricas de tempo de reconhecimento
5. ⏳ Relatório de sensores mais reconhecidos

---

**Teste agora:** http://localhost:3000

Se tiver problemas, verifique:
1. Frontend compilou? `docker logs coruja-frontend`
2. Migração rodou? `docker exec -it coruja-api python migrate_acknowledgement.py`
3. Cache limpo? Ctrl+Shift+R no navegador
