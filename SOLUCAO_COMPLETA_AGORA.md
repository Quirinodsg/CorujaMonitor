# 🔧 SOLUÇÃO COMPLETA - ERRO NAS PÁGINAS

## 📋 RESUMO DO PROBLEMA

### Problema 1: Páginas com erro 404
- **Causa**: URL duplicada `/api/v1/api/v1/...`
- **Solução**: Corrigido `config.js` para usar apenas `/api/v1`

### Problema 2: Docker build falhou
- **Erro**: `parent snapshot does not exist: not found`
- **Causa**: Cache corrompido do Docker BuildKit
- **Solução**: Limpar cache antes do rebuild

---

## 🚀 PASSO A PASSO

### PASSO 1: Enviar arquivos para o Git (Windows)

1. Abra o **Git Bash**
2. Abra o arquivo: `COMANDOS_GIT_BASH_AGORA.txt`
3. Copie TODOS os comandos
4. Cole no Git Bash
5. Aguarde o push concluir

---

### PASSO 2: Executar no servidor Linux

1. Conecte no servidor Linux via SSH
2. Abra o arquivo: `RESOLVER_ERRO_DOCKER_BUILD.txt`
3. Copie os comandos:

```bash
cd ~/CorujaMonitor
git pull origin master
chmod +x rebuild_frontend_limpo.sh
./rebuild_frontend_limpo.sh
```

4. Cole no terminal Linux
5. Aguarde 3-5 minutos

---

### PASSO 3: Criar tabelas do banco

Após o rebuild do frontend, execute:

```bash
chmod +x corrigir_tabelas_banco.sh
./corrigir_tabelas_banco.sh
```

---

### PASSO 4: Testar o sistema

1. Abra o navegador em **modo anônimo** (Ctrl+Shift+N)
2. Acesse: `http://192.168.31.161:3000`
3. Faça login:
   - Usuário: `admin@coruja.com`
   - Senha: `admin123`
4. Teste as páginas:
   - ✅ Empresas
   - ✅ Incidentes
   - ✅ Relatórios
   - ✅ Base de Conhecimento
   - ✅ Atividades da IA
   - ✅ Configurações

---

## 📁 ARQUIVOS CRIADOS

| Arquivo | Descrição |
|---------|-----------|
| `COMANDOS_GIT_BASH_AGORA.txt` | Comandos para enviar ao Git |
| `RESOLVER_ERRO_DOCKER_BUILD.txt` | Comandos para executar no Linux |
| `rebuild_frontend_limpo.sh` | Script que limpa cache e reconstrói |
| `corrigir_tabelas_banco.sh` | Script que cria tabelas faltantes |
| `diagnostico_erros_paginas.sh` | Script de diagnóstico |

---

## ⏱️ TEMPO ESTIMADO

- Enviar para Git: **1 minuto**
- Rebuild do frontend: **3-5 minutos**
- Criar tabelas: **1 minuto**
- **TOTAL: ~7 minutos**

---

## 🔍 O QUE CADA SCRIPT FAZ

### `rebuild_frontend_limpo.sh`
1. Para o frontend
2. Remove container antigo
3. **Limpa cache do Docker** (resolve o erro)
4. Remove imagens antigas
5. Reconstrói do zero
6. Sobe o frontend
7. Aguarda 30 segundos
8. Testa se está funcionando

### `corrigir_tabelas_banco.sh`
1. Verifica tabelas existentes
2. Cria tabelas faltantes via `models.py`
3. Popula Knowledge Base com dados iniciais
4. Reinicia API
5. Testa endpoints

---

## ❌ SE AINDA DER ERRO

Execute limpeza completa do Docker:

```bash
docker system prune -af --volumes
cd ~/CorujaMonitor
docker-compose up -d
```

⚠️ **ATENÇÃO**: Isso vai parar TODOS os containers!

---

## ✅ VERIFICAÇÃO FINAL

Após executar tudo, verifique:

- [ ] Frontend carrega sem erro
- [ ] Login funciona
- [ ] Página "Empresas" carrega
- [ ] Página "Incidentes" carrega
- [ ] Página "Relatórios" carrega
- [ ] Página "Base de Conhecimento" carrega
- [ ] Página "Atividades da IA" carrega
- [ ] Página "Configurações" carrega

---

## 📞 SUPORTE

Se alguma página ainda der erro:
1. Verifique os logs: `docker-compose logs frontend | tail -50`
2. Verifique os logs da API: `docker-compose logs api | tail -50`
3. Execute o diagnóstico: `./diagnostico_erros_paginas.sh`

---

**Data**: 06/03/2026  
**Status**: Pronto para executar
