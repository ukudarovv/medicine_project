<template>
  <n-modal
    v-model:show="visible"
    title="Добавить пациента по ИИН"
    preset="card"
    style="width: 600px"
    :segmented="{ content: 'soft' }"
    :mask-closable="false"
  >
    <n-steps :current="currentStep" :status="stepStatus">
      <n-step title="Ввод ИИН" />
      <n-step title="SMS верификация" />
      <n-step title="Завершение" />
    </n-steps>

    <div style="margin-top: 24px;">
      <!-- Step 1: Ввод ИИН -->
      <div v-if="currentStep === 1">
        <n-alert type="info" style="margin-bottom: 16px">
          Введите ИИН пациента для поиска в базе данных
        </n-alert>

        <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
          <n-form-item label="ИИН (12 цифр)" path="iin">
            <n-input
              v-model:value="formData.iin"
              placeholder="123456789012"
              maxlength="12"
              :loading="searching"
              @keyup.enter="searchPatient"
            >
              <template #suffix>
                <n-button
                  text
                  type="primary"
                  :loading="searching"
                  :disabled="!formData.iin || formData.iin.length !== 12"
                  @click="searchPatient"
                >
                  Найти
                </n-button>
              </template>
            </n-input>
          </n-form-item>
        </n-form>

        <n-alert v-if="patientInfo" type="success" style="margin-top: 16px">
          <div style="margin-bottom: 8px">
            <strong>Найден пациент:</strong>
          </div>
          <n-descriptions :column="1" size="small" bordered>
            <n-descriptions-item label="ФИО">
              {{ patientInfo.patient_name }}
            </n-descriptions-item>
            <n-descriptions-item label="Телефон">
              {{ patientInfo.phone }}
            </n-descriptions-item>
          </n-descriptions>
        </n-alert>
      </div>

      <!-- Step 2: SMS Verification -->
      <div v-if="currentStep === 2">
        <n-alert type="success" style="margin-bottom: 16px">
          SMS код отправлен на номер <strong>{{ patientInfo?.phone }}</strong>
          <br/>
          <small style="color: #666;">Для тестирования используйте код: <strong>1234</strong></small>
        </n-alert>

        <n-form>
          <n-form-item label="Введите SMS код">
            <n-input
              v-model:value="smsCode"
              placeholder="1234"
              maxlength="4"
              :disabled="verifying"
              @keyup.enter="verifyCode"
            />
          </n-form-item>

          <n-countdown
            v-if="codeExpiresAt && !codeExpired"
            :duration="codeExpiresDuration"
            :active="true"
            @finish="handleCodeExpired"
          >
            <template #default="{ minutes, seconds }">
              <n-text depth="3">Код действителен: {{ minutes }}:{{ String(seconds).padStart(2, '0') }}</n-text>
            </template>
          </n-countdown>

          <n-space v-if="codeExpired" style="margin-top: 12px">
            <n-text type="error">Код истек</n-text>
            <n-button text type="primary" @click="resendCode" :loading="sending">
              Отправить новый код
            </n-button>
          </n-space>
        </n-form>
      </div>

      <!-- Step 3: Success -->
      <div v-if="currentStep === 3">
        <n-result status="success" title="Пациент успешно добавлен!" style="padding: 20px 0">
          <template #footer>
            <n-descriptions bordered :column="2">
              <n-descriptions-item label="ФИО" :span="2">
                {{ addedPatient?.last_name }} {{ addedPatient?.first_name }} {{ addedPatient?.middle_name }}
              </n-descriptions-item>
              <n-descriptions-item label="Телефон">
                {{ addedPatient?.phone }}
              </n-descriptions-item>
              <n-descriptions-item label="ID">
                #{{ addedPatient?.id }}
              </n-descriptions-item>
            </n-descriptions>
          </template>
        </n-result>
      </div>
    </div>

    <template #footer>
      <n-space justify="end">
        <n-button v-if="currentStep < 3" @click="handleClose">Отмена</n-button>
        <n-button v-if="currentStep === 3" type="primary" @click="handleClose">Закрыть</n-button>

        <n-button
          v-if="currentStep === 1 && patientInfo"
          type="primary"
          :loading="sending"
          @click="sendVerificationCode"
        >
          Отправить SMS
        </n-button>

        <n-button
          v-if="currentStep === 2"
          type="primary"
          :loading="verifying"
          :disabled="!smsCode || smsCode.length !== 4"
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

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()

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
  iin: ''
})

// Form rules
const rules = {
  iin: [
    { required: true, message: 'Введите ИИН', trigger: 'blur' },
    { len: 12, message: 'ИИН должен содержать 12 цифр', trigger: 'blur' },
    { pattern: /^\d{12}$/, message: 'ИИН должен содержать только цифры', trigger: 'blur' }
  ]
}

// Search & Verification
const searching = ref(false)
const patientInfo = ref(null)
const smsCode = ref('')
const verificationId = ref(null)
const sending = ref(false)
const verifying = ref(false)
const codeExpiresAt = ref(null)
const codeExpiresDuration = ref(0)
const codeExpired = ref(false)
const addedPatient = ref(null)

// Search patient by IIN
async function searchPatient() {
  try {
    await formRef.value?.validate()
    searching.value = true
    patientInfo.value = null

    // This will also send SMS code
    const response = await apiClient.post('/patients/patients/send-verification/', {
      iin: formData.value.iin
    })

    patientInfo.value = response.data
    verificationId.value = response.data.verification_id
    codeExpiresAt.value = Date.now() + (response.data.expires_in_seconds * 1000)
    codeExpiresDuration.value = response.data.expires_in_seconds * 1000
    codeExpired.value = false

    message.success('Пациент найден! SMS код отправлен')
    message.info('Тестовый код: 1234', { duration: 10000 })
    
    // Move to step 2
    currentStep.value = 2
  } catch (error) {
    console.error('Failed to search patient:', error)
    if (error.response?.data?.error) {
      message.error(error.response.data.error)
    } else {
      message.error('Ошибка поиска пациента')
    }
    patientInfo.value = null
  } finally {
    searching.value = false
  }
}

// Send verification code (already sent in search)
async function sendVerificationCode() {
  // Code is already sent in searchPatient
  currentStep.value = 2
}

// Resend code
async function resendCode() {
  smsCode.value = ''
  codeExpired.value = false
  currentStep.value = 1
  await searchPatient()
}

// Verify code
async function verifyCode() {
  if (!smsCode.value || smsCode.value.length !== 4) {
    message.warning('Введите 4-значный код')
    return
  }

  try {
    verifying.value = true

    const response = await apiClient.post('/patients/patients/verify-code/', {
      verification_id: verificationId.value,
      code: smsCode.value
    })

    addedPatient.value = response.data.patient
    currentStep.value = 3
    stepStatus.value = 'finish'

    message.success(response.data.message || 'Пациент успешно добавлен!')
    
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
  patientInfo.value = null
  smsCode.value = ''
  verificationId.value = null
  codeExpiresAt.value = null
  codeExpired.value = false
  addedPatient.value = null
  
  formData.value = {
    iin: ''
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

