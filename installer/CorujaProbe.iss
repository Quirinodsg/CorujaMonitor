[Setup]
AppName=Coruja Monitor Probe
AppVersion=1.0.0
AppPublisher=Coruja Monitor
AppPublisherURL=http://192.168.31.161:3000
DefaultDirName={autopf}\CorujaMonitor\Probe
DefaultGroupName=Coruja Monitor
OutputDir=output
OutputBaseFilename=CorujaMonitorProbe-Setup-v1.0.0
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
DisableProgramGroupPage=yes
DisableWelcomePage=no

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[CustomMessages]
brazilianportuguese.PythonInstalling=Instalando Python 3.11 (pode demorar alguns minutos)...
brazilianportuguese.PythonInstalled=Python instalado com sucesso
brazilianportuguese.InstallingDeps=Instalando dependências Python...
brazilianportuguese.ConfiguringFirewall=Configurando firewall...
brazilianportuguese.CreatingShortcuts=Criando atalhos...

[Files]
; Arquivos da Probe
Source: "..\probe\*.py"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
Source: "..\probe\*.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\probe\*.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\probe\collectors\*.py"; DestDir: "{app}\collectors"; Flags: ignoreversion recursesubdirs

[Dirs]
Name: "{app}\logs"; Permissions: users-full
Name: "{app}\collectors"

[Icons]
; Atalho Menu Iniciar
Name: "{group}\Configurar Coruja Probe"; Filename: "{app}\configurar_probe.bat"; WorkingDir: "{app}"; Comment: "Configurar conexão com servidor"
Name: "{group}\Instalar Serviço"; Filename: "{app}\install.bat"; WorkingDir: "{app}"; Comment: "Instalar probe como serviço Windows"
Name: "{group}\Ver Logs"; Filename: "{app}\logs"; Comment: "Abrir pasta de logs"
Name: "{group}\Desinstalar"; Filename: "{uninstallexe}"; Comment: "Desinstalar Coruja Monitor Probe"

; Atalho Desktop
Name: "{autodesktop}\Configurar Coruja Probe"; Filename: "{app}\configurar_probe.bat"; WorkingDir: "{app}"; Comment: "Configurar Coruja Monitor Probe"

[Registry]
; Registrar instalação
Root: HKLM; Subkey: "SOFTWARE\CorujaMonitor\Probe"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\CorujaMonitor\Probe"; ValueType: string; ValueName: "Version"; ValueData: "1.0.0"
Root: HKLM; Subkey: "SOFTWARE\CorujaMonitor\Probe"; ValueType: string; ValueName: "PythonPath"; ValueData: "{code:GetPythonPath}"

[Run]
; Instalar Python se não existir
Filename: "{tmp}\python-installer.exe"; Parameters: "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1"; StatusMsg: "{cm:PythonInstalling}"; Flags: waituntilterminated; Check: NeedsPython

; Instalar dependências Python
Filename: "{code:GetPythonExe}"; Parameters: "-m pip install --quiet --upgrade pip"; StatusMsg: "Atualizando pip..."; Flags: runhidden waituntilterminated; Check: HasPython
Filename: "{code:GetPythonExe}"; Parameters: "-m pip install --quiet psutil httpx pywin32 pysnmp pyyaml"; StatusMsg: "{cm:InstallingDeps}"; Flags: runhidden waituntilterminated; Check: HasPython

; Configurar Firewall
Filename: "{sys}\netsh.exe"; Parameters: "advfirewall firewall set rule group=""Windows Management Instrumentation (WMI)"" new enable=yes"; StatusMsg: "{cm:ConfiguringFirewall}"; Flags: runhidden waituntilterminated

[Code]
var
  PythonPath: String;
  DownloadPage: TDownloadWizardPage;

function NeedsPython: Boolean;
var
  ResultCode: Integer;
begin
  // Verificar se Python está instalado
  Result := not RegQueryStringValue(HKLM, 'SOFTWARE\Python\PythonCore\3.11\InstallPath', '', PythonPath);
  if Result then
    Result := not RegQueryStringValue(HKLM, 'SOFTWARE\Python\PythonCore\3.10\InstallPath', '', PythonPath);
  if Result then
    Result := not RegQueryStringValue(HKLM, 'SOFTWARE\Python\PythonCore\3.9\InstallPath', '', PythonPath);
  if Result then
    Result := not RegQueryStringValue(HKLM, 'SOFTWARE\Python\PythonCore\3.8\InstallPath', '', PythonPath);
  
  // Tentar via comando
  if Result then
  begin
    if Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
      Result := False;
  end;
end;

function HasPython: Boolean;
begin
  Result := not NeedsPython;
end;

function GetPythonPath(Param: String): String;
begin
  if PythonPath <> '' then
    Result := PythonPath
  else
    Result := 'C:\Program Files\Python311';
end;

function GetPythonExe(Param: String): String;
var
  ResultCode: Integer;
begin
  // Tentar python no PATH
  if Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := 'python';
    Exit;
  end;
  
  // Usar caminho registrado
  if PythonPath <> '' then
    Result := AddBackslash(PythonPath) + 'python.exe'
  else
    Result := 'C:\Program Files\Python311\python.exe';
end;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), nil);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  if CurPageID = wpReady then
  begin
    if NeedsPython then
    begin
      DownloadPage.Clear;
      DownloadPage.Add('https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe', 'python-installer.exe', '');
      DownloadPage.Show;
      try
        try
          DownloadPage.Download;
          Result := True;
        except
          if DownloadPage.AbortedByUser then
            Log('Download abortado pelo usuário')
          else
            SuppressibleMsgBox(AddPeriod(GetExceptionMessage), mbCriticalError, MB_OK, IDOK);
          Result := False;
        end;
      finally
        DownloadPage.Hide;
      end;
    end else
      Result := True;
  end else
    Result := True;
end;

[UninstallRun]
; Parar e remover serviço se existir
Filename: "{sys}\sc.exe"; Parameters: "stop CorujaProbe"; Flags: runhidden
Filename: "{sys}\sc.exe"; Parameters: "delete CorujaProbe"; Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\collectors\__pycache__"
