<template>
  <n-modal
    v-model:show="visible"
    title="Услуги сотрудника"
    preset="card"
    style="width: 800px"
  >
    <n-space vertical size="large">
      <n-form inline :model="searchForm">
        <n-form-item label="Поиск услуги">
          <n-input
            v-model:value="searchForm.query"
            placeholder="Найти услугу..."
            style="width: 300px"
          />
        </n-form-item>
        <n-button type="primary" @click="addService">
          + Добавить услугу
        </n-button>
      </n-form>

      <n-data-table
        :columns="columns"
        :data="services"
        :pagination="false"
        size="small"
        max-height="400px"
      />
    </n-space>

    <template #footer>
      <n-space justify="end">
        <n-button @click="visible = false">Закрыть</n-button>
        <n-button type="primary" @click="handleSaveAll" :loading="saving">
          Сохранить все
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { NButton, NInputNumber, useMessage } from 'naive-ui'

const props = defineProps({
  show: Boolean,
  employeeId: Number
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const saving = ref(false)
const services = ref([])

const visible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

const searchForm = ref({
  query: ''
})

const columns = [
  {
    title: 'Код',
    key: 'code',
    width: 100
  },
  {
    title: 'Название услуги',
    key: 'name'
  },
  {
    title: 'Базовая цена',
    key: 'base_price',
    width: 120,
    render: (row) => `${row.base_price} ₸`
  },
  {
    title: 'Индивидуальная цена',
    key: 'custom_price',
    width: 150,
    render: (row) => {
      return h(NInputNumber, {
        value: row.custom_price,
        min: 0,
        placeholder: 'Цена',
        'onUpdate:value': (value) => {
          row.custom_price = value
        }
      })
    }
  },
  {
    title: 'Действия',
    key: 'actions',
    width: 80,
    render: (row, index) => {
      return h(
        NButton,
        {
          size: 'small',
          type: 'error',
          onClick: () => removeService(index)
        },
        { default: () => '🗑️' }
      )
    }
  }
]

function addService() {
  // Mock service - в реальности нужен поиск по API
  services.value.push({
    id: Date.now(),
    code: 'SVC' + services.value.length,
    name: 'Новая услуга',
    base_price: 10000,
    custom_price: null
  })
}

function removeService(index) {
  services.value.splice(index, 1)
}

async function handleSaveAll() {
  saving.value = true
  try {
    emit('saved', services.value)
    message.success('Услуги сохранены')
    visible.value = false
  } catch (error) {
    message.error('Ошибка сохранения')
  } finally {
    saving.value = false
  }
}
</script>

