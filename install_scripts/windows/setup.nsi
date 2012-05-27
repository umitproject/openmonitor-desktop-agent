!include "MUI2.nsh"

!define APPLICATION_NAME "icmagent"
!define APPLICATION_SHORTNAME "icm"
!define APPLICATION_VERSION "0.1Alpha"
!define APPLICATION_HOMEPAGE "http://www.openmonitor.org"

!define PY2EXE_OUTPUTDIR 'dist'
!define EXE_OUTFILE '${APPLICATION_NAME}-${APPLICATION_VERSION}-installer.exe'

!define APPLICATION_ICON 'G:\gsoc\final\icmagent\share\images\icm-agent.ico'

!define AddRemKey "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPLICATION_NAME} ${APPLICATION_VERSION}"

!define exe             'icmagent.exe'
!define compressor      'lzma'  ;one of 'zlib', 'bzip2', 'lzma'
!define onlyOneInstance

VIProductVersion 0.1.0.0
VIAddVersionKey FileVersion     "${APPLICATION_VERSION}"
VIAddVersionKey FileDescription "Open Monitor Desktop Agent made easy"
VIAddVersionKey ProductName     "${APPLICATION_NAME}"
VIAddVersionKey ProductVersion  "${APPLICATION_VERSION}"
VIAddVersionKey CompanyWebsite  "${APPLICATION_HOMEPAGE}"
VIAddVersionKey LegalCopyright  ""

;==============================================================================
; General section
;==============================================================================

Name "${APPLICATION_NAME}"
OutFile "${EXE_OUTFILE}"
InstallDir "$PROGRAMFILES\${APPLICATION_NAME}"

Icon ${APPLICATION_ICON}

; Get installation folder from registry if avaiable
InstallDirRegKey HKCU "Software\${APPLICATION_NAME}" ""

;==============================================================================
; Interface Settings
;==============================================================================

!define MUI_ABORTWARNING
!define MUI_UNABORTWARNING
!define MUI_PAGE_HEADER_SUBTEXT ${APPLICATION_NAME}
!define MUI_FINISHPAGE_LINK "Don't forget to visit ${APPLICATION_SHORTNAME}'s website!"
!define MUI_FINISHPAGE_LINK_LOCATION ${APPLICATION_HOMEPAGE}

;==============================================================================
; Pages
;==============================================================================

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;==============================================================================
; Languages
;==============================================================================

!insertmacro MUI_LANGUAGE "English"

Section
	SetOutPath '$INSTDIR'

	File /r '${PY2EXE_OUTPUTDIR}\*.*'

	; Store installation folder
	WriteRegStr HKCU "Software\${APPLICATION_NAME}" "" $INSTDIR

	; Create uninstaller
	WriteUninstaller "$INSTDIR\Uninstall.exe"

	SetOutPath "$SMPROGRAMS\${APPLICATION_NAME}\"
	CreateShortCut "$SMPROGRAMS\${APPLICATION_NAME}\${APPLICATION_NAME}.lnk" "$INSTDIR\${APPLICATION_NAME}.exe" "" "$INSTDIR\icmagent\share\images\icm-agent.ico"
	; CreateShortCut "$SMPROGRAMS\${APPLICATION_NAME}\${APPLICATION_NAME} Documentation.lnk" "$INSTDIR\html\index.html"
	CreateShortCut "$SMPROGRAMS\${APPLICATION_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

    ; Add uninstall information to "Add/Remove Programs"
    WriteRegStr HKLM '${AddRemKey}' "DisplayName" ${APPLICATION_NAME}
    WriteRegStr HKLM '${AddRemKey}' "DisplayVersion" ${APPLICATION_VERSION}
    WriteRegStr HKLM '${AddRemKey}' "DisplayIcon" ${APPLICATION_ICON}
    WriteRegStr HKLM '${AddRemKey}' "UrlInfoAbout" ${APPLICATION_HOMEPAGE}
    WriteRegStr HKLM '${AddRemKey}' "UninstallString" "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
	RMDir /r "$SMPROGRAMS\${APPLICATION_NAME}\"
	RMDir /r "$INSTDIR"

	DeleteRegKey /ifempty HKCU "Software\${APPLICATION_NAME}"
SectionEnd
