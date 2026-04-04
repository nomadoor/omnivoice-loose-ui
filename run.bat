@echo off
setlocal

cd /d "%~dp0"

set "OPEN_BROWSER=1"
set "APP_PORT=8000"

:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--no-browser" (
  set "OPEN_BROWSER=0"
  shift
  goto parse_args
)
if /i "%~1"=="--port" (
  if "%~2"=="" (
    echo [ERROR] --port requires a value.
    exit /b 1
  )
  set "APP_PORT=%~2"
  shift
  shift
  goto parse_args
)

echo [ERROR] Unknown argument: %~1
exit /b 1

:args_done
if "%HF_HOME%"=="" set "HF_HOME=%~dp0backend\hf-cache"
if "%HUGGINGFACE_HUB_CACHE%"=="" set "HUGGINGFACE_HUB_CACHE=%~dp0backend\hf-cache"
set "OMNIVOICE_PORT=%APP_PORT%"

if not exist "backend\.venv\Scripts\python.exe" (
  echo [ERROR] backend\.venv was not found.
  echo Run install.bat first.
  exit /b 1
)

if not exist "frontend\node_modules" (
  echo [ERROR] frontend\node_modules was not found.
  echo Run install.bat first.
  exit /b 1
)

echo [INFO] Building frontend...
call npm run build --prefix frontend
if errorlevel 1 exit /b 1

if "%OPEN_BROWSER%"=="1" (
  echo [INFO] Opening browser...
  start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:%APP_PORT%/'"
)

echo [INFO] Starting app on http://127.0.0.1:%APP_PORT%
backend\.venv\Scripts\python.exe backend\run.py
