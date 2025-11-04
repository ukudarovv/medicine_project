<template>
  <n-modal
    v-model:show="visible"
    title="Добавить услугу к визиту"
    preset="card"
    style="width: 600px"
  >
    <n-form ref="formRef" :model="formData" :rules="rules">
      <n-form-item label="Услуга" path="service">
        <n-select
          v-model:value="formData.service"
          :options="serviceOptions"
          placeholder="Выберите услугу"
          filterable
          :loading="loadingServices"
          @update:value="onServiceSelect"
        />
      </n-form-item>

      <n-grid :cols="2" :x-gap="12">
        <n-grid-item>
          <n-form-item label="Количество" path="qty">
            <n-input-number
              v-model:value="formData.qty"
              :min="1"
              placeholder="1"
              style="width: 100%"
            />
          </n-form-item>
        </n-grid-item>
        <n-grid-item>
          <n-form-item label="Длительность (мин)" path="duration">
            <n-input-number
              v-model:value="formData.duration"
              :min="0"
              placeholder="30"
              style="width: 100%"
            />
          </n-form-item>
        </n-grid-item>
      </n-grid>

      <n-grid :cols="2" :x-gap="12">
        <n-grid-item>
          <n-form-item label="Цена" path="price">
            <n-input-number
              v-model:value="formData.price"
              :min="0"
              placeholder="Цена"
              style="width: 100%"
            >
              <template #suffix>₸</template>
            </n-input-number>
          </n-form-item>
        </n-grid-item>
        <n-grid-item>
          <n-form-item label="Скидка %" path="discount_percent">
            <n-input-number
              v-model:value="formData.discount_percent"
              :min="0"
              :max="100"
              placeholder="0"
              style="width: 100%"
            >
              <template #suffix>%</template>
            </n-input-number>
          </n-form-item>
        </n-grid-item>
      </n-grid>

      <n-form-item label="Номер зуба">
        <n-input
          v-model:value="formData.tooth_number"
          placeholder="Например: 36"
        />
      </n-form-item>
    </n-form>

    <template #footer>
      <n-space justify="end">
        <n-button @click="visible = false">Отмена</n-button>
        <n-button type="primary" @click="handleSubmit" :loading="saving">
          Добавить
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import apiClient from '@/api/axios'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  visitId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const visible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val)
})

const formRef = ref(null)
const saving = ref(false)
const loadingServices = ref(false)
const services = ref([])

const formData = ref({
  service: null,
  qty: 1,
  duration: 30,
  price: 0,
  discount_percent: 0,
  tooth_number: ''
})

const rules = {
  service: {
    required: true,
    message: 'Выберите услугу',
    trigger: 'change'
  },
  qty: {
    required: true,
    type: 'number',
    message: 'Укажите количество',
    trigger: 'change'
  },
  price: {
    required: true,
    type: 'number',
    message: 'Укажите цену',
    trigger: 'change'
  }
}

const serviceOptions = computed(() => {
  return services.value.map(service => ({
    label: `${service.name} - ${service.price} ₸`,
    value: service.id,
    price: service.price,
    duration: service.duration
  }))
})

// Загрузка списка услуг
async function loadServices() {
  loadingServices.value = true
  try {
    const response = await apiClient.get('/services/services')
    services.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading services:', error)
    message.error('Ошибка загрузки списка услуг')
  } finally {
    loadingServices.value = false
  }
}

// Обработка выбора услуги
function onServiceSelect(serviceId) {
  const selectedService = services.value.find(s => s.id === serviceId)
  if (selectedService) {
    formData.value.price = selectedService.price
    formData.value.duration = selectedService.duration || 30
  }
}

// Отправка формы
async function handleSubmit() {
  try {
    await formRef.value?.validate()
    
    saving.value = true
    
    const payload = {
      service: formData.value.service,
      qty: formData.value.qty,
      duration: formData.value.duration,
      price: formData.value.price,
      discount_percent: formData.value.discount_percent,
      discount_amount: 0,
      tooth_number: formData.value.tooth_number
    }
    
    await apiClient.post(`/visits/visits/${props.visitId}/add_service`, payload)
    
    message.success('Услуга добавлена к визиту')
    visible.value = false
    emit('saved')
    
    // Сброс формы
    formData.value = {
      service: null,
      qty: 1,
      duration: 30,
      price: 0,
      discount_percent: 0,
      tooth_number: ''
    }
  } catch (error) {
    if (error?.message === 'Validation failed') {
      return
    }
    console.error('Error adding service:', error)
    message.error('Ошибка при добавлении услуги')
  } finally {
    saving.value = false
  }
}

// Загружать услуги при открытии модала
watch(() => props.show, (newVal) => {
  if (newVal && services.value.length === 0) {
    loadServices()
  }
})
</script>

<style scoped>
:deep(.n-input),
:deep(.n-input-number),
:deep(.n-select) {
  background-color: #2a2a2a;
  color: #e0e0e0;
  border-color: #404040;
}

:deep(.n-form-item-label) {
  color: #b0b0b0;
}
</style>

