[Setup]
AppName=Coruja Monitor Probe
AppVersion=1.0.0
AppPublisher=Coruja Monitor
AppPublisherURL=http://192.168.31.161:3000
DefaultDirName={autopf}\CorujaMonitor\Probe
DefaultGroupName=Coruja Monitor
OutputDir=output
OutputBaseFilename=CorujaMonitorProbe-Simples-v1.0.0
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
DisableProgramGroupPage=yes
DisableWelcomePage=no

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

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

[UninstallRun]
; Parar e remover serviço se existir
Filename: "{sys}\sc.exe"; Parameters: "stop CorujaProbe"; Flags: runhidden
Filename: "{sys}\sc.exe"; Parameters: "delete CorujaProbe"; Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\collectors\__pycache__"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Criar arquivo de instruções pós-instalação
    SaveStringToFile(ExpandConstant('{app}\INSTRUCOES_POS_INSTALACAO.txt'), 
      '========================================' + #13#10 +
      'CORUJA MONITOR PROBE - INSTALADO!' + #13#10 +
      '========================================' + #13#10 + #13#10 +
      'PRÓXIMOS PASSOS:' + #13#10 + #13#10 +
      '1. INSTALAR PYTHON (se não tiver):' + #13#10 +
      '   - Baixe: https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' + #13#10 +
      '   - Execute como Administrador' + #13#10 +
      '   - Marque "Add Python to PATH"' + #13#10 + #13#10 +
      '2. INSTALAR DEPENDÊNCIAS:' + #13#10 +
      '   Abra CMD como Administrador e execute:' + #13#10 +
      '   python -m pip install psutil httpx pywin32 pysnmp pyyaml' + #13#10 + #13#10 +
      '3. CONFIGURAR FIREWALL (WMI):' + #13#10 +
      '   netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes' + #13#10 + #13#10 +
      '4. CONFIGURAR PROBE:' + #13#10 +
      '   - Execute: Configurar Coruja Probe (atalho no Desktop)' + #13#10 +
      '   - Informe IP do servidor: 192.168.31.161' + #13#10 +
      '   - Informe token da probe' + #13#10 + #13#10 +
      '5. INSTALAR COMO SERVIÇO:' + #13#10 +
      '   - Execute: Instalar Serviço (Menu Iniciar > Coruja Monitor)' + #13#10 + #13#10 +
      '========================================' + #13#10 +
      'SUPORTE: http://192.168.31.161:3000' + #13#10 +
      '========================================', 
      False);
    
    // Abrir arquivo de instruções
    Exec('notepad.exe', ExpandConstant('{app}\INSTRUCOES_POS_INSTALACAO.txt'), '', SW_SHOW, ewNoWait, ResultCode);
  end;
end;
