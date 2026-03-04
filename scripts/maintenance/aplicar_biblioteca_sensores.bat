@echo off
echo ========================================
echo   BIBLIOTECA DE SENSORES INDEPENDENTES
echo ========================================
echo.

REM Detectar e ativar ambiente virtual
if exist "venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual: venv
    call venv\Scripts\activate.bat
    goto :install
)

if exist ".venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual: .venv
    call .venv\Scripts\activate.bat
    goto :install
)

if exist "env\Scripts\activate.bat" (
    echo Ativando ambiente virtual: env
    call env\Scripts\activate.bat
    goto :install
)

echo AVISO: Ambiente virtual nao encontrado!
echo Continuando com Python global...
echo.

:install
echo 0. Instalando dependencias Python...
echo.

cd api

REM Instalar todas as dependências
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo AVISO: Erro ao instalar dependencias.
    echo Tentando instalar individualmente...
    echo.
    
    pip install azure-identity
    pip install azure-mgmt-resource
    pip install azure-mgmt-compute
    pip install azure-mgmt-monitor
    pip install pysnmp
    pip install requests
)

echo.
echo OK Dependencias instaladas!
echo.

REM Executar migração
echo 1. Executando migracao do banco de dados...
echo.

python migrate_standalone_sensors.py

if errorlevel 1 (
    echo.
    echo ERRO: Falha na migracao do banco de dados!
    echo Verifique os logs acima.
    echo.
    echo Dicas:
    echo 1. Certifique-se que o ambiente virtual esta ativado
    echo 2. Verifique se as dependencias foram instaladas
    echo 3. Confirme que o banco de dados esta acessivel
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo OK Migracao concluida com sucesso!
echo.

REM Próximos passos
echo ========================================
echo   PROXIMOS PASSOS
echo ========================================
echo.
echo 2. Reinicie os servicos:
echo    - API Backend (FastAPI)
echo    - Frontend (React)
echo.
echo 3. Acesse a nova funcionalidade:
echo    - Faca login no sistema
echo    - Clique em 'Biblioteca de Sensores' no menu lateral
echo    - Clique em '+ Adicionar Sensor'
echo.
echo ========================================
echo   TIPOS DE SENSORES DISPONIVEIS
echo ========================================
echo.
echo SNMP:
echo    - Access Points (WiFi)
echo    - Ar-Condicionado (Temperatura)
echo    - Nobreaks (UPS)
echo    - Impressoras
echo    - Switches
echo    - Roteadores
echo.
echo Microsoft Azure:
echo    - Virtual Machines
echo    - Web Apps
echo    - SQL Database
echo    - Storage Account
echo    - AKS (Kubernetes)
echo    - Functions
echo    - Backup Vault
echo    - E muito mais...
echo.
echo Storage:
echo    - Dell EqualLogic
echo    - NetApp Filer
echo    - EMC VNX
echo    - HP 3PAR
echo    - Synology NAS
echo    - QNAP NAS
echo.
echo Network:
echo    - HTTP/HTTPS
echo    - SSL Certificates
echo    - DNS Query
echo.
echo ========================================
echo   DOCUMENTACAO
echo ========================================
echo.
echo Leia os arquivos:
echo - BIBLIOTECA_SENSORES_IMPLEMENTADA.md
echo - TESTE_CONEXAO_IMPLEMENTADO.md
echo - RESUMO_BIBLIOTECA_SENSORES_COMPLETA.md
echo.
echo OK Configuracao concluida!
echo.
pause
