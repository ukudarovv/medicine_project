# Модуль HR (Управление персоналом)

## Обзор

Модуль HR предоставляет полный функционал управления персоналом для ERP системы стоматологических клиник. Включает управление сотрудниками, должностями, задачами и схемами расчёта зарплаты.

## Архитектура

### Backend (Django)

#### Модели

1. **Position** - Справочник должностей
   - `name` - название должности
   - `comment` - комментарий
   - `hidden_in_schedule_filter` - скрыть из фильтра расписания
   - Связь: один ко многим с Employee

2. **Employee** (расширенная) - Сотрудники
   - Персональные данные: ФИО, телефон, email
   - Трудоустройство: `position` (FK), `hired_at`, `fired_at`, `employment_status`
   - Документы: ИНН, СНИЛС, паспорт, доверенность
   - Флаги: `show_in_schedule`, `can_accept_payments`, `can_be_assistant`
   - Онлайн-запись: `online_slot_step_minutes`, `min_gap_between_visits_minutes`, `min_gap_between_days_hours`
   - Финансы: `markup_percent`, `salary`
   - Склад: `warehouse` (FK), `warehouse_lock`
   - Печать: `is_chief_accountant`, `is_cashier`, `is_org_head`
   - Календарь: `calendar_color`
   - Доступ: `is_user_enabled`, `access_template_id`

3. **SalarySchemaTemplate** - Шаблоны расчёта ЗП
   - Комиссии:
     - `pct_of_own_sales` + `pct_value` - процент от собственных продаж
     - `direction_bonus_enabled` + `direction_bonus_pct` - бонус за направление
     - `pct_per_created_visits_enabled` + `pct_per_visit` - за созданные визиты
   - Фиксированная ЗП:
     - `fixed_salary_enabled` + `fixed_amount` + `currency`
     - `min_rate_enabled` + `min_rate_amount` - минимальная ставка
   - Дополнительно:
     - `honor_patient_discount_enabled` - учитывать скидку пациенту
     - `subscription_services_pct_enabled` + `subscription_pct` - от абонементов
     - `calc_from_profit_instead_of_revenue` - от прибыли vs выручки

4. **EmployeeSalarySchema** - История назначений схем ЗП
   - `employee` (FK) - сотрудник
   - `salary_template` (FK) - шаблон
   - `starts_at`, `ends_at` - период действия
   - `is_active` - активность
   - `created_by` (FK) - кто назначил

5. **EmployeeResult** - Справочник результатов задач
   - `name` - название результата
   - `comment` - комментарий
   - `positions` (M2M) - привязка к должностям

6. **EmployeeTask** - Задачи сотрудникам
   - `title`, `description` - название и описание
   - `assignee` (FK) - исполнитель
   - `author` (FK) - автор
   - `status` - статус (new/in_progress/done/cancelled)
   - `result` (FK) - результат
   - `deadline_at` - дедлайн
   - `completed_at` - дата завершения

7. **EmployeeTaskComment** - Комментарии к задачам
   - `task` (FK) - задача
   - `author` (FK) - автор
   - `comment` - текст комментария

8. **EmployeeTaskAttachment** - Вложения к задачам
   - `task` (FK) - задача
   - `file` - файл
   - `filename` - имя файла
   - `uploaded_by` (FK) - кто загрузил

#### API Endpoints

**Сотрудники:**
```
GET    /api/staff/employees/                    # Список
POST   /api/staff/employees/                    # Создать
GET    /api/staff/employees/{id}/               # Детали
PATCH  /api/staff/employees/{id}/               # Обновить
DELETE /api/staff/employees/{id}/               # Удалить
POST   /api/staff/employees/{id}/grant_access   # Дать доступ
POST   /api/staff/employees/{id}/toggle_user_access   # Включить/выключить доступ
POST   /api/staff/employees/{id}/assign_salary_schema # Назначить схему ЗП
DELETE /api/staff/employees/{id}/remove_salary_schema # Убрать схему ЗП
GET    /api/staff/employees/doctors/            # Только врачи
```

**Должности:**
```
GET    /api/staff/positions/         # Список
POST   /api/staff/positions/         # Создать
PATCH  /api/staff/positions/{id}/    # Обновить
DELETE /api/staff/positions/{id}/    # Удалить
```

**Шаблоны ЗП:**
```
GET    /api/staff/salary-templates/                       # Список
POST   /api/staff/salary-templates/                       # Создать
PATCH  /api/staff/salary-templates/{id}/                  # Обновить
DELETE /api/staff/salary-templates/{id}/                  # Удалить
POST   /api/staff/salary-templates/{id}/apply_to_employees # Массовое применение
```

**Задачи:**
```
GET    /api/staff/tasks/                      # Список
POST   /api/staff/tasks/                      # Создать
PATCH  /api/staff/tasks/{id}/                 # Обновить
DELETE /api/staff/tasks/{id}/                 # Удалить
POST   /api/staff/tasks/{id}/add_comment      # Добавить комментарий
POST   /api/staff/tasks/{id}/upload_attachment # Загрузить файл
POST   /api/staff/tasks/{id}/change_status    # Изменить статус
```

**Результаты:**
```
GET    /api/staff/results/           # Список
POST   /api/staff/results/           # Создать
PATCH  /api/staff/results/{id}/      # Обновить
DELETE /api/staff/results/{id}/      # Удалить
```

**Интеграция с календарём:**
```
GET    /api/calendar/appointments/available_employees/  # Доступные сотрудники
GET    /api/calendar/appointments/online_booking_slots/ # Слоты онлайн-записи
GET    /api/calendar/appointments/conflicts/            # Проверка конфликтов (с HR полями)
```

#### Фильтрация

**Сотрудники:**
- `search` - поиск по ФИО, телефону, email, ИИН
- `position` - фильтр по должности
- `employment_status` - по статусу (active/fired/on_leave)
- `is_active` - активные/неактивные
- `show_in_schedule` - видимые в расписании
- `branch` - по филиалу
- `hired_from`, `hired_to` - по датам приёма

**Задачи:**
- `search` - поиск по названию и описанию
- `assignee` - по исполнителю
- `author` - по автору
- `status` - по статусу
- `result` - по результату
- `deadline_from`, `deadline_to` - по дедлайну

#### Уведомления (Signals)

1. **task_created_notification** - при создании задачи
   - Уведомление исполнителю
   - Подтверждение автору

2. **task_status_changed_notification** - при изменении статуса
   - Уведомление исполнителю и автору

3. **task_comment_notification** - при добавлении комментария
   - Уведомление всем участникам задачи

#### Celery Tasks

1. **check_task_deadlines** - проверка дедлайнов
   - Запускается периодически (настроить в Celery Beat)
   - Проверяет задачи с дедлайном в течение 24 часов
   - Проверяет просроченные задачи
   - Отправляет уведомления

2. **calculate_employee_salary** - расчёт ЗП
   - Принимает: employee_id, period_from, period_to
   - Возвращает: детализированный расчёт с разбивкой
   - Учитывает все настройки из SalarySchemaTemplate

### Frontend (Vue.js)

#### Компоненты

1. **PositionModal.vue** - Модалка для должностей
   - Создание/редактирование должности
   - Поля: название, комментарий, видимость в расписании

2. **EmployeeTaskModal.vue** - Модалка для задач
   - Создание/редактирование задачи
   - Выбор исполнителя из списка сотрудников
   - Выбор результата из справочника
   - Дедлайн: дата + время
   - Комментарии (добавление)
   - Вложения (загрузка файлов)

3. **SalaryTemplateModal.vue** - Модалка для шаблонов ЗП
   - Название шаблона
   - Настройка комиссий (checkboxes + проценты)
   - Фиксированный оклад + валюта
   - Минимальная ставка
   - Дополнительные флаги

4. **StaffHRPage.vue** - Главная страница HR модуля
   - 4 вкладки:
     - **Сотрудники**: список с фильтрами, CRUD
     - **Должности**: справочник, CRUD
     - **Задачи**: список задач с фильтрами, CRUD
     - **Шаблоны ЗП**: список шаблонов, CRUD
   - Поиск и фильтрация на каждой вкладке
   - Цветные статусные теги
   - Действия: редактировать, удалить

#### Роутинг

```javascript
{
  path: '/staff-hr',
  name: 'staff-hr',
  component: () => import('@/pages/StaffHRPage.vue')
}
```

## Интеграция с другими модулями

### Календарь (Calendar)

1. **Фильтрация сотрудников**
   - `show_in_schedule` - контролирует видимость в расписании
   - `employment_status` - учитывается при выборе сотрудников

2. **Цвета в календаре**
   - `calendar_color` используется для отображения записей сотрудника

3. **Онлайн-запись**
   - `online_slot_step_minutes` - индивидуальный шаг слотов
   - `min_gap_between_visits_minutes` - валидация перерывов
   - `min_gap_between_days_hours` - перерыв между днями

4. **Проверка конфликтов**
   - Расширенная проверка с учётом HR полей
   - Валидация минимальных перерывов

### Warehouse (Склад)

- `warehouse` + `warehouse_lock` - закрепление склада за сотрудником
- Ограничение списаний только с прикреплённого склада

### Billing (Финансы)

- `can_accept_payments` - право принимать оплату
- `markup_percent` - персональная наценка на услуги
- Схемы ЗП для расчёта зарплаты

### Visits (Визиты)

- Связь с визитами для расчёта комиссий
- `limit_goods_sales_today_only` - ограничение финансов

## Миграции

### Пошаговая миграция поля Position

1. **0002_step1_rename_position.py**
   - Переименование `position` → `position_legacy` (CharField)

2. **0003_salaryschematemplate_...py**
   - Создание всех новых моделей
   - Добавление всех новых полей
   - Создание FK поля `position`

3. **0004_migrate_legacy_data.py**
   - Data migration: копирование данных
   - Создание Position записей из `position_legacy`
   - Копирование legacy полей (hire_date → hired_at, color → calendar_color)
   - Установка `employment_status` на основе `fire_date`

## Права доступа (RBAC)

- **IsBranchMember** - базовый доступ к HR модулю
- **IsBranchAdmin** - полный доступ, включая:
  - Управление схемами ЗП
  - Предоставление доступа сотрудникам
  - Массовые операции

## Использование

### Создание сотрудника

```python
# API request
POST /api/staff/employees/
{
  "first_name": "Иван",
  "last_name": "Иванов",
  "position": 1,  # ID должности
  "phone": "+7 777 123 45 67",
  "hired_at": "2025-01-01",
  "employment_status": "active",
  "show_in_schedule": true,
  "calendar_color": "#2196F3"
}
```

### Назначение схемы ЗП

```python
# Создать шаблон
POST /api/staff/salary-templates/
{
  "name": "Врач базовая ставка",
  "pct_of_own_sales": true,
  "pct_value": 30,
  "min_rate_enabled": true,
  "min_rate_amount": 200000,
  "currency": "KZT"
}

# Применить к сотрудникам
POST /api/staff/salary-templates/{id}/apply_to_employees
{
  "employee_ids": [1, 2, 3],
  "starts_at": "2025-01-01",
  "ends_at": null
}
```

### Создание задачи

```python
POST /api/staff/tasks/
{
  "title": "Подготовить отчёт",
  "description": "Ежемесячный отчёт по визитам",
  "assignee": 5,  # ID сотрудника
  "deadline_at": "2025-01-15T18:00:00Z",
  "status": "new"
}

# Добавить комментарий
POST /api/staff/tasks/{id}/add_comment
{
  "comment": "Не забудь про новые метрики"
}

# Загрузить файл
POST /api/staff/tasks/{id}/upload_attachment
FormData: { file: File }
```

### Расчёт ЗП (Celery)

```python
from apps.staff.tasks import calculate_employee_salary

result = calculate_employee_salary.delay(
    employee_id=5,
    period_from="2025-01-01",
    period_to="2025-01-31"
)

# Результат:
{
  "employee_id": 5,
  "employee_name": "Иванов Иван",
  "total_salary": 450000.0,
  "currency": "KZT",
  "breakdown": {
    "own_sales_commission": {
      "base_amount": 1000000.0,
      "percent": 30.0,
      "commission": 300000.0
    },
    "fixed_salary": 150000.0
  }
}
```

## Тестирование

### Unit Tests

```bash
pytest backend/apps/staff/tests/test_models.py
pytest backend/apps/staff/tests/test_views.py
pytest backend/apps/staff/tests/test_salary_calculation.py
```

### API Tests

```bash
pytest backend/apps/staff/tests/test_api.py
```

## Производительность

### Оптимизации

1. **Индексы БД**
   - `organization + employment_status`
   - `organization + position`
   - `organization + assignee + status` (задачи)

2. **Select Related**
   - Employee: position, user, warehouse
   - Task: assignee, author, result
   - SalarySchema: salary_template

3. **Pagination**
   - Все списки: 25 записей по умолчанию

## Известные ограничения

1. Уведомления временно отключены (требуется реализация `send_notification` в comms.tasks)
2. Расчёт ЗП - базовая реализация (требует доработки для сложных сценариев)
3. Нет поддержки рекуррентных задач
4. Файлы задач хранятся локально (рекомендуется S3)

## Roadmap

- [ ] Реализация уведомлений через WebSocket
- [ ] Продвинутый расчёт ЗП с учётом всех параметров
- [ ] Отчёты по задачам и производительности
- [ ] Экспорт данных в Excel
- [ ] Импорт сотрудников из CSV
- [ ] Календарь задач (Gantt chart)
- [ ] Шаблоны задач
- [ ] Автоматическое создание задач по расписанию


