# 📸 CAPTURAR SCREENSHOTS - GUIA RÁPIDO

**⏱️ Tempo: 10 minutos**

---

## 🎯 4 TELAS PARA CAPTURAR

### 1️⃣ Dashboard Principal
```
URL: http://localhost:3000
Arquivo: docs\screenshots\dashboard.png
```

### 2️⃣ NOC em Tempo Real
```
Menu: NOC → Tempo Real
Arquivo: docs\screenshots\noc.png
```

### 3️⃣ Métricas Grafana-Style
```
Menu: Métricas → Visualização
Arquivo: docs\screenshots\metrics.png
```

### 4️⃣ AIOps Dashboard
```
Menu: AIOps → Dashboard
Arquivo: docs\screenshots\aiops.png
```

---

## 🚀 COMO CAPTURAR

### Para Cada Tela:

1. **Navegue** até a página
2. **Pressione** Win + Shift + S
3. **Selecione** a área da interface
4. **Abra** Paint (Win + R → mspaint)
5. **Cole** Ctrl + V
6. **Salve** como PNG
7. **Copie** para docs\screenshots\

---

## ✅ VERIFICAR

```powershell
.\verificar_screenshots.ps1
```

Deve mostrar **[OK]** para todas as 4 imagens.

---

## 📤 ENVIAR PARA GIT

```powershell
git add docs/screenshots/*.png
git commit -m "docs: Adiciona screenshots do sistema ao README"
git push origin master
```

---

## 🌐 VERIFICAR NO GITHUB

```
1. Acesse: https://github.com/Quirinodsg/CorujaMonitor
2. Aguarde 2 minutos (cache)
3. Role até "Showcase"
4. Veja as imagens!
```

---

## 📋 CHECKLIST

- [ ] dashboard.png capturado
- [ ] noc.png capturado
- [ ] metrics.png capturado
- [ ] aiops.png capturado
- [ ] Verificado com script
- [ ] Git add/commit/push
- [ ] Verificado no GitHub

---

## 🆘 AJUDA

**Documentação completa:**
- `ADICIONAR_SCREENSHOTS_GIT.md`
- `STATUS_SCREENSHOTS_04MAR.md`
- `docs/screenshots/README.md`

**Sistema não rodando?**
```powershell
docker-compose up -d
```

---

**⏱️ COMECE AGORA - LEVA APENAS 10 MINUTOS!**

