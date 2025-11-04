<template>
  <n-modal
    v-model:show="visible"
    :title="isEdit ? 'Редактировать услугу' : 'Новая услуга'"
    preset="card"
    style="width: 800px"
  >
    <n-scrollbar style="max-height: 70vh">
      <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item label="Наименование" path="name">
              <n-input v-model:value="formData.name" placeholder="Название услуги" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Наименование для печати">
              <n-input v-model:value="formData.print_name" placeholder="Для документов" />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-grid :cols="3" :x-gap="12">
          <n-grid-item>
            <n-form-item label="Артикул">
              <n-input v-model:value="formData.code" placeholder="Код" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Налоговый код">
              <n-input v-model:value="formData.tax_code" placeholder="01" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Код номенклатуры">
              <n-input v-model:value="formData.nomenclature_code" placeholder="МКБ код">
                <template #suffix>
                  <n-icon>🔍</n-icon>
                </template>
              </n-input>
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-form-item label="Категория" path="category">
          <n-tree-select
            v-model:value="formData.category"
            :options="categoryOptions"
            placeholder="Выберите категорию"
            filterable
          />
        </n-form-item>

        <n-form-item label="Стоимость" path="base_price">
          <n-radio-group v-model:value="priceType" style="margin-bottom: 12px">
            <n-radio value="fixed">Фиксированная</n-radio>
            <n-radio value="range">Диапазон</n-radio>
          </n-radio-group>
          
          <n-grid v-if="priceType === 'fixed'" :cols="1">
            <n-grid-item>
              <n-input-number
                v-model:value="formData.base_price"
                :min="0"
                :precision="2"
                placeholder="Цена"
                style="width: 100%"
              >
                <template #suffix>₸</template>
              </n-input-number>
            </n-grid-item>
          </n-grid>
          
          <n-grid v-else :cols="2" :x-gap="12">
            <n-grid-item>
              <n-input-number
                v-model:value="formData.price_min"
                :min="0"
                :precision="2"
                placeholder="От"
                style="width: 100%"
              >
                <template #suffix>₸</template>
              </n-input-number>
            </n-grid-item>
            <n-grid-item>
              <n-input-number
                v-model:value="formData.price_max"
                :min="0"
                :precision="2"
                placeholder="До"
                style="width: 100%"
              >
                <template #suffix>₸</template>
              </n-input-number>
            </n-grid-item>
          </n-grid>
        </n-form-item>

        <n-form-item>
          <n-checkbox v-model:checked="formData.is_expensive">
            Дорогостоящая услуга (код 02)
          </n-checkbox>
        </n-form-item>

        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item label="Ставка НДС">
              <n-select v-model:value="formData.vat_rate" :options="vatOptions" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Размер НДС">
              <n-input-number
                v-model:value="formData.vat_amount"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-grid :cols="2" :x-gap="12">
          <n-grid-item>
            <n-form-item label="Единица измерения" path="unit">
              <n-select v-model:value="formData.unit" :options="unitOptions" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="Продолжительность (мин)">
              <n-input-number v-model:value="formData.duration" :min="0" style="width: 100%" />
            </n-form-item>
          </n-grid-item>
        </n-grid>

        <n-form-item label="Комментарий">
          <n-input
            v-model:value="formData.notes"
            type="textarea"
            :rows="2"
            placeholder="Примечания"
          />
        </n-form-item>

        <n-form-item label="Используемые ресурсы">
          <n-dynamic-input v-model:value="resources" placeholder="Добавить ресурс" />
        </n-form-item>

        <n-form-item label="Используемые материалы">
          <n-input placeholder="Поиск материалов">
            <template #suffix>
              <n-button text type="primary">Добавить</n-button>
            </template>
          </n-input>
        </n-form-item>

        <n-form-item label="Побочные эффекты и нагрузки">
          <n-dynamic-input v-model:value="sideEffects" placeholder="Добавить эффект" />
        </n-form-item>

        <n-form-item label="Изображение для онлайн-записи">
          <n-upload list-type="image-card" :max="1">
            добавить фото
          </n-upload>
        </n-form-item>

        <n-form-item label="Цвет в расписании">
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

        <n-form-item label="Описание услуги для онлайн-записи">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            :rows="4"
            placeholder="Подробное описание"
          />
        </n-form-item>
      </n-form>
    </n-scrollbar>

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
  service: {
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
const priceType = ref('fixed')
const resources = ref([])
const sideEffects = ref([])

const isEdit = computed(() => !!props.service)

const visible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

const colorPalette = [
  '#F44336', '#E91E63', '#9C27B0', '#673AB7',
  '#3F51B5', '#2196F3', '#03A9F4', '#00BCD4',
  '#009688', '#4CAF50', '#8BC34A', '#CDDC39',
  '#FFEB3B', '#FFC107', '#FF9800', '#FF5722'
]

const formData = ref({
  organization: null,
  category: null,
  code: '',
  name: '',
  print_name: '',
  description: '',
  nomenclature_code: '',
  tax_code: '01',
  unit: 'service',
  base_price: 0,
  price_min: null,
  price_max: null,
  vat_rate: 0,
  vat_amount: 0,
  duration: 30,
  notes: '',
  color: '#2196F3',
  is_expensive: false
})

const rules = {
  name: { required: true, message: 'Введите название', trigger: 'blur' },
  category: { required: true, type: 'number', message: 'Выберите категорию', trigger: 'change' },
  base_price: { required: true, type: 'number', message: 'Укажите цену', trigger: 'blur' },
  unit: { required: true, message: 'Выберите единицу', trigger: 'change' }
}

const categoryOptions = computed(() => {
  const buildTree = (items, parentId = null) => {
    return items
      .filter(item => item.parent === parentId)
      .map(item => ({
        label: item.name,
        value: item.id,
        children: buildTree(items, item.id)
      }))
  }
  return buildTree(props.categories)
})

const unitOptions = [
  { label: 'Услуга', value: 'service' },
  { label: 'Штука', value: 'piece' },
  { label: 'Час', value: 'hour' },
  { label: 'Визит', value: 'visit' },
  { label: 'Зуб', value: 'tooth' },
  { label: 'Единица', value: 'unit' }
]

const vatOptions = [
  { label: 'НДС не облагается', value: 0 },
  { label: '0%', value: 0 },
  { label: '10%', value: 10 },
  { label: '20%', value: 20 }
]

watch(
  () => props.service,
  (newVal) => {
    if (newVal) {
      formData.value = {
        organization: newVal.organization,
        category: newVal.category,
        code: newVal.code || '',
        name: newVal.name,
        print_name: newVal.print_name || '',
        description: newVal.description || '',
        nomenclature_code: newVal.nomenclature_code || '',
        tax_code: newVal.tax_code || '01',
        unit: newVal.unit || 'service',
        base_price: newVal.base_price || 0,
        price_min: newVal.price_min,
        price_max: newVal.price_max,
        vat_rate: newVal.vat_rate || 0,
        vat_amount: newVal.vat_amount || 0,
        duration: newVal.duration || 30,
        notes: newVal.notes || '',
        color: newVal.color || '#2196F3',
        is_expensive: newVal.is_expensive || false
      }
      priceType.value = newVal.price_min && newVal.price_max ? 'range' : 'fixed'
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

function resetForm() {
  formData.value = {
    organization: authStore.user?.organization || null,
    category: null,
    code: '',
    name: '',
    print_name: '',
    description: '',
    nomenclature_code: '',
    tax_code: '01',
    unit: 'service',
    base_price: 0,
    price_min: null,
    price_max: null,
    vat_rate: 0,
    vat_amount: 0,
    duration: 30,
    notes: '',
    color: '#2196F3',
    is_expensive: false
  }
  priceType.value = 'fixed'
  resources.value = []
  sideEffects.value = []
}

async function handleSave(closeAfter = false) {
  try {
    await formRef.value?.validate()
    saving.value = true

    const data = {
      organization: formData.value.organization || authStore.user?.organization,
      category: formData.value.category,
      code: formData.value.code,
      name: formData.value.name,
      print_name: formData.value.print_name,
      description: formData.value.description,
      nomenclature_code: formData.value.nomenclature_code,
      tax_code: formData.value.tax_code,
      unit: formData.value.unit,
      base_price: formData.value.base_price,
      price_min: priceType.value === 'range' ? formData.value.price_min : null,
      price_max: priceType.value === 'range' ? formData.value.price_max : null,
      vat_rate: formData.value.vat_rate,
      duration: formData.value.duration,
      notes: formData.value.notes,
      color: formData.value.color,
      is_expensive: formData.value.is_expensive
    }

    if (isEdit.value) {
      await apiClient.patch(`/services/services/${props.service.id}`, data)
      message.success('Услуга обновлена')
    } else {
      await apiClient.post('/services/services', data)
      message.success('Услуга создана')
    }

    emit('saved')

    if (closeAfter) {
      visible.value = false
      resetForm()
    }
  } catch (error) {
    console.error('Error saving service:', error)
    message.error('Ошибка сохранения услуги')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.color-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.color-item {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s;
  border: 2px solid transparent;
}

.color-item:hover {
  transform: scale(1.1);
}

.color-item.active {
  border-color: #000;
  transform: scale(1.15);
}
</style>

