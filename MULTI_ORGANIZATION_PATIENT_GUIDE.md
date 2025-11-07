# Руководство: Множественные организации для пациентов

## Что изменено

Система была модифицирована так, чтобы **один пациент мог быть зарегистрирован в нескольких организациях**. Ранее у пациента была связь `ForeignKey` с одной организацией, теперь используется `ManyToManyField`.

## Основные изменения

### 1. Модель Patient (`backend/apps/patients/models.py`)

**Было:**
```python
organization = models.ForeignKey(
    Organization,
    on_delete=models.CASCADE,
    related_name='patients'
)
```

**Стало:**
```python
organizations = models.ManyToManyField(
    Organization,
    related_name='patients',
    help_text='Организации, в которых зарегистрирован пациент'
)
```

### 2. Добавлены вспомогательные методы

```python
@property
def organization(self):
    """Получить основную организацию (первую добавленную) для обратной совместимости"""
    return self.organizations.first()

def has_organization(self, organization):
    """Проверить, принадлежит ли пациент определенной организации"""
    return self.organizations.filter(id=organization.id).exists()

def add_organization(self, organization):
    """Добавить организацию к пациенту"""
    if not self.has_organization(organization):
        self.organizations.add(organization)
        return True
    return False
```

### 3. Обновлена логика добавления пациента через ИИН

Теперь при добавлении существующего пациента через ИИН-верификацию:

**Было:** Создавалась полная копия пациента для новой организации

**Стало:** К существующему пациенту просто добавляется новая организация

Метод `verify_code` в `backend/apps/patients/views.py`:
```python
# Добавить организацию к пациенту (если еще не добавлена)
if patient.add_organization(verification.organization):
    message = f'Пациент {patient.full_name} успешно добавлен в вашу организацию'
else:
    message = f'Пациент {patient.full_name} уже был в вашей организации'
```

### 4. Обновлены фильтры и queryset'ы

Во всех ViewSet'ах и сериализаторах изменены фильтры:

**Было:**
```python
Patient.objects.filter(organization=user.organization)
```

**Стало:**
```python
Patient.objects.filter(organizations=user.organization)
```

Это затронуло следующие файлы:
- `backend/apps/patients/views.py` - все ViewSet'ы пациентов
- `backend/apps/patients/serializers.py` - валидация уникальности
- `backend/apps/calendar/views.py` - waitlist
- `backend/apps/billing/views.py` - справки на налоговый вычет
- `backend/apps/comms/views.py` - логи сообщений и контакты
- `backend/apps/reports/views.py` - отчеты
- `backend/apps/visits/serializers.py` - проверка доступа
- `backend/apps/ehr/serializers.py` - внешние записи
- `backend/apps/consent/permissions.py` - разрешения
- И другие...

## Применение изменений

### Шаг 1: Применить миграцию

Была создана миграция `0009_change_patient_organization_to_many.py`, которая:
1. Переименовывает старое поле `organization` во временное `organization_old`
2. Создает новое поле `organizations` (ManyToManyField)
3. Копирует данные из старого поля в новое
4. Удаляет старое поле

**Применить миграцию:**

```bash
# Для Windows PowerShell (используйте свой путь к Python или активируйте venv)
cd "C:\Users\Kudarov Umar\Desktop\My Projects\Medicine\backend"
python manage.py migrate patients
```

Или через docker-compose:
```bash
docker-compose exec backend python manage.py migrate patients
```

### Шаг 2: Проверить работу

После применения миграции проверьте:

1. **Создание нового пациента:** Пациент должен автоматически связываться с организацией пользователя
2. **Просмотр пациентов:** Каждая организация видит только своих пациентов
3. **Добавление существующего пациента по ИИН:**
   - Найти пациента по ИИН
   - Отправить SMS-код (тестовый код: 1234)
   - Подтвердить код
   - Пациент должен быть добавлен в вашу организацию без дублирования

## API для работы

### Поиск пациента по ИИН и добавление в организацию

**1. Отправить SMS-код для верификации:**

```http
POST /api/v1/patients/send-verification/
Content-Type: application/json

{
  "iin": "123456789012"
}
```

Ответ:
```json
{
  "message": "SMS код отправлен",
  "verification_id": 123,
  "phone": "7 XXX XXX XX 34",
  "patient_name": "Иванов Иван",
  "expires_in_seconds": 600,
  "test_code": "1234"
}
```

**2. Подтвердить код и добавить пациента:**

```http
POST /api/v1/patients/verify-code/
Content-Type: application/json

{
  "verification_id": 123,
  "code": "1234"
}
```

Ответ:
```json
{
  "message": "Пациент Иванов Иван Петрович успешно добавлен в вашу организацию",
  "patient": {
    "id": 456,
    "organizations": [1, 5],  // ID организаций
    "first_name": "Иван",
    "last_name": "Иванов",
    // ... остальные поля
  }
}
```

## Обратная совместимость

Для обеспечения обратной совместимости:

1. **Property `organization`** - возвращает первую организацию из списка
2. **Метод `has_organization(org)`** - проверяет принадлежность к организации
3. Все фильтры обновлены для работы с `organizations`

## Преимущества

1. **Нет дублирования данных:** Один пациент = одна запись в БД
2. **Общая медицинская история:** Все организации видят общую историю болезней, анализов и т.д.
3. **Легкое добавление:** Достаточно добавить организацию, не нужно копировать все данные
4. **Гибкость:** Пациент может обслуживаться в нескольких филиалах/клиниках

## Важно

- После миграции старые записи будут сохранены и корректно переданы в новую структуру
- Валидация уникальности телефона и ИИН теперь происходит в рамках каждой организации отдельно
- При создании нового пациента нужно указать organizations (массив ID) вместо organization (один ID)

## Тестирование

1. Создайте тестового пациента в первой организации
2. Войдите во вторую организацию
3. Попробуйте добавить того же пациента через ИИН-верификацию
4. Проверьте, что пациент не дублируется, а просто добавляется во вторую организацию
5. Проверьте, что обе организации видят этого пациента в своих списках

## Откат изменений

Если необходимо откатить изменения, выполните:

```bash
python manage.py migrate patients 0008_patientverification
```

Это откатит миграцию к предыдущему состоянию (с ForeignKey).

---

**Дата создания:** 2025-11-05
**Версия:** 1.0

