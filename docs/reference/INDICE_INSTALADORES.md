# Índice: Instaladores e Guias - Coruja Monitor

## 🚀 INSTALADORES (Escolha Um)

### ⭐ RECOMENDADO - Instalador com Elevação Automática
```
probe/INSTALAR_AQUI.bat
```
- ✅ Força execução como administrador
- ✅ Não fecha a janela
- ✅ Mais fácil de usar
- **Como usar**: Duplo clique

---

### 🎯 Instalador Universal (Menu Interativo)
```
probe/install.bat
```
- ✅ Menu com 5 opções
- ✅ Workgroup, Entra ID, Domínio, WMI Remoto, Auto
- ✅ Detecção automática
- **Como usar**: Execute como Admin

---

### 📦 Instaladores Específicos

#### Entra ID / Azure AD
```
probe/install_entraid.bat
```
- Para máquinas no Entra ID (Azure AD)
- Sua empresa usa este!

#### Workgroup (Sem Domínio)
```
probe/install_workgroup.bat
```
- Para máquinas em workgroup
- Rede local simples

#### Active Directory
```
probe/install_domain.bat
```
- Para máquinas em domínio AD tradicional

#### WMI Remoto
```
probe/install_remote.bat
```
- Apenas configura WMI
- Não instala probe

---

## 📚 GUIAS DE INSTALAÇÃO

### 🎯 Guia Rápido (COMECE AQUI)
```
COMO_INSTALAR_NOVA_PROBE.md
```
- ✅ Passo a passo completo
- ✅ Solução para janela que fecha
- ✅ Troubleshooting
- **Leia este primeiro!**

---

### 📖 Guias Detalhados

#### Instalador Universal
```
GUIA_INSTALADOR_UNIVERSAL.md
```
- Todas as opções do menu
- Quando usar cada uma
- Comparação entre opções

#### Passo a Passo Completo
```
PASSO_A_PASSO_NOVA_EMPRESA.md
```
- Criar empresa na interface web
- Criar probe
- Instalar na máquina
- Verificar no dashboard

#### Guia Rápido de Instalação
```
GUIA_RAPIDO_INSTALACAO.md
```
- Resumo executivo
- IPs corretos (192.168.0.9)
- Checklist

---

### 🔧 Guias Específicos por Ambiente

#### Entra ID / Azure AD
```
GUIA_ENTRA_ID_AZURE_AD.md
```
- Específico para Entra ID
- Sua empresa usa este!
- Microsoft 365 / Azure

#### Workgroup (Sem Domínio)
```
GUIA_MONITORAMENTO_SEM_DOMINIO.md
```
- Máquinas sem domínio
- Rede local simples

#### Active Directory
```
GUIA_INSTALADOR_DOMINIO.md
```
- Domínio AD tradicional
- On-premises

---

## 🆘 TROUBLESHOOTING

### Janela Fechou?
```
INSTALADOR_FECHOU_JANELA.md
```
- ✅ Por que fechou
- ✅ Como resolver
- ✅ Use INSTALAR_AQUI.bat

### Sensores "Desconhecido"?
```
SOLUCAO_SENSORES_DESCONHECIDOS.md
```
- ✅ Probe não está rodando
- ✅ Como iniciar probe
- ✅ Como verificar

---

## 🔄 SCRIPTS AUXILIARES

### Iniciar Probe Local
```
iniciar_probe.bat
```
- Inicia probe na sua máquina (192.168.0.9)
- Use se sensores estão "Desconhecido"

### Reinstalar Servidor
```
reinstalar_servidor_completo.bat
```
- Limpa servidor atual
- Recria sensores padrão
- Use se quiser começar do zero

### Sincronizar Pastas
```
sincronizar_pastas.bat
```
- Sincroniza entre:
  - `C:\Users\user\Coruja Monitor`
  - `C:\Users\user\OneDrive - ...\Coruja Monitor`

---

## 📊 ARQUITETURA E CONCEITOS

### Arquitetura Agentless
```
ARQUITETURA_PRTG_AGENTLESS.md
```
- Como funciona o monitoramento
- Probe coleta, não recebe
- Comparação com PRTG/Zabbix

### Arquitetura de Sensores
```
ARQUITETURA_SENSORES_PROBE.md
```
- Como sensores funcionam
- Coletores
- Fluxo de dados

---

## 📋 ÍNDICES GERAIS

### Índice de Documentação (20/Fev)
```
INDICE_DOCUMENTACAO_20FEV.md
```
- Todas as correções aplicadas
- Dashboard, NOC, Testes
- Sensores, Probes

### Índice de Instaladores (Este Arquivo)
```
INDICE_INSTALADORES.md
```
- Todos os instaladores
- Todos os guias
- Troubleshooting

---

## 🎯 FLUXO RECOMENDADO

### Para Instalar Nova Probe

```
1. Leia: COMO_INSTALAR_NOVA_PROBE.md
   ↓
2. Copie token da interface web (http://192.168.0.9:3000)
   ↓
3. Copie pasta probe para máquina nova
   ↓
4. Execute: probe/INSTALAR_AQUI.bat (duplo clique)
   ↓
5. Configure: IP 192.168.0.9 + Token
   ↓
6. Instale Python e dependências
   ↓
7. Execute: python probe_core.py
   ↓
8. Verifique no dashboard (aguarde 2-3 min)
```

---

## 🔑 INFORMAÇÕES IMPORTANTES

### Sua Configuração
- **IP Servidor**: 192.168.0.9
- **Frontend**: http://192.168.0.9:3000
- **API**: http://192.168.0.9:8000
- **Login**: admin@coruja.com / admin123
- **Ambiente**: Entra ID (Azure AD)

### Token da Probe
- Copie da interface web
- Empresas → + Nova Probe → Copiar token
- Cada probe tem seu próprio token

### Pastas
- **Pasta 1**: `C:\Users\user\Coruja Monitor`
- **Pasta 2**: `C:\Users\user\OneDrive - ...\Coruja Monitor`
- Use `sincronizar_pastas.bat` para manter sincronizadas

---

## ✅ CHECKLIST RÁPIDO

### Antes de Instalar
- [ ] Ler COMO_INSTALAR_NOVA_PROBE.md
- [ ] Copiar token da interface web
- [ ] Copiar pasta probe para máquina nova

### Durante Instalação
- [ ] Usar INSTALAR_AQUI.bat (duplo clique)
- [ ] Escolher opção 2 (Entra ID) ou 5 (Auto)
- [ ] Configurar IP: 192.168.0.9
- [ ] Colar token

### Após Instalação
- [ ] Instalar Python (se necessário)
- [ ] pip install -r requirements.txt
- [ ] python probe_core.py
- [ ] Deixar janela aberta

### Verificação
- [ ] Aguardar 2-3 minutos
- [ ] Verificar no dashboard
- [ ] Sensores coletando

---

## 📞 SUPORTE

### Interface Web
```
http://192.168.0.9:3000
```

### Documentação Completa
```
Todos os arquivos .md na raiz do projeto
```

### Logs
```
probe/logs/           ← Logs da probe
docker logs coruja-api ← Logs da API
```

---

**Use `probe/INSTALAR_AQUI.bat` para instalar novas probes!** 🚀
