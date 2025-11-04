<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    title="Добавить телефон"
    style="width: 500px"
    :bordered="false"
    :mask-closable="false"
    @update:show="handleClose"
  >
    <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
      <n-form-item label="Телефон *" path="phone">
        <n-input v-model:value="formData.phone" placeholder="+7 (___) ___-__-__" />
      </n-form-item>

      <n-form-item label="Тип телефона *" path="type">
        <n-select v-model:value="formData.type" :options="typeOptions" placeholder="Выберите тип" />
      </n-form-item>

      <n-form-item label="Примечание" path="note">
        <n-input
          v-model:value="formData.note"
          placeholder="Доп. информация"
          type="textarea"
          :rows="2"
        />
      </n-form-item>

      <n-form-item label="Основной" path="is_primary">
        <n-checkbox v-model:checked="formData.is_primary">Использовать как основной телефон</n-checkbox>
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
import { ref, watch } from 'vue'
import { NModal, NForm, NFormItem, NInput, NSelect, NCheckbox, NButton, useMessage } from 'naive-ui'
import { createPatientPhone, updatePatientPhone } from '@/api/patients'

const props = defineProps({
  show: Boolean,
  patientId: [Number, String],
  phone: Object
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const visible = ref(false)
const loading = ref(false)
const formRef = ref(null)

const typeOptions = [
  { label: 'Мобильный', value: 'mobile' },
  { label: 'Домашний', value: 'home' },
  { label: 'Рабочий', value: 'work' },
  { label: 'Другой', value: 'other' }
]

const formData = ref({
  phone: '',
  type: 'mobile',
  note: '',
  is_primary: false
})

const rules = {
  phone: [{ required: true, message: 'Укажите телефон', trigger: ['blur', 'input'] }],
  type: [{ required: true, message: 'Выберите тип', trigger: ['blur', 'change'] }]
}

watch(
  () => props.show,
  (val) => {
    visible.value = val
    if (val) {
      if (props.phone) {
        formData.value = { ...props.phone }
      } else {
        formData.value = {
          phone: '',
          type: 'mobile',
          note: '',
          is_primary: false
        }
      }
    }
  }
)

const handleClose = () => {
  emit('update:show', false)
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true

    const payload = {
      ...formData.value,
      patient: props.patientId
    }

    if (props.phone) {
      await updatePatientPhone(props.phone.id, payload)
      message.success('Телефон обновлен')
    } else {
      await createPatientPhone(payload)
      message.success('Телефон добавлен')
    }

    emit('saved')
    handleClose()
  } catch (error) {
    console.error('Error saving phone:', error)
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

