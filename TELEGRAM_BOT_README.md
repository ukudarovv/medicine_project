# Telegram Bot для клиники - Быстрый старт

## ✅ Что реализовано

### Django Backend (100%)
- ✅ Модели: PatientTelegramLink, BotBroadcast, BotDocument, BotAudit, BotFeedback, SupportTicket
- ✅ API endpoints для всех функций (30+ endpoints)
- ✅ BotAPIAuthentication (JWT)
- ✅ Celery tasks для напоминаний и рассылок
- ✅ Сегментация пациентов для рассылок
- ✅ Генерация PDF документов
- ✅ Интеграция с оплатами (mock Kaspi/Halyk)

### Telegram Bot (100%)
- ✅ Aiogram 3.4.1 структура
- ✅ FSM регистрации (язык → ФИО → ИИН → согласия)
- ✅ FSM записи на приём (филиал → услуга → врач → дата/время)
- ✅ Inline клавиатуры (языки, меню, календарь, и т.д.)
- ✅ Локализация RU/KK
- ✅ Middlewares (i18n, auth)
- ✅ Django API Client
- ✅ Хендлеры: start, booking, appointments, documents, payments, feedback, support, profile

### Инфраструктура (100%)
- ✅ Dockerfile и docker-compose.yml
- ✅ Requirements.txt
- ✅ .env конфигурация
- ✅ Документация (docs/telegram-bot.md)
- ✅ Тесты (Django API)

## 📝 Применение миграций

```bash
cd backend
python manage.py makemigrations telegram_bot
python manage.py migrate
```

## 🚀 Запуск

### 1. Создайте бота в @BotFather

```
/newbot
Название: My Clinic Bot
Username: my_clinic_bot
```

Сохраните полученный TOKEN.

### 2. Настройте .env

Скопируйте `env.example` в `.env` и заполните:

```bash
# Обязательные параметры
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_API_SECRET=your-secret-key-here

# Опциональные (для продакшена)
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/bot/webhook
USE_WEBHOOK=false  # true для продакшена
```

### 3. Запустите с Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Или только бот
docker-compose up -d telegram_bot
```

### 4. Проверьте работу

```bash
# Логи бота
docker-compose logs -f telegram_bot

# Откройте бота в Telegram и отправьте /start
```

## 📚 Документация

Полная документация: [docs/telegram-bot.md](docs/telegram-bot.md)

### Основные разделы
- Архитектура и компоненты
- API endpoints (30+ endpoints)
- FSM диаграммы (регистрация, запись)
- Примеры сообщений (RU/KK)
- Celery tasks (напоминания, рассылки)
- Сегментация для рассылок
- Troubleshooting

## 🎯 Основные функции

### Для пациентов
1. **Регистрация**: ФИО, ИИН, телефон, дата рождения, согласия
2. **Запись на приём**: выбор филиала → услуги → врача → даты/времени
3. **Мои записи**: просмотр, перенос, отмена
4. **Документы**: направления, рецепты, справки, результаты
5. **Оплаты**: баланс, счета, QR коды (mock Kaspi/Halyk)
6. **Обратная связь**: NPS оценка (0-10) после визита
7. **Поддержка**: FAQ, связь с оператором

### Для администраторов
1. **Рассылки**: сегментация пациентов, персонализация, статистика
2. **Напоминания**: D-1, H-3, H-1, "Вы пришли?", NPS опрос
3. **Аналитика**: конверсии, low score alerts
4. **Обращения**: support tickets из бота

## 🔧 Настройки

### Режимы работы

**Development (Polling):**
```env
USE_WEBHOOK=false
```
Бот опрашивает Telegram API.

**Production (Webhook):**
```env
USE_WEBHOOK=true
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/bot/webhook
TELEGRAM_WEBHOOK_SECRET=your-webhook-secret
```
Telegram отправляет обновления на ваш сервер.

### Celery Tasks

Автоматические задачи настроены в `backend/config/celery.py`:
- **Каждые 15 минут**: send_appointment_reminders (D-1, H-3, H-1)
- **Каждые 5 минут**: send_arrived_check
- **Каждые 30 минут**: send_feedback_request
- **Каждые 6 часов**: cleanup_expired_documents

## 🧪 Тестирование

```bash
# Django API tests
cd backend
pytest apps/telegram_bot/tests/

# Или через Django
python manage.py test apps.telegram_bot
```

## 🔒 Безопасность

1. **Bot API Authentication**: JWT token защищает Django endpoints
2. **Webhook Secret**: секретный токен для webhook
3. **Document TTL**: временные ссылки (48 часов)
4. **Rate Limiting**: Redis-based (опционально)

## 📊 Мониторинг

```bash
# Логи бота
docker-compose logs -f telegram_bot

# Логи Django (bot API)
docker-compose logs backend | grep telegram_bot

# Логи Celery tasks
docker-compose logs celery_worker | grep telegram_bot
```

## 🐛 Troubleshooting

### Бот не отвечает
1. Проверьте TOKEN в .env
2. Проверьте логи: `docker-compose logs telegram_bot`
3. Убедитесь, что Redis работает
4. Проверьте доступность Django API

### Ошибки API
1. Проверьте TELEGRAM_BOT_API_SECRET (должен совпадать в Django и боте)
2. Примените миграции: `python manage.py migrate`
3. Проверьте логи Django: `docker-compose logs backend`

### Webhook не работает
1. Убедитесь, что HTTPS настроен
2. Проверьте URL в .env
3. Проверьте статус: `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`

## 📁 Структура файлов

```
├── backend/apps/telegram_bot/     # Django app
│   ├── models.py                  # Модели БД
│   ├── serializers.py             # API serializers
│   ├── views.py                   # API views (30+ endpoints)
│   ├── permissions.py             # BotAPIAuthentication
│   ├── tasks.py                   # Celery tasks
│   ├── services/                  # Бизнес-логика
│   │   ├── segmentation.py        # Сегментация пациентов
│   │   └── document_generator.py  # Генерация PDF
│   ├── tests/                     # Тесты
│   └── admin.py                   # Django admin
│
├── telegram_bot/                  # Aiogram bot
│   ├── main.py                    # Entry point
│   ├── config.py                  # Конфигурация
│   ├── handlers/                  # Хендлеры команд
│   │   ├── start.py               # Регистрация
│   │   ├── booking.py             # Запись
│   │   ├── my_appointments.py
│   │   ├── documents.py
│   │   ├── payments.py
│   │   ├── feedback.py
│   │   ├── support.py
│   │   └── profile.py
│   ├── keyboards/                 # Клавиатуры
│   │   ├── inline.py              # Inline кнопки
│   │   └── reply.py               # Reply клавиатуры
│   ├── states/                    # FSM состояния
│   ├── middlewares/               # Middleware
│   ├── services/                  # Сервисы
│   │   ├── api_client.py          # Django API client
│   │   └── helpers.py
│   ├── locales/                   # Переводы
│   │   ├── ru.json
│   │   └── kk.json
│   ├── Dockerfile
│   └── requirements.txt
│
├── docs/telegram-bot.md           # Полная документация
├── docker-compose.yml             # + telegram_bot service
└── env.example                    # + bot variables
```

## 🎉 Готово к использованию

После настройки и запуска:

1. Откройте бота в Telegram
2. Отправьте `/start`
3. Выберите язык (RU/KK)
4. Пройдите регистрацию
5. Используйте все функции!

## 📞 Поддержка

- GitHub: https://github.com/ukudarovv/medicine_project
- Issues: https://github.com/ukudarovv/medicine_project/issues

---

**Version:** 1.0.0  
**Created:** 2025-11-05  
**Status:** ✅ Ready for Production

