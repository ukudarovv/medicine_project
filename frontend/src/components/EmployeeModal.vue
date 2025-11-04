<template>
  <n-modal
    v-model:show="visible"
    :title="isEdit ? 'Редактировать сотрудника' : 'Новый сотрудник'"
    preset="card"
    style="width: 900px"
    :segmented="{ content: 'soft' }"
  >
    <!-- Sub-modals -->
    <EmployeeServicesModal
      v-model:show="showServicesModal"
      :employee-id="formData.id"
      @saved="onServicesSaved"
    />
    <n-scrollbar style="max-height: 70vh">
      <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
        <!-- Основная информация -->
        <n-divider title-placement="left">Основная информация</n-divider>
        
        <n-grid :cols="3" :x-gap="12">
          <n-grid-item>
            <n-form-item label="Фамилия" path="last_name">
              <n-input v-model:value="formData.last_name" placeholder="Введите фамилию" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Имя" path="first_name">
              <n-input v-model:value="formData.first_name" placeholder="Введите имя" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Отчество" path="middle_name">
              <n-input v-model:value="formData.middle_name" placeholder="Введите отчество" />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <!-- Должность -->
        <n-divider title-placement="left">Должность</n-divider>
        
        <n-form-item label="Должность" path="position">
          <n-input v-model:value="formData.position" placeholder="Введите должность (например, Врач-стоматолог)" />
        </n-form-item>

        <n-form-item label="Специализация" path="specialization">
          <n-input v-model:value="formData.specialization" placeholder="Специализация" />
        </n-form-item>

        <!-- Трудоустройство -->
        <n-divider title-placement="left">Трудоустройство</n-divider>
        
        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item label="Дата приёма" path="hire_date">
              <n-date-picker
                v-model:value="formData.hire_date"
                type="date"
                placeholder="Выберите дату"
                style="width: 100%"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item>
              <n-checkbox v-model:checked="formData.is_fired">
                Уволен(а)
              </n-checkbox>
            </n-form-item>
            <n-form-item v-if="formData.is_fired" label="Дата увольнения" path="fire_date">
              <n-date-picker
                v-model:value="formData.fire_date"
                type="date"
                placeholder="Выберите дату"
                style="width: 100%"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <!-- Документы -->
        <n-divider title-placement="left">Документы</n-divider>
        
        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item label="ИИН" path="iin">
              <n-input v-model:value="formData.iin" placeholder="Введите ИИН" />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-grid :cols="3" :x-gap="12">
          <n-grid-item>
            <n-form-item label="Серия паспорта" path="passport_series">
              <n-input v-model:value="formData.passport_series" placeholder="Серия" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Номер паспорта" path="passport_number">
              <n-input v-model:value="formData.passport_number" placeholder="Номер" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Дата выдачи" path="passport_issued_date">
              <n-date-picker
                v-model:value="formData.passport_issued_date"
                type="date"
                placeholder="Дата"
                style="width: 100%"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-form-item label="Кем выдан" path="passport_issued_by">
          <n-input v-model:value="formData.passport_issued_by" placeholder="Орган выдачи" />
        </n-form-item>

        <!-- Контакты -->
        <n-divider title-placement="left">Контакты</n-divider>
        
        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item label="Телефон" path="phone">
              <n-input v-model:value="formData.phone" placeholder="+7 (XXX) XXX-XX-XX" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="E-mail" path="email">
              <n-input v-model:value="formData.email" placeholder="email@example.com" />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <!-- Финансы -->
        <n-divider title-placement="left">Финансы</n-divider>
        
        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item label="Процент комиссии, %" path="commission_percent">
              <n-input-number
                v-model:value="formData.commission_percent"
                :min="0"
                :max="100"
                placeholder="0"
                style="width: 100%"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Оклад, ₸" path="salary">
              <n-input-number
                v-model:value="formData.salary"
                :min="0"
                placeholder="0"
                style="width: 100%"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <!-- Services -->
        <n-divider title-placement="left">Услуги сотрудника</n-divider>
        
        <n-space vertical style="width: 100%">
          <n-button type="primary" @click="showServicesModal = true">
            📋 Управление услугами
          </n-button>
          
          <n-text v-if="employeeServices.length > 0" type="success">
            Привязано услуг: {{ employeeServices.length }}
          </n-text>
        </n-space>

        <!-- Роли -->
        <n-divider title-placement="left">Роли в системе</n-divider>
        
        <n-space vertical>
          <n-checkbox v-model:checked="formData.can_be_merchandiser">
            Может быть товароведом
          </n-checkbox>
          <n-checkbox v-model:checked="formData.is_chief_accountant">
            Главный бухгалтер
          </n-checkbox>
          <n-checkbox v-model:checked="formData.is_cashier">
            Кассир
          </n-checkbox>
          <n-checkbox v-model:checked="formData.is_head">
            Руководитель предприятия
          </n-checkbox>
        </n-space>

        <!-- Цвет в календаре -->
        <n-divider title-placement="left">Настройки календаря</n-divider>
        
        <n-form-item label="Цвет сотрудника в календаре">
          <div class="color-picker">
            <div
              v-for="color in colorPalette"
              :key="color"
              class="color-item"
              :class="{ active: formData.color === color }"
              :style="{ backgroundColor: color }"
              @click="formData.color = color"
            ></div>
          </div>
        </n-form-item>

        <!-- Управление доступом -->
        <n-divider title-placement="left">Управление доступом</n-divider>
        
        <n-form-item>
          <n-checkbox v-model:checked="formData.grant_access">
            Разрешить доступ к системе
          </n-checkbox>
        </n-form-item>

        <template v-if="formData.grant_access">
          <n-form-item label="Роль в системе" path="role">
            <n-select v-model:value="formData.role" :options="roleOptions" placeholder="Выберите роль" />
          </n-form-item>

          <n-form-item label="Пароль" path="password" v-if="!isEdit">
            <n-input
              v-model:value="formData.password"
              type="password"
              placeholder="Введите пароль (мин. 8 символов)"
            />
          </n-form-item>
        </template>
      </n-form>
    </n-scrollbar>

    <template #footer>
      <n-space justify="end">
        <n-button @click="handleClose">Отмена</n-button>
        <n-button type="warning" @click="handleSave(false)" :loading="saving">
          Сохранить
        </n-button>
        <n-button type="primary" @click="handleSave(true)" :loading="saving">
          Сохранить и закрыть
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import apiClient from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import EmployeeServicesModal from './EmployeeServicesModal.vue'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  employee: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const authStore = useAuthStore()
const formRef = ref(null)
const saving = ref(false)

// Modal states
const showServicesModal = ref(false)

// Data lists
const employeeServices = ref([])

const isEdit = computed(() => !!props.employee)

const visible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

// Color palette
const colorPalette = [
  '#F44336', '#E91E63', '#9C27B0', '#673AB7',
  '#3F51B5', '#2196F3', '#03A9F4', '#00BCD4',
  '#009688', '#4CAF50', '#8BC34A', '#CDDC39',
  '#FFEB3B', '#FFC107', '#FF9800', '#FF5722',
  '#795548', '#9E9E9E', '#607D8B', '#000000'
]

// Form data
const formData = ref({
  organization: null,
  first_name: '',
  last_name: '',
  middle_name: '',
  position: '',
  specialization: '',
  hire_date: null,
  is_fired: false,
  fire_date: null,
  iin: '',
  passport_series: '',
  passport_number: '',
  passport_issued_by: '',
  passport_issued_date: null,
  phone: '',
  email: '',
  commission_percent: 0,
  salary: null,
  color: '#2196F3',
  can_be_merchandiser: false,
  is_chief_accountant: false,
  is_cashier: false,
  is_head: false,
  grant_access: false,
  role: 'doctor',
  password: ''
})

const rules = {
  first_name: { required: true, message: 'Введите имя', trigger: 'blur' },
  last_name: { required: true, message: 'Введите фамилию', trigger: 'blur' },
  position: { required: true, message: 'Введите должность', trigger: 'blur' },
  phone: { required: true, message: 'Введите телефон', trigger: 'blur' },
  hire_date: { required: true, type: 'number', message: 'Выберите дату приёма', trigger: 'change' },
  password: {
    required: true,
    message: 'Введите пароль',
    trigger: 'blur',
    validator: (rule, value) => {
      if (formData.value.grant_access && !isEdit.value) {
        return value && value.length >= 8
      }
      return true
    }
  }
}

const roleOptions = [
  { label: 'Владелец', value: 'owner' },
  { label: 'Администратор филиала', value: 'branch_admin' },
  { label: 'Врач', value: 'doctor' },
  { label: 'Регистратор', value: 'registrar' },
  { label: 'Кассир', value: 'cashier' },
  { label: 'Кладовщик', value: 'warehouse' },
  { label: 'Маркетолог', value: 'marketer' },
  { label: 'Только просмотр', value: 'readonly' }
]

// Watch for employee prop changes
watch(
  () => props.employee,
  (newVal) => {
    if (newVal) {
      // Populate form with employee data
      formData.value = {
        organization: newVal.organization,
        first_name: newVal.first_name || '',
        last_name: newVal.last_name || '',
        middle_name: newVal.middle_name || '',
        position: newVal.position || '',
        specialization: newVal.specialization || '',
        hire_date: newVal.hire_date ? new Date(newVal.hire_date).getTime() : null,
        is_fired: !!newVal.fire_date,
        fire_date: newVal.fire_date ? new Date(newVal.fire_date).getTime() : null,
        iin: newVal.iin || '',
        passport_series: newVal.passport_series || '',
        passport_number: newVal.passport_number || '',
        passport_issued_by: newVal.passport_issued_by || '',
        passport_issued_date: newVal.passport_issued_date ? new Date(newVal.passport_issued_date).getTime() : null,
        phone: newVal.phone || '',
        email: newVal.email || '',
        commission_percent: newVal.commission_percent || 0,
        salary: newVal.salary || null,
        color: newVal.color || '#2196F3',
        can_be_merchandiser: false,
        is_chief_accountant: false,
        is_cashier: false,
        is_head: false,
        grant_access: !!newVal.user,
        role: newVal.user_info?.role || 'doctor',
        password: ''
      }
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

function resetForm() {
  formData.value = {
    organization: authStore.user?.organization || null,
    first_name: '',
    last_name: '',
    middle_name: '',
    position: '',
    specialization: '',
    hire_date: null,
    is_fired: false,
    fire_date: null,
    iin: '',
    passport_series: '',
    passport_number: '',
    passport_issued_by: '',
    passport_issued_date: null,
    phone: '',
    email: '',
    commission_percent: 0,
    salary: null,
    color: '#2196F3',
    can_be_merchandiser: false,
    is_chief_accountant: false,
    is_cashier: false,
    is_head: false,
    grant_access: false,
    role: 'doctor',
    password: ''
  }
}

function handleClose() {
  visible.value = false
  resetForm()
}

// Handle services saved
function onServicesSaved(services) {
  employeeServices.value = services
  message.success('Услуги обновлены')
}

async function handleSave(closeAfter = false) {
  try {
    await formRef.value?.validate()
    saving.value = true

    const data = {
      organization: formData.value.organization || authStore.user?.organization,
      first_name: formData.value.first_name,
      last_name: formData.value.last_name,
      middle_name: formData.value.middle_name,
      position: formData.value.position,
      specialization: formData.value.specialization,
      hire_date: formData.value.hire_date ? new Date(formData.value.hire_date).toISOString().split('T')[0] : null,
      fire_date: formData.value.is_fired && formData.value.fire_date ? new Date(formData.value.fire_date).toISOString().split('T')[0] : null,
      iin: formData.value.iin,
      passport_series: formData.value.passport_series,
      passport_number: formData.value.passport_number,
      passport_issued_by: formData.value.passport_issued_by,
      passport_issued_date: formData.value.passport_issued_date ? new Date(formData.value.passport_issued_date).toISOString().split('T')[0] : null,
      phone: formData.value.phone,
      email: formData.value.email,
      commission_percent: formData.value.commission_percent,
      salary: formData.value.salary,
      color: formData.value.color,
      is_active: !formData.value.is_fired
    }

    let employeeId = props.employee?.id

    if (isEdit.value) {
      // Update existing employee
      await apiClient.patch(`/staff/employees/${employeeId}`, data)
      message.success('Сотрудник обновлён')
    } else {
      // Create new employee
      const response = await apiClient.post('/staff/employees', data)
      employeeId = response.data.id
      message.success('Сотрудник создан')

      // Grant access if needed
      if (formData.value.grant_access) {
        try {
          await apiClient.post(`/staff/employees/${employeeId}/grant_access`, {
            role: formData.value.role,
            password: formData.value.password
          })
          message.success('Доступ к системе предоставлен')
        } catch (error) {
          console.error('Error granting access:', error)
          message.warning('Сотрудник создан, но не удалось предоставить доступ')
        }
      }
    }

    emit('saved')

    if (closeAfter) {
      handleClose()
    } else {
      resetForm()
    }
  } catch (error) {
    console.error('Error saving employee:', error)
    if (error.response?.data) {
      const errors = error.response.data
      const errorMsg = typeof errors === 'string' ? errors : JSON.stringify(errors)
      message.error('Ошибка: ' + errorMsg)
    } else {
      message.error('Ошибка сохранения сотрудника')
    }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/tokens.scss';

.color-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.color-item {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  transition: all $transition-fast;
  border: 2px solid transparent;
  
  &:hover {
    transform: scale(1.1);
  }
  
  &.active {
    border-color: $text-primary;
    box-shadow: 0 0 0 2px $bg-secondary, 0 0 0 4px $primary-color;
    transform: scale(1.15);
  }
}
</style>

