# Kazakhstan-Specific Features

Документация по KZ-специфичным функциям системы Medicine ERP

## Обзор

Система адаптирована для работы на рынке Казахстана с учетом местных требований к идентификации, адресации, медицинскому страхованию и нормативных требований.

## 1. Идентификация пациентов (ИИН)

### ИИН - Индивидуальный Идентификационный Номер

**Формат:** 12 цифр (ГГММДДCCCCCК)
- Позиции 1-6: дата рождения (YYMMDD)
- Позиция 7: индикатор века и пола
  - 1,2: 19 век (1800-1899)
  - 3,4: 20 век (1900-1999) 
  - 5,6: 21 век (2000-2099)
  - Нечетные (1,3,5) = мужской, четные (2,4,6) = женский
- Позиции 8-11: порядковый номер
- Позиция 12: контрольный разряд (алгоритм Luhn)

### Валидация ИИН

Файл: `backend/apps/patients/validators.py`

```python
from apps.patients.validators import validate_iin

result = validate_iin('960825400123')
# Returns: {
#   'valid': True/False,
#   'birth_date': date(1996, 8, 25),
#   'sex': 'F',
#   'error': None or 'error message'
# }
```

### API

**Верификация ИИН:**
```
POST /api/patients/patients/{id}/verify-iin/
```

Проверяет формат ИИН, контрольную сумму и извлекает данные (дату рождения, пол). При успешной верификации устанавливает флаг `iin_verified=True`.

## 2. КАТО (Адресация)

### Kazakhstan Administrative Territorial Objects

Структурированная система адресации по административно-территориальным объектам РК.

### Структура KATO Address

```json
{
  "region": "г. Алматы",
  "district": "Алмалинский район",
  "city": "Алматы",
  "street": "пр. Абая",
  "building": "123",
  "apartment": "45",
  "kato_code": "750100000",
  "coordinates": {
    "lat": 43.238293,
    "lon": 76.945465
  }
}
```

### Справочник КАТО

Файл: `backend/apps/patients/fixtures/kato.json`

Содержит:
- 17 областей
- 3 города республиканского значения (Астана, Алматы, Шымкент)
- Районы для крупных городов

### Использование

```python
from apps.patients.kato_utils import KATOHelper

# Получить все регионы
regions = KATOHelper.get_regions()

# Получить районы области
districts = KATOHelper.get_districts('750000000')  # Алматы

# Форматировать адрес
address_str = KATOHelper.format_address(patient.kato_address)
# "г. Алматы, Алмалинский район, пр. Абая, д. 123, кв. 45"
```

## 3. ОСМС (Медицинское страхование)

### Obligatory Social Medical Insurance

Система обязательного социального медицинского страхования РК.

### Поля модели Patient

- `osms_status` - Статус страхования:
  - `insured` - Застрахован
  - `not_insured` - Не застрахован

- `osms_category` - Категория плательщика:
  - `employee` - Наемный работник
  - `self_employed` - ИП/Самозанятый
  - `socially_vulnerable` - Социально уязвимый
  - `civil_servant` - Бюджетник
  - `pensioner` - Пенсионер
  - `other` - Другое

- `osms_verified_at` - Дата последней проверки статуса

## 4. Согласия пациентов (Compliance)

### ConsentHistory Model

Модель для аудита согласий пациентов в соответствии с требованиями защиты персональных данных РК.

### Типы согласий

- `personal_data` - Обработка персональных данных
- `medical_intervention` - Медицинское вмешательство
- `sms_marketing` - SMS-рассылки
- `whatsapp_marketing` - WhatsApp-рассылки

### Аудит

Каждое согласие записывается с:
- IP-адресом
- User Agent браузера
- Пользователем, зафиксировавшим согласие
- Временной меткой

### API

**Сохранение согласия:**
```
POST /api/patients/patients/{id}/save-consent/

Body: {
  "consent_type": "personal_data",
  "status": "accepted"
}
```

**Просмотр истории:**
```
GET /api/patients/patients/{id}/consent-history/
```

## 5. Настройки системы

### config/settings/base.py

```python
# KZ-specific settings
COUNTRY_CODE = 'KZ'
CURRENCY = 'KZT'
CURRENCY_SYMBOL = '₸'
PHONE_MASK = '+7 7XX XXX-XX-XX'
DATE_FORMAT = 'dd.mm.yyyy'
TIME_ZONE = 'Asia/Almaty'
HIDE_RF_FIELDS = True  # Скрыть РФ-специфичные поля
```

## 6. Лист ожидания (Waitlist)

### Модель Waitlist

Управление листом ожидания пациентов для записи на прием.

**Поля:**
- `patient` - Пациент
- `service` - Желаемая услуга (опционально)
- `employee` - Желаемый врач (опционально)
- `preferred_date` - Конкретная дата (или период)
- `preferred_period_start` / `preferred_period_end` - Диапазон дат
- `time_window` - Предпочитаемое время (morning/afternoon/evening/any)
- `priority` - Приоритет (0 = обычный, >0 = повышенный)
- `status` - Статус (waiting/contacted/scheduled/cancelled)
- `contact_result` - Результат связи с пациентом

## 7. История контактов (PatientContact)

### Модель PatientContact

Детальная история всех контактов с пациентом.

**Типы контактов:**
- `call` - Звонок
- `sms` - SMS
- `whatsapp` - WhatsApp
- `visit` - Визит в клинику
- `email` - Email

**Направление:**
- `inbound` - Входящий
- `outbound` - Исходящий

**Статусы:**
- `reached` - Дозвонились
- `no_answer` - Не ответил
- `callback_requested` - Перезвонить
- `message_left` - Оставлено сообщение
- `completed` - Выполнено

## 8. Расширенный дневник визита

### Visit.diary_structured

Структурированный дневник приема в формате JSON:

```json
{
  "complaints": "Жалобы пациента",
  "anamnesis": "Анамнез заболевания",
  "examination": "Данные осмотра",
  "conclusion": "Заключение",
  "recommendations": "Рекомендации"
}
```

### Visit.templates_used

Список ID использованных шаблонов для быстрого заполнения дневника визита.

## Миграции

### Применение миграций

```bash
cd backend
python manage.py migrate patients  # KZ identity fields + ConsentHistory
python manage.py migrate calendar  # Waitlist
python manage.py migrate visits    # Visit extensions + VisitFile
python manage.py migrate comms     # PatientContact
```

### Загрузка справочников

```bash
python manage.py loaddata kato  # KATO справочник
```

## Планируемые функции

### Sprint 3: Медосмотры и планы лечения
- Производственные медосмотры (комиссии)
- Планы лечения с этапами
- Шаблоны планов лечения

### Sprint 4: Финансы и интеграции KZ
- Kaspi QR оплаты
- Halyk Pay интеграция
- SMS-провайдеры Казахстана (Beeline, Altel)
- Справки для налогового вычета
- Экспорт в 1С

### Sprint 5: UX улучшения
- Автосохранение форм
- Горячие клавиши
- Глобальный поиск
- Sticky headers
- Маски ввода (ИИН, телефон)

## Поддержка

По вопросам KZ-адаптации:
- GitHub Issues: https://github.com/ukudarovv/medicine_project/issues
- Документация: https://github.com/ukudarovv/medicine_project/blob/master/docs/

## Changelog

См. [CHANGELOG.md](../CHANGELOG.md) для детального списка изменений.

