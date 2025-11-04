<template>
  <div class="services-page">
    <n-page-header title="Услуги">
      <template #extra>
        <n-space>
          <n-button type="primary" @click="showCategoryModal = true">
            + Новая категория услуг
          </n-button>
          <n-button type="primary" @click="showServiceModal = true">
            + Новая услуга
          </n-button>
          <n-button>
            <template #icon>
              <n-icon>🔍</n-icon>
            </template>
            Фильтр
          </n-button>
          <n-dropdown :options="exportOptions" @select="handleExport">
            <n-button>
              <template #icon>
                <n-icon>📊</n-icon>
              </template>
              Excel
              <template #icon-right>
                <n-icon>▼</n-icon>
              </template>
            </n-button>
          </n-dropdown>
        </n-space>
      </template>
    </n-page-header>

    <n-layout has-sider style="margin-top: 16px; height: calc(100vh - 120px)">
      <!-- Category Tree -->
      <n-layout-sider
        bordered
        :width="300"
        :native-scrollbar="false"
        style="background: #1e1e1e; border-color: #333"
      >
        <div style="padding: 16px">
          <n-input
            v-model:value="categorySearch"
            placeholder="Поиск категории..."
            clearable
            style="margin-bottom: 12px"
          >
            <template #prefix>
              <n-icon>🔍</n-icon>
            </template>
          </n-input>

          <n-tree
            block-line
            :data="categoryTree"
            :pattern="categorySearch"
            :selected-keys="selectedCategory ? [selectedCategory] : ['all']"
            :on-update:selected-keys="handleCategorySelect"
            :render-label="renderCategoryLabel"
            :render-suffix="renderCategorySuffix"
            :default-expanded-keys="['all']"
          />
        </div>
      </n-layout-sider>

      <!-- Services Table -->
      <n-layout-content
        :native-scrollbar="false"
        content-style="padding: 16px; background: #1e1e1e"
      >
        <n-data-table
          :columns="columns"
          :data="filteredServices"
          :pagination="pagination"
          :loading="loading"
          :row-key="(row) => row.id"
          size="small"
        />
      </n-layout-content>
    </n-layout>

    <!-- Modals -->
    <ServiceCategoryModal
      v-model:show="showCategoryModal"
      :category="editingCategory"
      :categories="categories"
      @saved="loadData"
    />

    <ServiceModal
      v-model:show="showServiceModal"
      :service="editingService"
      :categories="categories"
      @saved="loadData"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { NButton, NSpace, NIcon, NTag, useMessage } from 'naive-ui'
import apiClient from '@/api/axios'
import ServiceCategoryModal from '@/components/ServiceCategoryModal.vue'
import ServiceModal from '@/components/ServiceModal.vue'

const message = useMessage()

// Data
const categories = ref([])
const services = ref([])
const loading = ref(false)
const categorySearch = ref('')
const selectedCategory = ref(null)

// Modals
const showCategoryModal = ref(false)
const showServiceModal = ref(false)
const editingCategory = ref(null)
const editingService = ref(null)

// Pagination
const pagination = {
  page: 1,
  pageSize: 20,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  onChange: (page) => {
    pagination.page = page
  },
  onUpdatePageSize: (pageSize) => {
    pagination.pageSize = pageSize
    pagination.page = 1
  }
}

// Export options
const exportOptions = [
  {
    label: 'Экспорт всех услуг',
    key: 'all'
  },
  {
    label: 'Экспорт текущей категории',
    key: 'category'
  }
]

// Build category tree
const categoryTree = computed(() => {
  const buildTree = (items, parentId = null) => {
    const filtered = items.filter(item => {
      // Check if parent matches (null == null or id == id)
      if (parentId === null) {
        return item.parent === null || item.parent === undefined
      }
      return item.parent === parentId
    })
    
    return filtered.map(item => ({
      key: item.id,
      label: item.name,
      data: item,
      children: buildTree(items, item.id)
    }))
  }

  const tree = buildTree(categories.value)
  
  return [
    {
      key: 'all',
      label: 'Все категории',
      isLeaf: false,
      children: tree
    }
  ]
})

// Filter services by selected category
const filteredServices = computed(() => {
  console.log('Filtering services:', {
    selectedCategory: selectedCategory.value,
    totalServices: services.value.length,
    categories: categories.value.length
  })
  
  if (!selectedCategory.value) {
    console.log('No category selected, showing all services:', services.value.length)
    return services.value
  }
  
  // Get all child category IDs recursively
  const getCategoryIds = (categoryId) => {
    const ids = [categoryId]
    const children = categories.value.filter(c => c.parent === categoryId)
    children.forEach(child => {
      ids.push(...getCategoryIds(child.id))
    })
    return ids
  }

  const categoryIds = getCategoryIds(selectedCategory.value)
  const filtered = services.value.filter(s => categoryIds.includes(s.category))
  
  console.log('Category filter result:', {
    categoryIds,
    filteredCount: filtered.length,
    serviceCategories: services.value.map(s => s.category)
  })
  
  return filtered
})

// Table columns
const columns = [
  {
    title: '№',
    key: 'index',
    width: 60,
    render: (_, index) => index + 1
  },
  {
    title: 'Наименование',
    key: 'name',
    ellipsis: {
      tooltip: true
    },
    render: (row) => {
      return h('div', [
        row.code ? h('span', { style: 'color: #999; margin-right: 8px' }, row.code) : null,
        h('span', row.name)
      ])
    }
  },
  {
    title: 'Категория',
    key: 'category',
    width: 200,
    render: (row) => {
      const category = categories.value.find(c => c.id === row.category)
      return category ? category.name : '-'
    }
  },
  {
    title: 'Стоимость, ₸',
    key: 'base_price',
    width: 120,
    render: (row) => {
      if (row.price_min && row.price_max) {
        return `${row.price_min} - ${row.price_max}`
      }
      return row.base_price || 0
    }
  },
  {
    title: 'Ед. измерения',
    key: 'unit',
    width: 120,
    render: (row) => {
      const unitMap = {
        service: 'Услуга',
        piece: 'Штука',
        hour: 'Час',
        visit: 'Визит',
        tooth: 'Зуб',
        unit: 'Единица'
      }
      return unitMap[row.unit] || row.unit
    }
  },
  {
    title: 'Цвет',
    key: 'color',
    width: 80,
    render: (row) => {
      if (row.color) {
        return h('div', {
          style: {
            width: '32px',
            height: '20px',
            backgroundColor: row.color,
            borderRadius: '4px'
          }
        })
      }
      return '-'
    }
  },
  {
    title: 'Налоговый код',
    key: 'tax_code',
    width: 120
  },
  {
    title: 'Действия',
    key: 'actions',
    width: 120,
    render: (row) => {
      return h(NSpace, null, {
        default: () => [
          h(
            NButton,
            {
              size: 'small',
              secondary: true,
              onClick: () => handleCopy(row)
            },
            { default: () => '📋' }
          ),
          h(
            NButton,
            {
              size: 'small',
              secondary: true,
              onClick: () => handleEdit(row)
            },
            { default: () => '✏️' }
          ),
          h(
            NButton,
            {
              size: 'small',
              type: 'error',
              secondary: true,
              onClick: () => handleDelete(row)
            },
            { default: () => '❌' }
          )
        ]
      })
    }
  }
]

// Render category tree label
function renderCategoryLabel({ option }) {
  return h('span', option.label)
}

// Render category tree suffix with count
function renderCategorySuffix({ option }) {
  if (!option.data) return null
  
  const count = services.value.filter(s => s.category === option.data.id).length
  if (count > 0) {
    return h(NTag, { size: 'small', type: 'info' }, { default: () => count })
  }
  return null
}

// Handlers
function handleCategorySelect(keys) {
  const selectedKey = keys[0]
  // If 'all' is selected, show all services
  if (selectedKey === 'all' || !selectedKey) {
    selectedCategory.value = null
  } else {
    selectedCategory.value = selectedKey
  }
}

function handleEdit(service) {
  editingService.value = service
  showServiceModal.value = true
}

function handleCopy(service) {
  editingService.value = { ...service, id: null, code: `${service.code}_copy` }
  showServiceModal.value = true
}

async function handleDelete(service) {
  if (!confirm(`Удалить услугу "${service.name}"?`)) return

  try {
    await apiClient.delete(`/services/services/${service.id}`)
    message.success('Услуга удалена')
    loadData()
  } catch (error) {
    console.error('Error deleting service:', error)
    message.error('Ошибка удаления услуги')
  }
}

function handleExport(key) {
  message.info(`Экспорт: ${key}`)
  // TODO: Implement export
}

// Load data
async function loadData() {
  loading.value = true
  try {
    const [categoriesRes, servicesRes] = await Promise.all([
      apiClient.get('/services/categories'),
      apiClient.get('/services/services')
    ])
    categories.value = categoriesRes.data.results || categoriesRes.data
    services.value = servicesRes.data.results || servicesRes.data
    
    console.log('Data loaded:', {
      categories: categories.value.length,
      services: services.value.length,
      sampleService: services.value[0],
      sampleCategory: categories.value[0]
    })
    console.log('First 3 services full data:', services.value.slice(0, 3))
  } catch (error) {
    console.error('Error loading data:', error)
    message.error('Ошибка загрузки данных')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.services-page {
  padding: 24px;
  background: #121212;
  min-height: 100vh;
}

/* Dark theme input styling */
:deep(.n-input) {
  background-color: #2d2d2d;
  border-color: #404040;
  color: #e0e0e0;
}

:deep(.n-input__input-el) {
  color: #e0e0e0;
}

:deep(.n-input:hover) {
  border-color: #555;
}

:deep(.n-input:focus-within) {
  border-color: var(--n-border-focus);
}

/* Tree styling */
:deep(.n-tree) {
  color: #e0e0e0;
}

:deep(.n-tree-node-content) {
  color: #e0e0e0;
}

:deep(.n-tree-node-content:hover) {
  background-color: #2d2d2d;
}

:deep(.n-tree-node--selected .n-tree-node-content) {
  background-color: #383838;
}

/* Data table dark theme */
:deep(.n-data-table) {
  background-color: #1e1e1e;
}

:deep(.n-data-table-th) {
  background-color: #2d2d2d;
  color: #e0e0e0;
  border-color: #404040;
}

:deep(.n-data-table-td) {
  background-color: #1e1e1e;
  color: #e0e0e0;
  border-color: #333;
}

:deep(.n-data-table-tr:hover .n-data-table-td) {
  background-color: #2a2a2a;
}

/* Page header styling */
:deep(.n-page-header) {
  color: #e0e0e0;
}

:deep(.n-page-header__title) {
  color: #e0e0e0;
}

/* Button styling for dark theme */
:deep(.n-button--primary-type) {
  background-color: #18a058;
  border-color: #18a058;
}

:deep(.n-button--primary-type:hover) {
  background-color: #1fb76b;
  border-color: #1fb76b;
}

:deep(.n-button:not(.n-button--primary-type)) {
  background-color: #2d2d2d;
  border-color: #404040;
  color: #e0e0e0;
}

:deep(.n-button:not(.n-button--primary-type):hover) {
  background-color: #383838;
  border-color: #555;
}

/* Dropdown styling */
:deep(.n-dropdown-menu) {
  background-color: #2d2d2d;
  border-color: #404040;
}

:deep(.n-dropdown-option) {
  color: #e0e0e0;
}

:deep(.n-dropdown-option:hover) {
  background-color: #383838;
}

/* Empty state */
:deep(.n-empty) {
  color: #999;
}

:deep(.n-empty__description) {
  color: #999;
}

/* Tags */
:deep(.n-tag) {
  background-color: #2d2d2d;
  border-color: #404040;
  color: #18a058;
}

/* Pagination */
:deep(.n-pagination) {
  color: #e0e0e0;
}

:deep(.n-pagination-item) {
  background-color: #2d2d2d;
  border-color: #404040;
  color: #e0e0e0;
}

:deep(.n-pagination-item:hover) {
  background-color: #383838;
}

:deep(.n-pagination-item--active) {
  background-color: #18a058;
  border-color: #18a058;
}
</style>
