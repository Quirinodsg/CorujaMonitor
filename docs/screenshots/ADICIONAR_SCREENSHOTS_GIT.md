# 📸 COMO ADICIONAR SCREENSHOTS AO GIT

**Data:** 04 de Março de 2026  
**Status:** ⏳ AGUARDANDO SCREENSHOTS

---

## 🎯 Problema

As imagens dos screenshots não estão carregando no README.md do GitHub porque:

1. A pasta `docs/screenshots/` não contém as imagens
2. As imagens precisam ser capturadas e adicionadas ao Git
3. O README.md já está configurado para exibir as imagens

---

## 📋 Screenshots Necessários

### 1. Dashboard Principal
- **Arquivo:** `docs/screenshots/dashboard.png`
- **URL:** http://localhost:3000
- **O que capturar:** Tela completa do dashboard com cards de métricas

### 2. NOC em Tempo Real
- **Arquivo:** `docs/screenshots/noc.png`
- **URL:** http://localhost:3000 → Menu NOC
- **O que capturar:** Dashboard NOC com contadores e alertas

### 3. Métricas Grafana-Style
- **Arquivo:** `docs/screenshots/metrics.png`
- **URL:** http://localhost:3000 → Menu Métricas
- **O que capturar:** Gráficos de métricas com histórico

### 4. AIOps Dashboard
- **Arquivo:** `docs/screenshots/aiops.png`
- **URL:** http://localhost:3000 → Menu AIOps
- **O que capturar:** Interface AIOps com análises da IA

---

## 🚀 Passo a Passo

### Passo 1: Preparar o Sistema

```powershell
# 1. Certifique-se que o sistema está rodando
docker ps

# 2. Acesse o sistema
# http://localhost:3000

# 3. Faça login
# Usuário: admin@coruja.com
# Senha: admin123

# 4. Limpe o cache do navegador
# Ctrl + Shift + R
```

### Passo 2: Capturar as Telas

#### Windows (Ferramenta Nativa)
```
1. Pressione: Win + Shift + S
2. Selecione "Captura de janela" ou "Captura retangular"
3. Selecione a área da interface
4. A imagem vai para a área de transferência
5. Abra Paint ou outro editor
6. Cole (Ctrl + V)
7. Salve como PNG
```

#### Alternativa: Ferramenta de Terceiros
- **ShareX** (Recomendado): https://getsharex.com/
- **Greenshot**: https://getgreenshot.org/
- **Lightshot**: https://app.prntscr.com/

### Passo 3: Preparar as Imagens

```powershell
# 1. Renomeie os arquivos
dashboard.png
noc.png
metrics.png
aiops.png

# 2. Otimize o tamanho (opcional)
# Use TinyPNG: https://tinypng.com/
# Ou ImageOptim: https://imageoptim.com/

# 3. Verifique as especificações
# - Formato: PNG
# - Largura: ~1200px
# - Tamanho: <500KB por imagem
# - Qualidade: Alta
```

### Passo 4: Adicionar ao Git

```powershell
# 1. Copie as imagens para a pasta correta
copy C:\Users\seu_usuario\Downloads\dashboard.png docs\screenshots\
copy C:\Users\seu_usuario\Downloads\noc.png docs\screenshots\
copy C:\Users\seu_usuario\Downloads\metrics.png docs\screenshots\
copy C:\Users\seu_usuario\Downloads\aiops.png docs\screenshots\

# 2. Verifique se as imagens estão na pasta
dir docs\screenshots\

# 3. Adicione ao Git
git add docs/screenshots/*.png

# 4. Commit
git commit -m "docs: Adiciona screenshots do sistema ao README"

# 5. Push para GitHub
git push origin master
```

### Passo 5: Verificar no GitHub

```
1. Acesse: https://github.com/Quirinodsg/CorujaMonitor
2. Vá até o README.md
3. Role até a seção "Showcase"
4. Verifique se as imagens estão carregando
```

---

## 🎨 Dicas para Boas Screenshots

### Antes de Capturar

✅ **Faça:**
- Limpe o cache do navegador
- Use resolução 1920x1080 ou superior
- Zoom do navegador em 100%
- Feche abas desnecessárias
- Use dados reais (não de teste)
- Certifique-se que a interface está completa

❌ **Evite:**
- Dados sensíveis (IPs reais, nomes de clientes)
- Informações confidenciais
- Credenciais visíveis
- Erros ou bugs na tela
- Interface incompleta ou carregando
- Resolução muito baixa

### Durante a Captura

1. **Dashboard Principal**
   - Mostre todos os cards principais
   - Métricas visíveis e legíveis
   - Gráficos com dados reais
   - Navegação lateral visível

2. **NOC em Tempo Real**
   - Contadores de incidentes
   - Mapa de calor de servidores
   - Alertas recentes
   - Status geral do ambiente

3. **Métricas Grafana-Style**
   - Gráficos de linha com histórico
   - Múltiplas métricas visíveis
   - Legendas claras
   - Período de tempo visível

4. **AIOps Dashboard**
   - Análises da IA visíveis
   - Recomendações destacadas
   - Base de conhecimento
   - Histórico de ações

### Após a Captura

1. **Edição Básica**
   - Redimensione para 1200px de largura
   - Mantenha a proporção
   - Converta para PNG se necessário
   - Otimize o tamanho

2. **Verificação**
   - Abra a imagem e verifique a qualidade
   - Certifique-se que está legível
   - Verifique se não há informações sensíveis
   - Confirme o tamanho do arquivo (<500KB)

---

## 📝 Checklist Final

Antes de fazer o commit, verifique:

- [ ] 4 imagens capturadas (dashboard, noc, metrics, aiops)
- [ ] Todas em formato PNG
- [ ] Tamanho adequado (<500KB cada)
- [ ] Qualidade alta (legível)
- [ ] Sem informações sensíveis
- [ ] Nomes corretos dos arquivos
- [ ] Imagens na pasta `docs/screenshots/`
- [ ] Git add executado
- [ ] Commit realizado
- [ ] Push para GitHub concluído
- [ ] Verificado no GitHub que as imagens carregam

---

## 🔄 Atualização Futura

Atualize as screenshots quando:

- Nova versão major (1.0 → 2.0)
- Redesign da interface
- Novas funcionalidades importantes
- Correções visuais significativas

---

## 🆘 Problemas Comuns

### Imagem não aparece no GitHub

**Causa:** Caminho incorreto no README.md

**Solução:**
```markdown
# Correto
![Dashboard](docs/screenshots/dashboard.png)

# Incorreto
![Dashboard](screenshots/dashboard.png)
![Dashboard](/docs/screenshots/dashboard.png)
```

### Imagem muito grande

**Causa:** Arquivo PNG não otimizado

**Solução:**
1. Use TinyPNG: https://tinypng.com/
2. Ou redimensione para 1200px de largura
3. Ou use formato JPEG com qualidade 85%

### Imagem borrada

**Causa:** Resolução muito baixa ou compressão excessiva

**Solução:**
1. Capture novamente em resolução maior
2. Use PNG ao invés de JPEG
3. Não comprima demais

---

## 📞 Ajuda

Se tiver dúvidas:

1. Veja o arquivo: `docs/screenshots/README.md`
2. Consulte a documentação do Git
3. Entre em contato com o suporte

---

**Status:** ⏳ Aguardando captura e upload das screenshots  
**Próximo passo:** Capturar as 4 telas e adicionar ao Git
