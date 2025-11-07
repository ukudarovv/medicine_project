<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    title="Добавить перерыв"
    style="width: 600px"
  >
    <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
      <n-form-item label="Сотрудник" path="employee">
        <n-select
          v-model:value="formData.employee"
          :options="employeeOptions"
          placeholder="Выберите сотрудника"
          :disabled="!!employee"
        />
      </n-form-item>

      <n-form-item label="Тип перерыва">
        <n-radio-group v-model:value="formData.type">
          <n-radio value="lunch">Обед</n-radio>
          <n-radio value="break">Перерыв</n-radio>
          <n-radio value="meeting">Совещание</n-radio>
          <n-radio value="other">Другое</n-radio>
        </n-radio-group>
      </n-form-item>

      <n-grid :cols="2" :x-gap="12">
        <n-grid-item>
          <n-form-item label="Начало" path="start_time">
            <n-time-picker
              v-model:value="formData.start_time"
              format="HH:mm"
              placeholder="Выберите время"
              style="width: 100%"
            />
          </n-form-item>
        </n-grid-item>
        <n-grid-item>
          <n-form-item label="Окончание" path="end_time">
            <n-time-picker
              v-model:value="formData.end_time"
              format="HH:mm"
              placeholder="Выберите время"
              style="width: 100%"
            />
          </n-form-item>
        </n-grid-item>
      </n-grid>

      <n-form-item label="Дата">
        <n-date-picker
          v-model:value="formData.date"
          type="date"
          placeholder="Выберите дату"
          style="width: 100%"
        />
      </n-form-item>

      <n-form-item label="Примечание">
        <n-input
          v-model:value="formData.note"
          type="textarea"
          :rows="3"
          placeholder="Комментарий к перерыву"
        />
      </n-form-item>

      <n-form-item>
        <n-checkbox v-model:checked="formData.recurring">
          Повторяющийся перерыв (каждый день)
        </n-checkbox>
      </n-form-item>
    </n-form>

    <template #footer>
      <n-space justify="end">
        <n-button @click="visible = false">Отмена</n-button>
        <n-button type="primary" @click="handleSave" :loading="saving">
          Сохранить
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { createBreak } from '@/api/calendar'

const props = defineProps({
  show: Boolean,
  employee: {
    type: Object,
    default: null
  },
  employees: {
    type: Array,
    default: () => []
  },
  defaultDate: {
    type: Number,
    default: () => Date.now()
  }
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
  employee: props.employee?.id || null,
  type: 'break',
  start_time: null,
  end_time: null,
  date: Date.now(),
  note: '',
  recurring: false
})

// Watch for employee changes
watch(() => props.employee, (newEmployee) => {
  if (newEmployee) {
    formData.value.employee = newEmployee.id
  }
}, { immediate: true })

// Watch for date changes
watch(() => props.defaultDate, (newDate) => {
  if (newDate) {
    formData.value.date = newDate
  }
}, { immediate: true })

const rules = {
  employee: { required: true, type: 'number', message: 'Выберите сотрудника', trigger: 'change' },
  start_time: { required: true, type: 'number', message: 'Выберите время начала', trigger: 'change' },
  end_time: { required: true, type: 'number', message: 'Выберите время окончания', trigger: 'change' }
}

const employeeOptions = computed(() =>
  props.employees.map((e) => ({
    label: `${e.last_name} ${e.first_name}${e.position ? ' - ' + e.position : ''}`,
    value: e.id
  }))
)

function formatTimeForAPI(timestamp) {
  if (!timestamp) return null
  const date = new Date(timestamp)
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:00`
}

async function handleSave() {
  try {
    await formRef.value?.validate()
    saving.value = true

    const breakData = {
      employee: formData.value.employee,
      break_type: formData.value.type,
      start_time: formatTimeForAPI(formData.value.start_time),
      end_time: formatTimeForAPI(formData.value.end_time),
      date: new Date(formData.value.date).toISOString().split('T')[0],
      note: formData.value.note,
      is_recurring: formData.value.recurring
    }

    await createBreak(breakData)
    message.success('Перерыв добавлен')
    emit('saved', breakData)
    visible.value = false
    
    // Reset form
    formData.value = {
      employee: props.employee?.id || null,
      type: 'break',
      start_time: null,
      end_time: null,
      date: props.defaultDate || Date.now(),
      note: '',
      recurring: false
    }
  } catch (error) {
    console.error('Error saving break:', error)
    message.error(error.response?.data?.detail || 'Ошибка при сохранении перерыва')
  } finally {
    saving.value = false
  }
}
</script>

