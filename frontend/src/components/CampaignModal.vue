<template>
  <ModalWrapper
    :visible="visible"
    :title="isEdit ? 'Редактировать рассылку' : 'Новая рассылка'"
    @close="$emit('close')"
    width="1200px"
  >
    <div class="campaign-wizard">
      <!-- Steps indicator -->
      <div class="steps">
        <div
          v-for="(step, idx) in steps"
          :key="idx"
          class="step"
          :class="{
            active: currentStep === idx,
            completed: currentStep > idx,
          }"
          @click="goToStep(idx)"
        >
          <div class="step-number">{{ idx + 1 }}</div>
          <div class="step-label">{{ step }}</div>
        </div>
      </div>

      <!-- Step 1: Basic Info -->
      <div v-show="currentStep === 0" class="step-content">
        <h3>Основная информация</h3>
        
        <div class="form-group">
          <label>Название рассылки <span class="required">*</span></label>
          <input
            v-model="form.title"
            type="text"
            placeholder="Например: Акция на отбеливание"
            required
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Канал</label>
            <select v-model="form.channel">
              <option value="sms">SMS</option>
              <option value="whatsapp">WhatsApp</option>
              <option value="telegram">Telegram</option>
            </select>
          </div>

          <div class="form-group">
            <label>Отправитель</label>
            <input
              v-model="form.sender_name"
              type="text"
              placeholder="CLINIC"
              maxlength="20"
              required
            />
            <small>Максимум 20 символов</small>
          </div>
        </div>
      </div>

      <!-- Step 2: Audience Filters -->
      <div v-show="currentStep === 1" class="step-content">
        <h3>Фильтры аудитории</h3>
        
        <div class="form-group">
          <label class="checkbox-label">
            <input
              v-model="form.audience.filters.is_opt_in"
              type="checkbox"
            />
            <span>Только с согласием на рассылки</span>
          </label>
          <small>Рекомендуется для маркетинговых рассылок</small>
        </div>

        <div class="form-group">
          <label>Теги пациентов</label>
          <input
            v-model="tagsInput"
            type="text"
            placeholder="Введите теги через запятую: ортодонтия, имплантация"
            @blur="parseTags"
          />
          <div v-if="form.audience.filters.tags.length" class="tags-list">
            <span
              v-for="(tag, idx) in form.audience.filters.tags"
              :key="idx"
              class="tag-chip"
            >
              {{ tag }}
              <button @click="removeTag(idx)">×</button>
            </span>
          </div>
        </div>

        <div class="form-group">
          <label>Дата последнего визита</label>
          <div class="date-range">
            <input
              v-model="form.audience.filters.last_visit_from"
              type="date"
            />
            <span>—</span>
            <input
              v-model="form.audience.filters.last_visit_to"
              type="date"
            />
          </div>
        </div>

        <div class="form-group">
          <label>День рождения в период</label>
          <div class="date-range">
            <input
              v-model="form.audience.filters.birthdate_from"
              type="date"
            />
            <span>—</span>
            <input
              v-model="form.audience.filters.birthdate_to"
              type="date"
            />
          </div>
          <small>Для поздравлений с днём рождения</small>
        </div>
      </div>

      <!-- Step 3: Message -->
      <div v-show="currentStep === 2" class="step-content">
        <h3>Текст сообщения</h3>
        
        <div class="form-group">
          <label>Сообщение <span class="required">*</span></label>
          <textarea
            v-model="form.message_template.body"
            rows="6"
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
            <div>
              <strong>{{ smsSegments }} SMS</strong> ({{ messageLength }} символов)
            </div>
            <div v-if="prepareResult.total_recipients">
              Получателей: <strong>{{ prepareResult.total_recipients }}</strong> ×
              {{ smsSegments }} сегментов =
              <strong>{{ prepareResult.estimated_segments }}</strong> SMS
            </div>
            <small v-if="smsSegments > 3" class="warning">
              ⚠ Более 3 сегментов - высокая стоимость
            </small>
          </div>
        </div>

        <div class="preview-section">
          <h4>Предпросмотр</h4>
          <div class="message-preview">
            {{ previewMessage }}
          </div>
        </div>
      </div>

      <!-- Step 4: Schedule & Cost -->
      <div v-show="currentStep === 3" class="step-content">
        <h3>Планирование и запуск</h3>
        
        <div v-if="!prepareResult.total_recipients" class="prepare-prompt">
          <p>Сначала нужно подготовить аудиторию</p>
          <button @click="handlePrepare" class="btn-primary" :disabled="preparingLoading">
            {{ preparingLoading ? 'Подготовка...' : 'Подготовить аудиторию' }}
          </button>
        </div>

        <div v-else class="schedule-content">
          <div class="cost-estimate">
            <h4>Прогноз расхода</h4>
            <div class="cost-grid">
              <div class="cost-item">
                <div class="cost-label">Получателей</div>
                <div class="cost-value">{{ prepareResult.total_recipients }}</div>
              </div>
              <div class="cost-item">
                <div class="cost-label">Сегментов на сообщение</div>
                <div class="cost-value">{{ prepareResult.segments_per_message }}</div>
              </div>
              <div class="cost-item">
                <div class="cost-label">Всего SMS</div>
                <div class="cost-value">{{ prepareResult.estimated_segments }}</div>
              </div>
              <div class="cost-item">
                <div class="cost-label">Стоимость</div>
                <div class="cost-value highlight">{{ formatMoney(prepareResult.estimated_cost) }}</div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>Когда отправить</label>
            <select v-model="scheduleType">
              <option value="now">Сейчас</option>
              <option value="scheduled">По расписанию</option>
              <option value="batch">Батчами (соблюдать лимиты)</option>
            </select>
          </div>

          <div v-if="scheduleType === 'scheduled'" class="form-group">
            <label>Дата и время отправки</label>
            <input
              v-model="scheduledAt"
              type="datetime-local"
              required
            />
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="wizard-actions">
        <button
          v-if="currentStep > 0"
          type="button"
          class="btn-secondary"
          @click="prevStep"
        >
          Назад
        </button>
        
        <button type="button" class="btn-secondary" @click="$emit('close')">
          Отмена
        </button>
        
        <button
          v-if="currentStep < 3"
          type="button"
          class="btn-primary"
          @click="nextStep"
        >
          Далее
        </button>
        
        <button
          v-if="currentStep === 3"
          type="button"
          class="btn-success"
          @click="handleSchedule"
          :disabled="!prepareResult.total_recipients || schedulingLoading"
        >
          {{ schedulingLoading ? 'Запуск...' : 'Запустить рассылку' }}
        </button>
      </div>
    </div>
  </ModalWrapper>
</template>

<script>
import ModalWrapper from './ModalWrapper.vue'
import { createCampaign, updateCampaign, prepareCampaign, scheduleCampaign } from '@/api/marketing'

export default {
  name: 'CampaignModal',
  components: { ModalWrapper },
  props: {
    visible: Boolean,
    campaign: Object,
  },
  data() {
    return {
      currentStep: 0,
      preparingLoading: false,
      schedulingLoading: false,
      scheduleType: 'now',
      scheduledAt: '',
      prepareResult: {},
      steps: ['Информация', 'Аудитория', 'Сообщение', 'Запуск'],
      form: {
        title: '',
        channel: 'sms',
        sender_name: 'CLINIC',
        audience: {
          filters: {
            tags: [],
            services: [],
            last_visit_from: '',
            last_visit_to: '',
            birthdate_from: '',
            birthdate_to: '',
            is_opt_in: true,
          },
        },
        message_template: {
          body: '',
          placeholders: [],
          max_segments: 1,
        },
      },
      tagsInput: '',
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
      return !!this.campaign
    },
    messageLength() {
      return this.form.message_template.body.length
    },
    smsSegments() {
      const isCyrillic = /[\u0400-\u04FF]/.test(this.form.message_template.body)
      const maxChars = isCyrillic ? 70 : 160
      const maxCharsMulti = isCyrillic ? 67 : 153

      if (this.messageLength <= maxChars) return 1
      return Math.ceil(this.messageLength / maxCharsMulti)
    },
    previewMessage() {
      let msg = this.form.message_template.body
      msg = msg.replace('_ИМЯ_ПАЦИЕНТА_', 'Иван')
      msg = msg.replace('_ИМЯ_ОТЧЕСТВО_ПАЦИЕНТА_', 'Иван Иванович')
      msg = msg.replace('_ДАТА_ВИЗИТА_', new Date().toLocaleDateString('ru-RU'))
      msg = msg.replace('_ССЫЛКА_НА_ОНЛАЙН_ЗАПИСЬ_', 'https://clinic.example.com/booking')
      return msg || 'Введите текст сообщения...'
    },
  },
  watch: {
    visible(val) {
      if (val) {
        this.loadForm()
        this.currentStep = 0
      }
    },
  },
  methods: {
    loadForm() {
      if (this.campaign) {
        this.form = {
          title: this.campaign.title || '',
          channel: this.campaign.channel || 'sms',
          sender_name: this.campaign.sender_name || 'CLINIC',
          audience: this.campaign.audience || {
            filters: {
              tags: [],
              services: [],
              last_visit_from: '',
              last_visit_to: '',
              birthdate_from: '',
              birthdate_to: '',
              is_opt_in: true,
            },
          },
          message_template: this.campaign.message_template || {
            body: '',
            placeholders: [],
            max_segments: 1,
          },
        }
        this.tagsInput = this.form.audience.filters.tags.join(', ')
      }
    },
    goToStep(step) {
      if (step <= this.currentStep) {
        this.currentStep = step
      }
    },
    nextStep() {
      if (this.currentStep < 3) {
        this.currentStep++
      }
    },
    prevStep() {
      if (this.currentStep > 0) {
        this.currentStep--
      }
    },
    parseTags() {
      if (this.tagsInput) {
        this.form.audience.filters.tags = this.tagsInput
          .split(',')
          .map((t) => t.trim())
          .filter((t) => t)
      }
    },
    removeTag(index) {
      this.form.audience.filters.tags.splice(index, 1)
      this.tagsInput = this.form.audience.filters.tags.join(', ')
    },
    insertPlaceholder(placeholder) {
      const textarea = this.$el.querySelector('textarea')
      if (!textarea) return
      
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const text = this.form.message_template.body
      this.form.message_template.body = text.substring(0, start) + placeholder + text.substring(end)

      this.$nextTick(() => {
        textarea.focus()
        textarea.selectionStart = textarea.selectionEnd = start + placeholder.length
      })
    },
    async handlePrepare() {
      this.preparingLoading = true
      try {
        // Save campaign first if new
        let campaignId = this.campaign?.id
        
        if (!campaignId) {
          const response = await createCampaign(this.form)
          campaignId = response.data.id
          this.$emit('campaign-created', response.data)
        }
        
        // Prepare audience
        const prepareResponse = await prepareCampaign(campaignId, this.form.audience.filters)
        this.prepareResult = prepareResponse.data
        
        if (this.prepareResult.total_recipients === 0) {
          this.$emit('error', 'Нет пациентов, соответствующих критериям')
        } else {
          this.$emit('success', `Подготовлено: ${this.prepareResult.total_recipients} получателей`)
        }
      } catch (error) {
        console.error('Error preparing campaign:', error)
        this.$emit('error', error.response?.data?.error || 'Ошибка подготовки')
      } finally {
        this.preparingLoading = false
      }
    },
    async handleSchedule() {
      this.schedulingLoading = true
      try {
        let campaignId = this.campaign?.id
        
        // Create campaign if new
        if (!campaignId) {
          const response = await createCampaign(this.form)
          campaignId = response.data.id
        }
        
        // Schedule
        const scheduleData = {
          schedule_type: this.scheduleType,
          scheduled_at: this.scheduleType === 'scheduled' ? this.scheduledAt : undefined,
        }
        
        await scheduleCampaign(campaignId, scheduleData)
        
        this.$emit('success', 'Рассылка запущена')
        this.$emit('close')
      } catch (error) {
        console.error('Error scheduling campaign:', error)
        this.$emit('error', error.response?.data?.error || 'Ошибка запуска')
      } finally {
        this.schedulingLoading = false
      }
    },
    formatMoney(amount) {
      if (!amount) return '0 ₸'
      return `${Number(amount).toLocaleString()} ₸`
    },
  },
}
</script>

<style scoped>
.campaign-wizard {
  min-height: 500px;
  display: flex;
  flex-direction: column;
}

.steps {
  display: flex;
  justify-content: space-between;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 2px solid #ecf0f1;
}

.step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  position: relative;
}

.step:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 18px;
  left: 50%;
  width: 100%;
  height: 2px;
  background: #ecf0f1;
  z-index: -1;
}

.step.completed:not(:last-child)::after {
  background: #3498db;
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #ecf0f1;
  color: #7f8c8d;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-bottom: 8px;
  transition: all 0.3s;
}

.step.active .step-number {
  background: #3498db;
  color: #fff;
  transform: scale(1.1);
}

.step.completed .step-number {
  background: #27ae60;
  color: #fff;
}

.step-label {
  font-size: 13px;
  color: #7f8c8d;
}

.step.active .step-label {
  color: #3498db;
  font-weight: 500;
}

.step-content {
  flex: 1;
  overflow-y: auto;
  max-height: 500px;
  padding-right: 8px;
}

.step-content h3 {
  margin: 0 0 24px 0;
  font-size: 20px;
  font-weight: 600;
}

.step-content h4 {
  margin: 24px 0 16px 0;
  font-size: 16px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #333;
}

.required {
  color: #e74c3c;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3498db;
}

.form-group textarea {
  resize: vertical;
  font-family: inherit;
}

.form-group small {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #666;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-range input {
  flex: 1;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
}

.tags-list {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #e8f4fd;
  color: #2980b9;
  border-radius: 16px;
  font-size: 13px;
}

.tag-chip button {
  border: none;
  background: none;
  color: #2980b9;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  padding: 0;
}

.placeholder-hints {
  margin-top: 12px;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 6px;
}

.placeholder-hints strong {
  display: block;
  margin-bottom: 12px;
  font-size: 13px;
  color: #666;
}

.placeholder-chip {
  display: inline-block;
  padding: 6px 12px;
  margin: 6px 6px 0 0;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 12px;
  font-family: monospace;
  cursor: pointer;
  transition: all 0.2s;
}

.placeholder-chip:hover {
  background: #3498db;
  color: #fff;
  border-color: #3498db;
}

.sms-counter {
  margin-top: 12px;
  padding: 12px 16px;
  background: #e8f4fd;
  border-radius: 6px;
  font-size: 14px;
}

.sms-counter strong {
  color: #2980b9;
}

.sms-counter .warning {
  display: block;
  margin-top: 8px;
  color: #e67e22;
}

.preview-section {
  margin-top: 24px;
}

.message-preview {
  padding: 16px;
  background: #f8f9fa;
  border-left: 3px solid #3498db;
  border-radius: 6px;
  font-family: inherit;
  white-space: pre-wrap;
  line-height: 1.6;
}

.prepare-prompt {
  text-align: center;
  padding: 48px 24px;
}

.prepare-prompt p {
  margin-bottom: 24px;
  font-size: 16px;
  color: #7f8c8d;
}

.cost-estimate {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 24px;
}

.cost-estimate h4 {
  margin: 0 0 16px 0;
}

.cost-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.cost-item {
  text-align: center;
}

.cost-label {
  font-size: 12px;
  color: #7f8c8d;
  margin-bottom: 8px;
}

.cost-value {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.cost-value.highlight {
  color: #27ae60;
}

.wizard-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

.btn-primary,
.btn-secondary,
.btn-success {
  padding: 12px 28px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3498db;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-success {
  background: #27ae60;
  color: #fff;
}

.btn-success:hover:not(:disabled) {
  background: #229954;
}

.btn-primary:disabled,
.btn-success:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #ecf0f1;
  color: #333;
}

.btn-secondary:hover {
  background: #bdc3c7;
}
</style>


