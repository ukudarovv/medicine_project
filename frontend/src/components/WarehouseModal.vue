<template>
  <n-modal 
    v-model:show="show" 
    preset="card"
    :title="isEdit ? 'Редактировать склад' : 'Новый склад'"
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
      <n-form-item label="Филиал" path="branch">
        <n-select
          v-model:value="formData.branch"
          :options="branchOptions"
          placeholder="Выберите филиал"
          :loading="loadingBranches"
        />
      </n-form-item>

      <n-form-item label="Название склада" path="name">
        <n-input
          v-model:value="formData.name"
          placeholder="Введите название склада"
        />
      </n-form-item>

      <n-form-item label="Статус" path="is_active">
        <n-switch v-model:value="formData.is_active">
          <template #checked>Активен</template>
          <template #unchecked>Неактивен</template>
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
import { ref, computed, watch, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import warehouseAPI from '@/api/warehouse'
import api from '@/api/axios'

const props = defineProps({
  modelValue: Boolean,
  warehouse: Object
})

const emit = defineEmits(['update:modelValue', 'success'])

const message = useMessage()
const formRef = ref(null)
const loading = ref(false)
const loadingBranches = ref(false)
const branchOptions = ref([])

const show = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEdit = computed(() => !!props.warehouse?.id)

const formData = ref({
  branch: null,
  name: '',
  is_active: true
})

const rules = {
  branch: [
    { required: true, type: 'number', message: 'Выберите филиал', trigger: 'change' }
  ],
  name: [
    { required: true, message: 'Введите название склада', trigger: 'blur' }
  ]
}

const loadBranches = async () => {
  try {
    loadingBranches.value = true
    const response = await api.get('/org/branches/')
    // Handle both paginated and non-paginated responses
    const branches = Array.isArray(response.data) 
      ? response.data 
      : (response.data.results || [])
    branchOptions.value = branches.map(branch => ({
      label: branch.name,
      value: branch.id
    }))
  } catch (error) {
    console.error('Error loading branches:', error)
    message.error('Ошибка загрузки филиалов')
  } finally {
    loadingBranches.value = false
  }
}

const resetForm = () => {
  formData.value = {
    branch: null,
    name: '',
    is_active: true
  }
}

watch(() => props.warehouse, (newVal) => {
  if (newVal && newVal.id) {
    formData.value = {
      branch: newVal.branch || null,
      name: newVal.name || '',
      is_active: newVal.is_active !== false
    }
  } else {
    resetForm()
  }
}, { immediate: true })

onMounted(() => {
  loadBranches()
})

const handleCancel = () => {
  show.value = false
  resetForm()
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true

    if (isEdit.value) {
      await warehouseAPI.updateWarehouse(props.warehouse.id, formData.value)
      message.success('Склад обновлен')
    } else {
      await warehouseAPI.createWarehouse(formData.value)
      message.success('Склад создан')
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

