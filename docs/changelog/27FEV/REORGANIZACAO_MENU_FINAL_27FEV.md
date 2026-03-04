# 🔄 Reorganização do Menu - 27 FEV 2026

**Status:** EM IMPLEMENTAÇÃO

---

## 📋 NOVA ESTRUTURA DO MENU LATERAL

### Sidebar (10 itens principais)
1. 📊 Dashboard
2. 🏢 Empresas  
3. 🖥️ Servidores
4. 📡 Sensores
5. ⚠️ Incidentes
6. 📈 Relatórios
7. 🧠 Base de Conhecimento
8. 🤖 Atividades da IA
9. ⚙️ Configurações
10. 🔮 AIOps

---

## 🔘 BOTÕES DENTRO DAS PÁGINAS

### Dashboard (página principal)
**Botões de navegação rápida:**
- 🎯 NOC (já existe)
- 📈 Dashboard Avançado (adicionar)
- 📊 Métricas (Grafana) (adicionar)

### Empresas
**Botão adicional:**
- 🔌 Probes (gerenciar probes da empresa)

### Servidores  
**Botão adicional:**
- 📦 Servidores Agrupados (visualização agrupada)

### Incidentes
**Botões adicionais:**
- 🔧 GMUD (Janelas de Manutenção)
- 🧪 Testes de Sensores

---

## 🎨 CORREÇÃO DE CAMPOS CINZA

O problema dos campos cinza pode ser causado por:
1. CSS conflitante
2. Tema dark mode
3. Estilos inline sobrescrevendo

**Solução:** Verificar e corrigir os estilos CSS globais

---

## 📝 IMPLEMENTAÇÃO

### 1. Sidebar.js
✅ Atualizado com 10 itens principais

### 2. Dashboard.js  
⏳ Adicionar botões:
- Dashboard Avançado
- Métricas (Grafana)

### 3. Companies.js
⏳ Adicionar botão Probes

### 4. Servers.js
⏳ Adicionar botão Servidores Agrupados

### 5. Incidents.js
⏳ Adicionar botões GMUD e Testes

---

## 🔧 PRÓXIMOS PASSOS

1. Adicionar botões no Dashboard
2. Adicionar botão Probes em Empresas
3. Adicionar botão em Servidores
4. Adicionar botões em Incidentes
5. Corrigir estilos CSS (campos cinza)
6. Reiniciar frontend
7. Testar navegação

---

**Criado por:** Kiro AI Assistant  
**Data:** 27/02/2026
