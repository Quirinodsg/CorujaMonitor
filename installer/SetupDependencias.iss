; ========================================
; SETUP DEPENDENCIAS - INNO SETUP
; Coruja Monitor Probe v1.0.0
; Instala Python 3.11 + Dependências
; ========================================

#define MyAppName "Coruja Monitor - Dependências"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Coruja Monitor"
#define MyAppURL "http://192.168.31.161:3000"
#define MyAppContact "admin@coruja.com"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-123456789ABC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppContact={#MyAppContact}
DefaultDirName={autopf}\CorujaMonitor\Dependencies
DefaultGroupName=Coruja Monitor
DisableProgramGroupPage=yes
; LicenseFile=..\LICENSE.txt
OutputDir=output
OutputBaseFilename=SetupDependencias-v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\python-3.11.8-amd64.exe
; SetupIconFile=..\probe\coruja-icon.ico

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Dirs]
Name: "{app}\Python"
Name: "{app}\Scripts"

[Messages]
brazilianportuguese.WelcomeLabel2=Este assistente instalará o Python 3.11 e todas as dependências necessárias para o Coruja Monitor Probe.%n%nRecomenda-se fechar todos os outros aplicativos antes de continuar.
english.WelcomeLabel2=This will install Python 3.11 and all dependencies required for Coruja Monitor Probe.%n%nIt is recommended that you close all other applications before continuing.

[Files]
; Scripts
Source: "install_dependencies.bat"; DestDir: "{app}\Scripts"; Flags: ignoreversion
Source: "verify_dependencies.bat"; DestDir: "{app}\Scripts"; Flags: ignoreversion

[Icons]
Name: "{group}\Verificar Dependências"; Filename: "{app}\Scripts\verify_dependencies.bat"; WorkingDir: "{app}\Scripts"; Comment: "Verifica se Python e dependências estão instalados"

[Registry]
Root: HKLM; Subkey: "SOFTWARE\CorujaMonitor\Dependencies"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\CorujaMonitor\Dependencies"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"
Root: HKLM; Subkey: "SOFTWARE\CorujaMonitor\Dependencies"; ValueType: string; ValueName: "InstallDate"; ValueData: "{code:GetCurrentDateTime}"

[Run]
; Baixar e instalar Python
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -Command ""[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile '{app}\Python\python-3.11.8-amd64.exe' -UseBasicParsing"""; StatusMsg: "Baixando Python 3.11.8..."; Flags: waituntilterminated runhidden

; Instalar Python silenciosamente
Filename: "{app}\Python\python-3.11.8-amd64.exe"; Parameters: "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1"; StatusMsg: "Instalando Python 3.11.8..."; Flags: waituntilterminated

; Instalar dependências
Filename: "{app}\Scripts\install_dependencies.bat"; StatusMsg: "Instalando dependências Python..."; Flags: waituntilterminated runhidden

[Code]
function GetCurrentDateTime(Param: String): String;
begin
  Result := GetDateTimeString('yyyy/mm/dd hh:nn:ss', #0, #0);
end;

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // Verificar se Python já está instalado
  if RegKeyExists(HKLM, 'SOFTWARE\Python\PythonCore\3.11\InstallPath') then
  begin
    if MsgBox('Python 3.11 já está instalado. Deseja continuar?', mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
      Exit;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Aguardar Python terminar de instalar
    Sleep(5000);
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = wpWelcome then
  begin
    // Verificar se tem internet
    if not CheckForMutexes('Global\PythonInstaller') then
    begin
      MsgBox('Certifique-se de ter conexão com a internet para baixar o Python.', mbInformation, MB_OK);
    end;
  end;
end;
