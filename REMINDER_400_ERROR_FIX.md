# Fix: Reminder Creation 400 Error

## Проблема

При попытке создать новое напоминание в модуле маркетинга возникала ошибка:
```
Failed to load resource: the server responded with a status of 400 (Bad Request)
Error saving reminder: AxiosError
```

## Причина

В сериализаторе `ReminderSerializer` (backend/apps/comms/serializers.py) поля `organization` и `created_by` были включены в список полей, но не были помечены как read-only. Это означало, что Django REST Framework ожидал их в запросе от клиента, хотя они должны автоматически устанавливаться на бэкенде методом `perform_create`.

## Решение

### 1. Backend Fix (backend/apps/comms/serializers.py)

Добавлены поля `organization` и `created_by` в `read_only_fields`:

```python
class ReminderSerializer(serializers.ModelSerializer):
    # ... other fields ...
    
    class Meta:
        model = Reminder
        fields = [
            'id', 'organization', 'name', 'enabled', 'type', 'type_display',
            'link_service', 'link_service_name', 'offset_days', 'offset_hours',
            'channel', 'channel_display', 'body', 'sent_count', 'delivered_count',
            'visit_count', 'online_bookings_count', 'visit_amount', 'conversion_rate',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'organization', 'created_by',  # <-- Added these two
            'sent_count', 'delivered_count', 'visit_count',
            'online_bookings_count', 'visit_amount', 'created_at', 'updated_at'
        ]
```

Также добавлен `allow_null=True` для поля `link_service_name`, чтобы корректно обрабатывать случаи, когда услуга не указана.

### 2. Frontend Enhancement (frontend/src/components/ReminderModal.vue)

Улучшена обработка ошибок для отображения детальных сообщений о валидации:

```javascript
async handleSubmit() {
  this.loading = true
  try {
    if (this.isEdit) {
      await updateReminder(this.reminder.id, this.form)
      this.$emit('success', 'Напоминание обновлено')
    } else {
      await createReminder(this.form)
      this.$emit('success', 'Напоминание создано')
    }
    this.$emit('close')
  } catch (error) {
    console.error('Error saving reminder:', error)
    console.error('Error response:', error.response?.data)
    
    // Format validation errors
    if (error.response?.data) {
      const errors = error.response.data
      if (typeof errors === 'object' && !errors.detail) {
        let errorMessage = 'Ошибка валидации:\n'
        Object.keys(errors).forEach(key => {
          const value = Array.isArray(errors[key]) ? errors[key].join(', ') : errors[key]
          errorMessage += `${key}: ${value}\n`
        })
        this.$emit('error', errorMessage)
      } else {
        this.$emit('error', errors.detail || errors.error || 'Ошибка сохранения')
      }
    } else {
      this.$emit('error', 'Ошибка сохранения напоминания')
    }
  } finally {
    this.loading = false
  }
}
```

## Результат

Теперь создание напоминаний работает корректно:
- Поля `organization` и `created_by` автоматически устанавливаются на бэкенде
- Клиент не пытается отправить эти поля, что предотвращает ошибку валидации
- Улучшенная обработка ошибок показывает детальную информацию о проблемах валидации

## Тестирование

Для проверки:
1. Перейдите на страницу Маркетинг
2. Нажмите "+ Напоминание"
3. Заполните форму:
   - Название: "Тестовое напоминание"
   - Тип: любой (например, "После визита")
   - Текст сообщения: "Тестовое сообщение"
4. Нажмите "Сохранить"

Напоминание должно успешно создаться без ошибок 400.

## Коммит

```
Fix: Reminder creation 400 error - mark organization and created_by as read-only fields
```

Изменения отправлены в репозиторий: https://github.com/ukudarovv/medicine_project

