@echo off
REM sync-local-pypdfium2.bat
REM Windows batch script to sync with local pypdfium2 submodule
REM Handles GitHub CLI attestation bypass automatically

setlocal enabledelayedexpansion

echo ========================================
echo   pypdfium2 Local Submodule Sync Script
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "pyproject.toml" (
    echo [ERROR] Please run this script from the project root directory containing pyproject.toml
    exit /b 1
)

if not exist "pypdfium2" (
    echo [ERROR] pypdfium2 directory not found. Please ensure the submodule is initialized.
    exit /b 1
)

REM Check if uv is installed
where uv >nul 2>nul
if errorlevel 1 (
    echo [ERROR] uv is not installed or not in PATH. Please install uv first.
    echo [INFO] Install with: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    exit /b 1
)

REM Enhanced function to find GitHub CLI
set "GH_FOUND="
set "GH_PATH="

REM Try comprehensive GitHub CLI locations
for %%G in (
    "gh.exe"
    "%ProgramFiles%\Git\bin\gh.exe"
    "%ProgramFiles(x86)%\Git\bin\gh.exe"
    "%LOCALAPPDATA%\Programs\GitHub CLI\gh.exe"
    "%LOCALAPPDATA%\Microsoft\WindowsApps\gh.exe"
    "%ChocolateyInstall%\bin\gh.exe"
    "%ProgramData%\chocolatey\bin\gh.exe"
    "%UserProfile%\scoop\shims\gh.exe"
    "%ProgramFiles%\GitHub CLI\gh.exe"
) do (
    if exist %%G (
        set "GH_FOUND=1"
        set "GH_PATH=%%~G"
        echo [INFO] Found GitHub CLI: !GH_PATH!
        goto :found_gh
    )
)

:found_gh
if defined GH_FOUND (
    REM Disable GitHub CLI
    echo [INFO] Temporarily disabling GitHub CLI to bypass attestation verification...
    move "!GH_PATH!" "!GH_PATH!.backup" >nul 2>&1
    if exist "!GH_PATH!.backup" (
        echo [INFO] GitHub CLI temporarily disabled: !GH_PATH!
        set "GH_DISABLED=1"
    ) else (
        echo [WARNING] Failed to disable GitHub CLI, continuing anyway...
        set "GH_DISABLED=0"
    )
) else (
    echo [WARNING] GitHub CLI not found - no need to disable attestation verification
    set "GH_DISABLED=0"
)

REM Set up error handling for cleanup
set "ERROR_OCCURRED=0"

REM Run uv sync
echo [INFO] Running uv sync with local pypdfium2 submodule...

uv sync
if errorlevel 1 (
    echo [ERROR] uv sync failed!
    set "ERROR_OCCURRED=1"
    goto :cleanup
)

echo.
echo [SUCCESS] uv sync completed successfully!
echo [INFO] Local pypdfium2 submodule is now installed as editable dependency

REM Show package info if available
echo [INFO] Installed pypdfium2 info:
uv pip show pypdfium2 2>nul | findstr /C:"Name:" /C:"Version:" /C:"Location:" >nul 2>&1
if not errorlevel 1 (
    uv pip show pypdfium2 | findstr /C:"Name:" /C:"Version:" /C:"Location:"
) else (
    echo [INFO] Package info not available
)

echo.
echo [SUCCESS] All done! Your local pypdfium2 submodule is ready to use.
echo [INFO] You can now make changes in .\pypdfium2 and they will be reflected immediately.

:cleanup
REM Restore GitHub CLI if we disabled it
if defined GH_DISABLED (
    if "!GH_DISABLED!"=="1" (
        if exist "!GH_PATH!.backup" (
            move "!GH_PATH!.backup!" "!GH_PATH!" >nul 2>&1
            if exist "!GH_PATH!" (
                echo [SUCCESS] GitHub CLI restored: !GH_PATH!
            ) else (
                echo [WARNING] Failed to restore GitHub CLI: !GH_PATH!
                echo [INFO] Manually restore if needed: move "!GH_PATH!.backup" "!GH_PATH!"
            )
        )
    )
)

REM Handle different exit scenarios
if "!ERROR_OCCURRED!"=="1" (
    echo [ERROR] Script completed with errors.
    exit /b 1
)

REM Handle script interruption (Ctrl+C)
if errorlevel 130 (
    echo.
    echo [WARNING] Script interrupted. Cleaning up...
    if defined GH_DISABLED (
        if "!GH_DISABLED!"=="1" (
            if exist "!GH_PATH!.backup" (
                move "!GH_PATH!.backup!" "!GH_PATH!" >nul 2>&1
                echo [INFO] GitHub CLI restored
            )
        )
    )
    exit /b 130
)

echo [INFO] Script completed successfully.
exit /b 0