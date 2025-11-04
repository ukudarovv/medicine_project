<template>
  <n-modal
    v-model:show="visible"
    title="Добавить телефон"
    preset="card"
    style="width: 500px"
  >
    <n-form ref="formRef" :model="formData" :rules="rules">
      <n-form-item label="Номер телефона" path="phone">
        <n-input v-model:value="formData.phone" placeholder="+7 (XXX) XXX-XX-XX" />
      </n-form-item>

      <n-form-item label="Тип">
        <n-select v-model:value="formData.type" :options="phoneTypeOptions" />
      </n-form-item>

      <n-form-item label="Примечание">
        <n-input v-model:value="formData.note" placeholder="Например: рабочий, домашний" />
      </n-form-item>

      <n-form-item>
        <n-checkbox v-model:checked="formData.is_primary">
          Основной номер
        </n-checkbox>
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
  show: Boolean
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
  phone: '',
  type: 'mobile',
  note: '',
  is_primary: false
})

const rules = {
  phone: { required: true, message: 'Введите номер телефона', trigger: 'blur' }
}

const phoneTypeOptions = [
  { label: 'Мобильный', value: 'mobile' },
  { label: 'Домашний', value: 'home' },
  { label: 'Рабочий', value: 'work' },
  { label: 'Другой', value: 'other' }
]

async function handleSave() {
  try {
    await formRef.value?.validate()
    saving.value = true

    emit('saved', { ...formData.value })
    message.success('Телефон добавлен')
    visible.value = false
    
    // Reset form
    formData.value = {
      phone: '',
      type: 'mobile',
      note: '',
      is_primary: false
    }
  } catch (error) {
    console.error('Error:', error)
  } finally {
    saving.value = false
  }
}
</script>

