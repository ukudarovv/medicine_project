<template>
  <n-modal
    v-model:show="visible"
    title="Регистрация нового пациента"
    preset="card"
    style="width: 700px"
    :segmented="{ content: 'soft' }"
    :mask-closable="false"
  >
    <n-steps :current="currentStep" :status="stepStatus">
      <n-step title="Основные данные" />
      <n-step title="SMS верификация" />
      <n-step title="Завершение" />
    </n-steps>

    <div style="margin-top: 24px;">
      <!-- Step 1: Основные данные -->
      <div v-if="currentStep === 1">
        <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
          <n-grid :cols="2" :x-gap="12">
            <n-grid-item>
              <n-form-item label="Фамилия" path="last_name">
                <n-input v-model:value="formData.last_name" placeholder="Иванов" />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="Имя" path="first_name">
                <n-input v-model:value="formData.first_name" placeholder="Иван" />
              </n-form-item>
            </n-grid-item>
          </n-grid>

          <n-form-item label="Отчество">
            <n-input v-model:value="formData.middle_name" placeholder="Иванович (необязательно)" />
          </n-form-item>

          <n-grid :cols="2" :x-gap="12">
            <n-grid-item>
              <n-form-item label="Дата рождения" path="birth_date">
                <n-date-picker
                  v-model:value="formData.birth_date"
                  type="date"
                  placeholder="Выберите дату"
                  style="width: 100%"
                  :is-date-disabled="disableFutureDates"
                />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="Пол" path="sex">
                <n-radio-group v-model:value="formData.sex">
                  <n-radio value="M">Мужской</n-radio>
                  <n-radio value="F">Женский</n-radio>
                </n-radio-group>
              </n-form-item>
            </n-grid-item>
          </n-grid>

          <n-form-item label="Телефон" path="phone">
            <n-input v-model:value="formData.phone" placeholder="+7 777 123 45 67" />
          </n-form-item>

          <n-form-item label="Email">
            <n-input v-model:value="formData.email" type="email" placeholder="email@example.com" />
          </n-form-item>

          <n-form-item label="Адрес">
            <n-input v-model:value="formData.address" type="textarea" placeholder="Адрес проживания" :rows="2" />
          </n-form-item>
        </n-form>
      </div>

      <!-- Step 2: SMS Verification -->
      <div v-if="currentStep === 2">
        <n-alert v-if="!smsCodeSent" type="info" style="margin-bottom: 16px">
          На номер <strong>{{ patientInfo?.phone }}</strong> будет отправлен SMS код для подтверждения
        </n-alert>

        <n-alert v-if="smsCodeSent" type="success" style="margin-bottom: 16px">
          SMS код отправлен на номер <strong>{{ patientInfo?.phone }}</strong>
          <br/>
          <small>Для тестирования используйте код: <strong>1234</strong></small>
        </n-alert>

        <n-form v-if="smsCodeSent">
          <n-form-item label="Введите SMS код">
            <n-input
              v-model:value="smsCode"
              placeholder="123456"
              maxlength="6"
              :disabled="verifying"
              @keyup.enter="verifyCode"
            />
          </n-form-item>

          <n-countdown
            v-if="codeExpiresAt"
            :duration="codeExpiresDuration"
            :active="!codeExpired"
            @finish="handleCodeExpired"
          >
            <template #default="{ hours, minutes, seconds }">
              <n-text depth="3">Код действителен: {{ minutes }}:{{ String(seconds).padStart(2, '0') }}</n-text>
            </template>
          </n-countdown>

          <n-space v-if="codeExpired" style="margin-top: 12px">
            <n-text type="error">Код истек</n-text>
            <n-button text type="primary" @click="resendCode">Отправить новый код</n-button>
          </n-space>
        </n-form>
      </div>

      <!-- Step 3: Success -->
      <div v-if="currentStep === 3">
        <n-result status="success" title="Пациент успешно зарегистрирован!" style="padding: 20px 0">
          <template #footer>
            <n-descriptions bordered :column="2">
              <n-descriptions-item label="ФИО">
                {{ createdPatient?.last_name }} {{ createdPatient?.first_name }} {{ createdPatient?.middle_name }}
              </n-descriptions-item>
              <n-descriptions-item label="Телефон">
                {{ createdPatient?.phone }}
              </n-descriptions-item>
              <n-descriptions-item label="Дата рождения">
                {{ formatDate(createdPatient?.birth_date) }}
              </n-descriptions-item>
              <n-descriptions-item label="ID">
                #{{ createdPatient?.id }}
              </n-descriptions-item>
            </n-descriptions>
          </template>
        </n-result>
      </div>
    </div>

    <template #footer>
      <n-space justify="end">
        <n-button v-if="currentStep === 1" @click="handleClose">Отмена</n-button>
        <n-button v-if="currentStep === 2 && !smsCodeSent" @click="currentStep = 1">Назад</n-button>
        <n-button v-if="currentStep === 3" type="primary" @click="handleClose">Закрыть</n-button>

        <n-button
          v-if="currentStep === 1"
          type="primary"
          :loading="sending"
          @click="sendVerificationCode"
        >
          Далее
        </n-button>

        <n-button
          v-if="currentStep === 2 && !smsCodeSent"
          type="primary"
          :loading="sending"
          @click="sendVerificationCode"
        >
          Отправить SMS
        </n-button>

        <n-button
          v-if="currentStep === 2 && smsCodeSent"
          type="primary"
          :loading="verifying"
          :disabled="!smsCode || smsCode.length !== 6"
          @click="verifyCode"
        >
          Подтвердить
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import apiClient from '@/api/axios'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const authStore = useAuthStore()

// Reactive visibility
const visible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val)
})

// Steps
const currentStep = ref(1)
const stepStatus = ref('process')

// Form data
const formRef = ref(null)
const formData = ref({
  last_name: '',
  first_name: '',
  middle_name: '',
  birth_date: null,
  sex: 'M',
  phone: '',
  email: '',
  address: ''
})

// Form rules
const rules = {
  last_name: [
    { required: true, message: 'Введите фамилию', trigger: 'blur' }
  ],
  first_name: [
    { required: true, message: 'Введите имя', trigger: 'blur' }
  ],
  birth_date: [
    { required: true, message: 'Выберите дату рождения', trigger: 'change', type: 'number' }
  ],
  sex: [
    { required: true, message: 'Выберите пол', trigger: 'change' }
  ],
  phone: [
    { required: true, message: 'Введите номер телефона', trigger: 'blur' }
  ]
}

// SMS Verification
const smsCodeSent = ref(false)
const smsCode = ref('')
const verificationId = ref(null)
const sending = ref(false)
const verifying = ref(false)
const codeExpiresAt = ref(null)
const codeExpiresDuration = ref(0)
const codeExpired = ref(false)
const createdPatient = ref(null)

// Disable future dates
const disableFutureDates = (ts) => {
  return ts > Date.now()
}

// Format date
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('ru-RU')
}

// Send verification code
async function sendVerificationCode() {
  try {
    await formRef.value?.validate()
    sending.value = true

    // Convert date to ISO format
    const patientData = {
      ...formData.value,
      birth_date: formData.value.birth_date 
        ? new Date(formData.value.birth_date).toISOString().split('T')[0]
        : null
    }

    const response = await apiClient.post('/patients/patients/send-verification/', {
      phone: formData.value.phone,
      patient_data: patientData
    })

    verificationId.value = response.data.verification_id
    smsCodeSent.value = true
    codeExpiresAt.value = Date.now() + (response.data.expires_in_seconds * 1000)
    codeExpiresDuration.value = response.data.expires_in_seconds * 1000
    codeExpired.value = false
    currentStep.value = 2

    message.success(`SMS код отправлен на номер ${formData.value.phone}`)
    message.info('Тестовый код: 123456', { duration: 10000 })
  } catch (error) {
    console.error('Failed to send verification:', error)
    if (error.response?.data?.error) {
      message.error(error.response.data.error)
    } else {
      message.error('Ошибка отправки SMS')
    }
  } finally {
    sending.value = false
  }
}

// Resend code
async function resendCode() {
  smsCodeSent.value = false
  smsCode.value = ''
  await sendVerificationCode()
}

// Verify code
async function verifyCode() {
  if (!smsCode.value || smsCode.value.length !== 6) {
    message.warning('Введите 6-значный код')
    return
  }

  try {
    verifying.value = true

    const response = await apiClient.post('/patients/patients/verify-code/', {
      verification_id: verificationId.value,
      code: smsCode.value
    })

    createdPatient.value = response.data.patient
    currentStep.value = 3
    stepStatus.value = 'finish'

    message.success('Пациент успешно зарегистрирован!')
    
    // Notify parent
    emit('saved', response.data.patient)
  } catch (error) {
    console.error('Failed to verify code:', error)
    if (error.response?.data?.error) {
      message.error(error.response.data.error)
    } else {
      message.error('Ошибка проверки кода')
    }
  } finally {
    verifying.value = false
  }
}

// Handle code expired
function handleCodeExpired() {
  codeExpired.value = true
  message.warning('Код истек. Запросите новый код.')
}

// Handle close
function handleClose() {
  resetForm()
  visible.value = false
}

// Reset form
function resetForm() {
  currentStep.value = 1
  stepStatus.value = 'process'
  smsCodeSent.value = false
  smsCode.value = ''
  verificationId.value = null
  codeExpiresAt.value = null
  codeExpired.value = false
  createdPatient.value = null
  
  formData.value = {
    last_name: '',
    first_name: '',
    middle_name: '',
    birth_date: null,
    sex: 'M',
    phone: '',
    email: '',
    address: ''
  }
}

// Watch visibility
watch(() => props.show, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})
</script>

<style scoped>
:deep(.n-step) {
  cursor: default;
}
</style>

