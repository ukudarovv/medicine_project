<template>
  <div class="schedule-page">
    <div class="schedule-header">
      <div class="header-left">
        <h1>Расписание</h1>
        <n-button-group>
          <n-button 
            :type="viewMode === 'day' ? 'primary' : 'default'" 
            @click="viewMode = 'day'"
          >
            День
          </n-button>
          <n-button 
            :type="viewMode === 'week' ? 'primary' : 'default'" 
            @click="viewMode = 'week'"
          >
            Неделя
          </n-button>
          <n-button 
            :type="viewMode === 'month' ? 'primary' : 'default'" 
            @click="viewMode = 'month'"
          >
            Месяц
          </n-button>
        </n-button-group>
      </div>
      <div class="header-actions">
        <n-button-group>
          <n-button @click="scrollToTop" secondary>
            <template #icon>
              <n-icon><svg viewBox="0 0 24 24"><path fill="currentColor" d="M7,15L12,10L17,15H7Z"></path></svg></n-icon>
            </template>
            Начало дня
          </n-button>
          <n-button @click="scrollToCurrentTime" secondary>
            <template #icon>
              <n-icon><svg viewBox="0 0 24 24"><path fill="currentColor" d="M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z"></path></svg></n-icon>
            </template>
            Сейчас
          </n-button>
        </n-button-group>
        <n-select
          v-model:value="statusFilter"
          multiple
          :options="statusOptions"
          placeholder="Фильтр по статусам"
          style="width: 250px"
          clearable
        />
        <n-date-picker v-model:value="selectedDate" type="date" clearable />
        <n-button @click="showAccessRequestModal = true">
          🔐 Запрос доступа
        </n-button>
        <n-button type="primary" @click="showNewAppointment = true">
          + Новый визит
        </n-button>
      </div>
    </div>

    <div class="schedule-content">
      <!-- Employee tabs/columns header -->
      <div class="employees-header">
        <div class="time-column-header"></div>
        <n-dropdown
          v-for="employee in employees"
          :key="employee.id"
          trigger="click"
          :options="getEmployeeMenuOptions(employee)"
          @select="handleEmployeeAction"
        >
          <div
            class="employee-header"
            :class="{ active: selectedEmployees.includes(employee.id) }"
            @click.stop="toggleEmployee(employee.id)"
          >
            <div class="employee-avatar" :style="{ backgroundColor: employee.color }">
              {{ employee.first_name?.[0] || '' }}{{ employee.last_name?.[0] || '' }}
            </div>
            <div class="employee-info">
              <div class="employee-name">{{ employee.last_name }} {{ employee.first_name }}</div>
              <div class="employee-count">{{ getEmployeeAppointmentCount(employee.id) }}</div>
            </div>
            <n-icon size="18" class="employee-menu-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
              </svg>
            </n-icon>
          </div>
        </n-dropdown>
      </div>

      <!-- Schedule grid -->
      <div class="schedule-grid" ref="gridRef">
        <!-- Time column -->
        <div class="time-column">
          <div
            v-for="hour in timeSlots"
            :key="hour"
            class="time-slot"
            :style="{ height: slotHeight + 'px' }"
          >
            {{ hour }}
          </div>
        </div>

        <!-- Current time indicator -->
        <div
          v-if="currentTimePosition"
          class="current-time-line"
          :style="{ top: currentTimePosition + 'px' }"
        >
          <span class="current-time-label">{{ currentTime }}</span>
        </div>

        <!-- Employee columns -->
        <div
          v-for="employee in filteredEmployees"
          :key="employee.id"
          class="employee-column"
          @click="handleColumnClick($event, employee)"
        >
          <!-- Appointment blocks -->
          <div
            v-for="appointment in getEmployeeAppointments(employee.id)"
            :key="appointment.id"
            class="appointment-block"
            :class="[
              `status-${appointment.status}`,
              { 'has-visit': appointment.has_visit }
            ]"
            :style="getAppointmentStyle(appointment)"
            @click.stop="openAppointment(appointment)"
            @contextmenu.prevent="showAppointmentContextMenu($event, appointment)"
          >
            <!-- Visit indicator -->
            <div v-if="appointment.has_visit" class="visit-indicator" :class="`visit-${appointment.visit_status}`">
              <n-icon size="16">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M9,20.42L2.79,14.21L5.62,11.38L9,14.77L18.88,4.88L21.71,7.71L9,20.42Z"></path></svg>
              </n-icon>
            </div>
            <div class="appointment-patient">
              {{ appointment.patient_name }}
            </div>
            <div class="appointment-phone">
              {{ appointment.patient_phone }}
            </div>
            <div class="appointment-time">
              {{ formatTime(appointment.start_datetime) }} - {{ formatTime(appointment.end_datetime) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- New appointment modal -->
    <AppointmentFormModal
      v-model:show="showNewAppointment"
      :appointment="editingAppointment"
      :employees="employees"
      :patients="patients"
      :services="services"
      :prefilled-employee="prefilledEmployee"
      :prefilled-date-time="prefilledDateTime"
      @saved="handleAppointmentSaved"
      @search-patient="searchPatients"
      @patient-created="handlePatientCreated"
    />

    <!-- Break modal -->
    <BreakModal
      v-model:show="showBreakModal"
      :employee="selectedEmployeeForBreak"
      :employees="employees"
      @saved="handleBreakSaved"
    />

    <!-- Access Request Modal -->
    <AccessRequestModal
      :visible="showAccessRequestModal"
      @close="showAccessRequestModal = false"
      @request-completed="handleAccessRequestCompleted"
    />

    <!-- Context menu for appointments -->
    <n-dropdown
      placement="bottom-start"
      trigger="manual"
      :x="contextMenuX"
      :y="contextMenuY"
      :options="contextMenuOptions"
      :show="showContextMenu"
      :on-clickoutside="() => showContextMenu = false"
      @select="handleContextMenuSelect"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMessage } from 'naive-ui'
import apiClient from '@/api/axios'
import { format, parseISO } from 'date-fns'
import AppointmentFormModal from '@/components/AppointmentFormModal.vue'
import BreakModal from '@/components/BreakModal.vue'
import AccessRequestModal from '@/components/AccessRequestModal.vue'
import { useAuthStore } from '@/stores/auth'

const message = useMessage()
const authStore = useAuthStore()

// State
const selectedDate = ref(Date.now())
const employees = ref([])
const selectedEmployees = ref([])
const appointments = ref([])
const patients = ref([])
const rooms = ref([])
const services = ref([])
const showNewAppointment = ref(false)
const editingAppointment = ref(null)
const prefilledEmployee = ref(null)
const prefilledDateTime = ref(null)
const showBreakModal = ref(false)
const selectedEmployeeForBreak = ref(null)
const showAccessRequestModal = ref(false)
const showContextMenu = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextMenuAppointment = ref(null)
const loadingPatients = ref(false)
const saving = ref(false)
const gridRef = ref(null)
const currentTime = ref('')
const currentTimePosition = ref(0)
const viewMode = ref('day') // 'day', 'week', 'month'
const statusFilter = ref([])

// Constants
const slotHeight = 60 // 30 minutes = 60px
const workHoursStart = 9
const workHoursEnd = 20

// Time slots (09:00 - 20:00)
const timeSlots = computed(() => {
  const slots = []
  for (let hour = workHoursStart; hour <= workHoursEnd; hour++) {
    slots.push(`${hour.toString().padStart(2, '0')}:00`)
    if (hour < workHoursEnd) {
      slots.push(`${hour.toString().padStart(2, '0')}:30`)
    }
  }
  return slots
})

// Options
const employeeOptions = computed(() =>
  employees.value.map((e) => ({
    label: `${e.last_name} ${e.first_name} - ${e.position}`,
    value: e.id
  }))
)

const patientOptions = computed(() =>
  patients.value.map((p) => ({
    label: `${p.full_name} - ${p.phone}`,
    value: p.id
  }))
)

const roomOptions = computed(() =>
  rooms.value.map((r) => ({
    label: r.name,
    value: r.id
  }))
)

const statusOptions = [
  { label: 'Черновик', value: 'draft' },
  { label: 'Забронировано', value: 'booked' },
  { label: 'Подтверждено', value: 'confirmed' },
  { label: 'В процессе', value: 'in_progress' },
  { label: 'Выполнено', value: 'done' },
  { label: 'Не пришёл', value: 'no_show' },
  { label: 'Отменено', value: 'canceled' }
]

const contextMenuOptions = computed(() => [
  {
    label: 'Редактировать',
    key: 'edit',
    icon: () => '✏️'
  },
  {
    label: 'Копировать',
    key: 'copy',
    icon: () => '📋'
  },
  {
    label: 'Перенести',
    key: 'move',
    icon: () => '🔄'
  },
  {
    label: 'Отменить',
    key: 'cancel',
    icon: () => '🚫'
  },
  {
    type: 'divider',
    key: 'd1'
  },
  {
    label: 'Удалить',
    key: 'delete',
    icon: () => '🗑️'
  }
])


// Filtered employees
const filteredEmployees = computed(() => {
  if (selectedEmployees.value.length === 0) {
    return employees.value
  }
  return employees.value.filter((e) => selectedEmployees.value.includes(e.id))
})

// Functions
function toggleEmployee(employeeId) {
  const index = selectedEmployees.value.indexOf(employeeId)
  if (index === -1) {
    selectedEmployees.value.push(employeeId)
  } else {
    selectedEmployees.value.splice(index, 1)
  }
}

function getEmployeeAppointments(employeeId) {
  let filtered = appointments.value.filter((apt) => apt.employee === employeeId)
  
  // Apply status filter if any selected
  if (statusFilter.value.length > 0) {
    filtered = filtered.filter((apt) => statusFilter.value.includes(apt.status))
  }
  
  return filtered
}

function getEmployeeAppointmentCount(employeeId) {
  // Returns the count of appointments that match current filters
  return getEmployeeAppointments(employeeId).length
}

function getAppointmentStyle(appointment) {
  const start = parseISO(appointment.start_datetime)
  const end = parseISO(appointment.end_datetime)
  
  const startMinutes = start.getHours() * 60 + start.getMinutes()
  const endMinutes = end.getHours() * 60 + end.getMinutes()
  const workStartMinutes = workHoursStart * 60
  
  const top = ((startMinutes - workStartMinutes) / 30) * slotHeight
  const height = ((endMinutes - startMinutes) / 30) * slotHeight
  
  return {
    top: `${top}px`,
    height: `${height}px`,
    backgroundColor: appointment.color || '#2196F3'
  }
}

function formatTime(datetime) {
  if (!datetime) return ''
  return format(parseISO(datetime), 'HH:mm')
}

function openAppointment(appointment) {
  editingAppointment.value = appointment
  prefilledEmployee.value = null
  prefilledDateTime.value = null
  showNewAppointment.value = true
}

// Get employee menu options
function getEmployeeMenuOptions(employee) {
  return [
    {
      label: 'Расписание на неделю',
      key: `week-${employee.id}`,
      icon: () => '📅'
    },
    {
      label: 'Добавить перерыв',
      key: `break-${employee.id}`,
      icon: () => '☕'
    },
    {
      label: 'Отменить рабочий день',
      key: `cancel-day-${employee.id}`,
      icon: () => '🚫'
    },
    {
      label: 'Профиль сотрудника',
      key: `profile-${employee.id}`,
      icon: () => '👤'
    }
  ]
}

// Handle employee action from dropdown
function handleEmployeeAction(key) {
  const [action, employeeId] = key.split('-')
  const employee = employees.value.find(e => e.id === parseInt(employeeId))
  
  switch (action) {
    case 'week':
      message.info(`Показать расписание на неделю для ${employee.last_name} ${employee.first_name}`)
      viewMode.value = 'week'
      break
    case 'break':
      selectedEmployeeForBreak.value = employee
      showBreakModal.value = true
      break
    case 'cancel':
      if (confirm(`Отменить рабочий день для ${employee.last_name} ${employee.first_name}?`)) {
        message.warning('Функция отмены рабочего дня будет реализована')
        // TODO: Implement cancel day
      }
      break
    case 'profile':
      message.info(`Открыть профиль ${employee.last_name} ${employee.first_name}`)
      // TODO: Navigate to employee profile or open modal
      break
  }
}

// Handle click on empty slot in column
function handleColumnClick(event, employee) {
  const column = event.currentTarget
  const rect = column.getBoundingClientRect()
  const clickY = event.clientY - rect.top
  
  // Calculate time based on click position
  const slotIndex = Math.floor(clickY / slotHeight)
  const totalMinutes = workHoursStart * 60 + slotIndex * 30
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  
  // Create date with selected time
  const selectedDateTime = new Date(selectedDate.value)
  selectedDateTime.setHours(hours, minutes, 0, 0)
  
  // Set prefilled data for the modal
  prefilledEmployee.value = employee.id
  prefilledDateTime.value = selectedDateTime.getTime()
  editingAppointment.value = null
  
  showNewAppointment.value = true
  message.success(`Создание записи на ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`)
}

// Show context menu for appointment
function showAppointmentContextMenu(event, appointment) {
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  contextMenuAppointment.value = appointment
  showContextMenu.value = true
}

function handleContextMenuSelect(key) {
  showContextMenu.value = false
  
  if (!contextMenuAppointment.value) return
  
  switch (key) {
    case 'edit':
      openAppointment(contextMenuAppointment.value)
      break
    case 'copy':
      copyAppointment(contextMenuAppointment.value)
      break
    case 'move':
      message.info('Перетащите визит в нужное место или измените время в форме редактирования')
      openAppointment(contextMenuAppointment.value)
      break
    case 'cancel':
      cancelAppointment(contextMenuAppointment.value)
      break
    case 'delete':
      deleteAppointmentById(contextMenuAppointment.value.id)
      break
  }
}

function copyAppointment(appointment) {
  // Create a copy without ID
  prefilledEmployee.value = appointment.employee
  prefilledDateTime.value = new Date(appointment.start_datetime).getTime()
  editingAppointment.value = null
  showNewAppointment.value = true
  message.info('Создание копии визита')
}

async function cancelAppointment(appointment) {
  try {
    await apiClient.patch(`/calendar/appointments/${appointment.id}`, {
      status: 'canceled'
    })
    message.success('Визит отменен')
    await loadAppointments()
  } catch (error) {
    console.error('Error canceling appointment:', error)
    message.error('Ошибка отмены визита')
  }
}

async function deleteAppointmentById(appointmentId) {
  if (!confirm('Вы уверены, что хотите удалить этот визит?')) return
  
  try {
    await apiClient.delete(`/calendar/appointments/${appointmentId}`)
    message.success('Визит удален')
    await loadAppointments()
  } catch (error) {
    console.error('Error deleting appointment:', error)
    message.error('Ошибка удаления визита')
  }
}

async function handleBreakSaved() {
  // Reload appointments to show updated schedule
  await loadAppointments()
}

function handleAccessRequestCompleted(wasApproved) {
  if (wasApproved) {
    message.success('Доступ к медицинской карте предоставлен')
    // Reload patients to potentially include the new patient with access
    loadPatients()
  }
}

async function loadEmployees() {
  try {
    const response = await apiClient.get('/staff/employees', {
      params: { is_active: true }
    })
    employees.value = response.data.results || response.data
    
    // Select first 3 employees by default
    if (employees.value.length > 0) {
      selectedEmployees.value = employees.value.slice(0, 3).map((e) => e.id)
    }
  } catch (error) {
    console.error('Error loading employees:', error)
    message.error('Ошибка загрузки сотрудников')
  }
}

async function loadAppointments() {
  try {
    const date = new Date(selectedDate.value)
    const dateStr = format(date, 'yyyy-MM-dd')
    
    const response = await apiClient.get('/calendar/appointments', {
      params: {
        date_from: `${dateStr}T00:00:00`,
        date_to: `${dateStr}T23:59:59`
      }
    })
    appointments.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading appointments:', error)
    message.error('Ошибка загрузки записей')
  }
}

async function searchPatients(query) {
  if (!query || query.length < 2) {
    // If search is empty or too short, reload initial patients list
    await loadPatients()
    return
  }
  
  loadingPatients.value = true
  try {
    const response = await apiClient.get('/patients/patients', {
      params: { search: query }
    })
    patients.value = response.data.results || response.data
  } catch (error) {
    console.error('Error searching patients:', error)
  } finally {
    loadingPatients.value = false
  }
}

async function loadRooms() {
  try {
    const response = await apiClient.get('/org/rooms')
    rooms.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading rooms:', error)
  }
}

async function handleAppointmentSaved(appointmentData, servicesData) {
  try {
    saving.value = true
    
    if (editingAppointment.value) {
      await apiClient.patch(`/calendar/appointments/${editingAppointment.value.id}`, appointmentData)
      message.success('Запись обновлена')
    } else {
      await apiClient.post('/calendar/appointments', appointmentData)
      message.success('Запись создана')
    }
    
    await loadAppointments()
    
    // Reset prefilled data
    prefilledEmployee.value = null
    prefilledDateTime.value = null
    editingAppointment.value = null
  } catch (error) {
    console.error('Error saving appointment:', error)
    if (error.response?.data) {
      message.error('Ошибка: ' + JSON.stringify(error.response.data))
    } else {
      message.error('Ошибка сохранения записи')
    }
  } finally {
    saving.value = false
  }
}

function updateCurrentTime() {
  const now = new Date()
  currentTime.value = format(now, 'HH:mm')
  
  const minutes = now.getHours() * 60 + now.getMinutes()
  const workStartMinutes = workHoursStart * 60
  
  if (minutes >= workStartMinutes && minutes <= workHoursEnd * 60) {
    currentTimePosition.value = ((minutes - workStartMinutes) / 30) * slotHeight
  } else {
    currentTimePosition.value = 0
  }
}

// WebSocket connection
let ws = null

function connectWebSocket() {
  // Get from auth store or default to branch 1
  const branch_id = authStore.currentBranchId || 1
  
  // Use WebSocket proxy through Vite
  // In production, this will use the configured WS URL
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${wsProtocol}//${window.location.host}/ws/calendar/${branch_id}`
  
  try {
    ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('✓ WebSocket connected to', wsUrl)
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('WebSocket message:', data)
      
      if (data.type === 'appointment_created' || data.type === 'appointment_updated') {
        loadAppointments()
      } else if (data.type === 'appointment_deleted') {
        appointments.value = appointments.value.filter((a) => a.id !== data.appointment_id)
      }
    }
    
    ws.onerror = (error) => {
      console.warn('WebSocket error (will retry):', error.message || 'Connection failed')
    }
    
    ws.onclose = (event) => {
      if (event.code !== 1000) {
        // Only log if not a normal closure
        console.log('WebSocket disconnected (code:', event.code, '), reconnecting in 5s...')
        setTimeout(connectWebSocket, 5000) // Increased timeout to 5s
      }
    }
  } catch (error) {
    console.warn('WebSocket connection failed:', error.message, '- will retry in 10s')
    setTimeout(connectWebSocket, 10000)
  }
}

function disconnectWebSocket() {
  if (ws) {
    ws.close()
    ws = null
  }
}

// Lifecycle
let timeUpdateInterval = null

async function loadServices() {
  try {
    const response = await apiClient.get('/services/services')
    services.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading services:', error)
  }
}

async function loadPatients() {
  try {
    const response = await apiClient.get('/patients/patients', {
      params: { page_size: 100 }
    })
    patients.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading patients:', error)
  }
}

function handlePatientCreated(newPatient) {
  // Add the newly created patient to the patients list
  patients.value.unshift(newPatient)
  message.success(`Пациент ${newPatient.full_name} добавлен`)
}

function scrollToTop() {
  if (gridRef.value) {
    gridRef.value.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function scrollToCurrentTime() {
  const now = new Date()
  const currentHour = now.getHours()
  
  if (currentHour >= workHoursStart && currentHour <= workHoursEnd) {
    const scrollToHour = Math.max(workHoursStart, currentHour - 1)
    const slotsBeforeTarget = (scrollToHour - workHoursStart) * 2
    const scrollPosition = slotsBeforeTarget * slotHeight
    
    if (gridRef.value) {
      gridRef.value.scrollTo({ top: scrollPosition, behavior: 'smooth' })
    }
  }
}

onMounted(async () => {
  await Promise.all([
    loadEmployees(),
    loadAppointments(),
    loadRooms(),
    loadServices(),
    loadPatients()
  ])
  
  updateCurrentTime()
  timeUpdateInterval = setInterval(updateCurrentTime, 60000) // Update every minute
  
  connectWebSocket()
  
  // Scroll to current time or start of day
  setTimeout(() => {
    const now = new Date()
    const currentHour = now.getHours()
    
    // If within working hours, scroll to 1 hour before current time
    if (currentHour >= workHoursStart && currentHour <= workHoursEnd) {
      const scrollToHour = Math.max(workHoursStart, currentHour - 1)
      const slotsBeforeTarget = (scrollToHour - workHoursStart) * 2 // 2 slots per hour
      const scrollPosition = slotsBeforeTarget * slotHeight
      
      if (gridRef.value) {
        gridRef.value.scrollTop = scrollPosition
      }
    } else {
      // Outside working hours, scroll to top
      if (gridRef.value) {
        gridRef.value.scrollTop = 0
      }
    }
  }, 100) // Small delay to ensure DOM is ready
})

onUnmounted(() => {
  if (timeUpdateInterval) {
    clearInterval(timeUpdateInterval)
  }
  disconnectWebSocket()
})
</script>

<style scoped lang="scss">
@import '@/styles/tokens.scss';

// Dark theme overrides
$bg-primary: #121212;
$bg-secondary: #1e1e1e;
$bg-tertiary: #2d2d2d;
$text-primary: #e0e0e0;
$text-secondary: #999999;
$border-color: #333333;
$primary-color: #18a058;

.schedule-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: $bg-primary;
  color: $text-primary;
}

.schedule-header {
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

.header-left {
  display: flex;
  gap: $spacing-lg;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: $spacing-md;
  align-items: center;
}

.schedule-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.employees-header {
  display: flex;
  background: $bg-secondary;
  border-bottom: 2px solid $border-color;
  padding: $spacing-md;
  gap: $spacing-sm;
}

.time-column-header {
  width: 80px;
  flex-shrink: 0;
}

.employee-header {
  flex: 1;
  min-width: 250px;
  padding: $spacing-md;
  border-radius: $radius-md;
  background: $bg-tertiary;
  cursor: pointer;
  transition: all $transition-fast;
  display: flex;
  gap: $spacing-md;
  align-items: center;
  position: relative;
  
  &:hover {
    background: rgba(24, 160, 88, 0.2);
  }
  
  &.active {
    background: rgba(24, 160, 88, 0.3);
    border: 2px solid $primary-color;
  }
}

.employee-menu-icon {
  margin-left: auto;
  opacity: 0.6;
  transition: opacity $transition-fast;
  
  &:hover {
    opacity: 1;
  }
}

.employee-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.employee-info {
  flex: 1;
  min-width: 0;
}

.employee-name {
  font-weight: 600;
  font-size: 14px;
  color: $text-primary;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.employee-count {
  font-size: 16px;
  font-weight: 700;
  color: $text-primary;
  text-align: center;
  margin-top: 4px;
}

.employee-position {
  font-size: 12px;
  color: $text-secondary;
  text-transform: uppercase;
}

.schedule-grid {
  flex: 1;
  overflow: auto;
  position: relative;
  display: flex;
  gap: $spacing-sm;
  padding: $spacing-md;
  background: $bg-primary;
}

.time-column {
  width: 80px;
  flex-shrink: 0;
  position: sticky;
  left: 0;
  background: $bg-primary;
  z-index: 10;
}

.time-slot {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  font-size: 12px;
  color: $text-secondary;
  border-top: 1px solid $border-color;
  padding-top: 4px;
}

.employee-column {
  flex: 1;
  min-width: 250px;
  position: relative;
  border-left: 1px solid $border-color;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: repeating-linear-gradient(
      to bottom,
      $border-color 0px,
      $border-color 1px,
      transparent 1px,
      transparent 60px
    );
    pointer-events: none;
  }
}

.appointment-block {
  position: absolute;
  left: 4px;
  right: 4px;
  border-radius: $radius-md;
  border: 2px solid transparent;
  padding: $spacing-sm;
  cursor: pointer;
  transition: all $transition-fast;
  overflow: hidden;
  box-shadow: $shadow-sm;
  
  &.has-visit {
    border-left-width: 4px;
    border-left-style: solid;
    border-left-color: #4CAF50;
  }
  
  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }
}

// Visit indicator badge
.visit-indicator {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  z-index: 2;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  
  &.visit-completed {
    background: #4CAF50;
  }
  
  &.visit-in_progress {
    background: #FF9800;
  }
  
  &.visit-draft {
    background: #2196F3;
  }
  
  &.visit-canceled {
    background: #f44336;
  }
}

.status-draft {
  background: rgba(158, 158, 158, 0.2);
  border-left: 4px solid #9E9E9E;
}

.status-booked {
  background: rgba(33, 150, 243, 0.2);
  border-left: 4px solid #2196F3;
}

.status-confirmed {
  background: rgba(0, 194, 168, 0.2);
  border-left: 4px solid #00C2A8;
}

.status-in_progress {
  background: rgba(255, 152, 0, 0.2);
  border-left: 4px solid #FF9800;
}

.status-done {
  background: rgba(76, 175, 80, 0.2);
  border-left: 4px solid #4CAF50;
}

.status-no_show {
  background: rgba(244, 67, 54, 0.2);
  border-left: 4px solid #F44336;
}

.status-canceled {
  background: rgba(255, 205, 210, 0.2);
  border-left: 4px solid #FFCDD2;
}

.appointment-patient {
  font-weight: 600;
  font-size: 13px;
  color: $text-primary;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.appointment-phone {
  font-size: 11px;
  color: $text-secondary;
  margin-bottom: 4px;
}

.appointment-time {
  font-size: 11px;
  color: $text-secondary;
  font-weight: 500;
}

.current-time-line {
  position: absolute;
  left: 80px;
  right: 0;
  height: 2px;
  background: $status-no-show;
  z-index: 20;
  pointer-events: none;
  
  &::before {
    content: '';
    position: absolute;
    left: -6px;
    top: -4px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: $status-no-show;
  }
}

.current-time-label {
  position: absolute;
  left: -70px;
  top: -8px;
  font-size: 12px;
  font-weight: 600;
  color: $status-no-show;
  background: $bg-primary;
  padding: 2px 4px;
  border-radius: $radius-sm;
}

/* Dark theme for components */
:deep(.n-button-group .n-button) {
  background-color: $bg-tertiary;
  border-color: $border-color;
  color: $text-primary;
  
  &:hover {
    background-color: lighten($bg-tertiary, 5%);
  }
}

:deep(.n-button-group .n-button--primary-type) {
  background-color: $primary-color;
  border-color: $primary-color;
  color: white;
}

:deep(.n-select) {
  background-color: $bg-tertiary;
}

:deep(.n-base-selection) {
  background-color: $bg-tertiary !important;
  border-color: $border-color !important;
}

:deep(.n-base-selection-label) {
  color: $text-primary !important;
}

:deep(.n-base-selection:hover) {
  border-color: lighten($border-color, 10%) !important;
}

:deep(.n-base-selection--active) {
  border-color: $primary-color !important;
}

:deep(.n-input) {
  background-color: $bg-tertiary;
  border-color: $border-color;
  color: $text-primary;
}

:deep(.n-input__input-el) {
  color: $text-primary;
}

:deep(.n-date-picker) {
  background-color: $bg-tertiary;
}

:deep(.n-checkbox) {
  color: $text-primary;
}

:deep(.n-card) {
  background-color: $bg-secondary;
  color: $text-primary;
}

:deep(.n-card__content) {
  color: $text-primary;
}

:deep(.n-modal) {
  background-color: $bg-secondary;
}

:deep(.n-form-item-label) {
  color: $text-primary;
}

:deep(.n-dropdown-menu) {
  background-color: $bg-tertiary;
  border-color: $border-color;
}

:deep(.n-dropdown-option) {
  color: $text-primary;
  
  &:hover {
    background-color: lighten($bg-tertiary, 5%);
  }
}

:deep(.n-scrollbar-rail) {
  background-color: $bg-tertiary;
}

:deep(.n-scrollbar-content) {
  color: $text-primary;
}
</style>
