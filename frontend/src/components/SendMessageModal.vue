<template>
  <ModalWrapper
    :visible="visible"
    title="Отправить сообщение"
    @close="$emit('close')"
    width="800px"
  >
    <form @submit.prevent="handleSubmit" class="send-message-form">
      <div class="form-group">
        <label>Отправитель</label>
        <input
          :value="senderName"
          type="text"
          readonly
          disabled
        />
        <small>Имя отправителя из настроек провайдера</small>
      </div>

      <div class="form-group">
        <label>Канал</label>
        <select v-model="form.channel">
          <option value="sms">SMS</option>
          <option value="whatsapp">WhatsApp</option>
          <option value="telegram">Telegram</option>
        </select>
      </div>

      <div class="form-group">
        <label>Получатели <span class="required">*</span></label>
        <div class="recipient-search">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск пациентов по имени, телефону или тегам..."
            @input="searchPatients"
          />
          <div v-if="searchResults.length > 0" class="search-results">
            <div
              v-for="patient in searchResults"
              :key="patient.id"
              class="search-result-item"
              @click="selectPatient(patient)"
            >
              <div class="patient-info">
                <strong>{{ patient.full_name }}</strong>
                <small>{{ patient.phone }}</small>
              </div>
              <div v-if="patient.tags && patient.tags.length" class="patient-tags">
                <span v-for="tag in patient.tags.slice(0, 3)" :key="tag" class="tag-mini">
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="selectedPatients.length > 0" class="selected-patients">
          <h4>Выбрано: {{ selectedPatients.length }}</h4>
          <div class="patient-chips">
            <span
              v-for="patient in selectedPatients"
              :key="patient.id"
              class="patient-chip"
            >
              {{ patient.full_name }}
              <button @click="removePatient(patient.id)">×</button>
            </span>
          </div>
        </div>
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
          <div>
            <strong>{{ smsSegments }} SMS</strong> ({{ messageLength }} символов)
          </div>
          <div v-if="selectedPatients.length > 0" class="cost-info">
            Будет списано: <strong>{{ totalSms }} SMS</strong> на сумму
            <strong>{{ formatMoney(estimatedCost) }}</strong>
          </div>
          <small v-if="smsSegments > 3" class="warning">
            ⚠ Более 3 сегментов - высокая стоимость
          </small>
        </div>
      </div>

      <div class="form-actions">
        <button type="button" class="btn-secondary" @click="$emit('close')">
          Отмена
        </button>
        <button
          type="submit"
          class="btn-primary"
          :disabled="loading || selectedPatients.length === 0"
        >
          {{ loading ? 'Отправка...' : `Отправить (${selectedPatients.length})` }}
        </button>
      </div>
    </form>
  </ModalWrapper>
</template>

<script>
import ModalWrapper from './ModalWrapper.vue'
import { sendManualMessage } from '@/api/marketing'
import { getPatients } from '@/api/patients'

export default {
  name: 'SendMessageModal',
  components: { ModalWrapper },
  props: {
    visible: Boolean,
  },
  data() {
    return {
      loading: false,
      searchQuery: '',
      searchResults: [],
      selectedPatients: [],
      form: {
        patient_ids: [],
        body: '',
        channel: 'sms',
      },
      senderName: 'CLINIC',
      pricePerSms: 15,
      placeholders: [
        '_ИМЯ_ПАЦИЕНТА_',
        '_ИМЯ_ОТЧЕСТВО_ПАЦИЕНТА_',
        '_ДАТА_ВИЗИТА_',
        '_ССЫЛКА_НА_ОНЛАЙН_ЗАПИСЬ_',
      ],
      searchTimeout: null,
    }
  },
  computed: {
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
    totalSms() {
      return this.selectedPatients.length * this.smsSegments
    },
    estimatedCost() {
      return this.totalSms * this.pricePerSms
    },
  },
  watch: {
    visible(val) {
      if (val) {
        this.resetForm()
      }
    },
  },
  methods: {
    resetForm() {
      this.form = {
        patient_ids: [],
        body: '',
        channel: 'sms',
      }
      this.selectedPatients = []
      this.searchQuery = ''
      this.searchResults = []
    },
    searchPatients() {
      clearTimeout(this.searchTimeout)
      
      if (!this.searchQuery || this.searchQuery.length < 2) {
        this.searchResults = []
        return
      }
      
      this.searchTimeout = setTimeout(async () => {
        try {
          const response = await getPatients({ search: this.searchQuery, limit: 10 })
          this.searchResults = response.data.results || response.data || []
        } catch (error) {
          console.error('Error searching patients:', error)
        }
      }, 300)
    },
    selectPatient(patient) {
      // Check if already selected
      if (this.selectedPatients.find(p => p.id === patient.id)) {
        return
      }
      
      this.selectedPatients.push(patient)
      this.searchQuery = ''
      this.searchResults = []
    },
    removePatient(patientId) {
      this.selectedPatients = this.selectedPatients.filter(p => p.id !== patientId)
    },
    insertPlaceholder(placeholder) {
      const textarea = this.$el.querySelector('textarea')
      if (!textarea) return
      
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
      if (this.selectedPatients.length === 0) {
        this.$emit('error', 'Выберите хотя бы одного получателя')
        return
      }
      
      this.loading = true
      try {
        const payload = {
          patient_ids: this.selectedPatients.map(p => p.id),
          body: this.form.body,
          channel: this.form.channel,
        }
        
        const response = await sendManualMessage(payload)
        
        this.$emit('success', `Отправлено: ${response.data.sent}, ошибок: ${response.data.failed}. Стоимость: ${response.data.total_cost} ₸`)
        this.$emit('close')
      } catch (error) {
        console.error('Error sending manual message:', error)
        this.$emit('error', error.response?.data?.error || 'Ошибка отправки')
      } finally {
        this.loading = false
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
.send-message-form {
  max-width: 100%;
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
}

.form-group input:disabled {
  background: #f5f5f5;
  color: #666;
  cursor: not-allowed;
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

.recipient-search {
  position: relative;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 300px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 10;
  margin-top: 4px;
}

.search-result-item {
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #ecf0f1;
  transition: background 0.2s;
}

.search-result-item:hover {
  background: #f8f9fa;
}

.search-result-item:last-child {
  border-bottom: none;
}

.patient-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.patient-info strong {
  font-size: 14px;
}

.patient-info small {
  font-size: 12px;
  color: #7f8c8d;
}

.patient-tags {
  margin-top: 6px;
  display: flex;
  gap: 4px;
}

.tag-mini {
  display: inline-block;
  padding: 2px 8px;
  background: #e8f4fd;
  color: #2980b9;
  border-radius: 10px;
  font-size: 11px;
}

.selected-patients {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.selected-patients h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
}

.patient-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.patient-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 16px;
  font-size: 13px;
}

.patient-chip button {
  border: none;
  background: none;
  color: #e74c3c;
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

.cost-info {
  margin-top: 8px;
  font-size: 13px;
}

.cost-info strong {
  color: #27ae60;
}

.sms-counter .warning {
  display: block;
  margin-top: 8px;
  color: #e67e22;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

.btn-primary,
.btn-secondary {
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

.btn-primary:disabled {
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


