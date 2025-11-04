<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    title="Добавить заболевание"
    style="width: 650px"
    :bordered="false"
    :mask-closable="false"
    @update:show="handleClose"
  >
    <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
      <n-grid :cols="2" :x-gap="12">
        <n-gi>
          <n-form-item label="Дата начала наблюдения *" path="start_date">
            <n-date-picker
              v-model:value="formData.start_date"
              type="date"
              placeholder="дд.мм.гггг"
              style="width: 100%"
            />
          </n-form-item>
        </n-gi>
        <n-gi>
          <n-form-item label="Дата прекращения наблюдения" path="end_date">
            <n-date-picker
              v-model:value="formData.end_date"
              type="date"
              placeholder="дд.мм.гггг"
              style="width: 100%"
            />
          </n-form-item>
        </n-gi>
      </n-grid>

      <n-form-item label="Диагноз *" path="diagnosis">
        <n-input
          v-model:value="formData.diagnosis"
          placeholder="Описание заболевания"
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

      <n-form-item label="Врач" path="doctor">
        <n-select
          v-model:value="formData.doctor"
          :options="doctorOptions"
          filterable
          placeholder="Выберите врача"
          :loading="doctorsLoading"
        />
      </n-form-item>

      <n-form-item label="Примечания" path="notes">
        <n-input
          v-model:value="formData.notes"
          placeholder="Дополнительная информация"
          type="textarea"
          :rows="2"
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
import { createPatientDisease, updatePatientDisease } from '@/api/patients'
import { getEmployees } from '@/api/staff'
import { getICDCodes } from '@/api/services'

const props = defineProps({
  show: Boolean,
  patientId: [Number, String],
  disease: Object
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

const formData = ref({
  start_date: null,
  end_date: null,
  diagnosis: '',
  icd_code: null,
  doctor: null,
  notes: ''
})

const rules = {
  start_date: [{ type: 'number', required: true, message: 'Укажите дату начала', trigger: ['blur', 'change'] }],
  diagnosis: [{ required: true, message: 'Укажите диагноз', trigger: ['blur', 'input'] }]
}

watch(
  () => props.show,
  (val) => {
    visible.value = val
    if (val) {
      if (props.disease) {
        formData.value = {
          start_date: props.disease.start_date ? new Date(props.disease.start_date).getTime() : null,
          end_date: props.disease.end_date ? new Date(props.disease.end_date).getTime() : null,
          diagnosis: props.disease.diagnosis || '',
          icd_code: props.disease.icd_code || null,
          doctor: props.disease.doctor || null,
          notes: props.disease.notes || ''
        }
      } else {
        formData.value = {
          start_date: null,
          end_date: null,
          diagnosis: '',
          icd_code: null,
          doctor: null,
          notes: ''
        }
      }
    }
  }
)

onMounted(() => {
  loadDoctors()
  loadICDCodes()
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

const loadICDCodes = async () => {
  try {
    icdLoading.value = true
    // Assuming there's an ICD codes endpoint
    // const response = await getICDCodes()
    // For now, using placeholder
    icdOptions.value = []
  } catch (error) {
    console.error('Error loading ICD codes:', error)
  } finally {
    icdLoading.value = false
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
      diagnosis: formData.value.diagnosis,
      start_date: formData.value.start_date ? new Date(formData.value.start_date).toISOString().split('T')[0] : null,
      end_date: formData.value.end_date ? new Date(formData.value.end_date).toISOString().split('T')[0] : null,
      icd_code: formData.value.icd_code,
      doctor: formData.value.doctor,
      notes: formData.value.notes
    }

    if (props.disease) {
      await updatePatientDisease(props.disease.id, payload)
      message.success('Заболевание обновлено')
    } else {
      await createPatientDisease(payload)
      message.success('Заболевание добавлено')
    }

    emit('saved')
    handleClose()
  } catch (error) {
    console.error('Error saving disease:', error)
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

