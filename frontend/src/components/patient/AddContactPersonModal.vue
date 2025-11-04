<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    title="Добавить контактное лицо"
    style="width: 600px"
    :bordered="false"
    :mask-closable="false"
    @update:show="handleClose"
  >
    <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
      <n-grid :cols="2" :x-gap="12">
        <n-gi>
          <n-form-item label="Фамилия *" path="last_name">
            <n-input v-model:value="formData.last_name" placeholder="Иванов" />
          </n-form-item>
        </n-gi>
        <n-gi>
          <n-form-item label="Имя *" path="first_name">
            <n-input v-model:value="formData.first_name" placeholder="Иван" />
          </n-form-item>
        </n-gi>
      </n-grid>

      <n-form-item label="Степень родства *" path="relation">
        <n-input v-model:value="formData.relation" placeholder="Сын, дочь, супруг, брат..." />
      </n-form-item>

      <n-form-item label="Телефон *" path="phone">
        <n-input v-model:value="formData.phone" placeholder="+7 (___) ___-__-__" />
      </n-form-item>

      <n-form-item label="Email" path="email">
        <n-input v-model:value="formData.email" placeholder="email@example.com" />
      </n-form-item>

      <n-form-item label="Примечание" path="note">
        <n-input
          v-model:value="formData.note"
          placeholder="Доп. информация"
          type="textarea"
          :rows="3"
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
import { ref, watch } from 'vue'
import {
  NModal,
  NForm,
  NFormItem,
  NInput,
  NButton,
  NGrid,
  NGi,
  useMessage
} from 'naive-ui'
import { createPatientContactPerson, updatePatientContactPerson } from '@/api/patients'

const props = defineProps({
  show: Boolean,
  patientId: [Number, String],
  contactPerson: Object
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const visible = ref(false)
const loading = ref(false)
const formRef = ref(null)

const formData = ref({
  first_name: '',
  last_name: '',
  relation: '',
  phone: '',
  email: '',
  note: ''
})

const rules = {
  first_name: [{ required: true, message: 'Укажите имя', trigger: ['blur', 'input'] }],
  last_name: [{ required: true, message: 'Укажите фамилию', trigger: ['blur', 'input'] }],
  relation: [{ required: true, message: 'Укажите степень родства', trigger: ['blur', 'input'] }],
  phone: [{ required: true, message: 'Укажите телефон', trigger: ['blur', 'input'] }]
}

watch(
  () => props.show,
  (val) => {
    visible.value = val
    if (val) {
      if (props.contactPerson) {
        formData.value = { ...props.contactPerson }
      } else {
        formData.value = {
          first_name: '',
          last_name: '',
          relation: '',
          phone: '',
          email: '',
          note: ''
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

    if (props.contactPerson) {
      await updatePatientContactPerson(props.contactPerson.id, payload)
      message.success('Контактное лицо обновлено')
    } else {
      await createPatientContactPerson(payload)
      message.success('Контактное лицо добавлено')
    }

    emit('saved')
    handleClose()
  } catch (error) {
    console.error('Error saving contact person:', error)
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

