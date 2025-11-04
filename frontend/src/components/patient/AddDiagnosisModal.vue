<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    title="Добавить заключительный диагноз"
    style="width: 650px"
    :bordered="false"
    :mask-closable="false"
    @update:show="handleClose"
  >
    <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
      <n-grid :cols="2" :x-gap="12">
        <n-gi>
          <n-form-item label="Дата *" path="date">
            <n-date-picker
              v-model:value="formData.date"
              type="date"
              placeholder="дд.мм.гггг"
              style="width: 100%"
            />
          </n-form-item>
        </n-gi>
        <n-gi>
          <n-form-item label="Тип *" path="type">
            <n-select v-model:value="formData.type" :options="typeOptions" placeholder="Выберите тип" />
          </n-form-item>
        </n-gi>
      </n-grid>

      <n-form-item label="Заключительный диагноз *" path="diagnosis">
        <n-input
          v-model:value="formData.diagnosis"
          placeholder="Описание диагноза"
          type="textarea"
          :rows="3"
        />
      </n-form-item>

      <n-form-item label="Код МКБ-10" path="icd_code">
        <n-select
          v-model:value="formData.icd_code"
          :options="icdOptions"
          filterable
          placeholder="Выберите или введите код"
          :loading="icdLoading"
        />
      </n-form-item>

      <n-form-item label="Врач *" path="doctor">
        <n-select
          v-model:value="formData.doctor"
          :options="doctorOptions"
          filterable
          placeholder="Выберите врача"
          :loading="doctorsLoading"
        />
      </n-form-item>
    </n-form>

    <template #footer>
      <div style="display: flex; justify-content: flex-end; gap: 8px">
        <n-button @click="handleClose">Отмена</n-button>
        <n-button type="primary" :loading="loading" @click="handleSubmit">Сохранить</n-button>
      </div>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import {
  NModal,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NDatePicker,
  NButton,
  NGrid,
  NGi,
  useMessage
} from 'naive-ui'
import { createPatientDiagnosis, updatePatientDiagnosis } from '@/api/patients'
import { getEmployees } from '@/api/staff'

const props = defineProps({
  show: Boolean,
  patientId: [Number, String],
  diagnosis: Object
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const visible = ref(false)
const loading = ref(false)
const formRef = ref(null)
const doctorsLoading = ref(false)
const icdLoading = ref(false)
const doctorOptions = ref([])
const icdOptions = ref([])

const typeOptions = [
  { label: 'Первичный', value: '1' },
  { label: 'Повторный', value: '2' }
]

const formData = ref({
  date: null,
  diagnosis: '',
  icd_code: null,
  type: '1',
  doctor: null
})

const rules = {
  date: [{ type: 'number', required: true, message: 'Укажите дату', trigger: ['blur', 'change'] }],
  diagnosis: [{ required: true, message: 'Укажите диагноз', trigger: ['blur', 'input'] }],
  type: [{ required: true, message: 'Выберите тип', trigger: ['blur', 'change'] }],
  doctor: [{ type: 'number', required: true, message: 'Выберите врача', trigger: ['blur', 'change'] }]
}

watch(
  () => props.show,
  (val) => {
    visible.value = val
    if (val) {
      if (props.diagnosis) {
        formData.value = {
          date: props.diagnosis.date ? new Date(props.diagnosis.date).getTime() : null,
          diagnosis: props.diagnosis.diagnosis || '',
          icd_code: props.diagnosis.icd_code || null,
          type: props.diagnosis.type || '1',
          doctor: props.diagnosis.doctor || null
        }
      } else {
        formData.value = {
          date: null,
          diagnosis: '',
          icd_code: null,
          type: '1',
          doctor: null
        }
      }
    }
  }
)

onMounted(() => {
  loadDoctors()
})

const loadDoctors = async () => {
  try {
    doctorsLoading.value = true
    const response = await getEmployees({ role: 'doctor' })
    doctorOptions.value = response.data.results.map((doc) => ({
      label: `${doc.last_name} ${doc.first_name} - ${doc.position || 'Врач'}`,
      value: doc.id
    }))
  } catch (error) {
    console.error('Error loading doctors:', error)
  } finally {
    doctorsLoading.value = false
  }
}

const handleClose = () => {
  emit('update:show', false)
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true

    const payload = {
      patient: props.patientId,
      date: formData.value.date ? new Date(formData.value.date).toISOString().split('T')[0] : null,
      diagnosis: formData.value.diagnosis,
      icd_code: formData.value.icd_code,
      type: formData.value.type,
      doctor: formData.value.doctor
    }

    if (props.diagnosis) {
      await updatePatientDiagnosis(props.diagnosis.id, payload)
      message.success('Диагноз обновлен')
    } else {
      await createPatientDiagnosis(payload)
      message.success('Диагноз добавлен')
    }

    emit('saved')
    handleClose()
  } catch (error) {
    console.error('Error saving diagnosis:', error)
    if (error.message) {
      message.error(error.message)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
/* Modal styles */
</style>

