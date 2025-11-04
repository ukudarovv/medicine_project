<template>
  <n-modal
    v-model:show="visible"
    :title="isEdit ? 'Редактировать задачу' : 'Новая задача'"
    preset="card"
    style="width: 800px"
  >
    <n-scrollbar style="max-height: 70vh">
      <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
        <n-form-item label="Название задачи" path="title">
          <n-input v-model:value="formData.title" placeholder="Краткое описание задачи" />
        </n-form-item>

        <n-form-item label="Описание">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            placeholder="Подробное описание задачи"
            :rows="4"
          />
        </n-form-item>

        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item label="Исполнитель" path="assignee">
              <n-select
                v-model:value="formData.assignee"
                :options="employeeOptions"
                placeholder="Выберите сотрудника"
                filterable
                :loading="loadingEmployees"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Статус" path="status">
              <n-select
                v-model:value="formData.status"
                :options="statusOptions"
                placeholder="Выберите статус"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item label="Дата дедлайна" path="deadline_date">
              <n-date-picker
                v-model:value="formData.deadline_date"
                type="date"
                placeholder="Выберите дату"
                style="width: 100%"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Время дедлайна" path="deadline_time">
              <n-time-picker
                v-model:value="formData.deadline_time"
                format="HH:mm"
                placeholder="Выберите время"
                style="width: 100%"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-form-item label="Результат">
          <n-select
            v-model:value="formData.result"
            :options="resultOptions"
            placeholder="Выберите результат (опционально)"
            clearable
            filterable
            :loading="loadingResults"
          />
        </n-form-item>

        <n-divider title-placement="left" v-if="isEdit">Комментарии</n-divider>
        
        <n-space vertical v-if="isEdit && comments.length > 0">
          <n-card v-for="comment in comments" :key="comment.id" size="small">
            <template #header>
              <n-space align="center">
                <n-text strong>{{ comment.author_name }}</n-text>
                <n-text depth="3" style="font-size: 12px">
                  {{ formatDate(comment.created_at) }}
                </n-text>
              </n-space>
            </template>
            <n-text>{{ comment.comment }}</n-text>
          </n-card>
        </n-space>

        <n-form-item label="Добавить комментарий" v-if="isEdit">
          <n-input
            v-model:value="newComment"
            type="textarea"
            placeholder="Введите комментарий..."
            :rows="2"
          />
          <n-button type="primary" size="small" @click="addComment" :loading="addingComment" style="margin-top: 8px">
            Добавить комментарий
          </n-button>
        </n-form-item>

        <n-divider title-placement="left" v-if="isEdit">Вложения</n-divider>

        <n-form-item v-if="isEdit">
          <n-upload
            :action="`${apiBase}/staff/tasks/${props.task?.id}/upload_attachment`"
            :headers="uploadHeaders"
            @finish="handleUploadFinish"
          >
            <n-button>📎 Прикрепить файл</n-button>
          </n-upload>
        </n-form-item>

        <n-list v-if="isEdit && attachments.length > 0">
          <n-list-item v-for="attachment in attachments" :key="attachment.id">
            <n-space align="center">
              <n-text>📄 {{ attachment.filename }}</n-text>
              <n-text depth="3" style="font-size: 12px">
                ({{ attachment.uploaded_by_name }}, {{ formatDate(attachment.created_at) }})
              </n-text>
              <n-button text tag="a" :href="attachment.file_url" target="_blank">
                Скачать
              </n-button>
            </n-space>
          </n-list-item>
        </n-list>
      </n-form>
    </n-scrollbar>

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
import { ref, computed, watch, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import apiClient from '@/api/axios'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  task: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const authStore = useAuthStore()
const formRef = ref(null)
const saving = ref(false)
const loadingEmployees = ref(false)
const loadingResults = ref(false)
const addingComment = ref(false)

const employeeOptions = ref([])
const resultOptions = ref([])
const comments = ref([])
const attachments = ref([])
const newComment = ref('')

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.token}`
}))

const isEdit = computed(() => !!props.task)

const visible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

const formData = ref({
  title: '',
  description: '',
  assignee: null,
  status: 'new',
  deadline_date: null,
  deadline_time: null,
  result: null
})

const rules = {
  title: { required: true, message: 'Введите название задачи', trigger: 'blur' },
  assignee: { required: true, type: 'number', message: 'Выберите исполнителя', trigger: 'change' },
  deadline_date: { required: true, type: 'number', message: 'Выберите дату дедлайна', trigger: 'change' }
}

const statusOptions = [
  { label: 'Новая', value: 'new' },
  { label: 'В процессе', value: 'in_progress' },
  { label: 'Выполнена', value: 'done' },
  { label: 'Отменена', value: 'cancelled' }
]

watch(
  () => props.task,
  (newVal) => {
    if (newVal) {
      const deadlineDate = new Date(newVal.deadline_at)
      formData.value = {
        title: newVal.title || '',
        description: newVal.description || '',
        assignee: newVal.assignee || null,
        status: newVal.status || 'new',
        deadline_date: deadlineDate.getTime(),
        deadline_time: deadlineDate.getTime(),
        result: newVal.result || null
      }
      comments.value = newVal.comments || []
      attachments.value = newVal.attachments || []
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

watch(visible, (newVal) => {
  if (newVal) {
    loadEmployees()
    loadResults()
  }
})

function resetForm() {
  formData.value = {
    title: '',
    description: '',
    assignee: null,
    status: 'new',
    deadline_date: null,
    deadline_time: null,
    result: null
  }
  comments.value = []
  attachments.value = []
  newComment.value = ''
}

function handleClose() {
  visible.value = false
  resetForm()
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU')
}

async function loadEmployees() {
  try {
    loadingEmployees.value = true
    const response = await apiClient.get('/staff/employees')
    employeeOptions.value = (response.data.results || response.data).map(emp => ({
      label: emp.full_name,
      value: emp.id
    }))
  } catch (error) {
    console.error('Error loading employees:', error)
  } finally {
    loadingEmployees.value = false
  }
}

async function loadResults() {
  try {
    loadingResults.value = true
    const response = await apiClient.get('/staff/results')
    resultOptions.value = (response.data.results || response.data).map(result => ({
      label: result.name,
      value: result.id
    }))
  } catch (error) {
    console.error('Error loading results:', error)
  } finally {
    loadingResults.value = false
  }
}

async function addComment() {
  if (!newComment.value.trim()) {
    message.warning('Введите текст комментария')
    return
  }

  try {
    addingComment.value = true
    const response = await apiClient.post(`/staff/tasks/${props.task.id}/add_comment`, {
      comment: newComment.value
    })
    comments.value.push(response.data)
    newComment.value = ''
    message.success('Комментарий добавлен')
  } catch (error) {
    console.error('Error adding comment:', error)
    message.error('Ошибка добавления комментария')
  } finally {
    addingComment.value = false
  }
}

function handleUploadFinish({ event }) {
  const response = JSON.parse(event.target.response)
  attachments.value.push(response)
  message.success('Файл загружен')
}

async function handleSave() {
  try {
    await formRef.value?.validate()
    saving.value = true

    const deadlineDate = new Date(formData.value.deadline_date)
    const deadlineTime = new Date(formData.value.deadline_time || formData.value.deadline_date)
    
    deadlineDate.setHours(deadlineTime.getHours())
    deadlineDate.setMinutes(deadlineTime.getMinutes())

    const data = {
      organization: authStore.user?.organization,
      title: formData.value.title,
      description: formData.value.description,
      assignee: formData.value.assignee,
      status: formData.value.status,
      deadline_at: deadlineDate.toISOString(),
      result: formData.value.result
    }

    if (isEdit.value) {
      await apiClient.patch(`/staff/tasks/${props.task.id}`, data)
      message.success('Задача обновлена')
    } else {
      await apiClient.post('/staff/tasks', data)
      message.success('Задача создана')
    }

    emit('saved')
    handleClose()
  } catch (error) {
    console.error('Error saving task:', error)
    message.error('Ошибка сохранения задачи')
  } finally {
    saving.value = false
  }
}
</script>

