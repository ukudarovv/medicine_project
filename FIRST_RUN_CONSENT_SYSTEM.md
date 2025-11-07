# 🎬 Первый запуск Multi-Org Consent System

## Пошаговая инструкция для первого запуска

### Предварительные требования

✅ Python 3.10+  
✅ PostgreSQL 14+  
✅ Redis 6+  
✅ Node.js 18+ (для frontend)  
✅ Telegram Bot Token

---

## Шаг 1: Подготовка Backend

### 1.1 Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

**Новые критические зависимости:**
- `cryptography==42.0.0` - Шифрование ИИН
- `bcrypt==4.1.2` - OTP хеширование

### 1.2 Генерация ключей безопасности

```bash
python -c "from cryptography.fernet import Fernet; print('IIN_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

Сохраните вывод! Пример:
```
IIN_ENCRYPTION_KEY=mR3K8vN9pQ2wX7yZ...
```

```bash
python -c "import secrets; print('IIN_HASH_SALT=' + secrets.token_urlsafe(32))"
```

Сохраните вывод! Пример:
```
IIN_HASH_SALT=xY9zK3mN7...
```

### 1.3 Настройка .env

Создайте/обновите `backend/.env`:

```bash
# Django
DEBUG=True
SECRET_KEY=your-django-secret-key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/medicine_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Telegram Bot
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_API_SECRET=change-this-to-random-string

# ⚠️ КРИТИЧНО - Вставьте ключи из шага 1.2
IIN_ENCRYPTION_KEY=mR3K8vN9pQ2wX7yZ...
IIN_HASH_SALT=xY9zK3mN7...

# Consent Settings
ENABLE_MULTI_ORG_CONSENT=true
CONSENT_OTP_TTL_MINUTES=10
CONSENT_GRANT_DEFAULT_DAYS=30
CONSENT_RATE_LIMIT_PER_DAY=3
```

### 1.4 Проверка Redis

```bash
# Проверить, что Redis запущен
redis-cli ping
```

Должно вернуть: `PONG`

Если нет:
```bash
# Windows: скачать https://github.com/microsoftarchive/redis/releases
redis-server

# Docker:
docker run -d -p 6379:6379 redis:alpine

# Linux:
sudo systemctl start redis
```

---

## Шаг 2: Миграции базы данных

### 2.1 Применить миграции

```bash
cd backend
python manage.py migrate
```

Ожидаемый вывод:
```
Running migrations:
  Applying patients.0007_add_iin_encryption_fields... OK
  Applying consent.0001_initial... OK
  Applying ehr.0001_initial... OK
```

### 2.2 Проверить созданные таблицы

```bash
python manage.py dbshell
```

```sql
-- Проверить таблицы consent системы
\dt consent*

-- Должны быть:
-- consent_access_requests
-- consent_tokens
-- consent_access_grants
-- consent_audit_logs

-- Проверить таблицу EHR
\dt ehr_records

-- Проверить поля Patient
\d patients
-- Должны быть: iin_enc, iin_hash

\q
```

### 2.3 Зашифровать существующие ИИН (если есть данные)

```bash
# Превью - что будет зашифровано
python manage.py encrypt_existing_iins --dry-run
```

Вывод покажет:
```
Found 150 patients with plain IINs to encrypt
Would encrypt IIN for patient #1: Иванов Иван
Would encrypt IIN for patient #2: Петров Пётр
...
DRY RUN: Would encrypt 150 patients
```

**Если всё ОК, выполняем:**

```bash
python manage.py encrypt_existing_iins
```

Ожидаемый вывод:
```
Found 150 patients with plain IINs to encrypt
✓ Encrypted IIN for patient #1: Иванов Иван
✓ Encrypted IIN for patient #2: Петров Пётр
...
Successfully encrypted 150 patients
```

---

## Шаг 3: Создание тестовых данных

### 3.1 Создать суперпользователя (если нет)

```bash
python manage.py createsuperuser
```

### 3.2 Создать тестовые организации

```bash
python manage.py shell
```

```python
from apps.org.models import Organization, Branch

# Организация 1
org1 = Organization.objects.create(name='Клиника Здоровье')
branch1 = Branch.objects.create(
    organization=org1,
    name='Филиал №1',
    address='ул. Абая, 1'
)

# Организация 2  
org2 = Organization.objects.create(name='Медицинский центр Vita')
branch2 = Branch.objects.create(
    organization=org2,
    name='Центральный филиал',
    address='пр. Достык, 10'
)

print(f"Org 1 ID: {org1.id}")
print(f"Org 2 ID: {org2.id}")

exit()
```

### 3.3 Создать тестовых пользователей

```bash
python manage.py shell
```

```python
from apps.core.models import User
from apps.org.models import Organization

org1 = Organization.objects.get(name='Клиника Здоровье')
org2 = Organization.objects.get(name='Медицинский центр Vita')

# Врач из Org 1
doctor1 = User.objects.create_user(
    username='doctor1',
    email='doctor1@clinic.kz',
    password='test123',
    organization=org1,
    role='doctor',
    first_name='Алия',
    last_name='Ахметова'
)

# Врач из Org 2
doctor2 = User.objects.create_user(
    username='doctor2',
    email='doctor2@vita.kz',
    password='test123',
    organization=org2,
    role='doctor',
    first_name='Данияр',
    last_name='Каримов'
)

print(f"Doctor 1 (Org 1): {doctor1.username}")
print(f"Doctor 2 (Org 2): {doctor2.username}")

exit()
```

### 3.4 Создать тестового пациента

```bash
python manage.py shell
```

```python
from apps.patients.models import Patient
from apps.org.models import Organization

org1 = Organization.objects.get(name='Клиника Здоровье')

# Пациент с ИИН
patient = Patient.objects.create(
    organization=org1,
    first_name='Асель',
    last_name='Нурланова',
    middle_name='Ерлановна',
    birth_date='1995-05-15',
    sex='F',
    phone='+77771234567'
)

# Установить ИИН (автоматически зашифруется)
patient.set_iin('950515450789')
patient.save()

print(f"Patient ID: {patient.id}")
print(f"ИИН зашифрован: {bool(patient.iin_enc)}")
print(f"ИИН маска: {patient.iin_masked}")

exit()
```

---

## Шаг 4: Запуск сервисов

### 4.1 Backend (Terminal 1)

```bash
cd backend
python manage.py runserver
```

Ожидаемый вывод:
```
Django version 5.0.1, using settings 'config.settings.development'
Starting development server at http://127.0.0.1:8000/
```

Проверка: http://localhost:8000/admin/ должен открыться

### 4.2 Celery Worker (Terminal 2)

```bash
cd backend
celery -A config worker -l info
```

Ожидаемый вывод:
```
[tasks]
  . apps.telegram_bot.tasks.send_consent_request
  . apps.telegram_bot.tasks.send_consent_approved_notification
  
celery@hostname ready.
```

### 4.3 Telegram Bot (Terminal 3)

```bash
cd telegram_bot
python main.py
```

Ожидаемый вывод:
```
INFO - Bot starting...
INFO - Using polling mode
INFO - Bot started successfully
```

### 4.4 Frontend (Terminal 4)

```bash
cd frontend
npm run dev
```

Ожидаемый вывод:
```
VITE v4.x.x ready in xxx ms
Local:   http://localhost:5173/
```

---

## Шаг 5: Первый тест системы

### 5.1 Привязать Telegram к пациенту

1. Откройте вашего Telegram бота
2. Отправьте `/start`
3. Пройдите регистрацию:
   - Имя: Асель
   - Фамилия: Нурланова
   - Телефон: +77771234567
   - Дата рождения: 15.05.1995
   - Пол: Женский
   - ИИН: **950515450789**

4. Подтвердите согласия

### 5.2 Запросить доступ через Frontend

1. Откройте http://localhost:5173
2. Войдите как **doctor2** (из Org 2)
   - Username: `doctor2`
   - Password: `test123`

3. Перейдите на "Расписание"

4. Нажмите кнопку **"🔐 Запрос доступа"**

5. Введите ИИН: **950515450789**

6. Нажмите "Найти пациента"

7. Проверьте:
   - ✅ Показывается: "Нурланова А* Е."
   - ✅ Возраст: 30 лет
   - ✅ Telegram: Подключен

8. Нажмите "Продолжить"

9. Выберите scopes:
   - ✅ Чтение краткой информации
   - ✅ Чтение медицинских записей

10. Причина: "Консультация терапевта"

11. Нажмите "Отправить запрос"

### 5.3 Подтвердить в Telegram

1. Откройте Telegram (как пациент Асель)

2. Вы должны получить сообщение:
```
🏥 Запрос доступа к вашей медицинской карте

Организация: Медицинский центр Vita
Причина: Консультация терапевта

Запрашиваемый доступ:
• Чтение краткой информации
• Чтение медицинских записей

Код подтверждения: 123456

[✅ Разрешить] [❌ Отклонить]
```

3. Нажмите **"✅ Разрешить"**

### 5.4 Проверить результат

**В Frontend:**
- Должно показать: "✅ Доступ предоставлен"
- Показывается срок действия

**В Telegram:**
- Получите подтверждение: "✅ Доступ предоставлен"
- Команда `/my_access` покажет список доступов

**В Admin:**
- http://localhost:8000/admin/consent/accessgrant/
- Должен быть 1 grant со статусом active

**В Logs:**
- `backend/logs/django.log` - должны быть записи о создании grant

---

## Шаг 6: Проверка функциональности

### 6.1 Проверить EHR API

```bash
# Получить token для doctor2
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "doctor2", "password": "test123"}'

# Копируйте access token
TOKEN="<ваш-токен>"

# Запросить записи пациента (с внешними)
curl -X GET "http://localhost:8000/api/v1/ehr/records/?patient_id=<patient-id>&include_external=true" \
  -H "Authorization: Bearer $TOKEN"
```

### 6.2 Проверить Audit Log

```bash
python manage.py shell
```

```python
from apps.consent.models import AuditLog

# Показать последние события
for log in AuditLog.objects.all()[:5]:
    print(f"{log.created_at}: {log.action} - {log.patient.full_name} by {log.user or 'Patient'}")

# Должны быть:
# - 'request' - создание запроса
# - 'share' - предоставление доступа

exit()
```

### 6.3 Проверить Rate Limiting

```bash
redis-cli
```

```redis
# Посмотреть rate limit ключи
KEYS consent:rate:*

# Пример вывода:
# 1) "consent:rate:2:1"

# Посмотреть значение
GET consent:rate:2:1
# → "1" (один запрос использован)

# Посмотреть TTL
TTL consent:rate:2:1
# → 86399 (секунд до сброса)

quit
```

### 6.4 Проверить Fraud Detection

Попробуйте сделать 11 запросов за час от одного пользователя:

```bash
# Должен сработать fraud detector
# В логах появится: "Массовые запросы от пользователя doctor2"
```

---

## Шаг 7: Тестирование всех сценариев

### Сценарий 1: ✅ Успешный доступ
1. Врач запрашивает → 2. Пациент одобряет → 3. Доступ предоставлен

**Ожидаемый результат:**
- AccessRequest.status = 'approved'
- AccessGrant создан
- AuditLog имеет 2 записи (request + share)

### Сценарий 2: ❌ Отказ пациента
1. Врач запрашивает → 2. Пациент отклоняет

**Ожидаемый результат:**
- AccessRequest.status = 'denied'
- AccessGrant НЕ создан
- Denial counter увеличен в Redis
- AuditLog имеет 2 записи (request + deny)

### Сценарий 3: ⏰ Истечение времени
1. Врач запрашивает → 2. Пациент не отвечает 10 минут

**Ожидаемый результат:**
- AccessRequest.status = 'expired'
- Можно отправить новый запрос

### Сценарий 4: 🚫 Rate Limit
1. Врач делает 4 запроса за день к одному пациенту

**Ожидаемый результат:**
- 4-й запрос отклоняется с ошибкой: "Превышен лимит"

### Сценарий 5: 🔒 Denial Lockout
1. Пациент отклоняет 3 запроса подряд

**Ожидаемый результат:**
- 4-й запрос блокируется на 1 час

### Сценарий 6: 📝 Whitelist
1. Пациент в Telegram создаёт whitelist для клиники
2. Врач из этой клиники запрашивает доступ

**Ожидаемый результат:**
- Доступ предоставляется автоматически (без OTP)
- Или: требуется 1 OTP, затем долгий доступ

---

## Шаг 8: Мониторинг и логи

### 8.1 Проверить Django логи

```bash
tail -f backend/logs/django.log
```

Должны быть записи:
```
INFO ... Created AccessRequest ...
INFO ... Sent OTP to Telegram ...
INFO ... AccessGrant created ...
```

### 8.2 Проверить Celery логи

В терминале где запущен Celery:

```
[INFO/MainProcess] Task apps.telegram_bot.tasks.send_consent_request succeeded in 0.5s
```

### 8.3 Проверить Telegram Bot логи

```
INFO - Received callback: consent_approve:...
INFO - OTP verified successfully
INFO - Grant created: ...
```

### 8.4 Мониторинг через Admin

http://localhost:8000/admin/

- **Consent → Access Requests** - Все запросы
- **Consent → Access Grants** - Активные гранты
- **Consent → Audit Logs** - История доступа (READ ONLY)
- **EHR → EHR Records** - Медицинские записи

---

## Шаг 9: Проверка безопасности

### 9.1 Попытка доступа без гранта

```python
python manage.py shell
```

```python
from apps.ehr.models import EHRRecord
from apps.core.models import User

doctor2 = User.objects.get(username='doctor2')
patient = Patient.objects.first()

# Попытка создать запись без гранта
# (в production это будет заблокировано в middleware)

exit()
```

### 9.2 Проверить шифрование в БД

```bash
python manage.py dbshell
```

```sql
-- Посмотреть зашифрованные ИИН
SELECT id, last_name, iin, iin_enc, iin_hash 
FROM patients 
LIMIT 5;

-- iin_enc должен быть: gAAAAABl... (зашифрован)
-- iin_hash должен быть: a3f2c1... (хеш)
-- iin может быть пустым или легаси

\q
```

### 9.3 Проверить иммутабельность Audit Log

```python
python manage.py shell
```

```python
from apps.consent.models import AuditLog

log = AuditLog.objects.first()

# Попытка изменить
try:
    log.action = 'write'
    log.save()
    print("❌ ERROR: Audit log was modified!")
except Exception as e:
    print(f"✅ OK: Cannot modify audit log - {e}")

# Попытка удалить
try:
    log.delete()
    print("❌ ERROR: Audit log was deleted!")
except Exception as e:
    print(f"✅ OK: Cannot delete audit log - {e}")

exit()
```

---

## Шаг 10: Production готовность

### 10.1 Чеклист перед production

```bash
# Запустить все тесты
python manage.py test apps.consent apps.ehr

# Результат должен быть:
# Ran 15 tests in X.XXXs
# OK
```

### 10.2 Изменить настройки для production

В `backend/.env`:

```bash
# Обязательно изменить:
DEBUG=False
SECRET_KEY=<новый-случайный-ключ>
ALLOWED_HOSTS=your-domain.kz

# Проверить:
IIN_ENCRYPTION_KEY=<надёжно сохранён>
IIN_HASH_SALT=<надёжно сохранён>
```

### 10.3 Backup критических данных

**⚠️ СОХРАНИТЕ ЭТИ ДАННЫЕ В БЕЗОПАСНОМ МЕСТЕ:**

1. `IIN_ENCRYPTION_KEY` - БЕЗ НЕГО ИИН НЕ РАСШИФРУЮТСЯ!
2. `IIN_HASH_SALT` - БЕЗ НЕГО ПОИСК НЕ РАБОТАЕТ!
3. Database backup
4. Redis dump (если используете persistence)

---

## 🎉 Готово!

Система полностью развёрнута и протестирована.

### Следующие действия:

1. ✅ Обучить персонал
2. ✅ Запустить pilot с 1-2 организациями
3. ✅ Собрать feedback
4. ✅ Настроить мониторинг
5. ✅ Запланировать регулярные backups

### Быстрая справка команд

```bash
# Статус миграций
python manage.py showmigrations consent ehr

# Зашифровать ИИН
python manage.py encrypt_existing_iins

# Проверить Redis
redis-cli KEYS "consent:*"

# Запустить тесты
python manage.py test apps.consent apps.ehr

# Просмотр логов
tail -f backend/logs/django.log

# Celery tasks
celery -A config inspect active
```

### Полезные ссылки

- API Docs: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/
- Frontend: http://localhost:5173/

---

## 📞 Поддержка

При проблемах:

1. Проверить логи: `backend/logs/django.log`
2. Проверить Redis: `redis-cli ping`
3. Проверить Celery: `celery -A config inspect active`
4. Запустить тесты: `python manage.py test apps.consent`
5. Изучить документацию: `README_CONSENT_SYSTEM.md`

---

## ✨ Успешный запуск!

Система работает и готова обслуживать пациентов! 🚀

**Основные возможности доступны:**
- ✅ Межорганизационный доступ к медкартам
- ✅ OTP подтверждение через Telegram
- ✅ Управление доступами пациентом
- ✅ Полный audit trail
- ✅ Rate limiting и fraud protection
- ✅ Whitelist для постоянных врачей

**Enjoy! 🎊**

