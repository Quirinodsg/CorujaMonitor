# 🧪 TESTAR AIOPS AUTOMÁTICO - AGORA!

**Sistema implementado e pronto para testar**

---

## 🎯 O QUE TESTAR

Vamos criar um incidente e ver o AIOps funcionar automaticamente!

---

## ⚡ TESTE RÁPIDO (2 minutos)

### Opção 1: Via Ferramentas de Teste (MAIS FÁCIL)

1. **Acesse:** Menu → Ferramentas de Teste

2. **Simule uma falha:**
   - Escolha: "CPU Alta" ou "Memória Alta"
   - Clique em "Simular Falha"

3. **Aguarde 10 segundos**

4. **Verifique:**
   - Menu → Incidentes
   - Veja o incidente criado
   - Veja a descrição com análise AIOps incluída!

### Opção 2: Via Threshold Manual

1. **Acesse:** Menu → Sensores

2. **Edite um sensor:**
   - Escolha sensor de CPU ou Memória
   - Reduza threshold crítico para 50%
   - Salve

3. **Aguarde 1 minuto**
   - Sistema vai detectar threshold ultrapassado
   - Incidente será criado
   - AIOps executará automaticamente

4. **Verifique:**
   - Menu → Incidentes
   - Veja análise AIOps na descrição

---

## 📧 VERIFICAR NOTIFICAÇÕES

### TOPdesk:
1. Acesse seu TOPdesk
2. Veja o chamado criado
3. Descrição incluirá:
   - 🤖 ANÁLISE AIOPS
   - Causa raiz
   - Sintomas
   - 📋 PLANO DE AÇÃO
   - Ações imediatas com comandos

### Teams:
1. Verifique canal configurado
2. Mensagem incluirá análise completa

### Email:
1. Verifique caixa de entrada
2. Email incluirá análise completa

---

## 🔍 VER LOGS EM TEMPO REAL

### Para ver o AIOps funcionando:

```bash
# Abra PowerShell e execute:
docker logs coruja-worker --tail 50 -f
```

**Você verá:**
```
✅ Incidente criado: CPU - Limite critical ultrapassado (ID: 123)
🤖 Iniciando análise AIOps automática para incidente 123
🔍 Executando análise para CPU em SRV-PROD-01
📊 Executando análise de causa raiz...
✅ RCA concluído: Processo específico consumindo CPU
📋 Criando plano de ação...
✅ Plano de ação criado: AP-123-20260226191500
📧 Enviando notificações com análise AIOps...
✅ TOPdesk: Chamado 12345 criado com AIOps
✅ Teams: Mensagem enviada com AIOps
✅ Email: Enviado com AIOps
📊 Resumo: 3 enviadas, 0 falharam
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

Após criar um incidente, verifique:

- [ ] Incidente criado no sistema
- [ ] Descrição inclui "🤖 ANÁLISE AIOPS"
- [ ] Causa raiz está identificada
- [ ] Confiança está indicada
- [ ] Sintomas estão listados
- [ ] Descrição inclui "📋 PLANO DE AÇÃO"
- [ ] Ações imediatas estão listadas
- [ ] Comandos estão incluídos
- [ ] Notificação TOPdesk recebida (se configurado)
- [ ] Notificação Teams recebida (se configurado)
- [ ] Notificação Email recebida (se configurado)

---

## 📊 EXEMPLO DE RESULTADO ESPERADO

### No Incidente (Menu → Incidentes):

```
Título: CPU - Limite critical ultrapassado

Descrição:
CPU em 95% (Crítico: 85%, Aviso: 75%)

🤖 ANÁLISE AIOPS:
Causa Raiz: Processo específico consumindo CPU excessivamente
Confiança: 88%

Sintomas Detectados: 3

Fatores Contribuintes:
  • Processo descontrolado
  • Possível loop infinito
  • Sem limite de recursos

📋 PLANO DE AÇÃO:
ID: AP-123-20260226191500
Tempo Estimado: 15 minutos

🚨 AÇÕES IMEDIATAS:
1. Identificar processo com alto CPU
   Comando: Get-Process | Sort CPU -Desc | Select -First 10
   Tempo: 1 min

2. Verificar logs do processo
   Comando: Get-EventLog -LogName Application -Newest 50
   Tempo: 2 min
```

---

## 🎯 TESTE COMPLETO (5 minutos)

### 1. Preparação:
```bash
# Abra 2 janelas PowerShell:

# Janela 1: Ver logs
docker logs coruja-worker --tail 50 -f

# Janela 2: Ver logs da API
docker logs coruja-api --tail 50 -f
```

### 2. Criar Incidente:
- Use Ferramentas de Teste
- Ou reduza threshold de um sensor

### 3. Observar:
- Janela 1: Ver AIOps executando
- Janela 2: Ver chamadas da API

### 4. Verificar:
- Menu → Incidentes
- Ver análise completa
- Ver notificações recebidas

### 5. Dashboard AIOps:
- Menu → AIOps → Overview
- Ver atividade recente
- Ver análise listada

---

## ⏱️ TIMELINE ESPERADA

```
t=0s   - Threshold ultrapassado
t=1s   - Incidente criado
t=1s   - AIOps iniciado
t=2s   - RCA executando
t=4s   - RCA concluído
t=4s   - Plano de ação criando
t=5s   - Plano concluído
t=5s   - Notificações enviando
t=6s   - TOPdesk: Chamado criado
t=7s   - Teams: Mensagem enviada
t=8s   - Email: Enviado
t=8s   - ✅ CONCLUÍDO
```

**Tempo total: 8 segundos**

---

## 🐛 TROUBLESHOOTING

### Análise não aparece no incidente?

**Verifique logs:**
```bash
docker logs coruja-worker --tail 100 | grep -i "aiops\|rca\|action"
```

**Possíveis causas:**
- Worker não reiniciou: `docker restart coruja-worker`
- Erro na análise: Ver logs para detalhes
- Dados insuficientes: Sensor precisa de histórico

### Notificações não incluem análise?

**Verifique:**
- Análise foi executada? (ver logs)
- Notificação foi enviada depois da análise? (ver timeline)
- Configuração de notificações está correta?

### Análise demora muito?

**Normal:**
- RCA: 2-4 segundos
- Plano: 1-2 segundos
- Total: 3-6 segundos

**Se demorar mais:**
- Verificar carga do sistema
- Verificar logs para erros
- Verificar conectividade entre containers

---

## 📝 NOTAS

### 1. Primeira Execução
- Pode demorar um pouco mais (5-10 segundos)
- Sistema está "aquecendo"
- Próximas execuções serão mais rápidas

### 2. Dados Insuficientes
- Se sensor não tem histórico suficiente
- RCA pode retornar "Causa raiz desconhecida"
- É normal, não é erro

### 3. Análise Assíncrona
- AIOps executa em background
- Não bloqueia criação do incidente
- Notificação aguarda análise completar

---

## ✅ SUCESSO!

Se você viu:
- ✅ Incidente com análise AIOps
- ✅ Causa raiz identificada
- ✅ Plano de ação criado
- ✅ Notificações com análise

**O sistema está funcionando perfeitamente!** 🎉

---

## 🦉 PRÓXIMOS PASSOS

1. **Use em produção:**
   - Sistema está pronto
   - Análise automática ativa
   - Notificações completas

2. **Monitore:**
   - Ver logs periodicamente
   - Verificar performance
   - Ajustar se necessário

3. **Feedback:**
   - Coletar feedback da equipe
   - Ajustar formato de notificações
   - Melhorar descrições

---

**EXECUTE O TESTE AGORA E VEJA O AIOPS EM AÇÃO!** 🚀
