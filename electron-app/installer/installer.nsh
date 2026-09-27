; GeoCore NSIS customisation (wired up via build.nsis.include in package.json).
; Prepended to electron-builder's installer script before MUI2.nsh is loaded,
; so these top-level defines override the Modern UI defaults.
;
; Bitmaps (sidebar / header) live next to this file and are regenerated with
; installer/generate_assets.py.

; ---- Right-hand panel of the Welcome / Finish pages and the page header ----
; Light GeoCore background (--color-background) with the main text colour.
; Kept light on purpose: Windows ignores custom colours on themed checkboxes
; ("Run GeoCore"), so a dark panel would make their labels unreadable.
!define MUI_BGCOLOR "F5F7F3"
!define MUI_TEXTCOLOR "16201B"

!ifndef BUILD_UNINSTALLER
  !define MUI_WELCOMEPAGE_TITLE "Welcome to GeoCore ${VERSION}"
  !define MUI_WELCOMEPAGE_TEXT "GeoCore is a local geotechnical engineering suite with deterministic calculations and the GeoAI assistant, running entirely on this computer.$\r$\n$\r$\nIt is recommended that you close any running copy of GeoCore before continuing.$\r$\n$\r$\nClick Next to continue."

  !define MUI_FINISHPAGE_TITLE "GeoCore is ready"
  !define MUI_FINISHPAGE_TEXT "GeoCore ${VERSION} has been installed on your computer.$\r$\n$\r$\nCalculations and GeoAI run locally, so GeoCore works offline.$\r$\n$\r$\nClick Finish to close Setup."
  !define MUI_FINISHPAGE_RUN_TEXT "Launch GeoCore"
!else
  !define MUI_WELCOMEPAGE_TITLE "Uninstall GeoCore"
  !define MUI_WELCOMEPAGE_TEXT "This will remove GeoCore ${VERSION} from your computer.$\r$\n$\r$\nFiles you have saved or exported are not deleted.$\r$\n$\r$\nClick Next to continue."

  !define MUI_FINISHPAGE_TITLE "GeoCore has been removed"
  !define MUI_FINISHPAGE_TEXT "GeoCore has been uninstalled from your computer.$\r$\n$\r$\nClick Finish to close Setup."
!endif

; electron-builder's assisted installer has no Welcome page by default; add one.
!macro customWelcomePage
  !insertmacro MUI_PAGE_WELCOME
!macroend
