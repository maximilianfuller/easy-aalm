; Inno Setup Script for Easy AALM
; Creates a Windows installer that users can double-click to install

[Setup]
AppName=Easy AALM
AppVersion=1.0
AppPublisher=Easy AALM
AppPublisherURL=https://github.com/maximilianfuller/easy-aalm
DefaultDirName={autopf}\Easy AALM
DefaultGroupName=Easy AALM
OutputDir=.
OutputBaseFilename=Easy-AALM-Windows-Setup
Compression=lzma2
SolidCompression=yes
UninstallDisplayIcon={app}\Easy AALM.exe
WizardStyle=modern
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Files]
Source: "dist\EasyAALM\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Easy AALM"; Filename: "{app}\Easy AALM.exe"
Name: "{autodesktop}\Easy AALM"; Filename: "{app}\Easy AALM.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\Easy AALM.exe"; Description: "Launch Easy AALM"; Flags: nowait postinstall skipifsilent
