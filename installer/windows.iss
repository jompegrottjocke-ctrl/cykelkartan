#define AppName "Cykelfrämjandet Malmö"
[Setup]
AppId=CykelframjandetMalmo
AppName={#AppName}
AppVersion=0.1.0
DefaultDirName={localappdata}\Programs\CykelframjandetMalmo
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
OutputBaseFilename=CykelframjandetMalmo-Setup
SetupIconFile=..\assets\icons\cykel.ico
UninstallDisplayIcon={app}\CykelframjandetMalmo.exe
WizardStyle=modern
[Files]
Source: "..\dist\CykelframjandetMalmo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\CykelframjandetMalmo.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\CykelframjandetMalmo.exe"
[Run]
Filename: "{app}\CykelframjandetMalmo.exe"; Description: "Starta {#AppName}"; Flags: nowait postinstall skipifsilent
