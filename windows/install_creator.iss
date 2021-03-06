; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{1FB4614B-57A5-4F23-89D9-8BF61499B50B}
AppName=Supertree Toolkit
AppVersion=1.5
;AppVerName=Supertree Toolkit 1.5
AppPublisher=Supertree Toolkit Team
AppPublisherURL=www.supertreetoolkit.org
AppSupportURL=www.supertreetoolkit.org
AppUpdatesURL=www.supertreetoolkit.org
DefaultDirName={pf}\Supertree Toolkit
DefaultGroupName=Supertree Toolkit
LicenseFile=C:\Users\jhill1\Documents\Software\SupertreeToolkit\trunk\LICENSE
OutputBaseFilename=setup
SetupIconFile=C:\Users\jhill1\Documents\Software\SupertreeToolkit\trunk\stk_gui\gui\stk.ico
Compression=lzma
SolidCompression=yes
ChangesAssociations=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: modifypath; Description: &Add application directory to your system path
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "C:\Users\jhill1\Documents\Software\SupertreeToolkit\trunk\dist\stk.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\jhill1\Documents\Software\SupertreeToolkit\trunk\dist\stk-gui.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\jhill1\Documents\Software\SupertreeToolkit\trunk\dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\Supertree Toolkit"; Filename: "{app}\stk-gui.exe"
Name: "{group}\{cm:UninstallProgram,Supertree Toolkit}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Supertree Toolkit"; Filename: "{app}\stk-gui.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Supertree Toolkit"; Filename: "{app}\stk-gui.exe"; Tasks: quicklaunchicon

[Registry]
Root: HKCR; Subkey: ".phyml"; ValueType: string; ValueName: ""; ValueData: "Supertree-Toolkit"; Flags: uninsdeletevalue 
Root: HKCR; Subkey: "Supertree-Toolkit"; ValueType: string; ValueName: ""; ValueData: "Supertree Toolkit"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Supertree-Toolkit\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\stk-gui.exe,0"
Root: HKCR; Subkey: "Supertree-Toolkit\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\stk-gui.exe"" ""%1"""

[Run]
Filename: "{app}\stk-gui.exe"; Description: "{cm:LaunchProgram,Supertree Toolkit}"; Flags: nowait postinstall skipifsilent

[Code]
const
	ModPathName = 'modifypath';
	ModPathType = 'user';

function ModPathDir(): TArrayOfString;
begin
	setArrayLength(Result, 2)
	Result[0] := ExpandConstant('{app}');
	Result[1] := ExpandConstant('{app}\bin');
end;
#include "modpath.iss"
