<template>
  <div class="schedule-page">
    <div class="schedule-header">
      <h1>Расписание</h1>
      <div class="header-actions">
        <n-date-picker v-model:value="selectedDate" type="date" clearable />
        <n-button type="primary" @click="showNewAppointment = true">
          + Новый визит
        </n-button>
      </div>
    </div>

    <div class="schedule-content">
      <!-- Employee tabs/columns header -->
      <div class="employees-header">
        <div class="time-column-header"></div>
        <div
          v-for="employee in employees"
          :key="employee.id"
          class="employee-header"
          :class="{ active: selectedEmployees.includes(employee.id) }"
          @click="toggleEmployee(employee.id)"
        >
          <div class="employee-avatar" :style="{ backgroundColor: employee.color }">
            {{ employee.first_name?.[0] || '' }}{{ employee.last_name?.[0] || '' }}
          </div>
          <div class="employee-info">
            <div class="employee-name">{{ employee.last_name }} {{ employee.first_name }}</div>
            <div class="employee-position">{{ employee.position }}</div>
          </div>
        </div>
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
        >
          <!-- Appointment blocks -->
          <div
            v-for="appointment in getEmployeeAppointments(employee.id)"
            :key="appointment.id"
            class="appointment-block"
            :class="`status-${appointment.status}`"
            :style="getAppointmentStyle(appointment)"
            @click="openAppointment(appointment)"
          >
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
    <n-modal v-model:show="showNewAppointment" preset="card" title="Новый визит" style="width: 900px">
      <n-form ref="formRef" :model="appointmentForm">
        <n-form-item label="Сотрудник" path="employee">
          <n-select
            v-model:value="appointmentForm.employee"
            :options="employeeOptions"
            placeholder="Выберите сотрудника"
          />
        </n-form-item>
        
        <n-form-item label="Пациент" path="patient">
          <n-select
            v-model:value="appointmentForm.patient"
            :options="patientOptions"
            filterable
            placeholder="Выберите пациента"
            :loading="loadingPatients"
            @search="searchPatients"
          />
        </n-form-item>

        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item label="Дата и время начала" path="start_datetime">
              <n-date-picker
                v-model:value="appointmentForm.start_datetime"
                type="datetime"
                clearable
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Дата и время окончания" path="end_datetime">
              <n-date-picker
                v-model:value="appointmentForm.end_datetime"
                type="datetime"
                clearable
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-form-item label="Кабинет" path="room">
          <n-select
            v-model:value="appointmentForm.room"
            :options="roomOptions"
            placeholder="Выберите кабинет"
            clearable
          />
        </n-form-item>

        <n-form-item label="Статус" path="status">
          <n-select
            v-model:value="appointmentForm.status"
            :options="statusOptions"
            placeholder="Выберите статус"
          />
        </n-form-item>

        <n-form-item>
          <n-checkbox v-model:checked="appointmentForm.is_primary">
            Первичный приём
          </n-checkbox>
        </n-form-item>

        <n-form-item label="Примечание" path="note">
          <n-input
            v-model:value="appointmentForm.note"
            type="textarea"
            :rows="3"
            placeholder="Примечание к записи"
          />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showNewAppointment = false">Отмена</n-button>
          <n-button type="primary" @click="createAppointment" :loading="saving">
            Сохранить
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMessage } from 'naive-ui'
import apiClient from '@/api/axios'
import { format, parseISO } from 'date-fns'

const message = useMessage()

// State
const selectedDate = ref(Date.now())
const employees = ref([])
const selectedEmployees = ref([])
const appointments = ref([])
const patients = ref([])
const rooms = ref([])
const showNewAppointment = ref(false)
const loadingPatients = ref(false)
const saving = ref(false)
const gridRef = ref(null)
const currentTime = ref('')
const currentTimePosition = ref(0)

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

// Appointment form
const appointmentForm = ref({
  employee: null,
  patient: null,
  start_datetime: null,
  end_datetime: null,
  room: null,
  status: 'booked',
  is_primary: false,
  note: ''
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
  return appointments.value.filter((apt) => apt.employee === employeeId)
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
  message.info(`Открыть визит: ${appointment.patient_name}`)
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
  if (!query) return
  
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

async function createAppointment() {
  try {
    saving.value = true
    
    const data = {
      branch: 1, // TODO: get from auth store
      employee: appointmentForm.value.employee,
      patient: appointmentForm.value.patient,
      start_datetime: new Date(appointmentForm.value.start_datetime).toISOString(),
      end_datetime: new Date(appointmentForm.value.end_datetime).toISOString(),
      room: appointmentForm.value.room,
      status: appointmentForm.value.status,
      is_primary: appointmentForm.value.is_primary,
      note: appointmentForm.value.note
    }
    
    await apiClient.post('/calendar/appointments', data)
    
    message.success('Запись создана')
    showNewAppointment.value = false
    await loadAppointments()
  } catch (error) {
    console.error('Error creating appointment:', error)
    if (error.response?.data) {
      message.error('Ошибка: ' + JSON.stringify(error.response.data))
    } else {
      message.error('Ошибка создания записи')
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
  const branch_id = 1 // TODO: get from auth store
  ws = new WebSocket(`ws://localhost:8001/ws/calendar/${branch_id}`)
  
  ws.onopen = () => {
    console.log('WebSocket connected')
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
    console.error('WebSocket error:', error)
  }
  
  ws.onclose = () => {
    console.log('WebSocket disconnected, reconnecting in 3s...')
    setTimeout(connectWebSocket, 3000)
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

onMounted(async () => {
  await loadEmployees()
  await loadAppointments()
  await loadRooms()
  
  updateCurrentTime()
  timeUpdateInterval = setInterval(updateCurrentTime, 60000) // Update every minute
  
  connectWebSocket()
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

.schedule-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: $bg-primary;
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
  
  &:hover {
    background: rgba(255, 106, 61, 0.1);
  }
  
  &.active {
    background: rgba(255, 106, 61, 0.2);
    border: 2px solid $primary-color;
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
  padding: $spacing-sm;
  cursor: pointer;
  transition: all $transition-fast;
  overflow: hidden;
  box-shadow: $shadow-sm;
  
  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-2px);
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
</style>
