; ========================================
; SETUP PROBE - INNO SETUP
; Coruja Monitor Probe v1.0.0
; Instala arquivos da Probe + Atalhos
; ========================================

#define MyAppName "Coruja Monitor Probe"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Coruja Monitor"
#define MyAppURL "http://192.168.31.161:3000"
#define MyAppContact "admin@coruja.com"

[Setup]
AppId={{E5F6A7B8-C9D0-1234-EFGH-567890123EFG}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppContact={#MyAppContact}
DefaultDirName={autopf}\CorujaMonitor\Probe
DefaultGroupName=Coruja Monitor
DisableProgramGroupPage=yes
; LicenseFile=..\LICENSE.txt
OutputDir=output
OutputBaseFilename=SetupProbe-v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\probe_core.py
; SetupIconFile=..\probe\coruja-icon.ico

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
brazilianportuguese.WelcomeLabel2=Este assistente instalará o agente de monitoramento Coruja Monitor Probe.%n%nCertifique-se de ter instalado o Python e dependências primeiro (SetupDependencias.exe).
english.WelcomeLabel2=This will install the Coruja Monitor Probe monitoring agent.%n%nMake sure you have installed Python and dependencies first (SetupDependencias.exe).

[Dirs]
Name: "{app}\collectors"
Name: "{app}\logs"

[Files]
; Arquivos Python principais
Source: "..\probe\probe_core.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\probe\discovery_server.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\probe\config.yaml"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "..\probe\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

; Scripts BAT
Source: "..\probe\configurar_probe.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\probe\install.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\probe\install_service.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\probe\diagnostico_probe.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\probe\verificar_instalacao.bat"; DestDir: "{app}"; Flags: ignoreversion

; Documentação
Source: "..\probe\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "..\probe\INSTALACAO.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\probe\GUIA_INSTALACAO_SERVICO.md"; DestDir: "{app}"; Flags: ignoreversion

; Coletores
Source: "..\probe\collectors\system_collector.py"; DestDir: "{app}\collectors"; Flags: ignoreversion
Source: "..\probe\collectors\ping_collector.py"; DestDir: "{app}\collectors"; Flags: ignoreversion
Source: "..\probe\collectors\snmp_collector.py"; DestDir: "{app}\collectors"; Flags: ignoreversion
Source: "..\probe\collectors\docker_collector.py"; DestDir: "{app}\collectors"; Flags: ignoreversion
Source: "..\probe\collectors\generic_collector.py"; DestDir: "{app}\collectors"; Flags: ignoreversion
Source: "..\probe\collectors\kubernetes_collector.py"; DestDir: "{app}\collectors"; Flags: ignoreversion
Source: "..\probe\collectors\wmi_remote_collector.py"; DestDir: "{app}\collectors"; Flags: ignoreversion
Source: "..\probe\collectors\snmp_ac_collector.py"; DestDir: "{app}\collectors"; Flags: ignoreversion
Source: "..\probe\collectors\snmp_ap_collector.py"; DestDir: "{app}\collectors"; Flags: ignoreversion

[Icons]
; Desktop
Name: "{autodesktop}\Configurar Coruja Probe"; Filename: "{app}\configurar_probe.bat"; WorkingDir: "{app}"; Comment: "Configurar conexão com servidor Coruja Monitor"

; Menu Iniciar
Name: "{group}\Configurar Coruja Probe"; Filename: "{app}\configurar_probe.bat"; WorkingDir: "{app}"; Comment: "Configurar conexão com servidor"
Name: "{group}\Instalar Serviço Coruja"; Filename: "{app}\install_service.bat"; WorkingDir: "{app}"; Comment: "Instalar Probe como serviço do Windows"
Name: "{group}\Diagnóstico Coruja Probe"; Filename: "{app}\diagnostico_probe.bat"; WorkingDir: "{app}"; Comment: "Executar diagnóstico da Probe"
Name: "{group}\Verificar Instalação"; Filename: "{app}\verificar_instalacao.bat"; WorkingDir: "{app}"; Comment: "Verificar se a Probe está instalada corretamente"

[Registry]
Root: HKLM; Subkey: "SOFTWARE\CorujaMonitor\Probe"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\CorujaMonitor\Probe"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"
Root: HKLM; Subkey: "SOFTWARE\CorujaMonitor\Probe"; ValueType: string; ValueName: "InstallDate"; ValueData: "{code:GetCurrentDateTime}"

[Run]
; Configurar Firewall (WMI)
Filename: "netsh"; Parameters: "advfirewall firewall set rule group=""Windows Management Instrumentation (WMI)"" new enable=yes"; StatusMsg: "Configurando firewall..."; Flags: runhidden

; Oferecer configurar a Probe
Filename: "{app}\configurar_probe.bat"; Description: "Configurar Probe agora"; Flags: postinstall nowait skipifsilent unchecked

[Code]
function GetCurrentDateTime(Param: String): String;
begin
  Result := GetDateTimeString('yyyy/mm/dd hh:nn:ss', #0, #0);
end;

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
  PythonPath: String;
begin
  Result := True;
  
  // Verificar se Python está instalado
  if not RegQueryStringValue(HKLM, 'SOFTWARE\Python\PythonCore\3.11\InstallPath', '', PythonPath) then
  begin
    // Tentar Python no PATH
    if not Exec('cmd.exe', '/c python --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) or (ResultCode <> 0) then
    begin
      if MsgBox('Python não foi encontrado. Instale SetupDependencias.exe primeiro.', mbError, MB_OK) = IDOK then
      begin
        Result := False;
        Exit;
      end;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Verificar dependências
    if not Exec('cmd.exe', '/c python -c "import psutil, httpx, win32api, pysnmp, yaml"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) or (ResultCode <> 0) then
    begin
      MsgBox('Algumas dependências Python estão faltando. Execute SetupDependencias.exe.', mbInformation, MB_OK);
    end;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = wpSelectDir then
  begin
    // Avisar sobre a pasta de instalação
    if Pos('Program Files', WizardDirValue) = 0 then
    begin
      if MsgBox('Recomenda-se instalar em Program Files. Continuar mesmo assim?', mbConfirmation, MB_YESNO) = IDNO then
      begin
        Result := False;
      end;
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Perguntar se quer remover logs
    if MsgBox('Deseja remover os arquivos de log?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{app}\logs'), True, True, True);
    end;
    
    // Perguntar se quer remover configuração
    if MsgBox('Deseja remover o arquivo de configuração?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DeleteFile(ExpandConstant('{app}\config.yaml'));
    end;
  end;
end;
