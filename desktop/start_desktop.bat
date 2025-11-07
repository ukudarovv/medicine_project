@echo off
chcp 65001 >nul
echo ====================================
echo   Medicine Desktop App - Starting
echo ====================================
echo.

cd /d "%~dp0"

echo [1/4] Добавление Node.js в PATH...
set PATH=C:\Program Files\nodejs;%PATH%

echo [2/4] Проверка зависимостей...
if not exist "node_modules" (
    echo Устанавливаем зависимости...
    call npm install
)

echo [3/4] Загрузка конфигурации...
for /f "tokens=1,2 delims==" %%a in (.env) do (
    set "%%a=%%b"
    echo   %%a=%%b
)

echo [4/4] Запуск приложения...
echo.
echo API URL: %VITE_API_URL%
echo Десктоп-приложение запускается...
echo Откроется окно Electron через несколько секунд.
echo.
echo Логин: doctor
echo Пароль: doctor123
echo.
echo Для остановки закройте окно приложения или нажмите Ctrl+C
echo.

set NODE_ENV=development
call npm run dev

pause

