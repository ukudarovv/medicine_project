<template>
  <n-modal 
    v-model:show="show" 
    preset="card"
    :title="isEdit ? 'Редактировать номенклатуру' : 'Новая номенклатура'"
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
      <n-form-item label="Наименование" path="name">
        <n-input
          v-model:value="formData.name"
          placeholder="Введите наименование"
        />
      </n-form-item>

      <n-form-item label="Единица измерения" path="unit">
        <n-select
          v-model:value="formData.unit"
          :options="unitOptions"
          placeholder="Выберите единицу измерения"
          tag
          filterable
        />
      </n-form-item>

      <n-form-item label="Минимальный остаток" path="min_quantity">
        <n-input-number
          v-model:value="formData.min_quantity"
          placeholder="0.00"
          :min="0"
          :precision="2"
          style="width: 100%"
        />
      </n-form-item>

      <n-form-item label="Статус" path="is_active">
        <n-switch v-model:value="formData.is_active">
          <template #checked>Активно</template>
          <template #unchecked>Неактивно</template>
        </n-switch>
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
          {{ isEdit ? 'Сохранить' : 'Создать' }}
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import warehouseAPI from '@/api/warehouse'

const props = defineProps({
  modelValue: Boolean,
  item: Object
})

const emit = defineEmits(['update:modelValue', 'success'])

const message = useMessage()
const formRef = ref(null)
const loading = ref(false)

const show = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEdit = computed(() => !!props.item?.id)

const formData = ref({
  name: '',
  unit: 'шт',
  min_quantity: 0,
  is_active: true
})

const unitOptions = [
  { label: 'шт', value: 'шт' },
  { label: 'уп', value: 'уп' },
  { label: 'кг', value: 'кг' },
  { label: 'л', value: 'л' },
  { label: 'м', value: 'м' },
  { label: 'м²', value: 'м²' },
  { label: 'м³', value: 'м³' }
]

const rules = {
  name: [
    { required: true, message: 'Введите наименование', trigger: 'blur' }
  ],
  unit: [
    { required: true, message: 'Выберите единицу измерения', trigger: 'change' }
  ],
  min_quantity: [
    { required: true, type: 'number', message: 'Введите минимальный остаток', trigger: 'blur' }
  ]
}

const resetForm = () => {
  formData.value = {
    name: '',
    unit: 'шт',
    min_quantity: 0,
    is_active: true
  }
}

watch(() => props.item, (newVal) => {
  if (newVal && newVal.id) {
    formData.value = {
      name: newVal.name || '',
      unit: newVal.unit || 'шт',
      min_quantity: newVal.min_quantity || 0,
      is_active: newVal.is_active !== false
    }
  } else {
    resetForm()
  }
}, { immediate: true })

const handleCancel = () => {
  show.value = false
  resetForm()
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true

    if (isEdit.value) {
      await warehouseAPI.updateStockItem(props.item.id, formData.value)
      message.success('Номенклатура обновлена')
    } else {
      await warehouseAPI.createStockItem(formData.value)
      message.success('Номенклатура создана')
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

