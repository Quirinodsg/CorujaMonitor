# 🔧 CORRIGIR CARDS - GUIA RÁPIDO

## ⚠️ PROBLEMA
Docker Desktop não está rodando!

## ✅ SOLUÇÃO EM 3 PASSOS

### 1️⃣ INICIAR DOCKER DESKTOP
```
- Abra o Docker Desktop (ícone na área de trabalho ou menu iniciar)
- Aguarde o ícone ficar verde na bandeja do sistema
- Tempo estimado: 1-2 minutos
```

### 2️⃣ EXECUTAR SCRIPT
```powershell
.\verificar_e_corrigir_cards.ps1
```
O script fará tudo automaticamente:
- ✓ Verifica Docker
- ✓ Rebuild frontend
- ✓ Reinicia container

### 3️⃣ LIMPAR CACHE DO NAVEGADOR
```
1. Abra: http://localhost:3000
2. Pressione: Ctrl+Shift+R
3. Vá para: Servidores
4. Verifique os cards
```

## 🎯 RESULTADO ESPERADO

**ANTES (problema):**
```
[SISTEMA][DOCKER]
[SERVICOS]
[APLICACOES][REDE]
```

**DEPOIS (correto):**
```
[SISTEMA]  [DOCKER]   [SERVICOS]
[APLICACOES]  [REDE]
```

## 📋 CHECKLIST

- [ ] Docker Desktop iniciado (ícone verde)
- [ ] Script executado sem erros
- [ ] Cache do navegador limpo (Ctrl+Shift+R)
- [ ] Cards alinhados corretamente

## 🆘 SE NÃO FUNCIONAR

Teste em aba anônima:
```
Ctrl+Shift+N → http://localhost:3000
```

---

**Tempo total estimado:** 5 minutos
