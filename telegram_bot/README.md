# 🤖 Telegram Bot для Medicine ERP

Telegram бот для записи на приём, просмотра документов и взаимодействия с пациентами.

## 📋 Оглавление

- [Возможности](#возможности)
- [Архитектура](#архитектура)
- [Endpoints](#endpoints)
- [Быстрый старт](#быстрый-старт)
- [Настройка](#настройка)
- [Режимы работы](#режимы-работы)
- [Разработка](#разработка)
- [Production Deploy](#production-deploy)

## ✨ Возможности

### Для пациентов:
- 📝 **Регистрация** - создание профиля через бота
- 🗓️ **Запись на приём** - выбор филиала, услуги, врача и времени
- 📋 **Мои записи** - просмотр, изменение и отмена записей
- 📄 **Документы** - получение справок и результатов анализов
- 💳 **Оплата** - оплата через Kaspi QR
- ⭐ **Обратная связь** - NPS опросы и отзывы
- 🆘 **Поддержка** - тикеты в поддержку и FAQ

### Для администраторов:
- 📢 **Рассылки** - сегментированные массовые рассылки
- 📊 **Аналитика** - статистика по рассылкам

## 🏗️ Архитектура

```
telegram_bot/
├── handlers/          # Обработчики команд и сообщений
│   ├── start.py      # Команда /start и регистрация
│   ├── booking.py    # Запись на приём
│   ├── my_appointments.py  # Управление записями
│   ├── documents.py  # Документы
│   ├── payments.py   # Оплата
│   ├── feedback.py   # Обратная связь
│   ├── support.py    # Поддержка
│   └── profile.py    # Профиль пользователя
├── keyboards/         # Клавиатуры
│   ├── inline.py     # Inline клавиатуры
│   └── reply.py      # Reply клавиатуры
├── middlewares/       # Middleware
│   ├── auth.py       # Авторизация
│   └── i18n.py       # Интернационализация
├── services/          # Бизнес-логика
│   ├── api_client.py # Клиент Django API
│   └── helpers.py    # Вспомогательные функции
├── states/            # FSM состояния
│   ├── booking.py    # Состояния для бронирования
│   └── registration.py # Состояния для регистрации
├── locales/           # Переводы
│   ├── ru.json       # Русский
│   └── kk.json       # Казахский
├── config.py          # Конфигурация
├── main.py            # Точка входа
├── requirements.txt   # Зависимости
└── Dockerfile         # Docker образ
```

## 🔌 Endpoints

Бот использует следующие endpoints Django API (`/api/bot/`):

### Patient Management
- `POST /api/bot/patient/upsert/` - создание/обновление пациента
- `POST /api/bot/patient/verify-iin/` - проверка ИИН
- `GET /api/bot/patient/by-telegram/{id}/` - получение пациента по Telegram ID

### Booking
- `GET /api/bot/branches/` - список филиалов
- `GET /api/bot/services/` - список услуг
- `GET /api/bot/doctors/` - список врачей
- `GET /api/bot/slots/` - доступные слоты
- `POST /api/bot/appointments/` - создание записи
- `GET /api/bot/appointments/my/` - мои записи
- `PATCH /api/bot/appointments/{id}/` - изменение записи
- `POST /api/bot/appointments/{id}/cancel/` - отмена записи

### Documents
- `GET /api/bot/documents/` - список документов
- `POST /api/bot/documents/generate/` - генерация документа
- `GET /api/bot/documents/{id}/download/` - скачивание документа

### Payments
- `POST /api/bot/payments/invoice/` - создание счёта
- `GET /api/bot/payments/{id}/status/` - статус оплаты
- `GET /api/bot/payments/balance/` - баланс пациента

### Feedback & Support
- `POST /api/bot/feedback/` - создание отзыва
- `POST /api/bot/support/ticket/` - создание тикета
- `GET /api/bot/support/faq/` - FAQ

## 🚀 Быстрый старт

### Предварительные требования

1. **Telegram Bot Token**
   - Создайте бота через [@BotFather](https://t.me/BotFather)
   - Сохраните полученный token

2. **Backend должен быть запущен**
   - Django API должен работать на `http://backend:8000`

### Шаг 1: Настройка переменных окружения

Откройте файл `.env` в корне проекта и настройте:

```env
# Telegram Bot Settings
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz  # Ваш токен от BotFather
TELEGRAM_BOT_API_SECRET=your-secret-key-123              # Секрет для API (придумайте сложный)

# Webhook (для production, оставьте пустым для development)
TELEGRAM_WEBHOOK_URL=
TELEGRAM_WEBHOOK_SECRET=change-this-webhook-secret

# Режим работы (false = polling для dev, true = webhook для prod)
USE_WEBHOOK=false

# Default organization ID
DEFAULT_ORGANIZATION_ID=1
```

### Шаг 2: Запуск через Docker Compose

```bash
# Запуск всех сервисов (включая бота)
docker-compose up -d

# Или только бота (если остальное уже запущено)
docker-compose up -d telegram_bot

# Просмотр логов бота
docker-compose logs -f telegram_bot

# Остановка
docker-compose stop telegram_bot
```

### Шаг 3: Проверка

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Бот должен ответить приветственным сообщением

## ⚙️ Настройка

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `TELEGRAM_BOT_TOKEN` | Token от @BotFather | - (обязательно) |
| `TELEGRAM_BOT_API_SECRET` | Секрет для Django API | `change-this-secret-in-production` |
| `DJANGO_API_URL` | URL Django API | `http://backend:8000` |
| `REDIS_HOST` | Redis хост | `redis` |
| `REDIS_PORT` | Redis порт | `6379` |
| `REDIS_DB` | Redis database | `1` |
| `USE_WEBHOOK` | Использовать webhook | `false` |
| `TELEGRAM_WEBHOOK_URL` | URL для webhook | - |
| `TELEGRAM_WEBHOOK_SECRET` | Секрет webhook | `change-this-webhook-secret` |
| `DEFAULT_ORGANIZATION_ID` | ID организации по умолчанию | `1` |

### Аутентификация

Бот использует Bearer token аутентификацию для общения с Django API:

```python
headers = {
    'Authorization': f'Bearer {TELEGRAM_BOT_API_SECRET}',
    'Content-Type': 'application/json'
}
```

**⚠️ Важно:** `TELEGRAM_BOT_API_SECRET` должен совпадать на обеих сторонах:
- В `.env` для бота
- В `.env` для backend (используется в `backend/apps/telegram_bot/permissions.py`)

## 🔄 Режимы работы

### Polling Mode (Development)

**Рекомендуется для разработки**

```env
USE_WEBHOOK=false
```

Бот сам опрашивает Telegram API каждые несколько секунд.

**Преимущества:**
- ✅ Простая настройка
- ✅ Работает локально
- ✅ Не требует публичного URL

**Недостатки:**
- ❌ Задержка в получении сообщений
- ❌ Дополнительная нагрузка на Telegram API

### Webhook Mode (Production)

**Рекомендуется для production**

```env
USE_WEBHOOK=true
TELEGRAM_WEBHOOK_URL=https://yourdomain.com
TELEGRAM_WEBHOOK_SECRET=your-secret-123
```

Telegram отправляет обновления на ваш сервер.

**Преимущества:**
- ✅ Мгновенная доставка сообщений
- ✅ Меньше нагрузки
- ✅ Масштабируемость

**Требования:**
- Публичный HTTPS URL
- Валидный SSL сертификат

## 🛠️ Разработка

### Локальная разработка без Docker

```bash
cd telegram_bot

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Настроить .env
cp ../.env .env

# Запустить бота
python main.py
```

### Структура обработчиков

Пример обработчика:

```python
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer('Привет! 👋')
```

### Добавление нового обработчика

1. Создайте файл в `handlers/` (например, `new_feature.py`)
2. Создайте Router и добавьте обработчики
3. Зарегистрируйте в `main.py`:

```python
from handlers import new_feature

# В функции create_dispatcher():
dp.include_router(new_feature.router)
```

### Состояния (FSM)

Для многошаговых диалогов используйте FSM:

```python
from aiogram.fsm.state import State, StatesGroup

class BookingStates(StatesGroup):
    waiting_for_branch = State()
    waiting_for_service = State()
    waiting_for_doctor = State()
    waiting_for_date = State()
```

### Локализация

Переводы хранятся в `locales/`:

```json
{
  "welcome": "Добро пожаловать!",
  "menu": {
    "booking": "📅 Записаться",
    "my_appointments": "📋 Мои записи"
  }
}
```

## 🚀 Production Deploy

### 1. Настройка webhook

```bash
# Установить webhook
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourdomain.com/api/bot/webhook/",
    "secret_token": "your-webhook-secret"
  }'

# Проверить webhook
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

### 2. Docker Compose для production

```yaml
telegram_bot:
  build: ./telegram_bot
  environment:
    - USE_WEBHOOK=true
    - TELEGRAM_WEBHOOK_URL=https://yourdomain.com
  restart: always
  deploy:
    replicas: 1
    resources:
      limits:
        cpus: '0.5'
        memory: 512M
```

### 3. Мониторинг

```bash
# Логи
docker-compose logs -f telegram_bot

# Статус
docker-compose ps telegram_bot

# Health check
docker inspect telegram_bot | grep Health
```

### 4. Безопасность

**Обязательно:**
- 🔒 Используйте сильные секреты для `TELEGRAM_BOT_API_SECRET`
- 🔒 Используйте HTTPS для webhook
- 🔒 Валидируйте `secret_token` в webhook
- 🔒 Ограничьте доступ к `/api/bot/` только для бота
- 🔒 Регулярно обновляйте зависимости

## 📊 Мониторинг и отладка

### Логи

Бот использует стандартное логирование Python:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Сообщение")
logger.warning("Предупреждение")
logger.error("Ошибка")
```

### Просмотр логов

```bash
# Последние 100 строк
docker-compose logs --tail=100 telegram_bot

# Следить за логами в реальном времени
docker-compose logs -f telegram_bot

# Логи с временными метками
docker-compose logs -t telegram_bot
```

### Health Check

Docker автоматически проверяет здоровье контейнера:

```bash
# Проверить статус
docker inspect telegram_bot | grep -A 10 Health
```

## 🐛 Troubleshooting

### Бот не отвечает

1. Проверьте, что контейнер запущен:
   ```bash
   docker-compose ps telegram_bot
   ```

2. Проверьте логи:
   ```bash
   docker-compose logs telegram_bot
   ```

3. Проверьте, что `TELEGRAM_BOT_TOKEN` правильный

4. Проверьте подключение к Redis:
   ```bash
   docker-compose exec telegram_bot python -c "import redis; r = redis.Redis(host='redis'); print(r.ping())"
   ```

### Backend недоступен

1. Проверьте, что backend запущен:
   ```bash
   docker-compose ps backend
   ```

2. Проверьте `DJANGO_API_URL` в `.env`

3. Проверьте `TELEGRAM_BOT_API_SECRET` (должен совпадать на обеих сторонах)

### Webhook не работает

1. Проверьте webhook info:
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
   ```

2. Убедитесь, что URL доступен из интернета

3. Проверьте SSL сертификат

4. Удалите webhook и используйте polling:
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
   ```

## 📚 Документация

- [Aiogram Documentation](https://docs.aiogram.dev/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Django API Documentation](../docs/telegram-bot.md)
- [Architecture](../docs/architecture.md)

## 🤝 Контрибьюция

1. Fork проекта
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменений (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📝 Лицензия

Этот проект является частью Medicine ERP системы.

---

**Вопросы?** Создайте issue в репозитории или свяжитесь с командой разработки.

