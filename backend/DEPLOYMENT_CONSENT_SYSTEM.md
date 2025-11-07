# Deployment Guide: Multi-Org Consent System

## Пошаговая инструкция по развёртыванию

### Этап 1: Подготовка окружения

#### 1.1 Обновить зависимости

```bash
cd backend
pip install -r requirements.txt
```

Новые зависимости:
- `cryptography==42.0.0` - для шифрования ИИН
- `bcrypt==4.1.2` - для хеширования OTP

#### 1.2 Сгенерировать ключи шифрования

```bash
python manage.py shell
```

```python
from cryptography.fernet import Fernet
import secrets

# Генерация ключа шифрования ИИН
encryption_key = Fernet.generate_key().decode()
print(f"IIN_ENCRYPTION_KEY={encryption_key}")

# Генерация соли для хеширования
salt = secrets.token_urlsafe(32)
print(f"IIN_HASH_SALT={salt}")

exit()
```

Скопируйте эти значения в `.env`.

#### 1.3 Обновить .env файл

Добавьте в `backend/.env`:

```bash
# Multi-Org Consent System
IIN_ENCRYPTION_KEY=<ваш-ключ-из-шага-1.2>
IIN_HASH_SALT=<ваша-соль-из-шага-1.2>
ENABLE_MULTI_ORG_CONSENT=true
CONSENT_OTP_TTL_MINUTES=10
CONSENT_GRANT_DEFAULT_DAYS=30
CONSENT_RATE_LIMIT_PER_DAY=3

# Telegram Bot (если еще не настроено)
TELEGRAM_BOT_TOKEN=<ваш-токен-бота>
TELEGRAM_BOT_API_SECRET=<случайная-строка>

# Redis (если еще не настроено)
REDIS_URL=redis://localhost:6379/0
```

### Этап 2: Миграции базы данных

#### 2.1 Создать миграции (если не созданы)

```bash
cd backend
python manage.py makemigrations patients
python manage.py makemigrations consent
python manage.py makemigrations ehr
```

#### 2.2 Применить миграции

```bash
python manage.py migrate
```

Ожидаемые миграции:
- `patients.0007_add_iin_encryption_fields` - Добавление iin_enc, iin_hash
- `consent.0001_initial` - Модели consent системы
- `ehr.0001_initial` - EHR модели

#### 2.3 Зашифровать существующие ИИН

**⚠️ ВАЖНО: Сделайте резервную копию БД перед этим шагом!**

```bash
# Превью (dry run)
python manage.py encrypt_existing_iins --dry-run

# Фактическое шифрование
python manage.py encrypt_existing_iins
```

### Этап 3: Проверка миграции данных

```bash
python manage.py shell
```

```python
from apps.patients.models import Patient

# Проверить, что ИИН зашифрованы
patient = Patient.objects.first()
print(f"ИИН зашифрован: {bool(patient.iin_enc)}")
print(f"ИИН хеш: {bool(patient.iin_hash)}")
print(f"ИИН маска: {patient.iin_masked}")

# Проверить дешифрование
decrypted = patient.iin_decrypted
print(f"Расшифрованный ИИН: {decrypted}")

exit()
```

### Этап 4: Настройка Telegram бота

#### 4.1 Обновить handlers

Бот уже содержит handlers для consent. Проверьте, что:
- `telegram_bot/handlers/consent.py` существует
- Роутер добавлен в `telegram_bot/main.py`

#### 4.2 Перезапустить бота

```bash
cd telegram_bot
python main.py
```

Или используйте PowerShell скрипт:
```bash
.\start_bot.ps1
```

### Этап 5: Запуск Celery

Для отправки OTP через Telegram нужен Celery worker:

```bash
cd backend
celery -A config worker -l info
```

В production используйте supervisor/systemd:

```ini
# /etc/supervisor/conf.d/medicine-celery.conf
[program:medicine-celery]
command=/path/to/venv/bin/celery -A config worker -l info
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
```

### Этап 6: Тестирование системы

#### 6.1 Запустить тесты

```bash
cd backend

# Все тесты
python manage.py test

# Только consent
python manage.py test apps.consent.tests

# Только EHR
python manage.py test apps.ehr.tests
```

#### 6.2 Ручное тестирование

**Сценарий 1: Запрос доступа**

1. В frontend перейдите на SchedulePage
2. Нажмите "🔐 Запрос доступа"
3. Введите ИИН пациента (который зарегистрирован в Telegram)
4. Выберите scopes и укажите причину
5. Отправьте запрос

**Проверка:** Пациент должен получить сообщение в Telegram с кнопками.

**Сценарий 2: OTP подтверждение**

1. В Telegram нажмите "✅ Разрешить"
2. Backend должен создать AccessGrant
3. Frontend должен показать "✅ Доступ предоставлен"

**Проверка:** Записи пациента доступны врачу из другой клиники.

#### 6.3 Проверить логи

```bash
# Django logs
tail -f backend/logs/django.log

# Celery logs
# (в консоли где запущен celery)

# Telegram bot logs
# (в консоли где запущен bot)
```

### Этап 7: Мониторинг и безопасность

#### 7.1 Проверить Audit Logs

```bash
python manage.py shell
```

```python
from apps.consent.models import AuditLog

# Последние 10 событий
for log in AuditLog.objects.all()[:10]:
    print(f"{log.created_at}: {log.action} - {log.patient.full_name} by {log.user}")

exit()
```

#### 7.2 Мониторинг подозрительной активности

```python
from apps.consent.models import AuditLog

# Поиск fraud events
fraud_logs = AuditLog.objects.filter(
    details__fraud_detected=True
)

for log in fraud_logs:
    print(f"⚠️ Fraud: {log.organization.name} - {log.user} - {log.details}")
```

#### 7.3 Проверить rate limiting

```bash
# В Redis CLI
redis-cli

# Посмотреть ключи rate limiting
KEYS consent:rate:*
KEYS consent:denials:*

# Посмотреть значение
GET consent:rate:1:5

# Сбросить rate limit для тестирования
DEL consent:rate:1:5
```

### Этап 8: Production настройки

#### 8.1 Отключить DEBUG

В `backend/.env`:
```bash
DEBUG=False
```

#### 8.2 Настроить HTTPS

Убедитесь, что используется HTTPS для:
- Backend API
- Telegram webhook (если используется)
- Frontend

#### 8.3 Backup ключей шифрования

**⚠️ КРИТИЧЕСКИ ВАЖНО:**

Сохраните `IIN_ENCRYPTION_KEY` и `IIN_HASH_SALT` в безопасном месте!

Без этих ключей:
- ❌ Невозможно расшифровать ИИН
- ❌ Невозможно найти пациентов по ИИН
- ❌ Данные будут потеряны безвозвратно

Рекомендации:
1. Хранить в защищённом хранилище (Vault, AWS Secrets Manager)
2. Создать офлайн backup (зашифрованный USB)
3. Никогда не коммитить в Git

#### 8.4 Настроить логирование

Убедитесь, что логи AuditLog:
- Регулярно архивируются
- Доступны только администраторам
- Хранятся минимум 3 года (требование законодательства РК)

### Этап 9: Rollback план

Если что-то пошло не так:

#### 9.1 Откатить миграции

```bash
# Откатить до предыдущей версии
python manage.py migrate patients 0006
python manage.py migrate consent zero
python manage.py migrate ehr zero
```

#### 9.2 Восстановить данные

```bash
# Из backup БД
pg_restore -d medicine_db backup_before_consent.dump
```

#### 9.3 Отключить функциональность

В `backend/.env`:
```bash
ENABLE_MULTI_ORG_CONSENT=false
```

Система продолжит работать с legacy логикой (patient.organization).

## Troubleshooting

### Проблема: Миграции не применяются

```bash
# Показать статус миграций
python manage.py showmigrations

# Применить конкретное приложение
python manage.py migrate consent
python manage.py migrate ehr
```

### Проблема: Ошибка импорта cryptography

```bash
# Установить заново
pip uninstall cryptography
pip install cryptography==42.0.0

# Для Windows может потребоваться Visual C++
# Скачайте: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### Проблема: Redis не доступен

```bash
# Проверить Redis
redis-cli ping
# Должно вернуть: PONG

# Запустить Redis (Windows)
# Скачать: https://github.com/microsoftarchive/redis/releases
redis-server

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### Проблема: OTP не отправляется

Проверьте:
1. ✅ Celery worker запущен
2. ✅ TELEGRAM_BOT_TOKEN правильный
3. ✅ Пациент привязал Telegram
4. ✅ task `send_consent_request` в queue

```bash
# Проверить Celery
celery -A config inspect active
```

## Мониторинг production

### Метрики для отслеживания

1. **Запросы доступа**
   - Количество в день/неделю
   - Процент одобрений
   - Среднее время подтверждения

2. **Fraud события**
   - Количество блокировок
   - Организации с высокой активностью
   - Ночные запросы

3. **Performance**
   - Время ответа API
   - Redis hit rate
   - Размер AuditLog таблицы

### Настроить алерты

```python
# В apps/consent/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.consent.models import AuditLog

@receiver(post_save, sender=AuditLog)
def check_fraud_alert(sender, instance, created, **kwargs):
    if created and instance.details.get('fraud_detected'):
        # Отправить email/Telegram админу
        from django.core.mail import mail_admins
        mail_admins(
            'Fraud Alert',
            f"Suspicious activity: {instance.organization.name} - {instance.user}"
        )
```

## Готово! ✅

Система развёрнута и готова к использованию.

Следующие шаги:
1. Обучить персонал работе с системой
2. Настроить мониторинг
3. Запустить в pilot mode для одной организации
4. Собрать feedback и оптимизировать

