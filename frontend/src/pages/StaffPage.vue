<template>
  <div class="staff-page">
    <div class="page-header">
      <h1>Сотрудники</h1>
      <div class="header-actions">
        <n-input
          v-model:value="searchQuery"
          placeholder="Поиск по ФИО, телефону..."
          clearable
          style="width: 300px"
        >
          <template #prefix>
            <span>🔍</span>
          </template>
        </n-input>
        <n-button type="primary" @click="openNewEmployee">
          + Новый сотрудник
        </n-button>
      </div>
    </div>

    <div class="page-content">
      <n-data-table
        :columns="columns"
        :data="filteredEmployees"
        :loading="loading"
        :pagination="paginationProps"
        :row-key="(row) => row.id"
      />
    </div>

    <!-- Employee Modal -->
    <EmployeeModal
      v-model:show="showEmployeeModal"
      :employee="selectedEmployee"
      @saved="handleEmployeeSaved"
    />

    <!-- Delete Confirmation -->
    <n-modal
      v-model:show="showDeleteConfirm"
      preset="dialog"
      title="Удалить сотрудника?"
      positive-text="Удалить"
      negative-text="Отмена"
      @positive-click="confirmDelete"
    >
      <p>
        Вы уверены, что хотите удалить сотрудника
        <strong>{{ selectedEmployee?.full_name }}</strong>?
      </p>
      <p style="color: #f44336; margin-top: 8px">
        Это действие нельзя отменить!
      </p>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { NButton, NSpace, NTag, useMessage } from 'naive-ui'
import apiClient from '@/api/axios'
import EmployeeModal from '@/components/EmployeeModal.vue'
import StatusBadge from '@/components/StatusBadge.vue'

const message = useMessage()

// State
const employees = ref([])
const loading = ref(false)
const searchQuery = ref('')
const showEmployeeModal = ref(false)
const showDeleteConfirm = ref(false)
const selectedEmployee = ref(null)

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
    title: 'ФИО',
    key: 'full_name',
    render: (row) => {
      return h('div', { style: 'display: flex; align-items: center; gap: 8px' }, [
        h('div', {
          style: {
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            backgroundColor: row.color,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: '600',
            fontSize: '12px'
          }
        }, `${row.first_name?.[0] || ''}${row.last_name?.[0] || ''}`),
        h('span', row.full_name || `${row.last_name} ${row.first_name}`)
      ])
    },
    sorter: (a, b) => (a.last_name || '').localeCompare(b.last_name || '')
  },
  {
    title: 'Должность',
    key: 'position',
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: 'Специализация',
    key: 'specialization',
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: 'Телефон',
    key: 'phone'
  },
  {
    title: 'Комиссия',
    key: 'commission_percent',
    width: 100,
    render: (row) => `${row.commission_percent || 0}%`
  },
  {
    title: 'Статус',
    key: 'is_active',
    width: 120,
    render: (row) => {
      return h(
        NTag,
        {
          type: row.is_active ? 'success' : 'error',
          size: 'small'
        },
        { default: () => (row.is_active ? 'Активен' : 'Уволен') }
      )
    }
  },
  {
    title: 'Действия',
    key: 'actions',
    width: 180,
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
                onClick: () => openEditEmployee(row)
              },
              { default: () => '✏️ Изменить' }
            ),
            h(
              NButton,
              {
                size: 'small',
                type: 'error',
                onClick: () => openDeleteEmployee(row)
              },
              { default: () => '🗑️ Удалить' }
            )
          ]
        }
      )
    }
  }
]

// Computed
const filteredEmployees = computed(() => {
  if (!searchQuery.value) return employees.value

  const query = searchQuery.value.toLowerCase()
  return employees.value.filter((emp) => {
    const fullName = `${emp.last_name} ${emp.first_name} ${emp.middle_name}`.toLowerCase()
    const phone = emp.phone || ''
    const position = emp.position || ''

    return (
      fullName.includes(query) ||
      phone.includes(query) ||
      position.toLowerCase().includes(query)
    )
  })
})

// Functions
async function loadEmployees() {
  loading.value = true
  try {
    const response = await apiClient.get('/staff/employees')
    employees.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading employees:', error)
    message.error('Ошибка загрузки сотрудников')
  } finally {
    loading.value = false
  }
}

function openNewEmployee() {
  selectedEmployee.value = null
  showEmployeeModal.value = true
}

function openEditEmployee(employee) {
  selectedEmployee.value = employee
  showEmployeeModal.value = true
}

function openDeleteEmployee(employee) {
  selectedEmployee.value = employee
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  try {
    await apiClient.delete(`/staff/employees/${selectedEmployee.value.id}`)
    message.success('Сотрудник удалён')
    await loadEmployees()
  } catch (error) {
    console.error('Error deleting employee:', error)
    message.error('Ошибка удаления сотрудника')
  } finally {
    showDeleteConfirm.value = false
    selectedEmployee.value = null
  }
}

async function handleEmployeeSaved() {
  await loadEmployees()
}

// Lifecycle
onMounted(() => {
  loadEmployees()
})
</script>

<style scoped lang="scss">
@import '@/styles/tokens.scss';

.staff-page {
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
