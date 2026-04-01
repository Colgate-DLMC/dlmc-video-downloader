; Inno Setup script — DLMC Video Downloader (Windows)
; Produces: Output\dlmc-video-downloader-setup.exe

[Setup]
AppName=DLMC Video Downloader
AppVersion=1.2
AppPublisher=Colgate-DLMC
AppPublisherURL=https://github.com/Colgate-DLMC/dlmc-video-downloader
AppSupportURL=https://github.com/Colgate-DLMC/dlmc-video-downloader/issues
DefaultDirName={autopf}\DLMC Video Downloader
DefaultGroupName=DLMC Video Downloader
OutputDir=Output
OutputBaseFilename=dlmc-video-downloader-setup
SetupIconFile=icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
; All PyInstaller output
Source: "dist\dlmc-video-downloader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\DLMC Video Downloader"; Filename: "{app}\dlmc-video-downloader.exe"
Name: "{autodesktop}\DLMC Video Downloader"; Filename: "{app}\dlmc-video-downloader.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\dlmc-video-downloader.exe"; Description: "Launch DLMC Video Downloader"; Flags: nowait postinstall skipifsilent
