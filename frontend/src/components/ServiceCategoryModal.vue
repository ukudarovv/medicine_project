<template>
  <n-modal
    v-model:show="visible"
    :title="isEdit ? 'Редактировать категорию' : 'Новая категория услуг'"
    preset="card"
    style="width: 600px"
  >
    <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
      <n-form-item label="Наименование" path="name">
        <n-input v-model:value="formData.name" placeholder="Введите название категории" />
      </n-form-item>

      <n-form-item label="Родительская категория">
        <n-select
          v-model:value="formData.parent"
          :options="flatCategoryOptions"
          placeholder="Выберите категорию"
          clearable
          filterable
        />
      </n-form-item>

      <n-form-item label="Код">
        <n-input v-model:value="formData.code" placeholder="Код категории" />
      </n-form-item>

      <n-form-item label="Порядок сортировки">
        <n-input-number v-model:value="formData.order" :min="0" style="width: 100%" />
      </n-form-item>

      <n-form-item label="Комментарий">
        <n-input
          v-model:value="formData.description"
          type="textarea"
          :rows="3"
          placeholder="Описание категории"
        />
      </n-form-item>

      <n-form-item label="Изображение для онлайн-записи (min размер 320x200 px)">
        <n-upload
          list-type="image-card"
          :max="1"
          :default-file-list="fileList"
        >
          добавить фото
        </n-upload>
      </n-form-item>
    </n-form>

    <template #footer>
      <n-space justify="end">
        <n-button @click="visible = false">Отмена</n-button>
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

const props = defineProps({
  show: Boolean,
  category: {
    type: Object,
    default: null
  },
  categories: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const authStore = useAuthStore()
const formRef = ref(null)
const saving = ref(false)
const fileList = ref([])

const isEdit = computed(() => !!props.category)

const visible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

const formData = ref({
  organization: null,
  name: '',
  parent: null,
  code: '',
  description: '',
  order: 0
})

const rules = {
  name: { required: true, message: 'Введите название', trigger: 'blur' }
}

// Flat list of categories with visual hierarchy for parent selection
const flatCategoryOptions = computed(() => {
  const flattenCategories = (items, level = 0, excludeId = null) => {
    const result = []
    
    // Get root categories first
    const roots = items.filter(item => !item.parent && item.id !== excludeId)
    
    roots.forEach(item => {
      const prefix = '　'.repeat(level) // Use full-width space for indentation
      result.push({
        label: prefix + item.name,
        value: item.id
      })
      
      // Find children
      const children = items.filter(child => child.parent === item.id && child.id !== excludeId)
      if (children.length > 0) {
        result.push(...flattenCategories(children, level + 1, excludeId))
      }
    })
    
    return result
  }
  
  if (!props.categories || props.categories.length === 0) {
    return [{ label: 'Нет (корневая категория)', value: null }]
  }
  
  return [
    { label: 'Нет (корневая категория)', value: null },
    ...flattenCategories(props.categories, 0, props.category?.id)
  ]
})

// Build tree options for parent category selection (keep for reference)
const categoryOptions = computed(() => {
  const buildTree = (items, parentId = null) => {
    const filtered = items.filter(item => {
      // Exclude current category from being its own parent
      if (item.id === props.category?.id) return false
      
      if (parentId === null) {
        return item.parent === null || item.parent === undefined
      }
      return item.parent === parentId
    })
    
    return filtered.map(item => {
      const children = buildTree(items, item.id)
      const option = {
        label: item.name,
        value: item.id
      }
      if (children.length > 0) {
        option.children = children
      }
      return option
    })
  }
  
  return [
    { label: 'Нет (корневая категория)', value: null },
    ...buildTree(props.categories)
  ]
})

watch(
  () => props.category,
  (newVal) => {
    if (newVal) {
      formData.value = {
        organization: newVal.organization,
        name: newVal.name,
        parent: newVal.parent,
        code: newVal.code || '',
        description: newVal.description || '',
        order: newVal.order || 0
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
    name: '',
    parent: null,
    code: '',
    description: '',
    order: 0
  }
  fileList.value = []
}

async function handleSave(closeAfter = false) {
  try {
    await formRef.value?.validate()
    saving.value = true

    const data = {
      organization: formData.value.organization || authStore.user?.organization,
      name: formData.value.name,
      parent: formData.value.parent,
      code: formData.value.code,
      description: formData.value.description,
      order: formData.value.order
    }

    if (isEdit.value) {
      await apiClient.patch(`/services/categories/${props.category.id}`, data)
      message.success('Категория обновлена')
    } else {
      await apiClient.post('/services/categories', data)
      message.success('Категория создана')
    }

    emit('saved')

    if (closeAfter) {
      visible.value = false
      resetForm()
    }
  } catch (error) {
    console.error('Error saving category:', error)
    message.error('Ошибка сохранения категории')
  } finally {
    saving.value = false
  }
}
</script>

