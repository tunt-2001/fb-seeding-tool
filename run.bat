@echo off
chcp 65001 >nul
title HỆ THỐNG SEEDING FACEBOOK (UI DASHBOARD)
echo ========================================================
echo   ĐANG KHỞI CHẠY GIAO DIỆN ĐIỀU KHIỂN SEEDING FACEBOOK
echo ========================================================
echo.
echo Địa chỉ truy cập Dashboard: http://127.0.0.1:8000
echo.
start http://127.0.0.1:8000
python -m uvicorn server:app --host 127.0.0.1 --port 8000
pause
