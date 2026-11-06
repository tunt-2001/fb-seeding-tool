@echo off
chcp 65001 >nul
title HE THONG FB SEEDING PRO - SMART BOOTSTRAPPER

echo ===================================================================
echo             FB SEEDING PRO - TU DONG KIEM TRA MOI TRUONG
echo ===================================================================
echo.

:: 1. Kiem tra xem may da co Python chua
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Phat hien: May tinh cua ban CHUA CAI PYTHON.
    echo [*] Dang tien hanh tu dong tai va cai dat Python 3.12 (khoang 1-2 phut)...
    echo.

    :: Tao thu muc tam de tai installer
    if not exist "%temp%\python_installer" mkdir "%temp%\python_installer"
    set "INSTALLER_PATH=%temp%\python_installer\python-3.12.exe"

    :: Dung curl co san tren Windows 10/11 de tai Python chinh thuc
    echo [*] Dang tai Python tu python.org...
    curl -L -o "%INSTALLER_PATH%" https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe

    if not exist "%INSTALLER_PATH%" (
        echo [x] Loi: Khong the tai Python. Vui long kiem tra lai ket noi Internet!
        pause
        exit /b 1
    )

    echo [*] Dang cai dat Python am tham (Silent Install)...
    start /wait "" "%INSTALLER_PATH%" /passive InstallAllUsers=0 PrependPath=1 Include_test=0

    echo [✓] Cai dat Python thanh cong!
    echo [*] Dang khoi tao lai bien moi truong PATH...
    
    :: Cap nhat PATH cho phien chay hien tai
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
)

:: Kiem tra lai Python sau khi cai
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Vui long khoi dong lai may tinh hoac mo lai file run.bat de he thong nhan dien Python.
    pause
    exit /b 1
)

:: 2. Kiem tra va cai dat cac thu vien can thiet
echo [*] Dang kiem tra va dong bo thu vien (Pip packages)...
pip install -r requirements.txt --quiet --disable-pip-version-check

:: 3. Kiem tra va cai dat Playwright Chromium neu chua co
echo [*] Dang kiem tra trinh duyet Chromium chuyen dung...
python -m playwright install chromium

echo.
echo ===================================================================
echo [✓] MOI TRUONG DA SAN SANG 100%!
echo [*] Dang khoi dong Giao dien Dashboard tai: http://127.0.0.1:8000
echo ===================================================================
echo.

:: 4. Mo trinh duyet Dashboard va chay Web Server
start http://127.0.0.1:8000
python -m uvicorn server:app --host 127.0.0.1 --port 8000

pause
