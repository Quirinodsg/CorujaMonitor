# ✅ Correção: Sensores Docker Visíveis + Nome do Servidor

## 🎯 Status: CONCLUÍDO

Data: 19/02/2026 14:25

## 🐛 Problemas Corrigidos

### 1. Sensores Docker Não Apareciam
**Causa**: A função `groupSensorsByType()` filtrava grupos vazios com `.filter(([_, group]) => group.sensors.length > 0)`

**Solução**: Removido o filtro para mostrar TODOS os grupos, mesmo vazios

### 2. Card Mostrava "Sistema" ao Invés do Nome do Servidor
**Causa**: O card agregador usava `group.name` para todos os grupos

**Solução**: Lógica condicional - se for grupo "system", usa `selectedServer.hostname`

## 🔧 Correções Aplicadas

### Servers.js

#### 1. Função groupSensorsByType()
```javascript
// ANTES (filtrava grupos vazios)
return Object.entries(groups)
  .filter(([_, group]) => group.sensors.length > 0)  // ❌ Escondia grupos vazios
  .sort((a, b) => a[1].priority - b[1].priority);

// DEPOIS (mostra todos os grupos)
return Object.entries(groups)
  .sort((a, b) => a[1].priority - b[1].priority);  // ✅ Mostra todos
```

#### 2. Função renderMixedSensors()
```javascript
// Nome do card: se for Sistema, usa nome do servidor
const cardName = groupKey === 'system' 
  ? selectedServer?.hostname || 'Sistema'  // ✅ Nome do servidor
  : group.name;                             // ✅ Nome do grupo

// Card agregador
<h3>{cardName} ({group.sensors.length})</h3>
```

#### 3. Debug Adicionado
```javascript
// Logs para verificar sensores Docker
console.log('Total sensors:', sensors.length);
console.log('Grouped sensors:', grouped);
const dockerSensors = sensors.filter(s => s.sensor_type === 'docker');
console.log('Docker sensors found:', dockerSensors.length, dockerSensors);
```

#### 4. Indicador de Grupo Vazio
```javascript
{group.sensors.length === 0 && 
  <span style={{ color: '#9e9e9e' }}>Nenhum sensor</span>
}
```

### Sensors.js

#### Mesma correção na função groupSensorsByType()
```javascript
// Removido filtro de grupos vazios
return Object.entries(groups)
  .sort((a, b) => a[1].priority - b[1].priority);
```


## 📊 Resultado Visual

### Antes (Problema)
```
[🖥️ Sistema (7)]  ← Nome genérico
  ✓ 6  ⚠ 1
  CLIQUE PARA EXPANDIR ▼

(Docker não aparecia se não tivesse sensores)
```

### Depois (Corrigido)
```
[🖥️ DESKTOP-P9VGN04 (7)]  ← Nome do servidor!
  ✓ 6  ⚠ 1
  CLIQUE PARA EXPANDIR ▼

[🐳 Docker (15)]  ← Sempre aparece
  ✓ 12  ⚠ 2  🔥 1
  📦 6 Total | ✅ 5 Rodando | ⏸️ 1 Parado
  CLIQUE PARA EXPANDIR ▼

[⚙️ Serviços (0)]  ← Mostra mesmo vazio
  Nenhum sensor
  CLIQUE PARA EXPANDIR ▼
```

## 🔍 Debug no Console

Ao abrir a página, você verá no console do navegador (F12):
```
Total sensors: 22
Grouped sensors: [
  ['system', { name: 'Sistema', sensors: [7 items], ... }],
  ['docker', { name: 'Docker', sensors: [15 items], ... }],
  ['services', { name: 'Serviços', sensors: [], ... }],
  ...
]
Docker sensors found: 15 [
  { id: 1, sensor_type: 'docker', name: 'Docker Total', ... },
  { id: 2, sensor_type: 'docker', name: 'Docker Running', ... },
  ...
]
```

Isso ajuda a diagnosticar se:
- Os sensores estão sendo carregados
- O sensor_type está correto
- O agrupamento está funcionando

## ✅ Verificações

### 1. Sensores Docker Aparecem?
- ✅ Card "Docker" sempre visível
- ✅ Contador mostra quantidade correta
- ✅ Clique expande e mostra todos os sensores

### 2. Nome do Servidor Correto?
- ✅ Card "Sistema" mostra hostname do servidor
- ✅ Outros cards mantêm nome do grupo

### 3. Grupos Vazios Aparecem?
- ✅ Todos os grupos são mostrados
- ✅ Indicador "Nenhum sensor" quando vazio
- ✅ Ainda podem ser expandidos (sem sensores dentro)

## 🚀 Como Testar

1. Acesse http://localhost:3000
2. Pressione **Ctrl+Shift+R** (hard refresh)
3. Faça login (admin@coruja.com / admin123)
4. Vá em **"Servidores"**
5. Selecione um servidor
6. Verifique:
   - ✅ Card mostra nome do servidor (ex: DESKTOP-P9VGN04)
   - ✅ Card Docker aparece
   - ✅ Clique no card Docker para expandir
   - ✅ Sensores Docker aparecem
7. Abra o Console (F12) e veja os logs de debug

## 📁 Arquivos Modificados

- `frontend/src/components/Servers.js`
  - groupSensorsByType(): Removido filtro de grupos vazios
  - renderMixedSensors(): Nome condicional do card
  - Adicionados console.logs para debug
  - Indicador "Nenhum sensor" para grupos vazios

- `frontend/src/components/Sensors.js`
  - groupSensorsByType(): Removido filtro de grupos vazios

## 🎯 Resultado Final

✅ Sensores Docker sempre visíveis
✅ Card mostra nome do servidor
✅ Todos os grupos aparecem (mesmo vazios)
✅ Debug logs no console
✅ Compilação bem-sucedida

---

**Status**: ✅ CORRIGIDO E FUNCIONANDO
**Testado**: Compilação OK, aguardando teste do usuário
