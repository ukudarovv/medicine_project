# Quick Start: Multi-Org Consent System

## ⚡ Быстрый старт за 5 минут

### Шаг 1: Установка зависимостей (1 минута)

```bash
cd backend
pip install cryptography==42.0.0 bcrypt==4.1.2
```

### Шаг 2: Генерация ключей (30 секунд)

```bash
python manage.py shell
```

```python
from cryptography.fernet import Fernet
import secrets

# Копируйте эти строки в .env
print("IIN_ENCRYPTION_KEY=" + Fernet.generate_key().decode())
print("IIN_HASH_SALT=" + secrets.token_urlsafe(32))
exit()
```

### Шаг 3: Обновить .env (30 секунд)

Добавьте строки из Шага 2 в `backend/.env`

### Шаг 4: Миграции (1 минута)

```bash
python manage.py migrate
```

### Шаг 5: Зашифровать ИИН (опционально, 1 минута)

Если у вас уже есть пациенты:

```bash
python manage.py encrypt_existing_iins --dry-run  # Превью
python manage.py encrypt_existing_iins            # Выполнить
```

### Шаг 6: Запуск (1 минута)

Откройте 4 терминала:

```bash
# Terminal 1 - Django
cd backend
python manage.py runserver

# Terminal 2 - Celery
cd backend  
celery -A config worker -l info

# Terminal 3 - Telegram Bot
cd telegram_bot
python main.py

# Terminal 4 - Frontend
cd frontend
npm run dev
```

## ✅ Готово!

Откройте http://localhost:5173 и нажмите кнопку "🔐 Запрос доступа" в расписании.

## 🧪 Тест системы

### Быстрый тест

1. **Создать тестового пациента с ИИН:**
   - Admin: http://localhost:8000/admin/patients/patient/add/
   - ИИН: 900101300123 (тестовый)

2. **Привязать Telegram:**
   - В боте: /start
   - Зарегистрироваться с тем же ИИН

3. **Запросить доступ:**
   - Frontend → SchedulePage → "🔐 Запрос доступа"
   - Ввести ИИН: 900101300123

4. **Подтвердить в Telegram:**
   - Получить сообщение с OTP
   - Нажать "✅ Разрешить"

5. **Проверить доступ:**
   - Frontend должен показать "Доступ предоставлен"
   - В боте: /my_access - увидеть список

## 🔧 Troubleshooting

**OTP не приходит?**
→ Проверьте, что Celery запущен и TELEGRAM_BOT_TOKEN правильный

**Ошибка шифрования?**
→ Проверьте IIN_ENCRYPTION_KEY в .env

**403 Forbidden?**
→ Проверьте, что у пользователя есть role='doctor' или 'registrar'

**Redis ошибка?**
→ Запустите Redis: `redis-server` или `docker run -d -p 6379:6379 redis:alpine`

## 📚 Дополнительно

Полная документация: `backend/README_CONSENT_SYSTEM.md`  
Deployment guide: `backend/DEPLOYMENT_CONSENT_SYSTEM.md`

