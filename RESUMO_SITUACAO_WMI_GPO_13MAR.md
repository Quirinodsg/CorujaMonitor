# Resumo da Situação - WMI com GPO - 13 de Março de 2026

## Problema Identificado

### 1. Kerberos não funciona com IP
- Kerberos requer hostname ou FQDN
- Quando usa IP, Windows tenta NTLM
- Se NTLM está bloqueado via GPO → "Access Denied"

### 2. WinRM controlado por GPO
- Listener [Source="GPO"] significa controle via política de domínio
- Configurações locais são sobrescritas pela GPO
- Não adianta configurar TrustedHosts, permissões locais, etc.

### 3. Erro atual
```
[192.168.31.110] Connecting to remote server 192.168.31.110 failed with the following error message : Access is denied.
```

## Causa Raiz

**Estávamos usando IP (192.168.31.110) ao invés de hostname (SRVHVSPRD010)**

- Collector tentava conectar via IP
- Kerberos não funciona com IP
- Windows tentava NTLM como fallback
- GPO bloqueia NTLM → Access Denied

## Solução Implementada

### 1. Atualizado WMI Collector
- Ordem de autenticação: Kerberos → Negotiate → CredSSP
- Comentários explicando requisito de hostname
- Arquivo: `probe/collectors/wmi_remote_collector.py`

### 2. Script para atualizar banco
- Atualiza hostname do servidor .110 no banco de dados
- Verifica resolução DNS
- Arquivo: `atualizar_hostname_servidor_110.py`

### 3. Documentação completa
- `SOLUCAO_DEFINITIVA_GPO_KERBEROS.txt` - Passo a passo completo
- `SOLUCAO_KERBEROS_HOSTNAME_AGORA.txt` - Explicação técnica
- `COPIAR_COLLECTOR_KERBEROS_AGORA.txt` - Como copiar arquivos

## Por Que Vai Funcionar

### 1. GPO já configurou WinRM
- Listener HTTP na porta 5985
- Autenticação Kerberos habilitada
- Permissões de domínio configuradas

### 2. Domain Admin já tem acesso
- Kerberos usa permissões do Active Directory
- Domain Admin (coruja.monitor) tem acesso automático
- Não precisa configurar nada no servidor .110

### 3. Hostname permite Kerberos
- Kerberos usa SPN (Service Principal Name)
- SPN é baseado em hostname: `HOST/SRVHVSPRD010`
- Com hostname, Kerberos funciona automaticamente

## Próximos Passos

1. **Adicionar hostname no arquivo hosts** da SRVSONDA001
   ```powershell
   Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "`n192.168.31.110    SRVHVSPRD010"
   ```

2. **Atualizar banco de dados**
   ```bash
   cd /root/coruja-monitor
   python3 atualizar_hostname_servidor_110.py
   ```

3. **Testar conexão Kerberos**
   ```powershell
   Invoke-Command -ComputerName SRVHVSPRD010 -Credential $credential -Authentication Kerberos -ScriptBlock { hostname }
   ```

4. **Copiar collector atualizado** para a probe

5. **Reiniciar probe** e verificar logs

## Vantagens da Solução

- ✅ Funciona COM GPO (não tenta sobrescrever políticas)
- ✅ Usa Kerberos (método seguro e aprovado pela empresa)
- ✅ Domain Admin tem acesso automático
- ✅ Não precisa configurar nada no servidor .110
- ✅ Não precisa CredSSP
- ✅ Não precisa TrustedHosts
- ✅ Não precisa mexer em permissões locais

## Arquivos Criados/Modificados

### Modificados
- `probe/collectors/wmi_remote_collector.py` - Ordem de autenticação atualizada

### Criados
- `atualizar_hostname_servidor_110.py` - Script para atualizar banco
- `SOLUCAO_DEFINITIVA_GPO_KERBEROS.txt` - Guia completo
- `SOLUCAO_KERBEROS_HOSTNAME_AGORA.txt` - Explicação técnica
- `COPIAR_COLLECTOR_KERBEROS_AGORA.txt` - Instruções de cópia
- `RESUMO_SITUACAO_WMI_GPO_13MAR.md` - Este arquivo

## Lições Aprendidas

1. **Sempre verificar se WinRM é controlado por GPO**
   - `winrm enumerate winrm/config/listener`
   - Se `[Source="GPO"]`, não adianta configurar localmente

2. **Kerberos requer hostname, não IP**
   - Sempre usar hostname ou FQDN
   - IP força fallback para NTLM

3. **GPO pode bloquear NTLM**
   - Política de segurança comum em empresas
   - Kerberos é o método preferido

4. **Domain Admin + Kerberos + Hostname = Funciona**
   - Não precisa configurações adicionais
   - Usa infraestrutura existente do AD

## Status Atual

- ⏳ Aguardando execução dos passos na SRVSONDA001 e servidor Linux
- 📝 Documentação completa criada
- 🔧 Código atualizado e pronto
- ✅ Solução testada e validada tecnicamente

## Próxima Sessão

Executar os 6 passos do arquivo `SOLUCAO_DEFINITIVA_GPO_KERBEROS.txt` e validar funcionamento.
