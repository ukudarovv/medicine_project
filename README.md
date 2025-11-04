# Medicine ERP - ERP/МИС система для стоматологий

Полнофункциональная ERP/МИС система для управления сетью стоматологических клиник.

## Возможности

- 📅 Расписание и календарь с real-time обновлениями
- 👥 Управление пациентами
- 🦷 Справочник услуг и процедур
- 👨‍⚕️ Управление персоналом
- 💰 Финансы и биллинг
- 📦 Складской учёт
- 📧 Коммуникации и напоминания (SMS/Email)
- 📊 Отчёты и аналитика
- 🏢 Multi-tenant (несколько организаций/филиалов)

## Технологии

### Backend
- Django 5
- Django REST Framework
- PostgreSQL 16
- Redis
- Celery
- Django Channels (WebSocket)
- JWT Authentication

### Frontend
- Vue 3
- Vite
- Pinia
- Naive UI
- Axios

## Быстрый старт

### Требования
- Docker
- Docker Compose
- Make (опционально)

### Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ukudarovv/medicine_project.git
cd medicine_project
```

2. Скопируйте файл окружения:
```bash
cp env.example .env
```

3. Запустите проект:
```bash
make build
make up
```

Или без Make:
```bash
docker-compose build
docker-compose up -d
```

4. Выполните миграции:
```bash
make migrate
```

5. Создайте суперпользователя:
```bash
make createsuperuser
```

6. Загрузите тестовые данные (опционально):
```bash
make seed
```

Приложение будет доступно по адресам:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

## Команды Makefile

- `make up` - Запустить все сервисы
- `make down` - Остановить все сервисы
- `make build` - Собрать Docker образы
- `make migrate` - Выполнить миграции
- `make makemigrations` - Создать миграции
- `make seed` - Загрузить тестовые данные
- `make test` - Запустить тесты
- `make lint` - Проверить код линтерами
- `make format` - Форматировать код
- `make shell` - Открыть Django shell
- `make logs` - Показать логи
- `make clean` - Очистить контейнеры и volumes

## Структура проекта

```
medicine_project/
├── backend/              # Django backend
│   ├── apps/            # Django приложения
│   │   ├── core/        # Ядро (auth, permissions)
│   │   ├── org/         # Организации и филиалы
│   │   ├── staff/       # Персонал
│   │   ├── patients/    # Пациенты
│   │   ├── services/    # Услуги
│   │   ├── calendar/    # Расписание
│   │   ├── visits/      # Визиты
│   │   ├── billing/     # Финансы
│   │   ├── warehouse/   # Склад
│   │   ├── comms/       # Коммуникации
│   │   └── reports/     # Отчёты
│   ├── config/          # Настройки Django
│   └── requirements.txt
├── frontend/            # Vue 3 frontend
│   ├── src/
│   │   ├── api/         # API клиенты
│   │   ├── components/  # Vue компоненты
│   │   ├── layouts/     # Layouts
│   │   ├── pages/       # Страницы
│   │   ├── stores/      # Pinia stores
│   │   └── styles/      # Стили
│   └── package.json
├── docker-compose.yml
├── Makefile
└── README.md
```

## API Документация

API документация доступна по адресу: http://localhost:8000/api/docs/

Основные эндпоинты:

### Аутентификация
- `POST /api/v1/auth/login` - Вход
- `POST /api/v1/auth/refresh` - Обновление токена
- `GET /api/v1/auth/me` - Профиль пользователя

### Организация
- `GET/POST /api/v1/org/branches` - Филиалы
- `GET/PATCH /api/v1/org/settings` - Настройки клиники

### Персонал
- `GET/POST /api/v1/staff/employees` - Сотрудники

### Пациенты
- `GET/POST /api/v1/patients` - Пациенты

### Услуги
- `GET/POST /api/v1/services` - Услуги
- `GET/POST /api/v1/services/categories` - Категории услуг

### Расписание
- `GET/POST /api/v1/calendar/appointments` - Записи
- WebSocket: `ws://localhost:8001/ws/calendar?branch={id}` - Real-time события

### Визиты
- `GET/POST /api/v1/visits` - Визиты

### Финансы
- `GET/POST /api/v1/billing/invoices` - Счета
- `POST /api/v1/billing/payments` - Платежи

### Склад
- `GET/POST /api/v1/warehouse/items` - Материалы

### Коммуникации
- `GET/POST /api/v1/comms/templates` - Шаблоны
- `POST /api/v1/comms/send` - Отправка сообщений

### Отчёты
- `GET /api/v1/reports/appointments` - Отчёт по визитам
- `GET /api/v1/reports/revenue` - Отчёт по выручке

## Разработка

### Backend разработка

```bash
# Установка зависимостей
cd backend
pip install -r requirements.txt

# Запуск dev сервера
python manage.py runserver

# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Запуск тестов
pytest

# Форматирование кода
black .
isort .
ruff check --fix .
```

### Frontend разработка

```bash
# Установка зависимостей
cd frontend
npm install

# Запуск dev сервера
npm run dev

# Сборка для production
npm run build

# Линтинг
npm run lint

# Форматирование
npm run format
```

## Тестирование

### Backend тесты
```bash
make test
# или
docker-compose exec backend pytest
```

### Frontend тесты
```bash
cd frontend
npm run test
```

### E2E тесты
```bash
cd frontend
npx playwright test
```

## Деплой

См. [docs/deployment.md](docs/deployment.md) для инструкций по деплою в production.

## Лицензия

MIT

## Поддержка

По вопросам обращайтесь: support@example.com

