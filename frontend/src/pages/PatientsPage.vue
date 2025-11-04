<template>
  <div class="patients-page">
    <div class="page-header">
      <h1>Пациенты</h1>
      <div class="header-actions">
        <n-input
          v-model:value="searchQuery"
          placeholder="Поиск по ФИО, телефону, ИИН..."
          clearable
          style="width: 350px"
        >
          <template #prefix>
            <span>🔍</span>
          </template>
        </n-input>
        <n-button type="primary" @click="openNewPatient">
          + Новый пациент
        </n-button>
      </div>
    </div>

    <div class="page-content">
      <n-data-table
        :columns="columns"
        :data="filteredPatients"
        :loading="loading"
        :pagination="paginationProps"
        :row-key="(row) => row.id"
      />
    </div>

    <!-- Patient Modal -->
    <PatientModal
      v-model:show="showPatientModal"
      :patient="selectedPatient"
      @saved="handlePatientSaved"
    />

    <!-- Delete Confirmation -->
    <n-modal
      v-model:show="showDeleteConfirm"
      preset="dialog"
      title="Удалить пациента?"
      positive-text="Удалить"
      negative-text="Отмена"
      @positive-click="confirmDelete"
    >
      <p>
        Вы уверены, что хотите удалить пациента
        <strong>{{ selectedPatient?.full_name }}</strong>?
      </p>
      <p style="color: #f44336; margin-top: 8px">
        Это действие нельзя отменить! Будут удалены все связанные записи и визиты.
      </p>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { NButton, NSpace, NTag, useMessage } from 'naive-ui'
import apiClient from '@/api/axios'
import PatientModal from '@/components/PatientModal.vue'
import { format, parseISO } from 'date-fns'

const message = useMessage()

// State
const patients = ref([])
const loading = ref(false)
const searchQuery = ref('')
const showPatientModal = ref(false)
const showDeleteConfirm = ref(false)
const selectedPatient = ref(null)

// Pagination
const paginationProps = {
  pageSize: 25,
  pageSizes: [25, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }) => `Всего: ${itemCount}`
}

// Table columns
const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 60,
    sorter: (a, b) => a.id - b.id
  },
  {
    title: 'Карта №',
    key: 'id',
    width: 100,
    render: (row) => `№ ${row.id}`
  },
  {
    title: 'ФИО',
    key: 'full_name',
    render: (row) => row.full_name || `${row.last_name} ${row.first_name} ${row.middle_name || ''}`,
    sorter: (a, b) => (a.last_name || '').localeCompare(b.last_name || '')
  },
  {
    title: 'Дата рождения',
    key: 'birth_date',
    width: 130,
    render: (row) => {
      if (!row.birth_date) return '-'
      try {
        return format(parseISO(row.birth_date), 'dd.MM.yyyy')
      } catch {
        return row.birth_date
      }
    }
  },
  {
    title: 'Возраст',
    key: 'age',
    width: 80,
    render: (row) => row.age ? `${row.age} лет` : '-'
  },
  {
    title: 'Пол',
    key: 'sex',
    width: 80,
    render: (row) => {
      const sexMap = { M: 'Муж.', F: 'Жен.', '': '-' }
      return sexMap[row.sex] || '-'
    }
  },
  {
    title: 'Телефон',
    key: 'phone',
    width: 150
  },
  {
    title: 'Email',
    key: 'email',
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: 'Баланс',
    key: 'balance',
    width: 120,
    render: (row) => {
      const balance = parseFloat(row.balance) || 0
      const color = balance > 0 ? '#4CAF50' : balance < 0 ? '#F44336' : '#9E9E9E'
      return h('span', { style: { color, fontWeight: '500' } }, `${balance.toLocaleString()} ₸`)
    }
  },
  {
    title: 'Скидка',
    key: 'discount_percent',
    width: 80,
    render: (row) => `${row.discount_percent || 0}%`
  },
  {
    title: 'Статус',
    key: 'is_active',
    width: 100,
    render: (row) => {
      return h(
        NTag,
        {
          type: row.is_active ? 'success' : 'error',
          size: 'small'
        },
        { default: () => (row.is_active ? 'Активен' : 'Архив') }
      )
    }
  },
  {
    title: 'Действия',
    key: 'actions',
    width: 200,
    render: (row) => {
      return h(
        NSpace,
        { size: 'small' },
        {
          default: () => [
            h(
              NButton,
              {
                size: 'small',
                onClick: () => openEditPatient(row)
              },
              { default: () => '📋 Открыть' }
            ),
            h(
              NButton,
              {
                size: 'small',
                onClick: () => openEditPatient(row)
              },
              { default: () => '✏️' }
            ),
            h(
              NButton,
              {
                size: 'small',
                type: 'error',
                onClick: () => openDeletePatient(row)
              },
              { default: () => '🗑️' }
            )
          ]
        }
      )
    }
  }
]

// Computed
const filteredPatients = computed(() => {
  if (!searchQuery.value) return patients.value

  const query = searchQuery.value.toLowerCase()
  return patients.value.filter((patient) => {
    const fullName = `${patient.last_name} ${patient.first_name} ${patient.middle_name || ''}`.toLowerCase()
    const phone = patient.phone || ''
    const iin = patient.iin || ''

    return fullName.includes(query) || phone.includes(query) || iin.includes(query)
  })
})

// Functions
async function loadPatients() {
  loading.value = true
  try {
    const response = await apiClient.get('/patients/patients')
    patients.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading patients:', error)
    message.error('Ошибка загрузки пациентов')
  } finally {
    loading.value = false
  }
}

function openNewPatient() {
  selectedPatient.value = null
  showPatientModal.value = true
}

function openEditPatient(patient) {
  selectedPatient.value = patient
  showPatientModal.value = true
}

function openDeletePatient(patient) {
  selectedPatient.value = patient
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  try {
    await apiClient.delete(`/patients/patients/${selectedPatient.value.id}`)
    message.success('Пациент удалён')
    await loadPatients()
  } catch (error) {
    console.error('Error deleting patient:', error)
    message.error('Ошибка удаления пациента')
  } finally {
    showDeleteConfirm.value = false
    selectedPatient.value = null
  }
}

async function handlePatientSaved() {
  await loadPatients()
}

// Lifecycle
onMounted(() => {
  loadPatients()
})
</script>

<style scoped lang="scss">
@import '@/styles/tokens.scss';

.patients-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: $bg-primary;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color;
  background: $bg-secondary;

  h1 {
    margin: 0;
    font-size: 24px;
    color: $text-primary;
  }
}

.header-actions {
  display: flex;
  gap: $spacing-md;
  align-items: center;
}

.page-content {
  flex: 1;
  padding: $spacing-lg;
  overflow: auto;
}
</style>
