<template>
  <div class="visits-page">
    <!-- Модальное окно визита -->
    <VisitModal
      v-model:show="showVisitModal"
      :visit-id="selectedVisitId"
    />

    <n-page-header title="Журнал визитов">
      <template #extra>
        <n-space>
          <n-date-picker
            v-model:value="dateRange"
            type="daterange"
            clearable
            @update:value="loadVisits"
          />
          <n-select
            v-model:value="statusFilter"
            :options="statusOptions"
            placeholder="Все статусы"
            clearable
            style="width: 200px"
            @update:value="loadVisits"
          />
          <n-button type="primary">
            📊 Экспорт
          </n-button>
        </n-space>
      </template>
    </n-page-header>

    <n-data-table
      :columns="columns"
      :data="visits"
      :loading="loading"
      :pagination="pagination"
      :row-key="(row) => row.id"
      style="margin-top: 16px"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { NButton, NTag, useMessage } from 'naive-ui'
import apiClient from '@/api/axios'
import { format, parseISO } from 'date-fns'
import VisitModal from '@/components/VisitModal.vue'

const message = useMessage()
const visits = ref([])
const loading = ref(false)
const dateRange = ref(null)
const statusFilter = ref(null)

// Модальное окно
const showVisitModal = ref(false)
const selectedVisitId = ref(null)

const pagination = {
  page: 1,
  pageSize: 20,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100]
}

const statusOptions = [
  { label: 'Выполнено', value: 'done' },
  { label: 'В процессе', value: 'in_progress' },
  { label: 'Отменено', value: 'canceled' },
  { label: 'Не пришёл', value: 'no_show' }
]

const columns = [
  {
    title: '№',
    key: 'id',
    width: 80
  },
  {
    title: 'Дата и время',
    key: 'start_datetime',
    width: 160,
    render: (row) => format(parseISO(row.start_datetime), 'dd.MM.yyyy HH:mm')
  },
  {
    title: 'Пациент',
    key: 'patient_name',
    ellipsis: { tooltip: true }
  },
  {
    title: 'Сотрудник',
    key: 'employee_name',
    width: 200
  },
  {
    title: 'Услуги',
    key: 'services',
    width: 300,
    ellipsis: { tooltip: true },
    render: (row) => row.services?.join(', ') || '-'
  },
  {
    title: 'Статус',
    key: 'status',
    width: 140,
    render: (row) => {
      const statusMap = {
        done: { label: 'Выполнено', type: 'success' },
        in_progress: { label: 'В процессе', type: 'warning' },
        canceled: { label: 'Отменено', type: 'error' },
        no_show: { label: 'Не пришёл', type: 'error' }
      }
      const status = statusMap[row.status] || { label: row.status, type: 'default' }
      return h(NTag, { type: status.type }, { default: () => status.label })
    }
  },
  {
    title: 'Сумма',
    key: 'total_amount',
    width: 120,
    render: (row) => `${row.total_amount || 0} ₸`
  },
  {
    title: 'Действия',
    key: 'actions',
    width: 100,
    render: (row) => {
      return h(NButton, {
        size: 'small',
        onClick: () => openVisit(row)
      }, { default: () => 'Открыть' })
    }
  }
]

async function loadVisits() {
  loading.value = true
  try {
    const params = {}
    if (dateRange.value) {
      params.date_from = format(new Date(dateRange.value[0]), 'yyyy-MM-dd')
      params.date_to = format(new Date(dateRange.value[1]), 'yyyy-MM-dd')
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    
    const response = await apiClient.get('/visits/visits', { params })
    visits.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading visits:', error)
    message.error('Ошибка загрузки визитов')
  } finally {
    loading.value = false
  }
}

function openVisit(visit) {
  selectedVisitId.value = visit.id
  showVisitModal.value = true
}

onMounted(() => {
  loadVisits()
})
</script>

<style scoped>
.visits-page {
  padding: 24px;
  background: #121212;
  min-height: 100vh;
}

/* Dark theme */
:deep(.n-page-header) {
  color: #e0e0e0;
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

:deep(.n-data-table-tr:hover .n-data-table-td) {
  background-color: #2a2a2a;
}
</style>
