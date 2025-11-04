# ============================================================================
# ПРИМЕНЕНИЕ МИГРАЦИЙ - ИСПРАВЛЕНИЕ 500 ОШИБОК
# ============================================================================
# Этот скрипт применяет все миграции КZ-адаптации к базе данных

Write-Host "🚀 Применяем миграции для КZ-адаптации..." -ForegroundColor Green

cd backend

Write-Host "`n1️⃣ Применяем миграции Patient (IIN, OSMS, consents)..." -ForegroundColor Cyan
python manage.py migrate patients

Write-Host "`n2️⃣ Применяем миграции Visits (diary_structured, files)..." -ForegroundColor Cyan
python manage.py migrate visits

Write-Host "`n3️⃣ Применяем миграции Calendar (waitlist)..." -ForegroundColor Cyan
python manage.py migrate calendar

Write-Host "`n4️⃣ Применяем миграции Comms (contacts)..." -ForegroundColor Cyan
python manage.py migrate comms

Write-Host "`n5️⃣ Применяем миграции Billing (KZ payments)..." -ForegroundColor Cyan
python manage.py migrate billing

Write-Host "`n6️⃣ Загружаем КАТО справочник..." -ForegroundColor Cyan
python manage.py loaddata kato

Write-Host "`n✅ МИГРАЦИИ ПРИМЕНЕНЫ! Теперь:" -ForegroundColor Green
Write-Host "   1. Перезапустите Django сервер (Ctrl+C, потом python manage.py runserver)" -ForegroundColor Yellow
Write-Host "   2. Раскомментируйте новые API в backend/apps/patients/urls.py" -ForegroundColor Yellow
Write-Host "   3. Обновите фронтенд (F5 в браузере)" -ForegroundColor Yellow

cd ..

