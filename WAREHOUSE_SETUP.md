# Настройка складов / Warehouse Setup

## Проблема: "Склад не виден" в форме создания партии товара

### Описание
При попытке создать новую партию товара поле "Склад" может быть пустым или недоступным. Это происходит, если в системе нет созданных складов.

### Решение

#### Вариант 1: Создать склад через интерфейс (рекомендуется)

1. Перейдите на страницу **"Управление складом"**
2. Выберите вкладку **"Склады"**
3. Нажмите кнопку **🏢 Склад** в правом верхнем углу
4. Заполните форму:
   - **Филиал**: выберите филиал, к которому будет привязан склад
   - **Название склада**: например, "Основной склад", "Аптека №1", и т.д.
   - **Статус**: включите, чтобы склад был активен
5. Нажмите **"Создать"**

После создания склада вернитесь к форме создания партии товара - поле "Склад" теперь будет доступно.

#### Вариант 2: Создать склады автоматически через команду

Если у вас уже есть филиалы в системе, вы можете автоматически создать по одному складу для каждого филиала:

**На Windows (PowerShell):**
```powershell
cd backend
python manage.py create_default_warehouse
```

**На Linux/Mac:**
```bash
cd backend
python manage.py create_default_warehouse
```

Эта команда создаст склад с названием "Основной склад - [Название филиала]" для каждого филиала, у которого еще нет склада.

### Дополнительные улучшения

В обновленной версии формы создания партии товара:
- ✅ Добавлено предупреждение, если нет доступных складов
- ✅ Поле "Склад" блокируется, если складов нет
- ✅ Добавлена подсказка с инструкцией создания склада
- ✅ Улучшена обработка ошибок при загрузке складов
- ✅ Добавлено логирование для отладки

### Требования

Перед созданием склада убедитесь, что:
1. В системе созданы филиалы (модуль Organization)
2. У пользователя есть права доступа к выбранному филиалу
3. Пользователь авторизован в системе

### Проверка

После создания склада:
1. Откройте форму "Новая партия товара"
2. Поле "Склад" должно содержать список доступных складов
3. Вы можете выбрать склад из выпадающего списка

### Техническая информация

**Модели:**
- `Warehouse` - модель склада (привязан к филиалу)
- `StockBatch` - модель партии товара (привязана к складу и номенклатуре)

**API эндпоинты:**
- `GET /api/warehouse/warehouses/` - получить список складов
- `POST /api/warehouse/warehouses/` - создать склад
- `GET /api/warehouse/batches/` - получить список партий
- `POST /api/warehouse/batches/` - создать партию товара

**Фильтрация:**
- Склады фильтруются по организации пользователя
- Можно фильтровать по филиалу: `/api/warehouse/warehouses/?branch=1`
- Можно фильтровать по статусу: `/api/warehouse/warehouses/?is_active=true`

---

## Problem: "Warehouse not visible" in the new batch form

### Description
When trying to create a new stock batch, the "Warehouse" field may be empty or unavailable. This happens if there are no warehouses created in the system.

### Solution

#### Option 1: Create warehouse through the interface (recommended)

1. Go to the **"Warehouse Management"** page
2. Select the **"Warehouses"** tab
3. Click the **🏢 Warehouse** button in the top right corner
4. Fill in the form:
   - **Branch**: select the branch to which the warehouse will be linked
   - **Warehouse name**: e.g., "Main warehouse", "Pharmacy #1", etc.
   - **Status**: enable it to make the warehouse active
5. Click **"Create"**

After creating the warehouse, return to the batch creation form - the "Warehouse" field will now be available.

#### Option 2: Create warehouses automatically via command

If you already have branches in the system, you can automatically create one warehouse for each branch:

**On Windows (PowerShell):**
```powershell
cd backend
python manage.py create_default_warehouse
```

**On Linux/Mac:**
```bash
cd backend
python manage.py create_default_warehouse
```

This command will create a warehouse named "Main warehouse - [Branch Name]" for each branch that doesn't have a warehouse yet.

### Additional improvements

In the updated batch creation form:
- ✅ Added warning if no warehouses are available
- ✅ "Warehouse" field is disabled if there are no warehouses
- ✅ Added hint with warehouse creation instructions
- ✅ Improved error handling when loading warehouses
- ✅ Added logging for debugging

### Requirements

Before creating a warehouse, make sure that:
1. Branches are created in the system (Organization module)
2. The user has access rights to the selected branch
3. The user is authenticated in the system

### Verification

After creating a warehouse:
1. Open the "New stock batch" form
2. The "Warehouse" field should contain a list of available warehouses
3. You can select a warehouse from the dropdown list



