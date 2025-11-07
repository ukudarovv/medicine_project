<template>
  <ModalWrapper
    :visible="visible"
    :title="isEdit ? 'Редактировать напоминание' : 'Новое напоминание'"
    @close="$emit('close')"
  >
    <form @submit.prevent="handleSubmit" class="reminder-form">
      <div class="form-group">
        <label>Название <span class="required">*</span></label>
        <input
          v-model="form.name"
          type="text"
          placeholder="Например: Подтверждение записи"
          required
        />
      </div>

      <div class="form-group">
        <label>Тип напоминания <span class="required">*</span></label>
        <select v-model="form.type" required>
          <option value="">Выберите тип</option>
          <option value="MISSED_CALL">Пропущенный звонок</option>
          <option value="PREBOOK_CREATE">Создание предварительной записи</option>
          <option value="PREBOOK_UPDATE">Изменение предварительной записи</option>
          <option value="PREBOOK_DELETE">Удаление предварительной записи</option>
          <option value="PREBOOK_CANCEL">Отмена предварительной записи</option>
          <option value="ONLINE_CONFIRM">Подтверждение онлайн-записи</option>
          <option value="AFTER_VISIT">После визита</option>
          <option value="BIRTHDAY">День рождения</option>
          <option value="BONUS_LEFT">Остаток бонусов</option>
          <option value="BONUS_WRITEOFF">Списание бонусов</option>
          <option value="CUSTOM">Произвольное</option>
        </select>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Через дней</label>
          <input
            v-model.number="form.offset_days"
            type="number"
            min="0"
            placeholder="0"
          />
          <small>Дней после события</small>
        </div>

        <div class="form-group">
          <label>Через часов</label>
          <input
            v-model.number="form.offset_hours"
            type="number"
            min="0"
            placeholder="0"
          />
          <small>Часов после события</small>
        </div>
      </div>

      <div class="form-group">
        <label>Канал отправки</label>
        <select v-model="form.channel">
          <option value="sms">SMS</option>
          <option value="call">Звонок-робот</option>
          <option value="whatsapp">WhatsApp</option>
          <option value="telegram">Telegram</option>
        </select>
      </div>

      <div class="form-group">
        <label>Связанная услуга (опционально)</label>
        <select v-model="form.link_service">
          <option :value="null">Не указано (для всех услуг)</option>
          <!-- TODO: Load services from API -->
        </select>
        <small>Если указано, напоминание сработает только для этой услуги</small>
      </div>

      <div class="form-group">
        <label>Текст сообщения <span class="required">*</span></label>
        <textarea
          v-model="form.body"
          rows="5"
          placeholder="Введите текст с плейсхолдерами"
          required
        ></textarea>
        <div class="placeholder-hints">
          <strong>Доступные плейсхолдеры:</strong>
          <span
            v-for="ph in placeholders"
            :key="ph"
            class="placeholder-chip"
            @click="insertPlaceholder(ph)"
          >
            {{ ph }}
          </span>
        </div>
        <div class="sms-counter">
          <span>{{ smsSegments }} SMS ({{ messageLength }} символов)</span>
          <small v-if="smsSegments > 3" class="warning">
            ⚠ Более 3 сегментов - высокая стоимость
          </small>
        </div>
      </div>

      <div class="form-group">
        <label class="checkbox-label">
          <input
            v-model="form.enabled"
            type="checkbox"
          />
          <span>Включено</span>
        </label>
      </div>

      <div class="form-actions">
        <button type="button" class="btn-secondary" @click="$emit('close')">
          Отмена
        </button>
        <button type="button" class="btn-secondary" @click="handleTest" v-if="isEdit">
          Тест
        </button>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Сохранение...' : 'Сохранить' }}
        </button>
      </div>
    </form>

    <!-- Test Modal -->
    <div v-if="showTestModal" class="test-modal-overlay" @click="showTestModal = false">
      <div class="test-modal" @click.stop>
        <h3>Тестовая отправка</h3>
        <div class="form-group">
          <label>Номер телефона</label>
          <input
            v-model="testPhone"
            type="tel"
            placeholder="+7 777 123 45 67"
            required
          />
        </div>
        <div class="form-actions">
          <button @click="showTestModal = false" class="btn-secondary">Отмена</button>
          <button @click="sendTest" class="btn-primary" :disabled="!testPhone">Отправить</button>
        </div>
      </div>
    </div>
  </ModalWrapper>
</template>

<script>
import ModalWrapper from './ModalWrapper.vue'
import { createReminder, updateReminder, testReminder } from '@/api/marketing'

export default {
  name: 'ReminderModal',
  components: { ModalWrapper },
  props: {
    visible: Boolean,
    reminder: Object,
  },
  data() {
    return {
      loading: false,
      showTestModal: false,
      testPhone: '',
      form: {
        name: '',
        type: '',
        offset_days: 0,
        offset_hours: 0,
        channel: 'sms',
        link_service: null,
        body: '',
        enabled: true,
      },
      placeholders: [
        '_ИМЯ_ПАЦИЕНТА_',
        '_ИМЯ_ОТЧЕСТВО_ПАЦИЕНТА_',
        '_ДАТА_ВИЗИТА_',
        '_ССЫЛКА_НА_ОНЛАЙН_ЗАПИСЬ_',
      ],
    }
  },
  computed: {
    isEdit() {
      return !!this.reminder
    },
    messageLength() {
      return this.form.body.length
    },
    smsSegments() {
      const isCyrillic = /[\u0400-\u04FF]/.test(this.form.body)
      const maxChars = isCyrillic ? 70 : 160
      const maxCharsMulti = isCyrillic ? 67 : 153

      if (this.messageLength <= maxChars) return 1

      return Math.ceil(this.messageLength / maxCharsMulti)
    },
  },
  watch: {
    visible(val) {
      if (val) {
        this.loadForm()
      }
    },
  },
  methods: {
    loadForm() {
      if (this.reminder) {
        this.form = {
          name: this.reminder.name || '',
          type: this.reminder.type || '',
          offset_days: this.reminder.offset_days || 0,
          offset_hours: this.reminder.offset_hours || 0,
          channel: this.reminder.channel || 'sms',
          link_service: this.reminder.link_service || null,
          body: this.reminder.body || '',
          enabled: this.reminder.enabled !== false,
        }
      } else {
        this.form = {
          name: '',
          type: '',
          offset_days: 0,
          offset_hours: 0,
          channel: 'sms',
          link_service: null,
          body: '',
          enabled: true,
        }
      }
    },
    insertPlaceholder(placeholder) {
      const textarea = this.$el.querySelector('textarea')
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const text = this.form.body
      this.form.body = text.substring(0, start) + placeholder + text.substring(end)

      this.$nextTick(() => {
        textarea.focus()
        textarea.selectionStart = textarea.selectionEnd = start + placeholder.length
      })
    },
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
    },
    handleTest() {
      this.showTestModal = true
    },
    async sendTest() {
      if (!this.testPhone) return

      try {
        const result = await testReminder(this.reminder.id, this.testPhone)
        this.showTestModal = false
        this.testPhone = ''
        this.$emit('success', `Тестовое сообщение отправлено. Стоимость: ${result.data.cost} KZT`)
      } catch (error) {
        console.error('Error sending test:', error)
        this.$emit('error', error.response?.data?.error || 'Ошибка отправки')
      }
    },
  },
}
</script>

<style scoped lang="scss">
@import '@/styles/tokens.scss';

.reminder-form {
  max-width: 800px;
}

.form-group {
  margin-bottom: $spacing-md;
}

.form-group label {
  display: block;
  margin-bottom: $spacing-xs;
  font-weight: 500;
  color: $text-primary;
}

.required {
  color: $status-no-show;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid $border-color;
  border-radius: $radius-sm;
  font-size: 14px;
  background: $bg-tertiary;
  color: $text-primary;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.form-group textarea {
  resize: vertical;
  font-family: inherit;
}

.form-group small {
  display: block;
  margin-top: $spacing-xs;
  font-size: 12px;
  color: $text-secondary;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $spacing-md;
}

.placeholder-hints {
  margin-top: $spacing-sm;
  padding: 12px;
  background: $bg-tertiary;
  border-radius: $radius-sm;
  border: 1px solid $border-color;
}

.placeholder-hints strong {
  display: block;
  margin-bottom: $spacing-sm;
  font-size: 12px;
  color: $text-secondary;
}

.placeholder-chip {
  display: inline-block;
  padding: 4px 8px;
  margin: 4px 4px 0 0;
  background: $bg-secondary;
  border: 1px solid $border-color;
  border-radius: $radius-sm;
  font-size: 11px;
  font-family: monospace;
  cursor: pointer;
  transition: all 0.2s;
  color: $text-primary;
}

.placeholder-chip:hover {
  background: $primary-color;
  color: #fff;
  border-color: $primary-color;
}

.sms-counter {
  margin-top: $spacing-sm;
  padding: 8px 12px;
  background: rgba($status-booked, 0.15);
  border-radius: $radius-sm;
  font-size: 13px;
  color: $text-primary;
  border: 1px solid rgba($status-booked, 0.3);
}

.sms-counter .warning {
  display: block;
  margin-top: $spacing-xs;
  color: $status-in-progress;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  cursor: pointer;
  color: $text-primary;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  accent-color: $primary-color;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: $spacing-lg;
  padding-top: $spacing-md;
  border-top: 1px solid $border-color;
}

.btn-primary,
.btn-secondary {
  padding: 10px 24px;
  border: none;
  border-radius: $radius-sm;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: $primary-color;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: darken($primary-color, 10%);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: $bg-tertiary;
  color: $text-primary;
  border: 1px solid $border-color;
}

.btn-secondary:hover {
  background: lighten($bg-tertiary, 5%);
}

/* Test Modal */
.test-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: $z-modal + 1;
}

.test-modal {
  background: $bg-secondary;
  border-radius: $radius-md;
  padding: $spacing-lg;
  width: 90%;
  max-width: 400px;
  box-shadow: $shadow-lg;
  border: 1px solid $border-color;
}

.test-modal h3 {
  margin: 0 0 $spacing-md 0;
  font-size: 18px;
  color: $text-primary;
}
</style>

