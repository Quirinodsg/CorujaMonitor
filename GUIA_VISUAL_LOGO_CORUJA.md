# 🦉 Guia Visual - Logo Coruja Monitor

## Onde a Logo Aparece

### 1. 🔐 PÁGINA DE LOGIN
```
┌─────────────────────────────────┐
│                                 │
│         [LOGO 120x120]          │
│                                 │
│      Coruja Monitor             │
│  Plataforma de Monitoramento    │
│                                 │
│  ┌─────────────────────────┐   │
│  │ Email                   │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │ Senha                   │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │       ENTRAR            │   │
│  └─────────────────────────┘   │
│                                 │
└─────────────────────────────────┘
```

**Tamanho**: 120x120 pixels
**Localização**: Centro, acima do título
**Arquivo**: `frontend/src/components/Login.js`

---

### 2. 📊 HEADER DO SISTEMA
```
┌────────────────────────────────────────────────────┐
│ [🦉] André Quirino                    [Sair]      │
│  40px                                              │
└────────────────────────────────────────────────────┘
```

**Tamanho**: 40x40 pixels
**Localização**: Canto superior esquerdo, ao lado do nome
**Arquivo**: `frontend/src/components/MainLayout.js`

---

### 3. 💬 NOTIFICAÇÕES TEAMS
```
┌─────────────────────────────────────────┐
│ 🦉 Teste de Integração - Coruja Monitor│
│                                         │
│ [LOGO]  Teste de Notificação           │
│         25/02/2026 09:40:28            │
│                                         │
│ Este é um teste de integração...       │
│                                         │
│ Tenant: Default                         │
│ Usuário: admin@coruja.com              │
│ Data/Hora: 25/02/2026 09:40:28         │
│ Status: ✅ Integração Ativa            │
│                                         │
│ [Abrir Dashboard]                       │
└─────────────────────────────────────────┘
```

**URL**: https://i.imgur.com/LAr4IAQ.png
**Campo**: `activityImage` no Adaptive Card
**Arquivo**: `api/routers/notifications.py`

---

### 4. 🌐 FAVICON (ABA DO NAVEGADOR)
```
┌──────────────────────────────────┐
│ [🦉] Coruja Monitor - Monit... ▼│
└──────────────────────────────────┘
```

**Tamanho**: 16x16 pixels (auto-redimensionado)
**Localização**: Aba do navegador
**Arquivo**: `frontend/public/index.html`

---

## Especificações Técnicas

### Arquivo da Logo
- **Nome**: `coruja-logo.png`
- **Localização**: `frontend/public/coruja-logo.png`
- **Tamanho**: 273 KB
- **Formato**: PNG com transparência
- **URL Externa**: https://i.imgur.com/LAr4IAQ.png

### Cores do Sistema
- **Primária**: #667eea (Roxo/Azul)
- **Secundária**: #764ba2 (Roxo escuro)
- **Tema**: Gradiente roxo

### Responsividade
```css
/* Login - Grande */
.login-logo {
  width: 120px;
  height: 120px;
  margin-bottom: 20px;
  object-fit: contain;
}

/* Header - Pequena */
.header-logo {
  width: 40px;
  height: 40px;
  object-fit: contain;
}
```

---

## Como Testar

### 1. Teste Visual Completo
```bash
# Acesse o sistema
http://192.168.30.189:3000

# Você deve ver:
✅ Logo grande na tela de login (antes de fazer login)
✅ Logo pequena no header (depois de fazer login)
✅ Ícone da coruja na aba do navegador
```

### 2. Teste de Notificação Teams
```bash
# No sistema:
1. Login: admin@coruja.com / admin123
2. Vá em: Configurações → Notificações
3. Seção: Microsoft Teams
4. Clique: "Testar Integração"

# No Teams:
✅ Mensagem deve chegar com a logo da coruja
✅ Horário deve estar correto (Brasil UTC-3)
```

---

## Comparação: Antes vs Depois

### ANTES ❌
```
Login:
🦉 Coruja Monitor  ← Apenas emoji

Header:
André Quirino  ← Sem logo

Teams:
[SEM IMAGEM]  ← Sem logo
12:40:28  ← Horário errado (UTC)

Favicon:
[GENÉRICO]  ← Ícone padrão React
```

### DEPOIS ✅
```
Login:
[LOGO PROFISSIONAL 120x120]
Coruja Monitor  ← Logo + texto

Header:
[🦉 40x40] André Quirino  ← Logo + nome

Teams:
[LOGO CORUJA]  ← Logo profissional
09:40:28  ← Horário correto (Brasil)

Favicon:
[🦉]  ← Logo da coruja
```

---

## Troubleshooting

### Logo não aparece no navegador
```bash
# Limpar cache do navegador
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)

# Ou abrir em aba anônima
Ctrl + Shift + N
```

### Logo não aparece no Teams
```bash
# Verificar URL da logo
curl https://i.imgur.com/LAr4IAQ.png

# Se Imgur estiver fora, usar cópia local
# Editar: api/routers/notifications.py
"activityImage": "http://192.168.30.189:3000/coruja-logo.png"
```

### Horário ainda errado
```bash
# Verificar se API foi reiniciada
docker restart coruja-api

# Verificar timezone no código
grep "BRAZIL_TZ" api/routers/notifications.py
# Deve retornar: BRAZIL_TZ = timezone(timedelta(hours=-3))
```

---

## Próximas Melhorias (Opcional)

### 1. Logo na Sidebar
```jsx
// frontend/src/components/Sidebar.js
<div className="sidebar-header">
  <img src="/coruja-logo.png" alt="Coruja" />
  <span>Coruja Monitor</span>
</div>
```

### 2. Logo nos Relatórios PDF
```python
# api/routers/reports.py
from reportlab.lib.utils import ImageReader

logo = ImageReader('frontend/public/coruja-logo.png')
canvas.drawImage(logo, x, y, width=100, height=100)
```

### 3. Logo nos Emails HTML
```python
# api/routers/notifications.py
html_body = f"""
<div class="header">
  <img src="https://i.imgur.com/LAr4IAQ.png" width="80" height="80" />
  <h1>Coruja Monitor</h1>
</div>
"""
```

---

## Arquivos Relacionados

```
LOGO_E_TIMEZONE_IMPLEMENTADOS.md  ← Documentação técnica completa
GUIA_VISUAL_LOGO_CORUJA.md        ← Este arquivo (guia visual)
CONFIGURAR_LOGO_CORUJA.md         ← Instruções originais
GUIA_CONFIGURAR_TEAMS.md          ← Configuração Teams

frontend/public/coruja-logo.png   ← Arquivo da logo
frontend/src/components/Login.js  ← Logo na tela de login
frontend/src/components/MainLayout.js ← Logo no header
api/routers/notifications.py      ← Logo no Teams + Timezone
```

---

## Status: ✅ IMPLEMENTADO

**Data**: 25/02/2026
**Versão**: 1.0
**Testado**: ✅ Sim
**Funcionando**: ✅ Sim
