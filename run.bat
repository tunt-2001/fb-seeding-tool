@echo off
setlocal enabledelayedexpansion
title FB SEEDING PRO - BOOTSTRAPPER

echo ===================================================
echo       FB SEEDING PRO - KHOI DONG HE THONG
echo ===================================================
echo.

:: Tim kiem file python.exe thuc su tren he thong
set "PY_EXE="

:: 1. Kiem tra lenh python mac dinh
where python >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('where python') do (
        echo %%i | findstr /i "WindowsApps" >nul
        if errorlevel 1 (
            set "PY_EXE=%%i"
            goto :FOUND_PYTHON
        )
    )
)

:: 2. Kiem tra thu muc cai dat mac dinh cua user
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :FOUND_PYTHON
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :FOUND_PYTHON
)

if exist "%ProgramFiles%\Python312\python.exe" (
    set "PY_EXE=%ProgramFiles%\Python312\python.exe"
    goto :FOUND_PYTHON
)

:: Neu chua tim thay, tien hanh tai va cai dat tu dong
echo [!] Chua tim thay Python hop le. Dang tien hanh cai dat tu dong...
if not exist "%temp%\py_installer" mkdir "%temp%\py_installer"
set "INSTALLER=%temp%\py_installer\python_setup.exe"

echo [*] Dang tai Python 3.12 tu python.org...
curl -L -o "%INSTALLER%" https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe

if not exist "%INSTALLER%" (
    echo [x] Khong the tai bo cai Python. Vui long kiem tra Internet!
    pause
    exit /b 1
)

echo [*] Dang cai dat Python...
"%INSTALLER%" /passive InstallAllUsers=0 PrependPath=1 Include_test=0

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) else (
    echo [x] Cai dat khong thanh cong hoac can khoi dong lai CMD.
    pause
    exit /b 1
)

:FOUND_PYTHON
echo [✓] Da tim thay Python: "%PY_EXE%"
echo.

:: Dong bo thu vien pip
echo [*] Dang kiem tra va cai dat thu vien (pip packages)...
"%PY_EXE%" -m pip install -r requirements.txt --quiet --disable-pip-version-check

:: Kiem tra Playwright Chromium
echo [*] Dang kiem tra trinh duyet Chromium...
"%PY_EXE%" -m playwright install chromium

echo.
echo ===================================================
echo [✓] MOI TRUONG SAN SANG!
echo [*] Dang mo Dashboard tai: http://127.0.0.1:8000
echo ===================================================
echo.

start http://127.0.0.1:8000
"%PY_EXE%" -m uvicorn server:app --host 127.0.0.1 --port 8000

pause
