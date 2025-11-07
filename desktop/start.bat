@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   Medicine Desktop App
echo ========================================
echo.
echo API: http://localhost:18000/api/v1
echo.
echo Логин: doctor
echo Пароль: doctor123
echo.
echo ИИН пациента: 040309500033
echo.

set "PATH=C:\Program Files\nodejs;%PATH%"
set "VITE_API_URL=http://localhost:18000/api/v1"
set "NODE_ENV=development"

echo Запуск приложения...
echo.

call npm run dev

pause

