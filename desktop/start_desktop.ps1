# Medicine Desktop App Launcher
# PowerShell script for reliable startup

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  Medicine Desktop App - Starting" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Add Node.js to PATH
Write-Host "[1/4] Добавление Node.js в PATH..." -ForegroundColor Yellow
$env:Path = "C:\Program Files\nodejs;$env:Path"

# Verify Node.js
try {
    $nodeVersion = node --version
    Write-Host "  ✓ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js не найден!" -ForegroundColor Red
    Write-Host "  Установите Node.js: https://nodejs.org/" -ForegroundColor Yellow
    pause
    exit 1
}

# Step 2: Check dependencies
Write-Host "[2/4] Проверка зависимостей..." -ForegroundColor Yellow
if (-not (Test-Path "node_modules")) {
    Write-Host "  Устанавливаем зависимости..." -ForegroundColor Yellow
    npm install
}
Write-Host "  ✓ Зависимости установлены" -ForegroundColor Green

# Step 3: Load .env configuration
Write-Host "[3/4] Загрузка конфигурации..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^(.+?)=(.+)$') {
            $key = $matches[1]
            $value = $matches[2]
            Set-Item -Path "env:$key" -Value $value
            Write-Host "  $key=$value" -ForegroundColor Gray
        }
    }
    Write-Host "  ✓ Конфигурация загружена" -ForegroundColor Green
} else {
    Write-Host "  ✗ Файл .env не найден!" -ForegroundColor Red
}

# Step 4: Start the app
Write-Host "[4/4] Запуск приложения..." -ForegroundColor Yellow
Write-Host ""
Write-Host "API URL: $env:VITE_API_URL" -ForegroundColor Cyan
Write-Host "Десктоп-приложение запускается..." -ForegroundColor White
Write-Host "Откроется окно Electron через несколько секунд." -ForegroundColor White
Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "  Данные для входа:" -ForegroundColor White
Write-Host "  Логин:  doctor" -ForegroundColor Cyan
Write-Host "  Пароль: doctor123" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Для остановки закройте окно приложения или нажмите Ctrl+C" -ForegroundColor Gray
Write-Host ""

$env:NODE_ENV = "development"
npm run dev

