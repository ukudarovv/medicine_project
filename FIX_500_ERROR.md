# ⚠️ ИСПРАВЛЕНИЕ ОШИБКИ 500

## Проблема

Backend возвращает ошибку 500 при загрузке пациентов и календаря.

**Причина:** Новые поля были добавлены в модели, но миграции еще не применены к базе данных.

---

## ✅ РЕШЕНИЕ (3 шага)

### Шаг 1: Применить миграции

```bash
# Перейти в backend директорию
cd backend

# Применить все миграции
python manage.py migrate patients
python manage.py migrate visits  
python manage.py migrate calendar
python manage.py migrate comms
python manage.py migrate billing

# Или применить все сразу
python manage.py migrate

# Загрузить KATO справочник
python manage.py loaddata kato
```

**Ожидаемый результат:**
```
Running migrations:
  Applying patients.0005_add_kz_identity_fields... OK
  Applying patients.0006_add_sprint3_models... OK
  Applying visits.0003_add_sprint2_fields... OK
  Applying calendar.0003_add_waitlist... OK
  Applying comms.0004_add_patient_contact... OK
  Applying billing.0004_add_sprint4_models... OK
```

### Шаг 2: Перезапустить backend сервер

```bash
# Остановить (Ctrl+C) и запустить заново
python manage.py runserver

# Или если используете Docker
docker-compose restart backend
```

### Шаг 3: Обновить Frontend

```bash
# В браузере:
Ctrl + F5  # Hard refresh
Или
Очистить кэш браузера
```

---

## 🔍 ПРОВЕРКА

После применения миграций проверьте:

### 1. Backend работает:
```bash
curl http://localhost:8000/api/patients/patients/
# Должен вернуть JSON без ошибок
```

### 2. Новые поля в БД:
```sql
-- Подключитесь к PostgreSQL
psql -U postgres -d medicine_erp

-- Проверьте поля Patient
\d patients;

-- Должны быть поля:
-- iin_verified
-- kato_address
-- osms_status
-- osms_category
```

### 3. Frontend загружается:
- Откройте http://localhost:5173
- Перейдите на страницу "Пациенты"
- Должен загрузиться список без ошибок 500

---

## ❌ АЛЬТЕРНАТИВА: Откатить изменения

Если миграции не применяются или возникают другие проблемы:

```bash
# Вернуться к предыдущей версии
git checkout HEAD~1

# Перезапустить backend
python manage.py runserver
```

---

## 🐛 TROUBLESHOOTING

### Ошибка: "No such table"
**Решение:** Запустите `python manage.py migrate`

### Ошибка: "Column does not exist"
**Решение:** 
```bash
python manage.py migrate patients --fake-initial
python manage.py migrate patients
```

### Ошибка: "Dependency error"
**Решение:** Примените миграции по порядку:
```bash
python manage.py migrate patients 0005
python manage.py migrate patients 0006
python manage.py migrate visits 0003
python manage.py migrate calendar 0003
python manage.py migrate comms 0004
python manage.py migrate billing 0004
```

### Backend не запускается
**Решение:**
```bash
# Проверьте логи
python manage.py check
python manage.py showmigrations

# Проверьте PostgreSQL
docker-compose ps
# Должен быть running
```

### Frontend всё еще показывает 500
**Решение:**
1. Очистите кэш браузера (Ctrl+Shift+Delete)
2. Проверьте консоль браузера (F12)
3. Проверьте Network tab - какой точно endpoint возвращает 500
4. Проверьте backend logs в терминале

---

## 📋 CHECKLIST

После исправления проверьте:

- [ ] `python manage.py migrate` выполнена успешно
- [ ] Backend запущен без ошибок
- [ ] `curl http://localhost:8000/api/patients/patients/` возвращает JSON
- [ ] Frontend загружает страницу Пациенты без ошибок
- [ ] В консоли браузера нет ошибок 500
- [ ] Можно создать нового пациента

---

## 📞 ЕЩЕ ПОМОЩЬ?

### Если проблема не решена:

1. **Соберите информацию:**
   - Backend logs (из терминала где runserver)
   - Browser console errors (F12 → Console)
   - Network tab (F12 → Network → ошибочный запрос)

2. **Проверьте:**
```bash
# Backend статус
python manage.py check

# Список миграций
python manage.py showmigrations

# Тест БД подключения
python manage.py shell
>>> from apps.patients.models import Patient
>>> Patient.objects.count()
```

3. **Создайте issue на GitHub** с полной информацией

---

## ⚡ БЫСТРОЕ ИСПРАВЛЕНИЕ

Если нет времени разбираться, выполните эти команды последовательно:

```bash
cd backend
python manage.py migrate
python manage.py loaddata kato
python manage.py runserver
```

В другом терминале:
```bash
cd frontend
npm run dev
```

Откройте http://localhost:5173 и обновите страницу (Ctrl+F5).

**Должно заработать! ✅**

---

**Created:** November 4, 2025  
**Issue:** 500 Internal Server Error  
**Solution:** Apply migrations

