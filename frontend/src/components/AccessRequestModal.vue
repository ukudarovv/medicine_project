<template>
  <ModalWrapper
    :visible="visible"
    title="Запросить доступ к медицинской карте"
    width="700px"
    @close="handleClose"
  >
    <div class="access-request-form">
      <!-- Step 1: Search Patient -->
      <div v-if="step === 1" class="form-step">
        <div class="form-group">
          <label for="iin">ИИН пациента <span class="required">*</span></label>
          <input
            id="iin"
            v-model="form.iin"
            type="text"
            class="form-control"
            placeholder="Введите 12 цифр ИИН"
            maxlength="12"
            @input="validateIIN"
          />
          <div v-if="errors.iin" class="error-message">{{ errors.iin }}</div>
        </div>

        <button
          class="btn btn-primary"
          :disabled="!form.iin || form.iin.length !== 12 || searchingPatient"
          @click="searchPatient"
        >
          <span v-if="searchingPatient">Поиск...</span>
          <span v-else>Найти пациента</span>
        </button>

        <div v-if="patientFound" class="patient-info">
          <h4>Пациент найден:</h4>
          <div class="patient-card">
            <div class="patient-field">
              <strong>ФИО:</strong> {{ patientData.fio_masked }}
            </div>
            <div class="patient-field">
              <strong>Возраст:</strong> {{ patientData.age }} лет
            </div>
            <div class="patient-field">
              <strong>ИИН:</strong> {{ patientData.iin_masked }}
            </div>
            <div class="patient-field">
              <strong>Telegram:</strong> 
              <span :class="patientData.has_telegram ? 'badge-success' : 'badge-warning'">
                {{ patientData.has_telegram ? 'Подключен' : 'Не подключен' }}
              </span>
            </div>
          </div>

          <button class="btn btn-primary" @click="step = 2">
            Продолжить
          </button>
        </div>
      </div>

      <!-- Step 2: Request Details -->
      <div v-if="step === 2" class="form-step">
        <div class="patient-summary">
          <strong>Пациент:</strong> {{ patientData.fio_masked }}, {{ patientData.age }} лет
        </div>

        <div class="form-group">
          <label>Запрашиваемые права <span class="required">*</span></label>
          <div class="scopes-list">
            <label class="scope-item">
              <input type="checkbox" v-model="form.scopes" value="read_summary" />
              <span class="scope-label">
                <strong>Чтение краткой информации</strong>
                <small>ФИО, возраст, аллергии, контакты</small>
              </span>
            </label>
            <label class="scope-item">
              <input type="checkbox" v-model="form.scopes" value="read_records" />
              <span class="scope-label">
                <strong>Чтение медицинских записей</strong>
                <small>История визитов, диагнозы, назначения</small>
              </span>
            </label>
            <label class="scope-item">
              <input type="checkbox" v-model="form.scopes" value="write_records" />
              <span class="scope-label">
                <strong>Создание медицинских записей</strong>
                <small>Внесение новых записей о визитах</small>
              </span>
            </label>
            <label class="scope-item">
              <input type="checkbox" v-model="form.scopes" value="read_images" />
              <span class="scope-label">
                <strong>Просмотр изображений</strong>
                <small>Рентген, КТ, МРТ, фотографии</small>
              </span>
            </label>
          </div>
          <div v-if="errors.scopes" class="error-message">{{ errors.scopes }}</div>
        </div>

        <div class="form-group">
          <label for="reason">Причина запроса <span class="required">*</span></label>
          <textarea
            id="reason"
            v-model="form.reason"
            class="form-control"
            placeholder="Укажите причину запроса доступа (например: консультация, плановый осмотр, экстренная помощь)"
            rows="3"
          ></textarea>
          <div v-if="errors.reason" class="error-message">{{ errors.reason }}</div>
        </div>

        <div class="form-group">
          <label for="duration">Срок доступа</label>
          <select id="duration" v-model.number="form.requested_duration_days" class="form-control">
            <option :value="1">1 день</option>
            <option :value="7">7 дней</option>
            <option :value="14">14 дней</option>
            <option :value="30">30 дней</option>
            <option :value="90">90 дней</option>
          </select>
        </div>

        <div class="form-actions">
          <button class="btn btn-secondary" @click="step = 1">
            Назад
          </button>
          <button
            class="btn btn-primary"
            :disabled="!canSubmit || submitting"
            @click="submitRequest"
          >
            <span v-if="submitting">Отправка...</span>
            <span v-else>Отправить запрос</span>
          </button>
        </div>
      </div>

      <!-- Step 3: Request Status -->
      <div v-if="step === 3" class="form-step">
        <div class="request-status">
          <div v-if="requestStatus === 'pending'" class="status-pending">
            <div class="spinner"></div>
            <h3>⏳ Ожидание ответа пациента</h3>
            <p>Запрос отправлен пациенту через Telegram.</p>
            <p>Код подтверждения будет действителен 10 минут.</p>
            <div class="countdown" v-if="timeLeft > 0">
              Осталось: {{ formatTime(timeLeft) }}
            </div>
          </div>

          <div v-if="requestStatus === 'approved'" class="status-success">
            <div class="status-icon">✅</div>
            <h3>Доступ предоставлен</h3>
            <p>Пациент одобрил ваш запрос.</p>
            <div class="grant-info">
              <strong>Доступ действителен до:</strong> {{ grantValidTo }}
            </div>
          </div>

          <div v-if="requestStatus === 'denied'" class="status-error">
            <div class="status-icon">❌</div>
            <h3>Доступ отклонён</h3>
            <p>Пациент отклонил ваш запрос на доступ.</p>
          </div>

          <div v-if="requestStatus === 'expired'" class="status-warning">
            <div class="status-icon">⏰</div>
            <h3>Запрос истёк</h3>
            <p>Пациент не ответил в течение 10 минут.</p>
            <p>Вы можете отправить новый запрос.</p>
          </div>
        </div>

        <div class="form-actions">
          <button class="btn btn-secondary" @click="handleClose">
            Закрыть
          </button>
          <button
            v-if="requestStatus !== 'approved'"
            class="btn btn-primary"
            @click="resetForm"
          >
            Новый запрос
          </button>
        </div>
      </div>
    </div>
  </ModalWrapper>
</template>

<script>
import ModalWrapper from './ModalWrapper.vue'
import { searchPatientByIIN, createAccessRequest, getAccessRequest } from '@/api/consent'

export default {
  name: 'AccessRequestModal',
  components: {
    ModalWrapper
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      step: 1,
      form: {
        iin: '',
        scopes: ['read_summary', 'read_records'],
        reason: '',
        requested_duration_days: 30
      },
      errors: {},
      searchingPatient: false,
      patientFound: false,
      patientData: null,
      submitting: false,
      requestId: null,
      requestStatus: null,
      grantValidTo: null,
      timeLeft: 600, // 10 minutes in seconds
      pollingInterval: null
    }
  },
  computed: {
    canSubmit() {
      return (
        this.form.scopes.length > 0 &&
        this.form.reason.trim().length > 0
      )
    }
  },
  watch: {
    visible(val) {
      if (!val) {
        this.resetForm()
      }
    }
  },
  beforeUnmount() {
    this.stopPolling()
  },
  methods: {
    validateIIN() {
      // Remove non-digits
      this.form.iin = this.form.iin.replace(/\D/g, '')
      
      if (this.form.iin.length === 12) {
        delete this.errors.iin
      }
    },

    async searchPatient() {
      this.errors = {}
      
      if (this.form.iin.length !== 12) {
        this.errors.iin = 'ИИН должен состоять из 12 цифр'
        return
      }

      this.searchingPatient = true

      try {
        const data = await searchPatientByIIN(this.form.iin)
        this.patientData = data
        this.patientFound = true
      } catch (error) {
        this.errors.iin = error.response?.data?.error || 'Пациент с таким ИИН не найден'
        this.patientFound = false
      } finally {
        this.searchingPatient = false
      }
    },

    async submitRequest() {
      this.errors = {}

      if (this.form.scopes.length === 0) {
        this.errors.scopes = 'Выберите хотя бы один тип доступа'
        return
      }

      if (!this.form.reason.trim()) {
        this.errors.reason = 'Укажите причину запроса'
        return
      }

      this.submitting = true

      try {
        const data = await createAccessRequest({
          patient_iin: this.form.iin,
          scopes: this.form.scopes,
          reason: this.form.reason,
          requested_duration_days: this.form.requested_duration_days
        })

        this.requestId = data.id
        this.requestStatus = data.status
        this.step = 3
        this.startPolling()
        this.startCountdown()
      } catch (error) {
        const errorData = error.response?.data
        if (errorData) {
          if (errorData.patient_iin) {
            this.errors.scopes = errorData.patient_iin[0]
          } else if (errorData.non_field_errors) {
            this.errors.reason = errorData.non_field_errors[0]
          } else {
            this.errors.reason = 'Ошибка при создании запроса'
          }
        }
      } finally {
        this.submitting = false
      }
    },

    startPolling() {
      // Poll for status updates every 2 seconds
      this.pollingInterval = setInterval(async () => {
        try {
          const data = await getAccessRequest(this.requestId)
          this.requestStatus = data.status

          if (data.status === 'approved') {
            this.grantValidTo = data.grant?.valid_to
            this.stopPolling()
          } else if (data.status === 'denied' || data.status === 'expired') {
            this.stopPolling()
          }
        } catch (error) {
          console.error('Error polling request status:', error)
        }
      }, 2000)
    },

    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
        this.pollingInterval = null
      }
    },

    startCountdown() {
      const countdownInterval = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) {
          clearInterval(countdownInterval)
        }
      }, 1000)
    },

    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    },

    resetForm() {
      this.step = 1
      this.form = {
        iin: '',
        scopes: ['read_summary', 'read_records'],
        reason: '',
        requested_duration_days: 30
      }
      this.errors = {}
      this.patientFound = false
      this.patientData = null
      this.requestId = null
      this.requestStatus = null
      this.grantValidTo = null
      this.timeLeft = 600
      this.stopPolling()
    },

    handleClose() {
      this.stopPolling()
      this.$emit('close')
      this.$emit('request-completed', this.requestStatus === 'approved')
    }
  }
}
</script>

<style scoped lang="scss">
.access-request-form {
  padding: 20px 0;
}

.form-step {
  min-height: 300px;
}

.form-group {
  margin-bottom: 20px;

  label {
    display: block;
    font-weight: 600;
    margin-bottom: 8px;
    color: #333;

    .required {
      color: #e74c3c;
    }
  }

  .form-control {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;

    &:focus {
      outline: none;
      border-color: #3498db;
    }
  }

  textarea.form-control {
    resize: vertical;
    min-height: 80px;
  }
}

.error-message {
  color: #e74c3c;
  font-size: 13px;
  margin-top: 5px;
}

.patient-info {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;

  h4 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #2c3e50;
  }
}

.patient-card {
  background: white;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 15px;
}

.patient-field {
  padding: 8px 0;
  border-bottom: 1px solid #ecf0f1;

  &:last-child {
    border-bottom: none;
  }

  strong {
    display: inline-block;
    width: 120px;
    color: #7f8c8d;
  }
}

.badge-success {
  padding: 3px 10px;
  background: #27ae60;
  color: white;
  border-radius: 12px;
  font-size: 12px;
}

.badge-warning {
  padding: 3px 10px;
  background: #f39c12;
  color: white;
  border-radius: 12px;
  font-size: 12px;
}

.patient-summary {
  padding: 12px;
  background: #e8f5e9;
  border-left: 4px solid #27ae60;
  margin-bottom: 20px;
  border-radius: 4px;
}

.scopes-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.scope-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  border: 2px solid #ecf0f1;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #3498db;
    background: #f8f9fa;
  }

  input[type="checkbox"] {
    margin-right: 12px;
    margin-top: 2px;
  }

  input[type="checkbox"]:checked + .scope-label {
    color: #2c3e50;
  }
}

.scope-label {
  flex: 1;
  color: #7f8c8d;

  strong {
    display: block;
    margin-bottom: 4px;
    color: #2c3e50;
  }

  small {
    display: block;
    font-size: 12px;
    color: #95a5a6;
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.btn-primary {
  background: #3498db;
  color: white;

  &:hover:not(:disabled) {
    background: #2980b9;
  }
}

.btn-secondary {
  background: #95a5a6;
  color: white;

  &:hover:not(:disabled) {
    background: #7f8c8d;
  }
}

.request-status {
  text-align: center;
  padding: 40px 20px;
}

.status-pending,
.status-success,
.status-error,
.status-warning {
  h3 {
    margin: 20px 0 10px;
    font-size: 20px;
  }

  p {
    color: #7f8c8d;
    margin: 10px 0;
  }
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #ecf0f1;
  border-top-color: #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.status-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.countdown {
  margin-top: 20px;
  font-size: 24px;
  font-weight: 700;
  color: #3498db;
}

.grant-info {
  margin-top: 20px;
  padding: 15px;
  background: #e8f5e9;
  border-radius: 6px;
  color: #27ae60;
  font-weight: 600;
}
</style>

