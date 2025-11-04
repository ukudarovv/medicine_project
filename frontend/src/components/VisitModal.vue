<template>
  <n-modal
    v-model:show="visible"
    :title="`Визит #${visitData?.id || ''} ${isEditMode ? '(Редактирование)' : ''}`"
    preset="card"
    style="width: 1200px"
    :segmented="{ content: 'soft' }"
  >
    <!-- Модал добавления услуги -->
    <AddServiceModal
      v-model:show="showAddServiceModal"
      :visit-id="props.visitId"
      @saved="handleServiceAdded"
    />

    <n-spin :show="loading">
      <n-scrollbar style="max-height: 75vh">
        <n-form ref="formRef" :model="formData" :disabled="!isEditMode">
          <n-tabs v-model:value="activeTab" type="line" animated>
            <!-- Основная информация -->
            <n-tab-pane name="general" tab="Основная информация">
              <n-space vertical :size="16">
                <!-- Информация о визите -->
                <n-card title="Информация о визите" :bordered="false">
                  <template v-if="!isEditMode">
                    <n-descriptions :column="2" label-placement="left">
                      <n-descriptions-item label="№ визита">
                        {{ visitData?.id }}
                      </n-descriptions-item>
                      <n-descriptions-item label="Дата и время">
                        {{ formatDateTime(visitData?.start_datetime) }}
                      </n-descriptions-item>
                      <n-descriptions-item label="Пациент">
                        {{ visitData?.patient_name }}
                      </n-descriptions-item>
                      <n-descriptions-item label="Сотрудник">
                        {{ visitData?.employee_name }}
                      </n-descriptions-item>
                      <n-descriptions-item label="Филиал">
                        {{ visitData?.branch_name }}
                      </n-descriptions-item>
                      <n-descriptions-item label="Статус">
                        <n-tag :type="getStatusType(visitData?.status)">
                          {{ getStatusLabel(visitData?.status) }}
                        </n-tag>
                      </n-descriptions-item>
                      <n-descriptions-item label="Пациент пришел" :span="2">
                        <n-tag :type="visitData?.is_patient_arrived ? 'success' : 'warning'">
                          {{ visitData?.is_patient_arrived ? `Да (${formatDateTime(visitData?.arrived_at)})` : 'Нет' }}
                        </n-tag>
                      </n-descriptions-item>
                    </n-descriptions>
                  </template>
                  <template v-else>
                    <n-form-item label="Статус визита">
                      <n-select
                        v-model:value="formData.status"
                        :options="statusOptions"
                        placeholder="Выберите статус"
                      />
                    </n-form-item>
                    <n-form-item label="Пациент пришел">
                      <n-switch v-model:value="formData.is_patient_arrived">
                        <template #checked>Да</template>
                        <template #unchecked>Нет</template>
                      </n-switch>
                    </n-form-item>
                  </template>
                </n-card>

                <!-- Диагноз и лечение -->
                <n-card title="Диагноз и план лечения" :bordered="false">
                  <n-space vertical :size="12">
                    <n-form-item label="Диагноз">
                      <n-input
                        v-if="isEditMode"
                        v-model:value="formData.diagnosis"
                        type="textarea"
                        :rows="3"
                        placeholder="Введите диагноз"
                      />
                      <div v-else>{{ visitData?.diagnosis || 'Не указан' }}</div>
                    </n-form-item>
                    <n-form-item label="План лечения">
                      <n-input
                        v-if="isEditMode"
                        v-model:value="formData.treatment_plan"
                        type="textarea"
                        :rows="3"
                        placeholder="Введите план лечения"
                      />
                      <div v-else>{{ visitData?.treatment_plan || 'Не указан' }}</div>
                    </n-form-item>
                    <n-form-item label="Комментарий">
                      <n-input
                        v-if="isEditMode"
                        v-model:value="formData.comment"
                        type="textarea"
                        :rows="2"
                        placeholder="Добавьте комментарий"
                      />
                      <div v-else>{{ visitData?.comment || 'Нет комментариев' }}</div>
                    </n-form-item>
                  </n-space>
                </n-card>

                <!-- Дневник (если есть структурированные данные) -->
                <n-card v-if="visitData?.diary_structured" title="Структурированный дневник" :bordered="false">
                  <n-form-item v-if="isEditMode">
                    <n-input
                      v-model:value="diaryStructuredJson"
                      type="textarea"
                      :rows="8"
                      placeholder="JSON структура дневника"
                    />
                  </n-form-item>
                  <pre v-else style="white-space: pre-wrap; color: #e0e0e0;">{{ JSON.stringify(visitData.diary_structured, null, 2) }}</pre>
                </n-card>
              </n-space>
            </n-tab-pane>

            <!-- Услуги -->
            <n-tab-pane name="services" tab="Услуги">
              <n-card :bordered="false">
                <template #header>
                  <n-space justify="space-between" align="center">
                    <span>Услуги</span>
                    <n-button v-if="isEditMode" type="primary" size="small" @click="addService">
                      + Добавить услугу
                    </n-button>
                  </n-space>
                </template>
                <n-data-table
                  :columns="isEditMode ? servicesColumnsEdit : servicesColumns"
                  :data="isEditMode ? formData.services_list : visitData?.services_list || []"
                  :pagination="false"
                  size="small"
                />
                <n-divider />
                <n-space justify="end">
                  <n-text strong style="font-size: 16px">
                    Итого: {{ totalAmount }} ₸
                  </n-text>
                </n-space>
              </n-card>
            </n-tab-pane>

            <!-- Назначения -->
            <n-tab-pane name="prescriptions" tab="Назначения">
              <n-card :bordered="false">
                <template #header>
                  <n-space justify="space-between" align="center">
                    <span>Назначения</span>
                    <n-button v-if="isEditMode" type="primary" size="small" @click="addPrescription">
                      + Добавить назначение
                    </n-button>
                  </n-space>
                </template>
                <n-empty v-if="!prescriptionsList.length" description="Нет назначений" />
                <n-list v-else bordered>
                  <n-list-item v-for="(prescription, index) in prescriptionsList" :key="prescription.id || index">
                    <template v-if="!isEditMode">
                      <n-thing :title="prescription.medication">
                        <template #description>
                          <n-space vertical :size="4">
                            <div><n-text depth="3">Дозировка:</n-text> {{ prescription.dosage }}</div>
                            <div><n-text depth="3">Частота:</n-text> {{ prescription.frequency }}</div>
                            <div><n-text depth="3">Длительность:</n-text> {{ prescription.duration_days }} дней</div>
                            <div v-if="prescription.instructions"><n-text depth="3">Инструкции:</n-text> {{ prescription.instructions }}</div>
                          </n-space>
                        </template>
                      </n-thing>
                    </template>
                    <template v-else>
                      <n-space vertical style="width: 100%">
                        <n-input v-model:value="prescription.medication" placeholder="Название препарата" />
                        <n-grid :cols="3" :x-gap="12">
                          <n-grid-item>
                            <n-input v-model:value="prescription.dosage" placeholder="Дозировка" />
                          </n-grid-item>
                          <n-grid-item>
                            <n-input v-model:value="prescription.frequency" placeholder="Частота приема" />
                          </n-grid-item>
                          <n-grid-item>
                            <n-input-number v-model:value="prescription.duration_days" placeholder="Длительность (дней)" style="width: 100%" />
                          </n-grid-item>
                        </n-grid>
                        <n-input v-model:value="prescription.instructions" placeholder="Инструкции" type="textarea" :rows="2" />
                        <n-button type="error" size="small" @click="removePrescription(index)">
                          Удалить
                        </n-button>
                      </n-space>
                    </template>
                  </n-list-item>
                </n-list>
              </n-card>
            </n-tab-pane>

            <!-- Ресурсы -->
            <n-tab-pane name="resources" tab="Использованные ресурсы">
              <n-card :bordered="false">
                <n-empty v-if="!visitData?.resources?.length" description="Нет использованных ресурсов" />
                <n-data-table
                  v-else
                  :columns="resourcesColumns"
                  :data="visitData.resources"
                  :pagination="false"
                  size="small"
                />
              </n-card>
            </n-tab-pane>

            <!-- Файлы -->
            <n-tab-pane name="files" tab="Файлы">
              <n-card :bordered="false">
                <template #header>
                  <n-space justify="space-between" align="center">
                    <span>Файлы</span>
                    <n-upload
                      v-if="isEditMode"
                      :action="`/api/v1/visits/visits/${visitData?.id}/upload_file`"
                      :data="{ file_type: 'document' }"
                      :show-file-list="false"
                      @finish="handleFileUpload"
                      @error="handleFileError"
                    >
                      <n-button type="primary" size="small">
                        📎 Загрузить файл
                      </n-button>
                    </n-upload>
                  </n-space>
                </template>
                <n-empty v-if="!filesList.length" description="Нет прикрепленных файлов" />
                <n-list v-else bordered>
                  <n-list-item v-for="file in filesList" :key="file.id">
                    <n-thing :title="file.title || 'Без названия'">
                      <template #description>
                        <n-space vertical :size="4">
                          <div><n-text depth="3">Тип:</n-text> {{ file.file_type_display }}</div>
                          <div v-if="file.description"><n-text depth="3">Описание:</n-text> {{ file.description }}</div>
                          <div><n-text depth="3">Загружено:</n-text> {{ formatDateTime(file.created_at) }} {{ file.uploaded_by_name ? `(${file.uploaded_by_name})` : '' }}</div>
                        </n-space>
                      </template>
                      <template #action>
                        <n-space>
                          <n-button size="small" @click="downloadFile(file)">
                            Скачать
                          </n-button>
                          <n-button v-if="isEditMode" size="small" type="error" @click="deleteFile(file)">
                            Удалить
                          </n-button>
                        </n-space>
                      </template>
                    </n-thing>
                  </n-list-item>
                </n-list>
              </n-card>
            </n-tab-pane>
          </n-tabs>
        </n-form>
      </n-scrollbar>
    </n-spin>

    <template #footer>
      <n-space justify="space-between">
        <n-space>
          <n-button v-if="!isEditMode" type="info" @click="printVisit">
            🖨️ Печать
          </n-button>
          <n-button v-if="!isEditMode" @click="exportVisit">
            📊 Экспорт
          </n-button>
        </n-space>
        <n-space>
          <n-button @click="closeModal">Закрыть</n-button>
          <n-button v-if="!isEditMode" type="primary" @click="toggleEditMode">
            Редактировать
          </n-button>
          <template v-else>
            <n-button @click="cancelEdit">Отмена</n-button>
            <n-button type="primary" @click="saveVisit" :loading="saving">
              Сохранить
            </n-button>
          </template>
        </n-space>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import apiClient from '@/api/axios'
import { format, parseISO } from 'date-fns'
import { ru } from 'date-fns/locale'
import { h } from 'vue'
import { NButton, NInputNumber } from 'naive-ui'
import AddServiceModal from './AddServiceModal.vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  visitId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const dialog = useDialog()
const visible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val)
})

const activeTab = ref('general')
const loading = ref(false)
const saving = ref(false)
const visitData = ref(null)
const isEditMode = ref(false)
const formRef = ref(null)
const showAddServiceModal = ref(false)

// Форма для редактирования
const formData = ref({
  status: '',
  is_patient_arrived: false,
  diagnosis: '',
  treatment_plan: '',
  comment: '',
  services_list: [],
  prescriptions: [],
  diary_structured: {}
})

const diaryStructuredJson = ref('')

// Опции статусов
const statusOptions = [
  { label: 'В процессе', value: 'in_progress' },
  { label: 'Выполнено', value: 'done' },
  { label: 'Отменено', value: 'canceled' },
  { label: 'Не пришёл', value: 'no_show' }
]

// Колонки для таблицы услуг (режим просмотра)
const servicesColumns = [
  {
    title: 'Услуга',
    key: 'service_name',
    ellipsis: { tooltip: true }
  },
  {
    title: 'Кол-во',
    key: 'qty',
    width: 80
  },
  {
    title: 'Длительность',
    key: 'duration',
    width: 120,
    render: (row) => row.duration ? `${row.duration} мин` : '-'
  },
  {
    title: 'Цена',
    key: 'price',
    width: 100,
    render: (row) => `${row.price} ₸`
  },
  {
    title: 'Скидка',
    key: 'discount_percent',
    width: 100,
    render: (row) => row.discount_percent ? `${row.discount_percent}%` : '-'
  },
  {
    title: 'Зуб №',
    key: 'tooth_number',
    width: 80
  },
  {
    title: 'Итого',
    key: 'total_price',
    width: 100,
    render: (row) => `${row.total_price} ₸`
  }
]

// Колонки для таблицы услуг (режим редактирования)
const servicesColumnsEdit = [
  ...servicesColumns,
  {
    title: 'Действия',
    key: 'actions',
    width: 100,
    render: (row, index) => {
      return h(NButton, {
        size: 'small',
        type: 'error',
        onClick: () => removeService(index)
      }, { default: () => 'Удалить' })
    }
  }
]

// Колонки для таблицы ресурсов
const resourcesColumns = [
  {
    title: 'Ресурс',
    key: 'resource_name',
    ellipsis: { tooltip: true }
  },
  {
    title: 'Время использования',
    key: 'used_time',
    width: 180,
    render: (row) => formatDateTime(row.used_time)
  }
]

// Вычисляемые свойства
const prescriptionsList = computed(() => {
  return isEditMode.value ? formData.value.prescriptions : (visitData.value?.prescriptions || [])
})

const filesList = computed(() => {
  return visitData.value?.files || []
})

const totalAmount = computed(() => {
  const services = isEditMode.value ? formData.value.services_list : (visitData.value?.services_list || [])
  const total = services.reduce((sum, service) => sum + (parseFloat(service.total_price) || 0), 0)
  return total.toFixed(2)
})

// Загрузка данных визита
async function loadVisit() {
  if (!props.visitId) return
  
  loading.value = true
  try {
    const response = await apiClient.get(`/visits/visits/${props.visitId}`)
    visitData.value = response.data
  } catch (error) {
    console.error('Error loading visit:', error)
    message.error('Ошибка загрузки данных визита')
  } finally {
    loading.value = false
  }
}

// Переключение режима редактирования
function toggleEditMode() {
  isEditMode.value = true
  // Копируем данные в форму
  formData.value = {
    status: visitData.value.status,
    is_patient_arrived: visitData.value.is_patient_arrived,
    diagnosis: visitData.value.diagnosis || '',
    treatment_plan: visitData.value.treatment_plan || '',
    comment: visitData.value.comment || '',
    services_list: JSON.parse(JSON.stringify(visitData.value.services_list || [])),
    prescriptions: JSON.parse(JSON.stringify(visitData.value.prescriptions || [])),
    diary_structured: visitData.value.diary_structured || {}
  }
  diaryStructuredJson.value = JSON.stringify(visitData.value.diary_structured || {}, null, 2)
}

// Отмена редактирования
function cancelEdit() {
  dialog.warning({
    title: 'Отменить изменения?',
    content: 'Все несохраненные изменения будут потеряны',
    positiveText: 'Да, отменить',
    negativeText: 'Нет',
    onPositiveClick: () => {
      isEditMode.value = false
    }
  })
}

// Сохранение визита
async function saveVisit() {
  saving.value = true
  try {
    // Парсим JSON дневника если он был изменен
    if (diaryStructuredJson.value) {
      try {
        formData.value.diary_structured = JSON.parse(diaryStructuredJson.value)
      } catch (e) {
        message.error('Ошибка в JSON структуре дневника')
        saving.value = false
        return
      }
    }

    // Отправляем только измененные поля
    const updateData = {
      status: formData.value.status,
      is_patient_arrived: formData.value.is_patient_arrived,
      diagnosis: formData.value.diagnosis,
      treatment_plan: formData.value.treatment_plan,
      comment: formData.value.comment,
      diary_structured: formData.value.diary_structured
    }

    // Сохраняем основные данные визита
    await apiClient.patch(`/visits/visits/${props.visitId}`, updateData)
    
    // Сохраняем назначения если они были изменены
    if (formData.value.prescriptions && formData.value.prescriptions.length > 0) {
      await apiClient.post(`/visits/visits/${props.visitId}/update_prescriptions`, {
        prescriptions: formData.value.prescriptions
      })
    }
    
    message.success('Визит успешно обновлен')
    isEditMode.value = false
    await loadVisit()
    emit('saved')
  } catch (error) {
    console.error('Error saving visit:', error)
    message.error('Ошибка при сохранении визита')
  } finally {
    saving.value = false
  }
}

// Добавить услугу
function addService() {
  showAddServiceModal.value = true
}

// Обработка добавления услуги
async function handleServiceAdded() {
  await loadVisit()
  message.success('Услуга успешно добавлена')
}

// Удалить услугу
async function removeService(index) {
  const service = formData.value.services_list[index]
  if (service.id) {
    // Если услуга уже сохранена на сервере - удаляем через API
    try {
      await apiClient.delete(`/visits/visit-services/${service.id}`)
      message.success('Услуга удалена')
      await loadVisit()
    } catch (error) {
      message.error('Ошибка при удалении услуги')
    }
  } else {
    // Если услуга только добавлена локально - просто убираем из массива
    formData.value.services_list.splice(index, 1)
  }
}

// Добавить назначение
function addPrescription() {
  formData.value.prescriptions.push({
    medication: '',
    dosage: '',
    frequency: '',
    duration_days: 7,
    instructions: ''
  })
}

// Удалить назначение
function removePrescription(index) {
  formData.value.prescriptions.splice(index, 1)
}

// Обработка загрузки файла
function handleFileUpload({ file, event }) {
  try {
    const response = JSON.parse(event.target.response)
    message.success('Файл успешно загружен')
    loadVisit() // Перезагрузить данные
  } catch (error) {
    console.error('File upload error:', error)
    message.error('Ошибка при загрузке файла')
  }
}

// Обработка ошибки загрузки файла
function handleFileError({ file, event }) {
  console.error('File upload failed:', event)
  message.error(`Не удалось загрузить файл: ${file.name}`)
}

// Скачать файл
function downloadFile(file) {
  if (file.file) {
    window.open(file.file, '_blank')
  } else {
    message.error('Ссылка на файл недоступна')
  }
}

// Удалить файл
function deleteFile(file) {
  dialog.warning({
    title: 'Удалить файл?',
    content: `Вы уверены, что хотите удалить файл "${file.title || 'Без названия'}"?`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await apiClient.delete(`/visits/files/${file.id}`)
        message.success('Файл удален')
        await loadVisit()
      } catch (error) {
        message.error('Ошибка при удалении файла')
      }
    }
  })
}

// Печать визита
function printVisit() {
  dialog.info({
    title: 'Печать визита',
    content: 'Выберите формат печати',
    positiveText: 'Выписка из визита',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        const response = await apiClient.get(`/reports/visit-extract/${props.visitId}`, {
          responseType: 'blob'
        })
        const blob = new Blob([response.data], { type: 'application/pdf' })
        const url = window.URL.createObjectURL(blob)
        window.open(url, '_blank')
        message.success('Документ открыт в новой вкладке')
      } catch (error) {
        message.error('Ошибка при формировании документа')
      }
    }
  })
}

// Экспорт визита
function exportVisit() {
  const data = JSON.stringify(visitData.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `visit-${props.visitId}-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  window.URL.revokeObjectURL(url)
  message.success('Данные визита экспортированы')
}

// Закрыть модал
function closeModal() {
  if (isEditMode.value) {
    dialog.warning({
      title: 'Закрыть без сохранения?',
      content: 'Все несохраненные изменения будут потеряны',
      positiveText: 'Да, закрыть',
      negativeText: 'Нет',
      onPositiveClick: () => {
        isEditMode.value = false
        visible.value = false
      }
    })
  } else {
    visible.value = false
  }
}

// Форматирование даты и времени
function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  try {
    return format(parseISO(dateStr), 'dd.MM.yyyy HH:mm', { locale: ru })
  } catch (e) {
    return dateStr
  }
}

// Получить тип тега для статуса
function getStatusType(status) {
  const statusMap = {
    done: 'success',
    in_progress: 'warning',
    canceled: 'error',
    no_show: 'error'
  }
  return statusMap[status] || 'default'
}

// Получить текст статуса
function getStatusLabel(status) {
  const statusMap = {
    done: 'Выполнено',
    in_progress: 'В процессе',
    canceled: 'Отменено',
    no_show: 'Не пришёл'
  }
  return statusMap[status] || status
}

// Следить за открытием модала и загружать данные
watch(() => props.show, (newVal) => {
  if (newVal && props.visitId) {
    loadVisit()
    activeTab.value = 'general'
    isEditMode.value = false
  }
})
</script>

<style scoped>
/* Dark theme */
:deep(.n-card) {
  background-color: #1e1e1e;
  color: #e0e0e0;
}

:deep(.n-card-header) {
  color: #e0e0e0;
  border-bottom-color: #333;
}

:deep(.n-descriptions-table-content) {
  color: #e0e0e0;
}

:deep(.n-descriptions-table-row) {
  border-bottom-color: #333;
}

:deep(.n-data-table) {
  background-color: #1e1e1e;
}

:deep(.n-data-table-th) {
  background-color: #2d2d2d;
  color: #e0e0e0;
  border-color: #404040;
}

:deep(.n-data-table-td) {
  background-color: #1e1e1e;
  color: #e0e0e0;
  border-color: #333;
}

:deep(.n-list) {
  background-color: #1e1e1e;
  border-color: #333;
}

:deep(.n-list-item) {
  background-color: #1e1e1e;
  color: #e0e0e0;
  border-color: #333;
}

:deep(.n-thing-header__title) {
  color: #e0e0e0;
}

:deep(.n-divider) {
  background-color: #333;
}

:deep(.n-tabs-tab) {
  color: #a0a0a0;
}

:deep(.n-tabs-tab--active) {
  color: #63e2b7;
}

:deep(.n-input),
:deep(.n-input__textarea-el),
:deep(.n-input__input-el) {
  background-color: #2a2a2a;
  color: #e0e0e0;
  border-color: #404040;
}

:deep(.n-input:hover),
:deep(.n-input--focus) {
  border-color: #63e2b7;
}

:deep(.n-form-item-label) {
  color: #b0b0b0;
}
</style>
