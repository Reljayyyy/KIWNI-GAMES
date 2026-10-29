; OPTIONAL: turns dist\KwinsGreatAdventure.exe into a proper Setup installer.
; 1) run build.bat first   2) install the free "Inno Setup" (jrsoftware.org)   3) open this file in it and press Compile.
; The installer appears in the "installer" folder.
[Setup]
AppName=Kwin's Great Adventure
AppVersion=1.0
DefaultDirName={autopf}\KwinsGreatAdventure
DefaultGroupName=Kwin's Great Adventure
OutputDir=installer
OutputBaseFilename=KwinsGreatAdventure-Setup
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\KwinsGreatAdventure.exe
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\KwinsGreatAdventure.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Kwin's Great Adventure"; Filename: "{app}\KwinsGreatAdventure.exe"
Name: "{autodesktop}\Kwin's Great Adventure"; Filename: "{app}\KwinsGreatAdventure.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Extra icons:"

[Run]
Filename: "{app}\KwinsGreatAdventure.exe"; Description: "Play now"; Flags: nowait postinstall skipifsilent
