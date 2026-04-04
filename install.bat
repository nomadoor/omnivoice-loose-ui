@echo off
setlocal

cd /d "%~dp0"

set "TORCH_VARIANT=%OMNIVOICE_TORCH_VARIANT%"
if "%TORCH_VARIANT%"=="" set "TORCH_VARIANT=auto"

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] python was not found in PATH.
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] npm was not found in PATH.
  exit /b 1
)

if not exist "backend\.venv\Scripts\python.exe" (
  echo [INFO] Creating backend virtual environment...
  python -m venv backend\.venv
  if errorlevel 1 exit /b 1
)

echo [INFO] Installing backend requirements...
call "backend\.venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

call "backend\.venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
if errorlevel 1 exit /b 1

if /i "%TORCH_VARIANT%"=="auto" (
  where nvidia-smi >nul 2>nul
  if errorlevel 1 (
    set "TORCH_VARIANT=cpu"
  ) else (
    set "TORCH_VARIANT=cu128"
  )
)

echo [INFO] Selected PyTorch variant: %TORCH_VARIANT%

echo [INFO] Removing existing torch packages...
call "backend\.venv\Scripts\python.exe" -m pip uninstall -y torch torchaudio >nul 2>nul

if /i "%TORCH_VARIANT%"=="cu128" (
  echo [INFO] Installing CUDA 12.8 PyTorch and torchaudio...
  call "backend\.venv\Scripts\python.exe" -m pip install torch==2.8.0+cu128 torchaudio==2.8.0+cu128 --extra-index-url https://download.pytorch.org/whl/cu128
) else (
  echo [INFO] Installing CPU PyTorch and torchaudio...
  call "backend\.venv\Scripts\python.exe" -m pip install torch torchaudio
)
if errorlevel 1 exit /b 1

if /i "%OMNIVOICE_INSTALL_SOURCE%"=="git" (
  echo [INFO] Installing OmniVoice from GitHub...
  call "backend\.venv\Scripts\python.exe" -m pip install git+https://github.com/k2-fsa/OmniVoice.git
) else (
  echo [INFO] Installing OmniVoice from PyPI...
  call "backend\.venv\Scripts\python.exe" -m pip install omnivoice
)
if errorlevel 1 exit /b 1

echo [INFO] Installing frontend dependencies...
call npm install --prefix frontend
if errorlevel 1 exit /b 1

echo.
echo [DONE] Installation finished.
echo [INFO] Torch variant used: %TORCH_VARIANT%
echo [NOTE] If you want to install OmniVoice from GitHub instead of PyPI, run:
echo        set OMNIVOICE_INSTALL_SOURCE=git ^&^& install.bat
echo [NOTE] If you want to force CUDA or CPU, run:
echo        set OMNIVOICE_TORCH_VARIANT=cu128 ^&^& install.bat
echo        set OMNIVOICE_TORCH_VARIANT=cpu ^&^& install.bat
exit /b 0
