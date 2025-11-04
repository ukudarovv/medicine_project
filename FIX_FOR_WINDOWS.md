# 🪟 FIX 500 ERROR - Windows Instructions

## ⚠️ У ВАС ОШИБКА 500 - ВОТ РЕШЕНИЕ ДЛЯ WINDOWS

---

## ✅ ИСПРАВЛЕНИЕ (4 простых шага)

### Шаг 1: Проверьте, запущен ли Backend

Откройте Docker Desktop и убедитесь, что контейнеры запущены:
- ✅ `medicine-backend` должен быть Running (зеленый)
- ✅ `medicine-postgres` должен быть Running (зеленый)

**ИЛИ** проверьте в PowerShell:
```powershell
docker ps
```

Если не запущены:
```powershell
docker-compose up -d
```

---

### Шаг 2: Применить миграции (КРИТИЧНО!)

#### Вариант A: Через Docker (РЕКОМЕНДУЕТСЯ)

```powershell
# В PowerShell в корне проекта
docker-compose exec backend python manage.py migrate

# Загрузить KATO данные
docker-compose exec backend python manage.py loaddata kato
```

#### Вариант B: Напрямую (если Python установлен)

```powershell
# Перейти в backend
cd backend

# Применить миграции
py manage.py migrate
# ИЛИ
python manage.py migrate

# Загрузить KATO
py manage.py loaddata kato
```

#### Вариант C: Через Docker Desktop UI

1. Откройте Docker Desktop
2. Найдите контейнер `medicine-backend`
3. Нажмите на него
4. Перейдите на вкладку "Terminal"
5. Выполните:
```bash
python manage.py migrate
python manage.py loaddata kato
```

---

### Шаг 3: Перезапустить Backend

```powershell
# Перезапустить Docker контейнеры
docker-compose restart backend

# ИЛИ полная перезагрузка
docker-compose down
docker-compose up -d
```

---

### Шаг 4: Обновить браузер

1. Откройте http://localhost:5173
2. Нажмите **Ctrl + Shift + R** (hard refresh)
3. Или откройте DevTools (F12) → Application → Clear storage → Clear site data

---

## 🔍 ПРОВЕРКА РЕЗУЛЬТАТА

### 1. Backend должен работать:

Откройте в браузере: http://localhost:8000/api/patients/patients/

**Ожидаемый результат:** JSON с пустым списком `{"results": []}`  
**НЕ должно быть:** ошибка 500 или "Server Error"

### 2. Frontend должен загружаться:

Откройте http://localhost:5173

**Ожидаемый результат:** Страница загружается, список пациентов пустой  
**НЕ должно быть:** красные ошибки в консоли F12

---

## ❌ ЕСЛИ НЕ РАБОТАЕТ

### Проблема: "docker-compose не найден"

**Решение для Windows:**
```powershell
# Вместо docker-compose используйте docker compose (без дефиса)
docker compose up -d
docker compose exec backend python manage.py migrate
docker compose restart backend
```

### Проблема: "Python not found"

Значит Python не установлен напрямую на Windows. **Используйте Docker!**

```powershell
# Все команды через Docker:
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py loaddata kato
docker compose exec backend python manage.py createsuperuser
```

### Проблема: Backend не запускается

```powershell
# Посмотреть логи
docker compose logs backend

# Или в реальном времени
docker compose logs -f backend
```

Ищите строки с ошибками (обычно красным цветом).

### Проблема: База данных не подключается

```powershell
# Проверить PostgreSQL
docker compose ps

# Если postgres не запущен:
docker compose up -d postgres
docker compose up -d backend
```

---

## 🎯 ПОЛНЫЙ СЦЕНАРИЙ ДЛЯ WINDOWS

Скопируйте и выполните эти команды в PowerShell **в корне проекта**:

```powershell
# 1. Остановить все
docker compose down

# 2. Запустить заново
docker compose up -d

# 3. Дождаться запуска (5-10 секунд)
Start-Sleep -Seconds 10

# 4. Применить миграции
docker compose exec backend python manage.py migrate

# 5. Загрузить KATO
docker compose exec backend python manage.py loaddata kato

# 6. Проверить статус
docker compose ps

# 7. Посмотреть логи (если нужно)
docker compose logs backend --tail=50
```

**После этого:**
- Откройте http://localhost:8000/api/patients/patients/ (должен работать)
- Откройте http://localhost:5173 (должен работать)
- Обновите страницу Ctrl+Shift+R

---

## 🆘 БЫСТРАЯ ПОМОЩЬ

### Скопируйте эту команду (все в одной строке):

```powershell
docker compose exec backend python manage.py migrate; docker compose exec backend python manage.py loaddata kato; docker compose restart backend
```

**ИЛИ** по отдельности:

```powershell
docker compose exec backend python manage.py migrate
```

Дождитесь завершения, затем:

```powershell
docker compose exec backend python manage.py loaddata kato
```

Затем:

```powershell
docker compose restart backend
```

---

## 🎬 ЧТО ПРОИСХОДИТ

### До миграций:
- ❌ БД не знает о новых полях (iin_verified, kato_address, osms_status и т.д.)
- ❌ Serializer пытается сериализовать несуществующие поля
- ❌ Django возвращает 500 error

### После миграций:
- ✅ БД обновлена с новыми полями
- ✅ Serializer корректно работает
- ✅ API возвращает данные
- ✅ Frontend загружается

---

## 📋 CHECKLIST

После выполнения команд проверьте:

- [ ] `docker compose ps` показывает backend в состоянии "Up"
- [ ] http://localhost:8000/api/patients/patients/ возвращает JSON
- [ ] http://localhost:5173 загружается без ошибок 500
- [ ] В консоли браузера (F12) нет красных ошибок
- [ ] Можно перейти на страницу "Пациенты"

---

## 💡 СОВЕТ

После исправления ошибки:

1. **Читайте:** `START_HERE.md` - начало работы
2. **Тестируйте:** Создайте пациента через UI
3. **Изучайте:** `README_KZ.md` - что реализовано

---

## 🔗 ПОЛЕЗНЫЕ ССЫЛКИ

- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/
- Frontend: http://localhost:5173
- API Schema: http://localhost:8000/api/schema/

---

## 📞 ЕСЛИ ВСЁ ЕЩЁ НЕ РАБОТАЕТ

### Соберите информацию:

```powershell
# 1. Статус контейнеров
docker compose ps > status.txt

# 2. Логи backend
docker compose logs backend --tail=100 > backend_logs.txt

# 3. Проверка миграций
docker compose exec backend python manage.py showmigrations > migrations.txt
```

Отправьте эти файлы или их содержимое в GitHub issue.

---

**Создано:** November 4, 2025  
**Для:** Windows Users  
**Проблема:** 500 Internal Server Error  
**Решение:** Применить миграции через Docker

