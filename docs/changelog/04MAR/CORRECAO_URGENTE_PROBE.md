# 🚨 CORREÇÃO URGENTE - Probe Não Subiu

## O Problema

Você configurou a probe com a URL **errada**:
- ❌ Usou: `http://localhost:3000` (frontend)
- ✅ Deve ser: `http://localhost:8000` (API)

## Solução em 3 Passos

### 1️⃣ Execute o Script de Correção

Abra o CMD como **Administrador** e execute:

```batch
cd C:\Users\user\OneDrive - EmpresaXPTO Ltda\Desktop\probe
corrigir_url.bat
```

### 2️⃣ Cole o Token Novamente

Quando o script pedir, cole o token do probe (o mesmo que você usou antes).

### 3️⃣ Aguarde 1-2 Minutos

O serviço vai reiniciar e começar a enviar dados.

## Como Verificar

1. Abra: http://localhost:3000
2. Vá em **Servidores**
3. Seu computador deve aparecer como **Online**
4. Métricas devem começar a aparecer

## Se Não Funcionar

Execute o diagnóstico:
```batch
cd C:\Users\user\OneDrive - EmpresaXPTO Ltda\Desktop\probe
diagnostico_probe.bat
```

## Explicação Rápida

```
Frontend (3000) ← Você acessa no navegador
     ↑
     │ Busca dados
     │
API (8000) ← Probe envia métricas AQUI
     ↑
     │ Envia métricas
     │
Probe ← Coleta dados do sistema
```

A probe precisa falar com a **API (8000)**, não com o **Frontend (3000)**!

## Arquivos Criados

- `probe/corrigir_url.bat` - Corrige a URL automaticamente
- `probe/diagnostico_probe.bat` - Mostra informações de debug
- `PROBLEMA_URL_PROBE.md` - Documentação completa

## Status

✅ Scripts de correção criados
✅ Pronto para executar
⏳ Aguardando você executar `corrigir_url.bat`
