@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "POWERSHELL_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
set "START_FLAGS="

:parse_args
if "%~1"=="" goto run_start
if /I "%~1"=="--with-training" (
    set "START_FLAGS=%START_FLAGS% -StartTrainingService"
    shift
    goto parse_args
)
if /I "%~1"=="--skip-docker" (
    set "START_FLAGS=%START_FLAGS% -SkipDocker"
    shift
    goto parse_args
)
shift
goto parse_args

:run_start
echo Starting the web system from %SCRIPT_DIR%
echo Frontend, backend, and inference runtime will be prepared automatically.
"%POWERSHELL_EXE%" -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\start_web_system.ps1" %START_FLAGS%
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Startup failed with exit code %EXIT_CODE%.
)

endlocal & exit /b %EXIT_CODE%
