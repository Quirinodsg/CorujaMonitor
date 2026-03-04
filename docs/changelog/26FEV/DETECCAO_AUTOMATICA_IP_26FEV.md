# Detecção Automática de IP - 26 FEV 2026

## ✅ PROBLEMA RESOLVIDO

O frontend não atualizava automaticamente quando o IP da máquina mudava. O IP estava hardcoded em vários componentes.

---

## 🔧 SOLUÇÃO IMPLEMENTADA

### Configuração Centralizada com Detecção Automática

Criado arquivo `frontend/src/config.js` que detecta automaticamente o IP do host:

```javascript
const getApiUrl = () => {
  // 1. Se REACT_APP_API_URL está definido, usa ele
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // 2. Detecta automaticamente o IP do host atual
  const hostname = window.location.hostname;
  
  // 3. Se estiver em localhost, usa localhost
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  
  // 4. Caso contrário, usa o IP do host atual na porta 8000
  return `http://${hostname}:8000`;
};

export const API_URL = getApiUrl();
```

---

## 📝 COMO FUNCIONA

### Prioridade de Detecção:

1. **Variável de Ambiente** (mais alta prioridade)
   - Se `REACT_APP_API_URL` está definida, usa ela
   - Útil para ambientes de produção com URL fixa

2. **Localhost**
   - Se acessar via `localhost` ou `127.0.0.1`
   - Usa `http://localhost:8000`

3. **Detecção Automática** (padrão)
   - Detecta o IP/hostname do navegador
   - Usa `http://{IP_DETECTADO}:8000`
   - **Funciona automaticamente quando o IP muda!**

---

## 📂 ARQUIVOS MODIFICADOS

### 1. Criado: `frontend/src/config.js`
Arquivo centralizado de configuração com detecção automática

### 2. Atualizado: `frontend/src/components/KnowledgeBase.js`
```javascript
// ANTES:
const API_URL = process.env.REACT_APP_API_URL || 'http://192.168.30.189:8000';

// DEPOIS:
import { API_URL } from '../config';
```

### 3. Atualizado: `frontend/src/components/ThresholdConfig.js`
```javascript
// ANTES:
const API_URL = process.env.REACT_APP_API_URL || 'http://192.168.30.189:8000';

// DEPOIS:
import { API_URL } from '../config';
```

### 4. Atualizado: `frontend/src/components/AIActivities.js`
```javascript
// ANTES:
const API_URL = process.env.REACT_APP_API_URL || 'http://192.168.30.189:8000';

// DEPOIS:
import { API_URL } from '../config';
```

### 5. Atualizado: `frontend/src/services/api.js`
```javascript
// ANTES:
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

// DEPOIS:
import { API_URL } from '../config';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});
```

---

## 🎯 CENÁRIOS DE USO

### Cenário 1: IP Mudou de 192.168.30.189 para 192.168.0.41
**Antes:** Precisava editar código e reiniciar
**Depois:** Apenas acessar `http://192.168.0.41:3000` - funciona automaticamente!

### Cenário 2: Desenvolvimento Local
**Acesso:** `http://localhost:3000`
**API detectada:** `http://localhost:8000`

### Cenário 3: Acesso via IP na Rede
**Acesso:** `http://192.168.0.41:3000`
**API detectada:** `http://192.168.0.41:8000`

### Cenário 4: Produção com URL Fixa
**Configurar:** `REACT_APP_API_URL=https://api.coruja.com`
**API usada:** `https://api.coruja.com`

---

## 🔍 DEBUG

O sistema exibe logs no console do navegador (apenas em desenvolvimento):

```
🔧 API URL configurada: http://192.168.0.41:8000
🌐 Hostname detectado: 192.168.0.41
```

Para ver os logs:
1. Abra o navegador
2. Pressione F12 (DevTools)
3. Vá na aba Console
4. Veja a URL detectada

---

## ✅ BENEFÍCIOS

1. **Sem Hardcode:** Nenhum IP fixo no código
2. **Automático:** Detecta IP do host automaticamente
3. **Flexível:** Suporta variável de ambiente para produção
4. **Centralizado:** Um único arquivo de configuração
5. **Manutenível:** Fácil de atualizar e debugar

---

## 🚀 TESTE RÁPIDO

### Passo 1: Acesse o frontend
```
http://192.168.0.41:3000
```

### Passo 2: Abra o Console (F12)
Você verá:
```
🔧 API URL configurada: http://192.168.0.41:8000
🌐 Hostname detectado: 192.168.0.41
```

### Passo 3: Teste uma funcionalidade
- Vá em "Base de Conhecimento"
- Vá em "Atividades da IA"
- Vá em "Thresholds Temporais"

Tudo deve funcionar automaticamente!

---

## 📌 IMPORTANTE

### Quando o IP mudar novamente:

1. **NÃO precisa editar código**
2. **NÃO precisa reiniciar containers**
3. **Apenas acesse o novo IP no navegador**

Exemplo:
- IP mudou para `192.168.1.100`
- Acesse: `http://192.168.1.100:3000`
- API será detectada automaticamente: `http://192.168.1.100:8000`

---

## 🔧 CONFIGURAÇÃO AVANÇADA (Opcional)

Se quiser forçar uma URL específica, crie arquivo `.env` no frontend:

```bash
# frontend/.env
REACT_APP_API_URL=http://192.168.0.41:8000
```

Depois reinicie o frontend:
```bash
docker-compose restart frontend
```

---

## 📊 RESUMO

| Item | Antes | Depois |
|------|-------|--------|
| IP Hardcoded | ✅ Sim (192.168.30.189) | ❌ Não |
| Detecção Automática | ❌ Não | ✅ Sim |
| Precisa Editar Código | ✅ Sim | ❌ Não |
| Precisa Reiniciar | ✅ Sim | ❌ Não |
| Arquivos Modificados | 0 | 5 |
| Configuração Centralizada | ❌ Não | ✅ Sim |

---

**Data:** 26 de Fevereiro de 2026
**Status:** ✅ CONCLUÍDO
**Versão:** 1.0
**IP Atual:** 192.168.0.41
