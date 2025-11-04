<template>
  <n-modal
    v-model:show="visible"
    title="Добавить диагноз"
    preset="card"
    style="width: 800px"
  >
    <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
      <n-form-item label="Дата" path="date">
        <n-date-picker
          v-model:value="formData.date"
          type="date"
          placeholder="Выберите дату"
          style="width: 100%"
        />
      </n-form-item>

      <n-form-item label="Заключительный (уточненный) диагноз" path="diagnosis">
        <n-input
          v-model:value="formData.diagnosis"
          type="textarea"
          :rows="3"
          placeholder="Описание диагноза"
        />
      </n-form-item>

      <n-form-item label="Код МКБ-10" path="icd_code">
        <n-input v-model:value="formData.icd_code" placeholder="Например: K02.1" />
      </n-form-item>

      <n-form-item label="Тип">
        <n-radio-group v-model:value="formData.type">
          <n-radio value="1">Первичный</n-radio>
          <n-radio value="2">Повторный</n-radio>
        </n-radio-group>
      </n-form-item>

      <n-grid :cols="3" :x-gap="12">
        <n-grid-item>
          <n-form-item label="ФИО врача">
            <n-input v-model:value="formData.doctor" placeholder="ФИО" />
          </n-form-item>
        </n-grid-item>
        <n-grid-item>
          <n-form-item label="Должность">
            <n-input v-model:value="formData.position" placeholder="Должность" />
          </n-form-item>
        </n-grid-item>
        <n-grid-item>
          <n-form-item label="Специальность">
            <n-input v-model:value="formData.specialty" placeholder="Специальность" />
          </n-form-item>
        </n-grid-item>
      </n-grid>
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
  date: null,
  diagnosis: '',
  icd_code: '',
  type: '1',
  doctor: '',
  position: '',
  specialty: ''
})

const rules = {
  date: { required: true, type: 'number', message: 'Выберите дату', trigger: 'change' },
  diagnosis: { required: true, message: 'Введите диагноз', trigger: 'blur' },
  icd_code: { required: true, message: 'Введите код МКБ', trigger: 'blur' }
}

async function handleSave() {
  try {
    await formRef.value?.validate()
    saving.value = true

    emit('saved', { ...formData.value })
    message.success('Диагноз добавлен')
    visible.value = false
    
    // Reset
    formData.value = {
      date: null,
      diagnosis: '',
      icd_code: '',
      type: '1',
      doctor: '',
      position: '',
      specialty: ''
    }
  } catch (error) {
    console.error('Error:', error)
  } finally {
    saving.value = false
  }
}
</script>

