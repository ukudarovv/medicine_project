<template>
  <n-modal
    v-model:show="visible"
    :title="isEdit ? 'Редактировать должность' : 'Новая должность'"
    preset="card"
    style="width: 600px"
  >
    <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
      <n-form-item label="Название должности" path="name">
        <n-input v-model:value="formData.name" placeholder="Например: Врач-стоматолог" />
      </n-form-item>

      <n-form-item label="Комментарий">
        <n-input
          v-model:value="formData.comment"
          type="textarea"
          placeholder="Дополнительная информация о должности"
          :rows="3"
        />
      </n-form-item>

      <n-form-item>
        <n-checkbox v-model:checked="formData.hidden_in_schedule_filter">
          Скрыть из фильтра в расписании
        </n-checkbox>
      </n-form-item>
    </n-form>

    <template #footer>
      <n-space justify="end">
        <n-button @click="handleClose">Отмена</n-button>
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
import apiClient from '@/api/axios'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  position: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const authStore = useAuthStore()
const formRef = ref(null)
const saving = ref(false)

const isEdit = computed(() => !!props.position)

const visible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

const formData = ref({
  name: '',
  comment: '',
  hidden_in_schedule_filter: false
})

const rules = {
  name: { required: true, message: 'Введите название должности', trigger: 'blur' }
}

watch(
  () => props.position,
  (newVal) => {
    if (newVal) {
      formData.value = {
        name: newVal.name || '',
        comment: newVal.comment || '',
        hidden_in_schedule_filter: newVal.hidden_in_schedule_filter || false
      }
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

function resetForm() {
  formData.value = {
    name: '',
    comment: '',
    hidden_in_schedule_filter: false
  }
}

function handleClose() {
  visible.value = false
  resetForm()
}

async function handleSave() {
  try {
    await formRef.value?.validate()
    saving.value = true

    const data = {
      organization: authStore.user?.organization,
      ...formData.value
    }

    if (isEdit.value) {
      await apiClient.patch(`/staff/positions/${props.position.id}`, data)
      message.success('Должность обновлена')
    } else {
      await apiClient.post('/staff/positions', data)
      message.success('Должность создана')
    }

    emit('saved')
    handleClose()
  } catch (error) {
    console.error('Error saving position:', error)
    message.error('Ошибка сохранения должности')
  } finally {
    saving.value = false
  }
}
</script>

