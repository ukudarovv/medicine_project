<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    title="Добавить социальную сеть"
    style="width: 500px"
    :bordered="false"
    :mask-closable="false"
    @update:show="handleClose"
  >
    <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
      <n-form-item label="Социальная сеть *" path="network">
        <n-select v-model:value="formData.network" :options="networkOptions" placeholder="Выберите сеть" />
      </n-form-item>

      <n-form-item label="Никнейм/ID *" path="username">
        <n-input v-model:value="formData.username" placeholder="@username или ID" />
      </n-form-item>

      <n-form-item label="Ссылка" path="url">
        <n-input v-model:value="formData.url" placeholder="https://..." />
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
import { NModal, NForm, NFormItem, NInput, NSelect, NButton, useMessage } from 'naive-ui'
import { createPatientSocialNetwork, updatePatientSocialNetwork } from '@/api/patients'

const props = defineProps({
  show: Boolean,
  patientId: [Number, String],
  socialNetwork: Object
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const visible = ref(false)
const loading = ref(false)
const formRef = ref(null)

const networkOptions = [
  { label: 'WhatsApp', value: 'whatsapp' },
  { label: 'Telegram', value: 'telegram' },
  { label: 'Instagram', value: 'instagram' },
  { label: 'Facebook', value: 'facebook' },
  { label: 'VKontakte', value: 'vk' },
  { label: 'Другое', value: 'other' }
]

const formData = ref({
  network: '',
  username: '',
  url: ''
})

const rules = {
  network: [{ required: true, message: 'Выберите сеть', trigger: ['blur', 'change'] }],
  username: [{ required: true, message: 'Укажите никнейм', trigger: ['blur', 'input'] }]
}

watch(
  () => props.show,
  (val) => {
    visible.value = val
    if (val) {
      if (props.socialNetwork) {
        formData.value = { ...props.socialNetwork }
      } else {
        formData.value = {
          network: '',
          username: '',
          url: ''
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

    if (props.socialNetwork) {
      await updatePatientSocialNetwork(props.socialNetwork.id, payload)
      message.success('Соц. сеть обновлена')
    } else {
      await createPatientSocialNetwork(payload)
      message.success('Соц. сеть добавлена')
    }

    emit('saved')
    handleClose()
  } catch (error) {
    console.error('Error saving social network:', error)
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

