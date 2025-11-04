<template>
  <n-modal 
    v-model:show="show" 
    preset="card"
    :title="getMoveTitle"
    style="width: 600px"
    :segmented="{ content: 'soft', footer: 'soft' }"
  >
    <n-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-placement="top"
      require-mark-placement="right-hanging"
    >
      <n-form-item label="Тип движения" path="type">
        <n-select
          v-model:value="formData.type"
          :options="typeOptions"
          placeholder="Выберите тип"
        />
      </n-form-item>

      <n-form-item label="Филиал" path="branch">
        <n-select
          v-model:value="formData.branch"
          :options="branchOptions"
          placeholder="Выберите филиал"
          :loading="loadingBranches"
        />
      </n-form-item>

      <n-form-item label="Номенклатура" path="stockitem">
        <n-select
          v-model:value="formData.stockitem"
          :options="stockItemOptions"
          placeholder="Выберите номенклатуру"
          :loading="loadingItems"
          filterable
          @update:value="handleStockItemChange"
        />
      </n-form-item>

      <n-form-item label="Партия" path="batch">
        <n-select
          v-model:value="formData.batch"
          :options="batchOptions"
          placeholder="Выберите партию"
          :loading="loadingBatches"
          :disabled="!formData.stockitem"
          clearable
        />
      </n-form-item>

      <n-form-item label="Количество" path="qty">
        <n-input-number
          v-model:value="formData.qty"
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
        >
          Создать
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import warehouseAPI from '@/api/warehouse'
import api from '@/api/axios'

const props = defineProps({
  modelValue: Boolean,
  moveType: {
    type: String,
    default: 'in'
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const message = useMessage()
const formRef = ref(null)
const loading = ref(false)
const loadingItems = ref(false)
const loadingBranches = ref(false)
const loadingBatches = ref(false)
const stockItemOptions = ref([])
const branchOptions = ref([])
const batchOptions = ref([])

const show = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const getMoveTitle = computed(() => {
  const titles = {
    'in': 'Приход товара',
    'out': 'Списание товара',
    'transfer': 'Перемещение товара'
  }
  return titles[formData.value.type] || 'Движение товара'
})

const formData = ref({
  type: 'in',
  branch: null,
  stockitem: null,
  batch: null,
  qty: 0
})

const typeOptions = [
  { label: 'Приход', value: 'in' },
  { label: 'Расход', value: 'out' },
  { label: 'Перемещение', value: 'transfer' }
]

const rules = {
  type: [
    { required: true, message: 'Выберите тип движения', trigger: 'change' }
  ],
  branch: [
    { required: true, type: 'number', message: 'Выберите филиал', trigger: 'change' }
  ],
  stockitem: [
    { required: true, type: 'number', message: 'Выберите номенклатуру', trigger: 'change' }
  ],
  qty: [
    { required: true, type: 'number', message: 'Введите количество', trigger: 'blur' }
  ]
}

const loadStockItems = async () => {
  try {
    loadingItems.value = true
    const response = await warehouseAPI.getStockItemsSimple()
    stockItemOptions.value = response.data.map(item => ({
      label: `${item.name} (${item.unit})`,
      value: item.id
    }))
  } catch (error) {
    message.error('Ошибка загрузки номенклатуры')
  } finally {
    loadingItems.value = false
  }
}

const loadBranches = async () => {
  try {
    loadingBranches.value = true
    const response = await api.get('/org/branches/')
    branchOptions.value = response.data.map(branch => ({
      label: branch.name,
      value: branch.id
    }))
  } catch (error) {
    message.error('Ошибка загрузки филиалов')
  } finally {
    loadingBranches.value = false
  }
}

const loadBatches = async (stockitemId) => {
  if (!stockitemId) {
    batchOptions.value = []
    return
  }
  
  try {
    loadingBatches.value = true
    const response = await warehouseAPI.getStockBatches({ stockitem: stockitemId })
    batchOptions.value = response.data.map(batch => ({
      label: `${batch.warehouse_name} - ${batch.lot || 'без номера'} (${batch.quantity} ${batch.stockitem_unit})`,
      value: batch.id
    }))
  } catch (error) {
    message.error('Ошибка загрузки партий')
  } finally {
    loadingBatches.value = false
  }
}

const handleStockItemChange = (value) => {
  formData.value.batch = null
  if (value) {
    loadBatches(value)
  }
}

watch(() => props.moveType, (newVal) => {
  if (newVal) {
    formData.value.type = newVal
  }
}, { immediate: true })

onMounted(() => {
  loadStockItems()
  loadBranches()
})

const resetForm = () => {
  formData.value = {
    type: props.moveType || 'in',
    branch: null,
    stockitem: null,
    batch: null,
    qty: 0
  }
  batchOptions.value = []
}

const handleCancel = () => {
  show.value = false
  resetForm()
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true

    await warehouseAPI.createStockMove(formData.value)
    message.success('Движение создано')

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

