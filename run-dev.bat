@echo off
setlocal

cd /d "%~dp0"

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

echo [INFO] Starting backend on http://127.0.0.1:8000
start "omnivoice-loose-ui backend" cmd /k "cd /d %~dp0 && backend\.venv\Scripts\python.exe backend\run.py"

echo [INFO] Starting frontend dev server on http://127.0.0.1:3000
cd frontend
call npm run dev
