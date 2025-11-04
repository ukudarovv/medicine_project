<template>
  <div class="staff-hr-page">
    <div class="page-header">
      <h1>Сотрудники (HR)</h1>
    </div>

    <div class="page-content">
      <n-tabs type="line" animated>
        <!-- Сотрудники -->
        <n-tab-pane name="employees" tab="Сотрудники">
          <div class="tab-header">
            <n-space>
              <n-input
                v-model:value="employeeSearch"
                placeholder="Поиск по ФИО, телефону..."
                clearable
                style="width: 300px"
              >
                <template #prefix>
                  <span>🔍</span>
                </template>
              </n-input>
              <n-select
                v-model:value="positionFilter"
                :options="positionFilterOptions"
                placeholder="Должность"
                clearable
                style="width: 200px"
              />
              <n-select
                v-model:value="statusFilter"
                :options="statusFilterOptions"
                placeholder="Статус"
                clearable
                style="width: 150px"
              />
            </n-space>
            <n-button type="primary" @click="openNewEmployee">
              + Новый сотрудник
            </n-button>
          </div>

          <n-data-table
            :columns="employeeColumns"
            :data="filteredEmployees"
            :loading="loadingEmployees"
            :pagination="paginationProps"
            :row-key="(row) => row.id"
          />
        </n-tab-pane>

        <!-- Должности -->
        <n-tab-pane name="positions" tab="Должности">
          <div class="tab-header">
            <n-input
              v-model:value="positionSearch"
              placeholder="Поиск должностей..."
              clearable
              style="width: 300px"
            >
              <template #prefix>
                <span>🔍</span>
              </template>
            </n-input>
            <n-button type="primary" @click="openNewPosition">
              + Новая должность
            </n-button>
          </div>

          <n-data-table
            :columns="positionColumns"
            :data="filteredPositions"
            :loading="loadingPositions"
            :pagination="paginationProps"
            :row-key="(row) => row.id"
          />
        </n-tab-pane>

        <!-- Задачи -->
        <n-tab-pane name="tasks" tab="Задачи сотрудников">
          <div class="tab-header">
            <n-space>
              <n-input
                v-model:value="taskSearch"
                placeholder="Поиск задач..."
                clearable
                style="width: 300px"
              >
                <template #prefix>
                  <span>🔍</span>
                </template>
              </n-input>
              <n-select
                v-model:value="taskStatusFilter"
                :options="taskStatusOptions"
                placeholder="Статус"
                clearable
                style="width: 150px"
              />
            </n-space>
            <n-button type="primary" @click="openNewTask">
              + Новая задача
            </n-button>
          </div>

          <n-data-table
            :columns="taskColumns"
            :data="filteredTasks"
            :loading="loadingTasks"
            :pagination="paginationProps"
            :row-key="(row) => row.id"
          />
        </n-tab-pane>

        <!-- Шаблоны ЗП -->
        <n-tab-pane name="salary" tab="Шаблоны ЗП">
          <div class="tab-header">
            <n-input
              v-model:value="salarySearch"
              placeholder="Поиск шаблонов..."
              clearable
              style="width: 300px"
            >
              <template #prefix>
                <span>🔍</span>
              </template>
            </n-input>
            <n-button type="primary" @click="openNewSalaryTemplate">
              + Новый шаблон ЗП
            </n-button>
          </div>

          <n-data-table
            :columns="salaryTemplateColumns"
            :data="filteredSalaryTemplates"
            :loading="loadingSalaryTemplates"
            :pagination="paginationProps"
            :row-key="(row) => row.id"
          />
        </n-tab-pane>
      </n-tabs>
    </div>

    <!-- Modals -->
    <EmployeeModal
      v-model:show="showEmployeeModal"
      :employee="selectedEmployee"
      @saved="handleEmployeeSaved"
    />

    <PositionModal
      v-model:show="showPositionModal"
      :position="selectedPosition"
      @saved="handlePositionSaved"
    />

    <EmployeeTaskModal
      v-model:show="showTaskModal"
      :task="selectedTask"
      @saved="handleTaskSaved"
    />

    <SalaryTemplateModal
      v-model:show="showSalaryTemplateModal"
      :template="selectedSalaryTemplate"
      @saved="handleSalaryTemplateSaved"
    />

    <!-- Delete Confirmations -->
    <n-modal
      v-model:show="showDeleteConfirm"
      preset="dialog"
      title="Удалить?"
      positive-text="Удалить"
      negative-text="Отмена"
      @positive-click="confirmDelete"
    >
      <p>Вы уверены, что хотите удалить <strong>{{ deleteItemName }}</strong>?</p>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { NButton, NSpace, NTag, useMessage } from 'naive-ui'
import apiClient from '@/api/axios'
import EmployeeModal from '@/components/EmployeeModal.vue'
import PositionModal from '@/components/PositionModal.vue'
import EmployeeTaskModal from '@/components/EmployeeTaskModal.vue'
import SalaryTemplateModal from '@/components/SalaryTemplateModal.vue'

const message = useMessage()

// State
const employees = ref([])
const positions = ref([])
const tasks = ref([])
const salaryTemplates = ref([])

const loadingEmployees = ref(false)
const loadingPositions = ref(false)
const loadingTasks = ref(false)
const loadingSalaryTemplates = ref(false)

// Search and filters
const employeeSearch = ref('')
const positionSearch = ref('')
const taskSearch = ref('')
const salarySearch = ref('')

const positionFilter = ref(null)
const statusFilter = ref(null)
const taskStatusFilter = ref(null)

// Modal states
const showEmployeeModal = ref(false)
const showPositionModal = ref(false)
const showTaskModal = ref(false)
const showSalaryTemplateModal = ref(false)
const showDeleteConfirm = ref(false)

const selectedEmployee = ref(null)
const selectedPosition = ref(null)
const selectedTask = ref(null)
const selectedSalaryTemplate = ref(null)

const deleteItem = ref(null)
const deleteItemType = ref('')
const deleteItemName = ref('')

// Pagination
const paginationProps = {
  pageSize: 25,
  pageSizes: [25, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }) => `Всего: ${itemCount}`
}

// Filter options
const positionFilterOptions = computed(() => [
  ...positions.value.map(p => ({ label: p.name, value: p.id }))
])

const statusFilterOptions = [
  { label: 'Активные', value: 'active' },
  { label: 'Уволенные', value: 'fired' },
  { label: 'В отпуске', value: 'on_leave' }
]

const taskStatusOptions = [
  { label: 'Новые', value: 'new' },
  { label: 'В процессе', value: 'in_progress' },
  { label: 'Выполнены', value: 'done' },
  { label: 'Отменены', value: 'cancelled' }
]

// Table columns
const employeeColumns = [
  {
    title: 'ID',
    key: 'id',
    width: 60
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
            backgroundColor: row.calendar_color || row.color,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: '600',
            fontSize: '12px'
          }
        }, `${row.first_name?.[0] || ''}${row.last_name?.[0] || ''}`),
        h('span', row.full_name)
      ])
    }
  },
  {
    title: 'Должность',
    key: 'position_name'
  },
  {
    title: 'Телефон',
    key: 'phone'
  },
  {
    title: 'Статус',
    key: 'employment_status',
    render: (row) => {
      const statusMap = {
        active: { type: 'success', label: 'Активен' },
        fired: { type: 'error', label: 'Уволен' },
        on_leave: { type: 'warning', label: 'В отпуске' }
      }
      const status = statusMap[row.employment_status] || statusMap.active
      return h(NTag, { type: status.type, size: 'small' }, { default: () => status.label })
    }
  },
  {
    title: 'Схема ЗП',
    render: (row) => row.current_salary_schema?.name || 'Не задана'
  },
  {
    title: 'Действия',
    key: 'actions',
    width: 180,
    render: (row) => {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NButton, { size: 'small', onClick: () => openEditEmployee(row) }, { default: () => '✏️' }),
          h(NButton, { size: 'small', type: 'error', onClick: () => openDeleteConfirmation('employee', row) }, { default: () => '🗑️' })
        ]
      })
    }
  }
]

const positionColumns = [
  { title: 'ID', key: 'id', width: 60 },
  { title: 'Название', key: 'name' },
  { title: 'Комментарий', key: 'comment' },
  {
    title: 'Скрыта в расписании',
    key: 'hidden_in_schedule_filter',
    render: (row) => row.hidden_in_schedule_filter ? '✓' : ''
  },
  {
    title: 'Действия',
    key: 'actions',
    width: 180,
    render: (row) => {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NButton, { size: 'small', onClick: () => openEditPosition(row) }, { default: () => '✏️' }),
          h(NButton, { size: 'small', type: 'error', onClick: () => openDeleteConfirmation('position', row) }, { default: () => '🗑️' })
        ]
      })
    }
  }
]

const taskColumns = [
  { title: 'Название', key: 'title' },
  { title: 'Исполнитель', key: 'assignee_name' },
  { title: 'Автор', key: 'author_name' },
  {
    title: 'Статус',
    key: 'status',
    render: (row) => {
      const statusMap = {
        new: { type: 'info', label: 'Новая' },
        in_progress: { type: 'warning', label: 'В процессе' },
        done: { type: 'success', label: 'Выполнена' },
        cancelled: { type: 'error', label: 'Отменена' }
      }
      const status = statusMap[row.status]
      return h(NTag, { type: status.type, size: 'small' }, { default: () => status.label })
    }
  },
  { 
    title: 'Дедлайн',
    key: 'deadline_at',
    render: (row) => new Date(row.deadline_at).toLocaleString('ru-RU')
  },
  {
    title: 'Действия',
    key: 'actions',
    width: 180,
    render: (row) => {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NButton, { size: 'small', onClick: () => openEditTask(row) }, { default: () => '✏️' }),
          h(NButton, { size: 'small', type: 'error', onClick: () => openDeleteConfirmation('task', row) }, { default: () => '🗑️' })
        ]
      })
    }
  }
]

const salaryTemplateColumns = [
  { title: 'Название', key: 'name' },
  {
    title: 'От продаж',
    key: 'pct_of_own_sales',
    render: (row) => row.pct_of_own_sales ? `${row.pct_value}%` : '-'
  },
  {
    title: 'Фикс. оклад',
    key: 'fixed_salary_enabled',
    render: (row) => row.fixed_salary_enabled ? `${row.fixed_amount} ${row.currency}` : '-'
  },
  {
    title: 'Мин. ставка',
    key: 'min_rate_enabled',
    render: (row) => row.min_rate_enabled ? `${row.min_rate_amount}` : '-'
  },
  {
    title: 'Действия',
    key: 'actions',
    width: 180,
    render: (row) => {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NButton, { size: 'small', onClick: () => openEditSalaryTemplate(row) }, { default: () => '✏️' }),
          h(NButton, { size: 'small', type: 'error', onClick: () => openDeleteConfirmation('salaryTemplate', row) }, { default: () => '🗑️' })
        ]
      })
    }
  }
]

// Computed filters
const filteredEmployees = computed(() => {
  let result = employees.value

  if (employeeSearch.value) {
    const query = employeeSearch.value.toLowerCase()
    result = result.filter((emp) => {
      const fullName = emp.full_name.toLowerCase()
      const phone = emp.phone || ''
      return fullName.includes(query) || phone.includes(query)
    })
  }

  if (positionFilter.value) {
    result = result.filter((emp) => emp.position === positionFilter.value)
  }

  if (statusFilter.value) {
    result = result.filter((emp) => emp.employment_status === statusFilter.value)
  }

  return result
})

const filteredPositions = computed(() => {
  if (!positionSearch.value) return positions.value

  const query = positionSearch.value.toLowerCase()
  return positions.value.filter((pos) => pos.name.toLowerCase().includes(query))
})

const filteredTasks = computed(() => {
  let result = tasks.value

  if (taskSearch.value) {
    const query = taskSearch.value.toLowerCase()
    result = result.filter((task) => task.title.toLowerCase().includes(query))
  }

  if (taskStatusFilter.value) {
    result = result.filter((task) => task.status === taskStatusFilter.value)
  }

  return result
})

const filteredSalaryTemplates = computed(() => {
  if (!salarySearch.value) return salaryTemplates.value

  const query = salarySearch.value.toLowerCase()
  return salaryTemplates.value.filter((tpl) => tpl.name.toLowerCase().includes(query))
})

// Functions
async function loadEmployees() {
  loadingEmployees.value = true
  try {
    const response = await apiClient.get('/staff/employees')
    employees.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading employees:', error)
    message.error('Ошибка загрузки сотрудников')
  } finally {
    loadingEmployees.value = false
  }
}

async function loadPositions() {
  loadingPositions.value = true
  try {
    const response = await apiClient.get('/staff/positions')
    positions.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading positions:', error)
    message.error('Ошибка загрузки должностей')
  } finally {
    loadingPositions.value = false
  }
}

async function loadTasks() {
  loadingTasks.value = true
  try {
    const response = await apiClient.get('/staff/tasks')
    tasks.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading tasks:', error)
    message.error('Ошибка загрузки задач')
  } finally {
    loadingTasks.value = false
  }
}

async function loadSalaryTemplates() {
  loadingSalaryTemplates.value = true
  try {
    const response = await apiClient.get('/staff/salary-templates')
    salaryTemplates.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading salary templates:', error)
    message.error('Ошибка загрузки шаблонов ЗП')
  } finally {
    loadingSalaryTemplates.value = false
  }
}

// Modal handlers
function openNewEmployee() {
  selectedEmployee.value = null
  showEmployeeModal.value = true
}

function openEditEmployee(employee) {
  selectedEmployee.value = employee
  showEmployeeModal.value = true
}

function openNewPosition() {
  selectedPosition.value = null
  showPositionModal.value = true
}

function openEditPosition(position) {
  selectedPosition.value = position
  showPositionModal.value = true
}

function openNewTask() {
  selectedTask.value = null
  showTaskModal.value = true
}

function openEditTask(task) {
  selectedTask.value = task
  showTaskModal.value = true
}

function openNewSalaryTemplate() {
  selectedSalaryTemplate.value = null
  showSalaryTemplateModal.value = true
}

function openEditSalaryTemplate(template) {
  selectedSalaryTemplate.value = template
  showSalaryTemplateModal.value = true
}

function openDeleteConfirmation(type, item) {
  deleteItemType.value = type
  deleteItem.value = item
  deleteItemName.value = item.name || item.title || item.full_name
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  try {
    const endpoints = {
      employee: `/staff/employees/${deleteItem.value.id}`,
      position: `/staff/positions/${deleteItem.value.id}`,
      task: `/staff/tasks/${deleteItem.value.id}`,
      salaryTemplate: `/staff/salary-templates/${deleteItem.value.id}`
    }

    await apiClient.delete(endpoints[deleteItemType.value])
    message.success('Удалено')

    // Reload data
    if (deleteItemType.value === 'employee') await loadEmployees()
    else if (deleteItemType.value === 'position') await loadPositions()
    else if (deleteItemType.value === 'task') await loadTasks()
    else if (deleteItemType.value === 'salaryTemplate') await loadSalaryTemplates()
  } catch (error) {
    console.error('Error deleting:', error)
    message.error('Ошибка удаления')
  } finally {
    showDeleteConfirm.value = false
  }
}

// Save handlers
async function handleEmployeeSaved() {
  await loadEmployees()
}

async function handlePositionSaved() {
  await loadPositions()
}

async function handleTaskSaved() {
  await loadTasks()
}

async function handleSalaryTemplateSaved() {
  await loadSalaryTemplates()
}

// Lifecycle
onMounted(() => {
  loadEmployees()
  loadPositions()
  loadTasks()
  loadSalaryTemplates()
})
</script>

<style scoped lang="scss">
@import '@/styles/tokens.scss';

.staff-hr-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: $bg-primary;
}

.page-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color;
  background: $bg-secondary;

  h1 {
    margin: 0;
    font-size: 24px;
    color: $text-primary;
  }
}

.page-content {
  flex: 1;
  padding: $spacing-lg;
  overflow: auto;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
  padding: $spacing-md 0;
}
</style>


