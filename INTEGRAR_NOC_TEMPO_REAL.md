# 🚀 Como Integrar o NOC em Tempo Real

## Passo 1: Importar o Componente

No arquivo onde você quer adicionar o botão "Modo NOC" (ex: `Dashboard.js` ou `App.js`):

```javascript
import NOCRealTime from './components/NOCRealTime';
```

## Passo 2: Adicionar Estado

```javascript
const [nocMode, setNocMode] = useState(false);
```

## Passo 3: Adicionar Botão

```javascript
<button 
  className="noc-mode-btn"
  onClick={() => setNocMode(true)}
>
  📺 Modo NOC
</button>
```

## Passo 4: Renderizar Condicionalmente

```javascript
{nocMode && (
  <NOCRealTime onExit={() => setNocMode(false)} />
)}
```

## Exemplo Completo

```javascript
import React, { useState } from 'react';
import NOCRealTime from './components/NOCRealTime';

function Dashboard() {
  const [nocMode, setNocMode] = useState(false);

  return (
    <div>
      {/* Seu dashboard normal */}
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <button 
          className="noc-mode-btn"
          onClick={() => setNocMode(true)}
        >
          📺 Modo NOC
        </button>
      </div>

      {/* Conteúdo do dashboard */}
      <div className="dashboard-content">
        {/* ... */}
      </div>

      {/* NOC em tela cheia */}
      {nocMode && (
        <NOCRealTime onExit={() => setNocMode(false)} />
      )}
    </div>
  );
}

export default Dashboard;
```

## CSS para o Botão (Opcional)

```css
.noc-mode-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
}

.noc-mode-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
}
```

## Pronto!

Agora você tem um botão que abre o NOC em tela cheia. O usuário pode:
- Ver todas as 4 views
- Ativar/desativar rotação automática
- Ativar/desativar alertas sonoros
- Sair do modo NOC clicando no ❌

## Testando

1. Acesse o dashboard
2. Clique em "📺 Modo NOC"
3. O NOC abrirá em tela cheia
4. Aguarde 3 segundos para ver a primeira atualização
5. Navegue entre as views ou deixe a rotação automática

## Dicas

- Use em tela grande (TV/Monitor) para melhor visualização
- Ative alertas sonoros em ambientes de NOC
- Deixe a rotação automática ativa para monitoramento passivo
- Use a view "Visão Geral" para executivos
- Use a view "Incidentes" para operadores de NOC
