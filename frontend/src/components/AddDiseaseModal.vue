<template>
  <n-modal
    v-model:show="visible"
    title="Добавить заболевание"
    preset="card"
    style="width: 700px"
  >
    <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
      <n-grid :cols="2" :x-gap="12">
        <n-grid-item>
          <n-form-item label="Дата начала наблюдения" path="start_date">
            <n-date-picker
              v-model:value="formData.start_date"
              type="date"
              placeholder="Выберите дату"
              style="width: 100%"
            />
          </n-form-item>
        </n-grid-item>
        <n-grid-item>
          <n-form-item label="Дата прекращения наблюдения">
            <n-date-picker
              v-model:value="formData.end_date"
              type="date"
              placeholder="Выберите дату"
              style="width: 100%"
            />
          </n-form-item>
        </n-grid-item>
      </n-grid>

      <n-form-item label="Диагноз" path="diagnosis">
        <n-input v-model:value="formData.diagnosis" placeholder="Описание заболевания" />
      </n-form-item>

      <n-form-item label="Код МКБ-10" path="icd_code">
        <n-input v-model:value="formData.icd_code" placeholder="Например: K02.1" />
      </n-form-item>

      <n-form-item label="Врач">
        <n-input v-model:value="formData.doctor" placeholder="ФИО врача" />
      </n-form-item>
    </n-form>

    <template #footer>
      <n-space justify="end">
        <n-button @click="visible = false">Отмена</n-button>
        <n-button type="primary" @click="handleSave" :loading="saving">
          Добавить
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'

const props = defineProps({
  show: Boolean,
  patientId: Number
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const formRef = ref(null)
const saving = ref(false)

const visible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

const formData = ref({
  start_date: null,
  end_date: null,
  diagnosis: '',
  icd_code: '',
  doctor: ''
})

const rules = {
  start_date: { required: true, type: 'number', message: 'Выберите дату начала', trigger: 'change' },
  diagnosis: { required: true, message: 'Введите диагноз', trigger: 'blur' },
  icd_code: { required: true, message: 'Введите код МКБ', trigger: 'blur' }
}

async function handleSave() {
  try {
    await formRef.value?.validate()
    saving.value = true

    emit('saved', { ...formData.value })
    message.success('Заболевание добавлено')
    visible.value = false
    
    // Reset
    formData.value = {
      start_date: null,
      end_date: null,
      diagnosis: '',
      icd_code: '',
      doctor: ''
    }
  } catch (error) {
    console.error('Error:', error)
  } finally {
    saving.value = false
  }
}
</script>

