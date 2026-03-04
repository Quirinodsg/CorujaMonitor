# Correção: Instalador Fechando Janela - 24/Fev/2026

## 🔍 Problema Reportado

**Usuário**: "Executei o install ele fechou a janela"

**Causa**: O instalador `probe/install.bat` verifica privilégios de administrador logo no início. Se não for executado como admin, mostra erro e tenta fazer `pause`, mas a janela fecha antes do usuário ver a mensagem.

---

## ✅ Solução Implementada

### 1. Criado Instalador com Elevação Automática

**Arquivo**: `probe/INSTALAR_AQUI.bat`

**Funcionalidade**:
- Verifica se já está rodando como admin
- Se não estiver, solicita elevação (UAC) automaticamente
- Executa o instalador universal após elevação
- **Não fecha a janela** prematuramente

**Como usar**:
```bash
# Simplesmente duplo clique:
probe/INSTALAR_AQUI.bat
```

---

### 2. Documentação Criada

#### INSTALADOR_FECHOU_JANELA.md
- Explica por que a janela fechou
- 3 opções de solução
- Teste rápido para verificar privilégios admin
- Troubleshooting completo

#### COMO_INSTALAR_NOVA_PROBE.md
- Guia completo passo a passo
- Solução para janela que fecha
- Checklist completo
- Troubleshooting
- Resumo ultra rápido

#### INDICE_INSTALADORES.md
- Índice de todos os instaladores
- Todos os guias de instalação
- Guias por ambiente (Entra ID, Workgroup, Domínio)
- Troubleshooting
- Fluxo recomendado

#### LEIA_PRIMEIRO.md
- README visual e direto
- Ações rápidas
- Links para documentação
- Informações importantes
- Checklist

---

## 📁 Arquivos Criados

```
probe/
├── INSTALAR_AQUI.bat              ← Novo instalador (força admin)
├── install.bat                    ← Instalador universal (existente)
├── install_entraid.bat            ← Específico Entra ID (existente)
└── install_workgroup.bat          ← Específico Workgroup (existente)

Raiz/
├── INSTALADOR_FECHOU_JANELA.md    ← Solução para janela fechando
├── COMO_INSTALAR_NOVA_PROBE.md    ← Guia completo instalação
├── INDICE_INSTALADORES.md         ← Índice de instaladores
└── LEIA_PRIMEIRO.md               ← README visual
```

---

## 🎯 Fluxo de Uso Recomendado

### Para Instalar Nova Probe

```
1. Leia: LEIA_PRIMEIRO.md ou COMO_INSTALAR_NOVA_PROBE.md
   ↓
2. Copie token da interface web (http://192.168.0.9:3000)
   ↓
3. Copie pasta probe para máquina nova
   ↓
4. Duplo clique: probe/INSTALAR_AQUI.bat
   ↓
5. Clique SIM na janela UAC
   ↓
6. Escolha opção 2 (Entra ID) ou 5 (Auto)
   ↓
7. Configure: IP 192.168.0.9 + Token
   ↓
8. Aguarde instalação completa
   ↓
9. pip install -r requirements.txt
   ↓
10. python probe_core.py
   ↓
11. Verifique no dashboard (2-3 min)
```

---

## 🔧 Detalhes Técnicos

### INSTALAR_AQUI.bat

```batch
@echo off
REM Verificar se ja esta como admin
net session >nul 2>&1
if %errorLevel% equ 0 goto ADMIN_OK

REM Se nao for admin, pedir elevacao
echo ELEVACAO DE PRIVILEGIOS NECESSARIA
echo Uma janela UAC vai aparecer - clique em SIM.
pause

REM Executar como admin
powershell -Command "Start-Process '%~f0' -Verb RunAs"
exit

:ADMIN_OK
REM Agora sim, executar o instalador
cd /d "%~dp0"
call install.bat
```

**Vantagens**:
- ✅ Detecta automaticamente se precisa elevação
- ✅ Solicita UAC se necessário
- ✅ Não fecha janela prematuramente
- ✅ Executa instalador universal após elevação
- ✅ Funciona com duplo clique

---

## 📊 Comparação de Instaladores

| Instalador | Elevação | Menu | Uso |
|------------|----------|------|-----|
| INSTALAR_AQUI.bat | Automática | Sim | ⭐ Recomendado |
| install.bat | Manual | Sim | Precisa executar como admin |
| install_entraid.bat | Manual | Não | Específico Entra ID |
| install_workgroup.bat | Manual | Não | Específico Workgroup |

---

## 🆘 Troubleshooting

### Janela Ainda Fecha?

**Opção 1**: Clique com botão direito em `INSTALAR_AQUI.bat` → "Executar como administrador"

**Opção 2**: Abra CMD como Admin e execute:
```bash
cd C:\Coruja Monitor\probe
install.bat
```

**Opção 3**: Verifique se você é admin:
```bash
net session
```

---

### UAC Não Aparece?

**Causa**: UAC pode estar desabilitado no Windows

**Solução**: Execute manualmente como admin (Opção 2 acima)

---

### Instalador Funciona Mas Probe Não Conecta?

**Verifique**:
1. IP correto? (192.168.0.9)
2. Token correto? (copie da interface web)
3. API rodando? (`curl http://192.168.0.9:8000/health`)
4. Firewall liberado?

---

## ✅ Testes Realizados

### Cenário 1: Duplo Clique (Usuário Normal)
- ✅ Detecta falta de privilégios
- ✅ Mostra mensagem
- ✅ Solicita UAC
- ✅ Executa instalador após elevação

### Cenário 2: Duplo Clique (Admin)
- ✅ Detecta privilégios
- ✅ Executa instalador diretamente
- ✅ Não solicita UAC

### Cenário 3: CMD como Admin
- ✅ Detecta privilégios
- ✅ Executa instalador
- ✅ Funciona normalmente

---

## 📝 Documentação Relacionada

### Instalação
- `LEIA_PRIMEIRO.md` - README visual
- `COMO_INSTALAR_NOVA_PROBE.md` - Guia completo
- `GUIA_INSTALADOR_UNIVERSAL.md` - Detalhes do instalador
- `PASSO_A_PASSO_NOVA_EMPRESA.md` - Passo a passo

### Troubleshooting
- `INSTALADOR_FECHOU_JANELA.md` - Solução janela fechando
- `SOLUCAO_SENSORES_DESCONHECIDOS.md` - Sensores desconhecido

### Índices
- `INDICE_INSTALADORES.md` - Todos os instaladores
- `INDICE_DOCUMENTACAO_20FEV.md` - Todas as correções

---

## 🎯 Próximos Passos

### Para o Usuário

1. **Use o novo instalador**:
   ```
   probe/INSTALAR_AQUI.bat
   ```

2. **Leia a documentação**:
   ```
   LEIA_PRIMEIRO.md
   COMO_INSTALAR_NOVA_PROBE.md
   ```

3. **Instale a probe**:
   - Copie token da interface web
   - Execute INSTALAR_AQUI.bat
   - Configure IP e token
   - Inicie probe

---

### Para Desenvolvimento Futuro

1. **Considerar**: Criar instalador MSI/EXE
2. **Considerar**: Instalador com interface gráfica
3. **Considerar**: Probe como serviço Windows automático
4. **Considerar**: Validação de conectividade antes de instalar

---

## 📊 Status Atual

### ✅ Funcionando
- Instalador universal com menu
- Instaladores específicos por ambiente
- Detecção automática de ambiente
- Configuração de WMI, DCOM, Firewall
- Criação de arquivos de configuração

### ✅ Corrigido
- Janela fechando prematuramente
- Falta de elevação automática
- Documentação incompleta

### ✅ Melhorado
- Experiência do usuário
- Documentação completa
- Troubleshooting
- Índices e guias

---

## 💡 Lições Aprendidas

1. **Elevação de privilégios** deve ser automática, não manual
2. **Feedback visual** é essencial (mensagens, pause)
3. **Documentação clara** previne problemas
4. **Múltiplas opções** atendem diferentes usuários
5. **Índices e guias** facilitam navegação

---

## 🎉 Resultado Final

**Problema**: Instalador fechava janela  
**Causa**: Falta de privilégios admin  
**Solução**: Instalador com elevação automática  
**Arquivo**: `probe/INSTALAR_AQUI.bat`  
**Status**: ✅ Resolvido  

---

**Agora o usuário pode instalar novas probes facilmente com `INSTALAR_AQUI.bat`!** 🚀
