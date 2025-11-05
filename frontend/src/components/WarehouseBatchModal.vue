<template>
  <n-modal 
    v-model:show="show" 
    preset="card"
    :title="isEdit ? 'Редактировать партию' : 'Новая партия товара'"
    style="width: 600px"
    :segmented="{ content: 'soft', footer: 'soft' }"
  >
    <n-alert 
      v-if="warehouseOptions.length === 0 && !loadingWarehouses"
      type="warning" 
      title="Внимание"
      style="margin-bottom: 16px"
    >
      Нет доступных складов. Пожалуйста, создайте склад на вкладке "Склады" перед добавлением партии товара.
    </n-alert>
    
    <n-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-placement="top"
      require-mark-placement="right-hanging"
    >
      <n-form-item label="Номенклатура" path="stockitem">
        <n-select
          v-model:value="formData.stockitem"
          :options="stockItemOptions"
          placeholder="Выберите номенклатуру"
          :loading="loadingItems"
          filterable
        />
      </n-form-item>

      <n-form-item label="Склад" path="warehouse">
        <n-select
          v-model:value="formData.warehouse"
          :options="warehouseOptions"
          :placeholder="warehouseOptions.length === 0 ? 'Нет доступных складов' : 'Выберите склад'"
          :loading="loadingWarehouses"
          :disabled="warehouseOptions.length === 0"
        />
      </n-form-item>

      <n-form-item label="Номер партии (лот)" path="lot">
        <n-input
          v-model:value="formData.lot"
          placeholder="Введите номер партии"
        />
      </n-form-item>

      <n-form-item label="Срок годности" path="exp_date">
        <n-date-picker
          v-model:value="formData.exp_date"
          type="date"
          placeholder="Выберите дату"
          style="width: 100%"
          :is-date-disabled="(ts) => ts < Date.now()"
        />
      </n-form-item>

      <n-form-item label="Количество" path="quantity">
        <n-input-number
          v-model:value="formData.quantity"
          placeholder="0.00"
          :min="0.01"
          :precision="2"
          style="width: 100%"
        />
      </n-form-item>
    </n-form>

    <template #footer>
      <n-space justify="end">
        <n-button @click="handleCancel">Отмена</n-button>
        <n-button
          type="primary"
          :loading="loading"
          @click="handleSubmit"
          :disabled="warehouseOptions.length === 0"
        >
          {{ isEdit ? 'Сохранить' : 'Добавить' }}
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import warehouseAPI from '@/api/warehouse'

const props = defineProps({
  modelValue: Boolean,
  batch: Object
})

const emit = defineEmits(['update:modelValue', 'success'])

const message = useMessage()
const formRef = ref(null)
const loading = ref(false)
const loadingItems = ref(false)
const loadingWarehouses = ref(false)
const stockItemOptions = ref([])
const warehouseOptions = ref([])

const show = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEdit = computed(() => !!props.batch?.id)

const formData = ref({
  stockitem: null,
  warehouse: null,
  lot: '',
  exp_date: null,
  quantity: 0
})

const rules = {
  stockitem: [
    { required: true, type: 'number', message: 'Выберите номенклатуру', trigger: 'change' }
  ],
  warehouse: [
    { required: true, type: 'number', message: 'Выберите склад', trigger: 'change' }
  ],
  quantity: [
    { required: true, type: 'number', message: 'Введите количество', trigger: 'blur' }
  ]
}

const loadStockItems = async () => {
  try {
    loadingItems.value = true
    const response = await warehouseAPI.getStockItemsSimple()
    // Handle both paginated and non-paginated responses
    const items = Array.isArray(response.data) 
      ? response.data 
      : (response.data.results || [])
    stockItemOptions.value = items.map(item => ({
      label: `${item.name} (${item.unit})`,
      value: item.id
    }))
  } catch (error) {
    console.error('Error loading stock items:', error)
    message.error('Ошибка загрузки номенклатуры')
  } finally {
    loadingItems.value = false
  }
}

const loadWarehouses = async () => {
  try {
    loadingWarehouses.value = true
    // Загружаем ВСЕ склады (убрали фильтр is_active для отладки)
    const response = await warehouseAPI.getWarehouses()
    console.log('Warehouses API response:', response.data)
    
    // Handle both paginated and non-paginated responses
    const warehouses = Array.isArray(response.data) 
      ? response.data 
      : (response.data.results || [])
    
    console.log('Parsed warehouses:', warehouses)
    
    warehouseOptions.value = warehouses.map(wh => ({
      label: wh.name,
      value: wh.id
    }))
    
    console.log('Warehouse options:', warehouseOptions.value)
    
    if (warehouseOptions.value.length === 0) {
      message.warning('Нет доступных складов. Создайте склад на вкладке "Склады".')
    }
  } catch (error) {
    console.error('Error loading warehouses:', error)
    message.error('Ошибка загрузки складов: ' + (error.response?.data?.detail || error.message))
  } finally {
    loadingWarehouses.value = false
  }
}

const resetForm = () => {
  formData.value = {
    stockitem: null,
    warehouse: null,
    lot: '',
    exp_date: null,
    quantity: 0
  }
}

watch(() => props.batch, (newVal) => {
  if (newVal && newVal.id) {
    formData.value = {
      stockitem: newVal.stockitem || null,
      warehouse: newVal.warehouse || null,
      lot: newVal.lot || '',
      exp_date: newVal.exp_date ? new Date(newVal.exp_date).getTime() : null,
      quantity: newVal.quantity || 0
    }
  } else {
    resetForm()
  }
}, { immediate: true })

onMounted(() => {
  loadStockItems()
  loadWarehouses()
})

const handleCancel = () => {
  show.value = false
  resetForm()
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true

    const payload = {
      ...formData.value,
      exp_date: formData.value.exp_date 
        ? new Date(formData.value.exp_date).toISOString().split('T')[0]
        : null
    }

    if (isEdit.value) {
      await warehouseAPI.updateStockBatch(props.batch.id, payload)
      message.success('Партия обновлена')
    } else {
      await warehouseAPI.createStockBatch(payload)
      message.success('Партия добавлена')
    }

    emit('success')
    show.value = false
    resetForm()
  } catch (error) {
    if (error?.message) {
      message.error(error.message)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
:deep(.n-card) {
  background-color: #1e1e1e;
}

:deep(.n-card__content) {
  color: #e0e0e0;
}

:deep(.n-form-item-label) {
  color: #e0e0e0;
}

:deep(.n-input) {
  background-color: #2d2d2d;
  color: #e0e0e0;
}

:deep(.n-input__input-el) {
  color: #e0e0e0;
}
</style>

