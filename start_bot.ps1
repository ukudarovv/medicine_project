# Script to start Telegram Bot
# Usage: .\start_bot.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Telegram Bot Starter" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating .env from env.example..." -ForegroundColor Yellow
    Copy-Item "env.example" ".env"
    Write-Host "✅ .env file created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  ВАЖНО: Настройте TELEGRAM_BOT_TOKEN в файле .env!" -ForegroundColor Red
    Write-Host "   1. Откройте .env в редакторе" -ForegroundColor Yellow
    Write-Host "   2. Найдите TELEGRAM_BOT_TOKEN=" -ForegroundColor Yellow
    Write-Host "   3. Вставьте токен от @BotFather" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Продолжить запуск? (y/n)"
    if ($continue -ne "y") {
        exit
    }
}

# Check if TELEGRAM_BOT_TOKEN is set
$envContent = Get-Content ".env" -Raw
if ($envContent -match "TELEGRAM_BOT_TOKEN=\s*$" -or $envContent -notmatch "TELEGRAM_BOT_TOKEN=") {
    Write-Host "❌ TELEGRAM_BOT_TOKEN не настроен в .env!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Как получить токен:" -ForegroundColor Yellow
    Write-Host "  1. Откройте Telegram и найдите @BotFather" -ForegroundColor White
    Write-Host "  2. Отправьте команду /newbot или /mybots" -ForegroundColor White
    Write-Host "  3. Скопируйте токен (формат: 123456789:ABCdefGHI...)" -ForegroundColor White
    Write-Host "  4. Добавьте в .env: TELEGRAM_BOT_TOKEN=ваш_токен" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "📋 Проверка зависимостей..." -ForegroundColor Yellow

# Check Docker
try {
    $null = docker --version
    Write-Host "✅ Docker найден" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker не установлен!" -ForegroundColor Red
    Write-Host "   Установите Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check Docker Compose
try {
    $null = docker-compose --version
    Write-Host "✅ Docker Compose найден" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose не установлен!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 Запуск Telegram Bot..." -ForegroundColor Cyan
Write-Host ""

# Start bot
Write-Host "Запуск контейнера telegram_bot..." -ForegroundColor Yellow
docker-compose up -d telegram_bot

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Telegram Bot успешно запущен!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Полезные команды:" -ForegroundColor Cyan
    Write-Host "  • Просмотр логов:     docker-compose logs -f telegram_bot" -ForegroundColor White
    Write-Host "  • Остановить бота:    docker-compose stop telegram_bot" -ForegroundColor White
    Write-Host "  • Перезапустить:      docker-compose restart telegram_bot" -ForegroundColor White
    Write-Host "  • Статус контейнера:  docker-compose ps telegram_bot" -ForegroundColor White
    Write-Host ""
    
    # Ask if user wants to see logs
    $showLogs = Read-Host "Показать логи бота? (y/n)"
    if ($showLogs -eq "y") {
        Write-Host ""
        Write-Host "📜 Логи бота (Ctrl+C для выхода):" -ForegroundColor Cyan
        Write-Host ""
        docker-compose logs -f telegram_bot
    }
} else {
    Write-Host ""
    Write-Host "❌ Ошибка при запуске бота!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Проверьте логи:" -ForegroundColor Yellow
    docker-compose logs telegram_bot
}

