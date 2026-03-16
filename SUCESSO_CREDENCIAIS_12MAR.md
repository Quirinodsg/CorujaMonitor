# ✅ Sistema de Credenciais - PRONTO PARA DEPLOY

## Situação Atual (12/MAR/2026)

### ✅ Completado no Linux
- Tabela `credentials` criada com sucesso
- 71 linhas da classe `Credential` aninhada removidas
- Migração executada sem erros
- Containers rodando (API, Frontend, PostgreSQL, Redis)

### ✅ Corrigido no Notebook
1. **api/models.py**: Classe `Credential` movida para nível raiz
2. **api/main.py**: Import `credentials` corrigido (removido texto duplicado)
3. **frontend/src/components/Settings.js**: Aba "🔑 Credenciais" adicionada

### 📋 Próximo Passo
Execute **CORRIGIR_SYNTAX_ERROR_AGORA.txt** para:
1. Fazer commit das correções
2. Aplicar no Linux via git pull
3. Rebuild do frontend
4. Testar o sistema

## Como Usar Após Deploy

1. Acesse: http://192.168.31.161:3000
2. Login: admin@coruja.com / admin123
3. Menu: Configurações > Credenciais
4. Adicionar credencial WMI:
   - Nome: "Domínio Principal"
   - Tipo: WMI
   - Nível: Empresa (Tenant)
   - Usuário: administrador
   - Senha: [sua senha]
   - Domínio: (vazio para workgroup)
5. Testar conectividade
6. SRVHVSPRD010 começará a coletar métricas WMI

## Arquivos Modificados
- api/models.py
- api/main.py  
- frontend/src/components/Settings.js
