# 📸 Screenshots do Coruja Monitor

Esta pasta contém as capturas de tela do sistema para documentação.

## 🎯 Como Adicionar Screenshots

### Passo 1: Capturar as Telas

Acesse o sistema e capture as seguintes telas:

1. **Dashboard Principal** (`dashboard.png`)
   - URL: http://localhost:3000
   - Login: admin@coruja.com / admin123
   - Capturar: Tela completa do dashboard

2. **NOC em Tempo Real** (`noc.png`)
   - Menu: NOC → Tempo Real
   - Capturar: Dashboard NOC com métricas

3. **Métricas Grafana-Style** (`metrics.png`)
   - Menu: Métricas → Visualização
   - Capturar: Gráficos de métricas

4. **AIOps Dashboard** (`aiops.png`)
   - Menu: AIOps → Dashboard
   - Capturar: Interface AIOps com análises

### Passo 2: Preparar as Imagens

```bash
# Redimensionar para largura máxima de 1200px
# Formato: PNG
# Qualidade: Alta
# Tamanho máximo: 500KB por imagem
```

### Passo 3: Adicionar ao Git

```bash
# Copiar imagens para esta pasta
cp ~/Downloads/dashboard.png docs/screenshots/
cp ~/Downloads/noc.png docs/screenshots/
cp ~/Downloads/metrics.png docs/screenshots/
cp ~/Downloads/aiops.png docs/screenshots/

# Adicionar ao Git
git add docs/screenshots/*.png
git commit -m "docs: Adiciona screenshots do sistema"
git push origin master
```

## 📋 Checklist de Screenshots

- [ ] dashboard.png - Dashboard Principal
- [ ] noc.png - NOC em Tempo Real
- [ ] metrics.png - Métricas Grafana-Style
- [ ] aiops.png - AIOps Dashboard

## 🎨 Dicas para Boas Screenshots

### Preparação
1. Limpe o cache do navegador (Ctrl+Shift+R)
2. Use resolução 1920x1080 ou superior
3. Zoom do navegador em 100%
4. Feche abas desnecessárias
5. Use dados reais (não de teste)

### Captura
1. Use ferramenta de captura (Windows: Win+Shift+S)
2. Capture a área completa da interface
3. Inclua a barra de navegação
4. Evite informações sensíveis

### Edição
1. Redimensione para 1200px de largura
2. Converta para PNG
3. Otimize o tamanho (TinyPNG, ImageOptim)
4. Verifique a qualidade

## 🖼️ Exemplos de Boas Screenshots

### Dashboard Principal
- Mostra todos os cards principais
- Métricas visíveis e legíveis
- Gráficos com dados reais
- Navegação lateral visível

### NOC em Tempo Real
- Contadores de incidentes
- Mapa de calor de servidores
- Alertas recentes
- Status geral do ambiente

### Métricas Grafana-Style
- Gráficos de linha com histórico
- Múltiplas métricas visíveis
- Legendas claras
- Período de tempo visível

### AIOps Dashboard
- Análises da IA visíveis
- Recomendações destacadas
- Base de conhecimento
- Histórico de ações

## 🚫 O Que Evitar

- ❌ Dados sensíveis (IPs reais, nomes de servidores)
- ❌ Informações de clientes
- ❌ Credenciais visíveis
- ❌ Erros ou bugs na tela
- ❌ Interface incompleta ou carregando
- ❌ Resolução muito baixa
- ❌ Imagens borradas ou pixeladas

## 📝 Notas

- As imagens devem estar em formato PNG
- Tamanho máximo recomendado: 500KB por imagem
- Largura recomendada: 1200px
- Altura: Proporcional ao conteúdo
- Qualidade: Alta (sem compressão excessiva)

## 🔄 Atualização

Atualize as screenshots sempre que houver mudanças significativas na interface:

- Nova versão major (1.0 → 2.0)
- Redesign da interface
- Novas funcionalidades importantes
- Correções visuais significativas

---

**Última atualização:** 04 de Março de 2026
