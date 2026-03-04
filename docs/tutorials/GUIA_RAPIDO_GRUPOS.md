# Guia Rápido - Sistema de Grupos Hierárquicos

## 🎯 Como Usar

### 1️⃣ Criar Grupo Raiz

1. Acesse **Servidores** no menu
2. Na sidebar esquerda, clique em **➕ Criar Grupo**
3. Preencha:
   - Nome (ex: "Produção", "Clientes", "Datacenter SP")
   - Descrição (opcional)
   - Escolha um ícone
   - Escolha uma cor
4. Clique em **Criar Grupo**

### 2️⃣ Criar Subgrupo

1. **Clique no grupo pai** para selecioná-lo (ficará com borda azul)
2. Aparecerá o botão **➕ Criar Subgrupo**
3. Clique nele
4. Preencha os dados
5. O subgrupo será criado dentro do grupo selecionado

### 3️⃣ Mover Grupo

1. Clique no botão **↔️** ao lado do grupo que deseja mover
2. Selecione o novo pai (ou deixe em branco para mover para raiz)
3. Clique em **Mover Grupo**

### 4️⃣ Excluir Grupo

1. Clique no botão **🗑️** ao lado do grupo
2. Confirme a exclusão
3. Os sensores do grupo ficarão sem grupo
4. Os subgrupos serão movidos para o pai do grupo excluído

### 5️⃣ Desselecionar Grupo

- Clique no botão **✕ Desselecionar** que aparece quando um grupo está selecionado

## 📋 Indicadores Visuais

- **Borda azul** = Grupo selecionado
- **Fundo cinza** = Grupo expandido
- **Número entre parênteses** = Quantidade de sensores no grupo
- **Indentação** = Nível na hierarquia

## 💡 Dicas

- Você pode criar quantos níveis quiser (hierarquia ilimitada)
- Cada grupo mostra quantos sensores possui
- Clique no grupo para expandir/colapsar seus subgrupos
- Use ícones e cores para organizar visualmente

## 🎨 Ícones Disponíveis

- 📁 Pasta
- 🏢 Empresa
- 🏭 Fábrica
- 🏪 Loja
- 🏥 Hospital
- 🏫 Escola
- 🌐 Rede
- ☁️ Nuvem
- 🖥️ Servidores
- 📊 Monitoramento

## ✅ Exemplo de Estrutura

```
📁 Produção (Raiz)
  └─ 🏢 Datacenter SP (Nível 1)
      ├─ 🖥️ Rack 01 (Nível 2)
      └─ 🖥️ Rack 02 (Nível 2)

🏪 Clientes (Raiz)
  ├─ 🏢 Cliente A (Nível 1)
  └─ 🏢 Cliente B (Nível 1)
```

## 🔧 Solução de Problemas

**Não consigo criar subgrupo:**
- Certifique-se de que clicou no grupo pai para selecioná-lo
- O grupo selecionado deve ter borda azul
- O botão "Criar Subgrupo" só aparece quando há um grupo selecionado

**Não vejo os botões de ação:**
- Os botões ↔️ e 🗑️ aparecem ao lado de cada grupo na árvore
- Passe o mouse sobre o grupo para ver melhor

**Grupo não aparece:**
- Recarregue a página (F5)
- Verifique se o grupo foi criado com sucesso (mensagem de confirmação)
