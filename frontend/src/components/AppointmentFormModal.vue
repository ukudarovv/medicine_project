<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    :title="title"
    style="width: 95%; max-width: 1400px"
    :segmented="{ content: 'soft' }"
  >
    <n-scrollbar style="max-height: 80vh">
      <!-- Header info -->
      <div class="appointment-header">
        <div class="appointment-info">
          <span class="appointment-datetime">
            {{ formattedDateTime }}
          </span>
          <span class="appointment-employee">{{ employeeName }}</span>
          <n-tag :type="getStatusType(formData.status)" size="small">
            {{ getStatusLabel(formData.status) }}
          </n-tag>
        </div>
        <div class="appointment-actions-top">
          <n-select
            v-model:value="formData.status"
            :options="statusOptions"
            style="width: 200px"
          />
          <n-checkbox v-model:checked="formData.is_primary">
            Первичный
          </n-checkbox>
        </div>
      </div>

      <n-divider />

      <!-- Action buttons -->
      <n-space style="margin-bottom: 16px">
        <n-button text type="primary">
          💬 Комментарий к визиту
        </n-button>
        <n-button text type="primary">
          📎 Добавить вложение
        </n-button>
      </n-space>

      <n-grid :cols="3" :x-gap="16">
        <!-- Left column - Patient info -->
        <n-grid-item :span="2">
          <n-card title="Информация о пациенте" :bordered="false" size="small">
            <n-space vertical size="large">
              <!-- Patient selection or creation -->
              <n-form-item label="Пациент">
                <n-select
                  v-model:value="formData.patient"
                  :options="patientOptions"
                  placeholder="Выберите пациента или создайте нового"
                  filterable
                  clearable
                  :loading="loadingPatients"
                  @search="onSearchPatient"
                >
                  <template #action>
                    <n-button text type="primary" @click="showCreatePatient = true">
                      + Создать нового пациента
                    </n-button>
                  </template>
                </n-select>
              </n-form-item>

              <!-- Patient quick form (if creating new) -->
              <template v-if="showCreatePatient">
                <n-alert type="info" size="small" style="margin-bottom: 12px">
                  Создание нового пациента
                </n-alert>
                
                <n-grid :cols="3" :x-gap="12">
                  <n-grid-item>
                    <n-form-item label="Фамилия">
                      <n-input v-model:value="patientData.last_name" placeholder="Фамилия" />
                    </n-form-item>
                  </n-grid-item>
                  <n-grid-item>
                    <n-form-item label="Имя">
                      <n-input v-model:value="patientData.first_name" placeholder="Имя" />
                    </n-form-item>
                  </n-grid-item>
                  <n-grid-item>
                    <n-form-item label="Отчество">
                      <n-input v-model:value="patientData.middle_name" placeholder="Отчество" />
                    </n-form-item>
                  </n-grid-item>
                </n-grid>

                <n-grid :cols="2" :x-gap="12">
                  <n-grid-item>
                    <n-form-item label="Телефон">
                      <n-input v-model:value="patientData.phone" placeholder="+7 (XXX) XXX-XX-XX" />
                    </n-form-item>
                  </n-grid-item>
                  <n-grid-item>
                    <n-form-item label="Доп. телефон">
                      <n-input v-model:value="patientData.phone_additional" placeholder="+7" />
                    </n-form-item>
                  </n-grid-item>
                </n-grid>

                <n-form-item label="Дата рождения">
                  <n-date-picker
                    v-model:value="patientData.birth_date"
                    type="date"
                    placeholder="дд.мм.гггг"
                    style="width: 100%"
                  />
                </n-form-item>

                <n-space>
                  <n-button text type="primary">
                    + Добавить представителя
                  </n-button>
                </n-space>

                <n-alert v-if="!patientData.medical_card" type="warning" size="small">
                  Мед. карта - номер не указан
                </n-alert>

                <n-space>
                  <n-checkbox v-model:checked="patientData.category">
                    Категория
                  </n-checkbox>
                  <n-checkbox v-model:checked="patientData.add_note">
                    Добавить примечание о пациенте
                  </n-checkbox>
                </n-space>
                
                <n-space style="margin-top: 12px">
                  <n-button type="primary" @click="createQuickPatient">
                    ✓ Создать пациента
                  </n-button>
                  <n-button @click="showCreatePatient = false">
                    Отмена
                  </n-button>
                </n-space>
              </template>
            </n-space>
          </n-card>

          <!-- Services and Products -->
          <n-card title="Услуги и товары" :bordered="false" size="small" style="margin-top: 16px">
            <template #header-extra>
              <n-space>
                <n-button size="small">Добавить</n-button>
                <n-button type="primary" size="small" @click="showServiceSelector = true">
                  Услугу
                </n-button>
                <n-button size="small">Товар</n-button>
                <n-button size="small" secondary>🏷️</n-button>
                <n-button size="small" secondary>📋</n-button>
              </n-space>
            </template>

            <!-- Services list -->
            <n-data-table
              v-if="selectedServices.length > 0"
              :columns="serviceColumns"
              :data="selectedServices"
              :pagination="false"
              size="small"
              style="margin-bottom: 16px"
            />
            <n-empty v-else description="Услуги не добавлены" size="small" />

            <!-- Summary -->
            <n-space justify="space-between" style="margin-top: 16px">
              <n-space>
                <n-button text type="primary">
                  💊 Рецепты
                </n-button>
                <n-button text type="primary">
                  ⚙️ Настроить
                </n-button>
              </n-space>
              <n-space>
                <n-text>Скидка: {{ totalDiscount }}%</n-text>
                <n-text strong>Итого: {{ totalAmount }} ₸</n-text>
              </n-space>
            </n-space>
          </n-card>

          <!-- Resources -->
          <n-card title="Ресурсы" :bordered="false" size="small" style="margin-top: 16px">
            <template #header-extra>
              <n-button type="primary" size="small">
                + Добавить
              </n-button>
            </template>
            <n-empty v-if="resources.length === 0" description="Ресурсы не добавлены" size="small" />
            <n-list v-else>
              <n-list-item v-for="(resource, idx) in resources" :key="idx">
                {{ resource.name }}
              </n-list-item>
            </n-list>
          </n-card>

          <!-- Patient arrived button -->
          <div style="margin-top: 24px; text-align: center">
            <n-button
              type="success"
              size="large"
              style="width: 100%; height: 60px; font-size: 18px; font-weight: bold"
              @click="markPatientArrived"
            >
              ПАЦИЕНТ ПРИШЕЛ
            </n-button>
          </div>
        </n-grid-item>

        <!-- Right column - Financial summary -->
        <n-grid-item>
          <n-card title="Финансы" :bordered="false" size="small">
            <n-space vertical>
              <div class="finance-item">
                <n-text depth="3">БАЛАНС</n-text>
                <n-text strong>{{ patientBalance }} ₸</n-text>
              </div>
              <n-divider style="margin: 8px 0" />
              <div class="finance-item">
                <n-text depth="3">СКИДКА</n-text>
                <n-text strong>{{ patientDiscount }}%</n-text>
              </div>
              <n-divider style="margin: 8px 0" />
              <div class="finance-item">
                <n-text depth="3">визитов</n-text>
                <n-text strong>{{ patientVisitsCount }}</n-text>
              </div>
              <n-divider style="margin: 8px 0" />
              <div class="finance-item">
                <n-text depth="3">СРЕДНИЙ ЧЕК</n-text>
                <n-text strong>{{ patientAvgCheck }} ₸</n-text>
              </div>
            </n-space>
          </n-card>
        </n-grid-item>
      </n-grid>
    </n-scrollbar>

    <template #footer>
      <n-space justify="space-between" style="width: 100%">
        <n-space>
          <n-dropdown :options="printOptions" @select="handlePrint">
            <n-button>
              🖨️ Печать
              <template #icon-right>
                <n-icon>▼</n-icon>
              </template>
            </n-button>
          </n-dropdown>
          <n-text depth="3">Автор: {{ authorName }}</n-text>
        </n-space>
        <n-space>
          <n-button @click="handleClose">Отмена</n-button>
          <n-button type="warning" @click="handleSave(false)" :loading="saving">
            Сохранить
          </n-button>
          <n-button type="primary" @click="handleSave(true)" :loading="saving">
            Сохранить и закрыть
          </n-button>
        </n-space>
      </n-space>
    </template>

    <!-- Service selector modal -->
    <n-modal v-model:show="showServiceSelector" preset="card" title="Выбрать услугу" style="width: 800px">
      <n-input
        v-model:value="serviceSearch"
        placeholder="Поиск услуги..."
        clearable
        style="margin-bottom: 16px"
      >
        <template #prefix>🔍</template>
      </n-input>
      
      <n-data-table
        :columns="serviceSelectorColumns"
        :data="filteredAvailableServices"
        :max-height="400"
        :pagination="{ pageSize: 10 }"
        size="small"
      />
    </n-modal>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch, h } from 'vue'
import { useMessage, NButton, NInputNumber } from 'naive-ui'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  show: Boolean,
  appointment: {
    type: Object,
    default: null
  },
  employees: {
    type: Array,
    default: () => []
  },
  patients: {
    type: Array,
    default: () => []
  },
  services: {
    type: Array,
    default: () => []
  },
  prefilledEmployee: Number,
  prefilledDateTime: Number
})

const emit = defineEmits(['update:show', 'saved', 'search-patient'])

const message = useMessage()
const authStore = useAuthStore()
const saving = ref(false)
const loadingPatients = ref(false)
const showCreatePatient = ref(false)
const showServiceSelector = ref(false)
const serviceSearch = ref('')

const visible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

const isEdit = computed(() => !!props.appointment)
const title = computed(() => isEdit.value ? 'Редактировать визит' : 'Новый визит')

// Form data
const formData = ref({
  employee: null,
  patient: null,
  start_datetime: null,
  end_datetime: null,
  room: null,
  status: 'booked',
  is_primary: true,
  note: '',
  source: 'admin'
})

const patientData = ref({
  last_name: '',
  first_name: '',
  middle_name: '',
  phone: '',
  phone_additional: '',
  birth_date: null,
  medical_card: '',
  category: false,
  add_note: false
})

const selectedServices = ref([])
const resources = ref([])

// Computed
const formattedDateTime = computed(() => {
  if (!formData.value.start_datetime) return 'Не выбрано'
  
  const date = new Date(formData.value.start_datetime)
  const duration = formData.value.end_datetime 
    ? Math.round((new Date(formData.value.end_datetime) - date) / 60000) 
    : 30
    
  return format(date, 'd MMMM, EEEE HH:mm', { locale: ru }) + `, ${duration} минут`
})

const employeeName = computed(() => {
  if (!formData.value.employee) return ''
  const emp = props.employees.find(e => e.id === formData.value.employee)
  return emp ? `${emp.last_name} ${emp.first_name?.[0]}.` : ''
})

const authorName = computed(() => {
  return authStore.user ? `${authStore.user.last_name} ${authStore.user.first_name}` : ''
})

const patientOptions = computed(() =>
  props.patients.map((p) => ({
    label: `${p.last_name} ${p.first_name} - ${p.phone}`,
    value: p.id
  }))
)

const patientBalance = computed(() => {
  if (!formData.value.patient) return 0
  const patient = props.patients.find(p => p.id === formData.value.patient)
  return patient?.balance || 0
})

const patientDiscount = computed(() => {
  if (!formData.value.patient) return 0
  const patient = props.patients.find(p => p.id === formData.value.patient)
  return patient?.discount_percent || 0
})

const patientVisitsCount = computed(() => {
  // TODO: Get from patient history
  return 0
})

const patientAvgCheck = computed(() => {
  // TODO: Calculate from patient history
  return 0
})

const totalDiscount = computed(() => {
  return patientDiscount.value
})

const totalAmount = computed(() => {
  const sum = selectedServices.value.reduce((acc, s) => acc + (s.price * s.quantity), 0)
  return sum * (1 - totalDiscount.value / 100)
})

const statusOptions = [
  { label: 'Не подтвержден', value: 'draft' },
  { label: 'Забронировано', value: 'booked' },
  { label: 'Подтверждено', value: 'confirmed' },
  { label: 'Пациент пришел', value: 'in_progress' },
  { label: 'Выполнено', value: 'done' },
  { label: 'Не пришёл', value: 'no_show' },
  { label: 'Отменено', value: 'canceled' }
]

const printOptions = [
  { label: 'Печать визита', key: 'visit' },
  { label: 'Печать чека', key: 'receipt' },
  { label: 'Печать медицинской карты', key: 'medical_card' }
]

// Service selector
const filteredAvailableServices = computed(() => {
  if (!serviceSearch.value) return props.services
  
  const query = serviceSearch.value.toLowerCase()
  return props.services.filter(s => 
    s.name.toLowerCase().includes(query) || 
    (s.code && s.code.toLowerCase().includes(query))
  )
})

const serviceColumns = [
  {
    title: 'Код',
    key: 'code',
    width: 100
  },
  {
    title: 'Наименование',
    key: 'name'
  },
  {
    title: 'Количество',
    key: 'quantity',
    width: 120,
    render: (row, index) => {
      return h(NInputNumber, {
        value: row.quantity,
        min: 1,
        size: 'small',
        'onUpdate:value': (value) => {
          selectedServices.value[index].quantity = value
        }
      })
    }
  },
  {
    title: 'Цена',
    key: 'price',
    width: 100,
    render: (row) => `${row.price} ₸`
  },
  {
    title: 'Сумма',
    key: 'total',
    width: 100,
    render: (row) => `${row.price * row.quantity} ₸`
  },
  {
    title: '',
    key: 'actions',
    width: 60,
    render: (row, index) => {
      return h(NButton, {
        size: 'small',
        type: 'error',
        secondary: true,
        onClick: () => removeService(index)
      }, { default: () => '🗑️' })
    }
  }
]

const serviceSelectorColumns = [
  {
    title: 'Код',
    key: 'code',
    width: 100
  },
  {
    title: 'Наименование',
    key: 'name'
  },
  {
    title: 'Цена',
    key: 'base_price',
    width: 120,
    render: (row) => `${row.base_price} ₸`
  },
  {
    title: '',
    key: 'actions',
    width: 100,
    render: (row) => {
      return h(NButton, {
        size: 'small',
        type: 'primary',
        onClick: () => addService(row)
      }, { default: () => 'Добавить' })
    }
  }
]

// Functions
function getStatusType(status) {
  const types = {
    draft: 'default',
    booked: 'info',
    confirmed: 'success',
    in_progress: 'warning',
    done: 'success',
    no_show: 'error',
    canceled: 'error'
  }
  return types[status] || 'default'
}

function getStatusLabel(status) {
  const option = statusOptions.find(o => o.value === status)
  return option?.label || status
}

async function onSearchPatient(query) {
  emit('search-patient', query)
}

async function createQuickPatient() {
  // Validate patient data
  if (!patientData.value.last_name || !patientData.value.first_name || !patientData.value.phone) {
    message.error('Заполните обязательные поля: Фамилия, Имя, Телефон')
    return
  }
  
  try {
    const apiClient = (await import('@/api/axios')).default
    
    const newPatientData = {
      organization: authStore.user?.organization,
      last_name: patientData.value.last_name,
      first_name: patientData.value.first_name,
      middle_name: patientData.value.middle_name,
      phone: patientData.value.phone,
      birth_date: patientData.value.birth_date 
        ? new Date(patientData.value.birth_date).toISOString().split('T')[0] 
        : null,
      sex: 'M', // Default
      email: '',
      address: ''
    }
    
    const response = await apiClient.post('/patients/patients', newPatientData)
    
    // Set the newly created patient as selected
    formData.value.patient = response.data.id
    showCreatePatient.value = false
    
    message.success('Пациент создан и выбран')
    
    // Clear patient form
    patientData.value = {
      last_name: '',
      first_name: '',
      middle_name: '',
      phone: '',
      phone_additional: '',
      birth_date: null,
      medical_card: '',
      category: false,
      add_note: false
    }
  } catch (error) {
    console.error('Error creating patient:', error)
    message.error('Ошибка создания пациента')
  }
}

function addService(service) {
  const exists = selectedServices.value.find(s => s.id === service.id)
  if (exists) {
    exists.quantity += 1
    message.info('Количество увеличено')
  } else {
    selectedServices.value.push({
      id: service.id,
      code: service.code,
      name: service.name,
      price: service.base_price,
      quantity: 1
    })
    message.success('Услуга добавлена')
  }
  showServiceSelector.value = false
}

function removeService(index) {
  selectedServices.value.splice(index, 1)
}

function markPatientArrived() {
  formData.value.status = 'in_progress'
  message.success('Статус изменен: Пациент пришел')
}

function handlePrint(key) {
  message.info(`Печать: ${key}`)
}

function handleClose() {
  visible.value = false
  resetForm()
}

function resetForm() {
  formData.value = {
    employee: null,
    patient: null,
    start_datetime: null,
    end_datetime: null,
    room: null,
    status: 'booked',
    is_primary: true,
    note: '',
    source: 'admin'
  }
  patientData.value = {
    last_name: '',
    first_name: '',
    middle_name: '',
    phone: '',
    phone_additional: '',
    birth_date: null,
    medical_card: '',
    category: false,
    add_note: false
  }
  selectedServices.value = []
  resources.value = []
  showCreatePatient.value = false
}

async function handleSave(closeAfter = false) {
  try {
    saving.value = true

    const data = {
      branch: 1,
      employee: formData.value.employee,
      patient: formData.value.patient,
      start_datetime: new Date(formData.value.start_datetime).toISOString(),
      end_datetime: new Date(formData.value.end_datetime).toISOString(),
      room: formData.value.room,
      status: formData.value.status,
      is_primary: formData.value.is_primary,
      note: formData.value.note,
      source: formData.value.source
    }

    emit('saved', data, selectedServices.value)
    message.success(isEdit.value ? 'Визит обновлен' : 'Визит создан')

    if (closeAfter) {
      handleClose()
    }
  } catch (error) {
    console.error('Error saving appointment:', error)
    message.error('Ошибка сохранения визита')
  } finally {
    saving.value = false
  }
}

// Watch for prefilled data
watch(
  () => [props.prefilledEmployee, props.prefilledDateTime],
  ([employee, datetime]) => {
    if (employee) {
      formData.value.employee = employee
    }
    if (datetime) {
      formData.value.start_datetime = datetime
      // Set end time 30 minutes later
      const end = new Date(datetime)
      end.setMinutes(end.getMinutes() + 30)
      formData.value.end_datetime = end.getTime()
    }
  },
  { immediate: true }
)

watch(
  () => props.appointment,
  (newVal) => {
    if (newVal) {
      formData.value = {
        employee: newVal.employee,
        patient: newVal.patient,
        start_datetime: new Date(newVal.start_datetime).getTime(),
        end_datetime: new Date(newVal.end_datetime).getTime(),
        room: newVal.room,
        status: newVal.status,
        is_primary: newVal.is_primary || false,
        note: newVal.note || '',
        source: newVal.source || 'admin'
      }
    }
  },
  { immediate: true }
)
</script>

<style scoped lang="scss">
.appointment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  margin-bottom: 16px;
}

.appointment-info {
  display: flex;
  gap: 16px;
  align-items: center;
}

.appointment-datetime {
  font-size: 16px;
  font-weight: 600;
}

.appointment-employee {
  color: #666;
}

.appointment-actions-top {
  display: flex;
  gap: 12px;
  align-items: center;
}

.finance-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

