<template>
  <n-modal
    v-model:show="visible"
    title="Добавить представителя"
    preset="card"
    style="width: 600px"
  >
    <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
      <n-grid :cols="2" :x-gap="12">
        <n-grid-item>
          <n-form-item label="Фамилия" path="last_name">
            <n-input v-model:value="formData.last_name" placeholder="Фамилия" />
          </n-form-item>
        </n-grid-item>
        <n-grid-item>
          <n-form-item label="Имя" path="first_name">
            <n-input v-model:value="formData.first_name" placeholder="Имя" />
          </n-form-item>
        </n-grid-item>
      </n-grid>

      <n-form-item label="Отчество">
        <n-input v-model:value="formData.middle_name" placeholder="Отчество" />
      </n-form-item>

      <n-form-item label="Степень родства" path="relation">
        <n-select v-model:value="formData.relation" :options="relationOptions" placeholder="Выберите" />
      </n-form-item>

      <n-form-item label="Телефон" path="phone">
        <n-input v-model:value="formData.phone" placeholder="+7 (XXX) XXX-XX-XX" />
      </n-form-item>

      <n-form-item label="Email">
        <n-input v-model:value="formData.email" placeholder="email@example.com" />
      </n-form-item>

      <n-form-item label="Документы (JSON)">
        <n-input
          v-model:value="formData.documents_json"
          type="textarea"
          :rows="3"
          placeholder='{"passport": "N12345678"}'
        />
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
  first_name: '',
  last_name: '',
  middle_name: '',
  relation: '',
  phone: '',
  email: '',
  documents_json: ''
})

const rules = {
  first_name: { required: true, message: 'Введите имя', trigger: 'blur' },
  last_name: { required: true, message: 'Введите фамилию', trigger: 'blur' },
  relation: { required: true, message: 'Выберите степень родства', trigger: 'change' },
  phone: { required: true, message: 'Введите телефон', trigger: 'blur' }
}

const relationOptions = [
  { label: 'Родитель', value: 'parent' },
  { label: 'Опекун', value: 'guardian' },
  { label: 'Супруг(а)', value: 'spouse' },
  { label: 'Ребенок', value: 'child' },
  { label: 'Другое', value: 'other' }
]

async function handleSave() {
  try {
    await formRef.value?.validate()
    saving.value = true

    const data = {
      patient: props.patientId,
      first_name: formData.value.first_name,
      last_name: formData.value.last_name,
      middle_name: formData.value.middle_name,
      relation: formData.value.relation,
      phone: formData.value.phone,
      email: formData.value.email,
      documents: formData.value.documents_json ? JSON.parse(formData.value.documents_json) : {}
    }

    emit('saved', data)
    message.success('Представитель добавлен')
    visible.value = false
    
    // Reset form
    formData.value = {
      first_name: '',
      last_name: '',
      middle_name: '',
      relation: '',
      phone: '',
      email: '',
      documents_json: ''
    }
  } catch (error) {
    console.error('Error:', error)
    if (!error.message?.includes('validate')) {
      message.error('Ошибка добавления представителя')
    }
  } finally {
    saving.value = false
  }
}
</script>

