========================================
CORUJA MONITOR PROBE - INSTALADOR COMPLETO
========================================

Este pacote instala TUDO automaticamente:
✅ Python 3.11 (se necessário)
✅ Dependências Python (psutil, httpx, pywin32, pysnmp, pyyaml)
✅ Arquivos da Probe
✅ Configuração de Firewall (WMI)
✅ Atalhos no Menu Iniciar e Desktop
✅ Registro no Windows


========================================
INSTALAÇÃO
========================================

1. Clique direito em "INSTALAR_TUDO.bat"
2. Selecione "Executar como Administrador"
3. Aguarde a instalação (pode demorar 5-10 minutos)
4. Siga as instruções na tela


========================================
APÓS A INSTALAÇÃO
========================================

1. CONFIGURAR PROBE:
   - Execute: "Configurar Coruja Probe" (atalho no Desktop)
   - Digite IP do servidor: 192.168.31.161
   - Digite o token da probe

2. INSTALAR COMO SERVIÇO (Opcional):
   - Execute: "Instalar Servico Coruja" (Menu Iniciar)
   - Probe iniciará automaticamente com Windows

3. VERIFICAR LOGS:
   - Pasta: C:\Program Files\CorujaMonitor\Probe\logs


========================================
DESINSTALAÇÃO
========================================

1. Clique direito em "DESINSTALAR.bat"
2. Selecione "Executar como Administrador"
3. Confirme a remoção


========================================
REQUISITOS
========================================

✅ Windows 7/Server 2008 R2 ou superior (64-bit)
✅ Privilégios de Administrador
✅ Conexão com Internet (para baixar Python)
✅ ~100 MB de espaço em disco


========================================
ARQUIVOS DO PACOTE
========================================

INSTALAR_TUDO.bat       - Instalador completo (execute este)
DESINSTALAR.bat         - Desinstalador
README.txt              - Este arquivo
INSTRUCOES.txt          - Instruções detalhadas
probe\                  - Arquivos da Probe
  ├── probe_core.py     - Core da probe
  ├── config.py         - Configuração
  ├── collectors\       - Coletores de dados
  ├── *.bat             - Scripts de configuração
  └── *.md              - Documentação


========================================
O QUE É INSTALADO
========================================

PYTHON 3.11:
- Instalado em: C:\Program Files\Python311
- Adicionado ao PATH automaticamente
- Inclui pip (gerenciador de pacotes)

DEPENDÊNCIAS:
- psutil: Monitoramento de sistema (CPU, RAM, Disco)
- httpx: Comunicação HTTP com servidor
- pywin32: Acesso WMI do Windows
- pysnmp: Monitoramento SNMP (switches, APs, UPS, AC)
- pyyaml: Leitura de arquivos de configuração

PROBE:
- Instalada em: C:\Program Files\CorujaMonitor\Probe
- Logs em: C:\Program Files\CorujaMonitor\Probe\logs
- Configuração: config.yaml

ATALHOS:
- Desktop: "Configurar Coruja Probe"
- Menu Iniciar: "Configurar Coruja Probe"
- Menu Iniciar: "Instalar Servico Coruja"

FIREWALL:
- Regra WMI habilitada (para monitoramento remoto)

REGISTRO:
- HKLM\SOFTWARE\CorujaMonitor\Probe
  - InstallPath: caminho de instalação
  - Version: versão instalada
  - InstallDate: data/hora da instalação


========================================
TROUBLESHOOTING
========================================

ERRO: "Execute como Administrador"
SOLUÇÃO: Clique direito no BAT e selecione "Executar como Administrador"

ERRO: "Falha ao baixar Python"
SOLUÇÃO: 
1. Baixe manualmente: https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
2. Coloque na mesma pasta do INSTALAR_TUDO.bat
3. Execute novamente

ERRO: "Python não encontrado" (após instalação)
SOLUÇÃO:
1. Reinicie o prompt de comando
2. Execute: set PATH=%PATH%;C:\Program Files\Python311
3. Teste: python --version

ERRO: "Algumas dependências podem estar faltando"
SOLUÇÃO:
1. Abra CMD como Administrador
2. Execute: python -m pip install psutil httpx pywin32 pysnmp pyyaml
3. Verifique: python -c "import psutil, httpx, win32api, pysnmp, yaml"


========================================
VERIFICAR INSTALAÇÃO
========================================

Abra CMD como Administrador e execute:

# Verificar Python
python --version

# Verificar dependências
python -c "import psutil, httpx, win32api, pysnmp, yaml; print('OK')"

# Verificar arquivos
dir "C:\Program Files\CorujaMonitor\Probe"

# Verificar registro
reg query "HKLM\SOFTWARE\CorujaMonitor\Probe"

# Verificar serviço (se instalado)
sc query CorujaProbe


========================================
SUPORTE
========================================

Interface Web: http://192.168.31.161:3000
Login: admin@coruja.com
Senha: admin123

Documentação: C:\Program Files\CorujaMonitor\Probe\INSTALACAO.md
Logs: C:\Program Files\CorujaMonitor\Probe\logs\


========================================
VERSÃO
========================================

Versão: 1.0.0
Data: 06/03/2026
Python: 3.11.8
Compatibilidade: Windows 7+ (64-bit)


