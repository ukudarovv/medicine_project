# Исправление ошибки подключения Telegram бота к Backend

## Проблема
При вводе ИИН в боте появляется ошибка: **"Произошла ошибка. Попробуйте позже."**

## Причина
Telegram бот не может подключиться к Django backend API. Это происходит потому, что:
1. В файле `.env` не указан параметр `DJANGO_API_URL`
2. Бот использует значение по умолчанию `http://backend:8000` (для Docker)
3. Но при локальном запуске нужен URL `http://localhost:8000`

## Решение

### Шаг 1: Добавьте настройки в ваш файл .env

Откройте файл `.env` в корне проекта и добавьте следующие строки в раздел Telegram Bot:

```bash
# Django API URL for bot to connect to backend
DJANGO_API_URL=http://localhost:8000

# Redis settings for bot (for local development)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=1
```

### Шаг 2: Проверьте, что backend запущен

Убедитесь, что Django backend запущен и доступен:

```powershell
# Откройте браузер и перейдите на:
http://localhost:8000/api/bot/patient/verify-iin/
```

Вы должны увидеть страницу API (возможно с ошибкой 405 Method Not Allowed - это нормально).

### Шаг 3: Перезапустите бота

Остановите бота (Ctrl+C) и запустите заново:

```powershell
.\start_bot.ps1
```

Или вручную:
```powershell
cd telegram_bot
python main.py
```

### Шаг 4: Проверьте в логах

При запуске вы должны увидеть:
```
INFO - Bot starting...
INFO - Using polling mode
```

Если видите ошибки подключения к Redis или backend - проверьте, что они запущены.

## Проверка работы

Попробуйте снова зарегистрироваться:

1. Отправьте `/start` боту
2. Заполните все данные
3. Введите ИИН: `040309500033`
4. Теперь должно работать! ✅

## Если проблема осталась

### Проверка 1: Backend запущен?

```powershell
# Проверьте процессы
Get-Process | Select-String python
```

Если backend не запущен:
```powershell
cd backend
python manage.py runserver
```

### Проверка 2: Redis запущен?

Redis нужен для работы FSM (Finite State Machine) бота.

**Если используете Docker:**
```powershell
docker ps | Select-String redis
```

**Если Redis не установлен локально:**

Вариант 1 - Используйте Docker:
```powershell
docker run -d -p 6379:6379 redis:alpine
```

Вариант 2 - Установите Redis для Windows:
1. Скачайте: https://github.com/microsoftarchive/redis/releases
2. Установите и запустите

Вариант 3 - Используйте Memory Storage (без Redis):

Измените `telegram_bot/main.py`:
```python
from aiogram.fsm.storage.memory import MemoryStorage

def create_dispatcher() -> Dispatcher:
    # Используйте Memory Storage вместо Redis
    storage = MemoryStorage()
    
    # ... остальной код
```

### Проверка 3: API Secret совпадает?

Убедитесь, что в `.env` секрет совпадает:

```bash
# В .env должно быть одинаково:
TELEGRAM_BOT_API_SECRET=ваш-секретный-ключ
```

И в `backend/config/settings/base.py` или `.env` backend:
```python
TELEGRAM_BOT_API_SECRET = "ваш-секретный-ключ"
```

## Готовый .env файл (пример)

```bash
# ==================== Telegram Bot ====================

# Bot token from @BotFather
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather

# Django API URL for bot to connect to backend
DJANGO_API_URL=http://localhost:8000

# API secret for Django API authentication
TELEGRAM_BOT_API_SECRET=change-this-secret-in-production

# Redis settings for bot
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=1

# Use webhook instead of polling
USE_WEBHOOK=false

# Default organization ID for bot registrations
DEFAULT_ORGANIZATION_ID=1
```

## Быстрая проверка подключения

Откройте Python и попробуйте:

```python
import requests

url = "http://localhost:8000/api/bot/patient/verify-iin/"
headers = {
    "Authorization": "Bearer change-this-secret-in-production",
    "Content-Type": "application/json"
}
data = {"iin": "040309500033"}

response = requests.post(url, json=data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

Должно вывести что-то вроде:
```
Status: 200
Response: {'valid': True, 'birth_date': '2004-03-09', 'sex': 'M'}
```

Если получаете ошибку - проблема в backend или секрете.

---

После этих исправлений бот должен работать! 🎉

