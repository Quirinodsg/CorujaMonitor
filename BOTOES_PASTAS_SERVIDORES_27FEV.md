# Botões de Ação nas Pastas de Servidores - 27/02/2026

## ✅ Implementado

Adicionados botões de ação nas pastas de servidores (sistema antigo - `group_name`).

## 🎯 Funcionalidades

### 1. ✏️ Renomear Pasta

**Como usar:**
1. Clique no botão **✏️** ao lado do nome da pasta
2. Digite o novo nome
3. Confirme

**O que acontece:**
- Todos os servidores da pasta são atualizados
- A pasta aparece com o novo nome
- Servidores permanecem associados

### 2. ➕ Criar Subpasta

**Como usar:**
1. Clique no botão **➕** ao lado do nome da pasta
2. Digite o nome da subpasta
3. Confirme

**O que acontece:**
- Cria uma subpasta hierárquica: "Pasta Pai / Subpasta"
- A subpasta aparece automaticamente na lista
- Para adicionar servidores, edite um servidor e defina o grupo como: "Pasta Pai / Subpasta"

**Exemplo:**
```
📁 Empresa Techbiz
  └─ 📁 Empresa Techbiz / Datacenter SP
      └─ 📁 Empresa Techbiz / Datacenter SP / Rack 01
```

### 3. 🗑️ Excluir Pasta

**Como usar:**
1. Clique no botão **🗑️** ao lado do nome da pasta
2. Confirme a exclusão

**O que acontece:**
- A pasta é removida
- Servidores ficam sem pasta (aparecem em "Sem Grupo")
- Servidores NÃO são excluídos

## 🎨 Visual

**Botões na pasta:**
- ✏️ Renomear (cinza)
- ➕ Criar Subpasta (verde)
- 🗑️ Excluir (vermelho)

**Localização:**
- Ao lado direito do nome da pasta
- Aparecem ao passar o mouse
- Não interferem no clique para expandir/colapsar

## 📋 Diferenças entre Sistemas

### Sistema Antigo (Pastas - group_name)
```
📁 Empresa Techbiz (1)
  ├─ DESKTOP-P9VGN04
  └─ [Botões: ✏️ ➕ 🗑️]
```
- Campo `group_name` nos servidores
- Hierarquia via nome: "Pai / Filho"
- Botões: Renomear, Criar Subpasta, Excluir

### Sistema Novo (Grupos Hierárquicos - sensor_groups)
```
⚙️ Gerenciar Grupos (2) ▼
  📁 Produção (5 sensores)
    └─ 🏢 Datacenter SP (3 sensores)
    └─ [Botões: ↔️ 🗑️]
```
- Tabela `sensor_groups` dedicada
- Hierarquia via `parent_id`
- Botões: Mover, Excluir
- Ícones e cores personalizáveis

## 💡 Dicas

### Criar Hierarquia de Pastas
1. Clique em **➕** na pasta pai
2. Digite nome da subpasta
3. Edite um servidor
4. No campo "Grupo / Empresa", digite: "Pasta Pai / Subpasta"
5. Salve

### Mover Servidor entre Pastas
1. Clique em **✏️** no servidor
2. Altere o campo "Grupo / Empresa"
3. Salve

### Organizar Pastas
- Use "/" para criar hierarquia: "Cliente A / Filial SP"
- Renomeie pastas para reorganizar
- Exclua pastas vazias

## 🔧 Implementação Técnica

**Renomear:**
- Atualiza `group_name` de todos os servidores da pasta
- Usa `Promise.all` para atualizar em lote

**Criar Subpasta:**
- Cria nome hierárquico: "Pai / Filho"
- Adiciona à lista de grupos expandidos
- Instrui usuário a editar servidor para associar

**Excluir:**
- Define `group_name = null` em todos os servidores
- Servidores vão para "Sem Grupo"

## ✅ Status

**IMPLEMENTADO E TESTADO** ✅

Frontend reiniciado. Acesse http://localhost:3000 e vá em Servidores para ver os botões nas pastas!

## 📝 Observações

- Botões aparecem ao lado do nome da pasta
- Clique nos botões não expande/colapsa a pasta
- Confirmação antes de excluir
- Mensagens de sucesso/erro
- Atualização automática da lista
