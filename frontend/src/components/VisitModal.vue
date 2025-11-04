<template>
  <n-modal
    v-model:show="visible"
    :title="`Визит #${visitData?.id || ''}`"
    preset="card"
    style="width: 1200px"
    :segmented="{ content: 'soft' }"
  >
    <n-spin :show="loading">
      <n-scrollbar style="max-height: 75vh">
        <n-tabs v-model:value="activeTab" type="line" animated>
          <!-- Основная информация -->
          <n-tab-pane name="general" tab="Основная информация">
            <n-space vertical :size="16">
              <!-- Информация о визите -->
              <n-card title="Информация о визите" :bordered="false">
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
              </n-card>

              <!-- Диагноз и лечение -->
              <n-card title="Диагноз и план лечения" :bordered="false">
                <n-space vertical :size="12">
                  <div>
                    <n-text strong>Диагноз:</n-text>
                    <div style="margin-top: 8px">
                      {{ visitData?.diagnosis || 'Не указан' }}
                    </div>
                  </div>
                  <n-divider style="margin: 8px 0" />
                  <div>
                    <n-text strong>План лечения:</n-text>
                    <div style="margin-top: 8px">
                      {{ visitData?.treatment_plan || 'Не указан' }}
                    </div>
                  </div>
                  <n-divider style="margin: 8px 0" />
                  <div>
                    <n-text strong>Комментарий:</n-text>
                    <div style="margin-top: 8px">
                      {{ visitData?.comment || 'Нет комментариев' }}
                    </div>
                  </div>
                </n-space>
              </n-card>

              <!-- Дневник (если есть структурированные данные) -->
              <n-card v-if="visitData?.diary_structured" title="Структурированный дневник" :bordered="false">
                <pre style="white-space: pre-wrap; color: #e0e0e0;">{{ JSON.stringify(visitData.diary_structured, null, 2) }}</pre>
              </n-card>
            </n-space>
          </n-tab-pane>

          <!-- Услуги -->
          <n-tab-pane name="services" tab="Услуги">
            <n-card :bordered="false">
              <n-data-table
                :columns="servicesColumns"
                :data="visitData?.services_list || []"
                :pagination="false"
                size="small"
              />
              <n-divider />
              <n-space justify="end">
                <n-text strong style="font-size: 16px">
                  Итого: {{ visitData?.total_amount || 0 }} ₸
                </n-text>
              </n-space>
            </n-card>
          </n-tab-pane>

          <!-- Назначения -->
          <n-tab-pane name="prescriptions" tab="Назначения">
            <n-card :bordered="false">
              <n-empty v-if="!visitData?.prescriptions?.length" description="Нет назначений" />
              <n-list v-else bordered>
                <n-list-item v-for="prescription in visitData.prescriptions" :key="prescription.id">
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
              <n-empty v-if="!visitData?.files?.length" description="Нет прикрепленных файлов" />
              <n-list v-else bordered>
                <n-list-item v-for="file in visitData.files" :key="file.id">
                  <n-thing :title="file.title || 'Без названия'">
                    <template #description>
                      <n-space vertical :size="4">
                        <div><n-text depth="3">Тип:</n-text> {{ file.file_type_display }}</div>
                        <div v-if="file.description"><n-text depth="3">Описание:</n-text> {{ file.description }}</div>
                        <div><n-text depth="3">Загружено:</n-text> {{ formatDateTime(file.created_at) }} {{ file.uploaded_by_name ? `(${file.uploaded_by_name})` : '' }}</div>
                      </n-space>
                    </template>
                    <template #action>
                      <n-button size="small" @click="downloadFile(file)">
                        Скачать
                      </n-button>
                    </template>
                  </n-thing>
                </n-list-item>
              </n-list>
            </n-card>
          </n-tab-pane>
        </n-tabs>
      </n-scrollbar>
    </n-spin>

    <template #footer>
      <n-space justify="end">
        <n-button @click="visible = false">Закрыть</n-button>
        <n-button type="primary" @click="editVisit">
          Редактировать
        </n-button>
        <n-button type="info" @click="printVisit">
          🖨️ Печать
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import apiClient from '@/api/axios'
import { format, parseISO } from 'date-fns'
import { ru } from 'date-fns/locale'

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

const emit = defineEmits(['update:show'])

const message = useMessage()
const visible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val)
})

const activeTab = ref('general')
const loading = ref(false)
const visitData = ref(null)

// Колонки для таблицы услуг
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

// Редактировать визит
function editVisit() {
  message.info('Редактирование визита (в разработке)')
  // TODO: Открыть форму редактирования
}

// Печать визита
function printVisit() {
  message.info('Печать визита (в разработке)')
  // TODO: Открыть диалог печати
}

// Скачать файл
function downloadFile(file) {
  message.info(`Скачивание файла: ${file.title}`)
  // TODO: Реализовать скачивание файла
  // window.open(file.file, '_blank')
}

// Следить за открытием модала и загружать данные
watch(() => props.show, (newVal) => {
  if (newVal && props.visitId) {
    loadVisit()
    activeTab.value = 'general'
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
</style>

