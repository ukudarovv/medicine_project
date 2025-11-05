<template>
  <div class="warehouse-page">
    <n-page-header title="Управление складом">
      <template #extra>
        <n-space>
          <n-button type="primary" @click="showItemModal = true">
            + Номенклатура
          </n-button>
          <n-button type="primary" @click="showWarehouseModal = true">
            🏢 Склад
          </n-button>
          <n-button type="primary" @click="openMoveModal('in')">
            📦 Приход
          </n-button>
          <n-button @click="openMoveModal('out')">
            📤 Списание
          </n-button>
          <n-button @click="showBatchModal = true">
            📊 Партия
          </n-button>
        </n-space>
      </template>
    </n-page-header>

    <n-tabs 
      v-model:value="activeTab" 
      type="line" 
      animated 
      style="margin-top: 16px"
      @update:value="handleTabChange"
    >
      <!-- Номенклатура -->
      <n-tab-pane name="nomenclature" tab="Номенклатура">
        <n-space vertical :size="16">
          <n-space>
            <n-input
              v-model:value="searchQuery"
              placeholder="Поиск по наименованию"
              style="width: 300px"
              clearable
              @update:value="handleSearch"
            >
              <template #prefix>
                <n-icon :component="SearchIcon" />
              </template>
            </n-input>
            <n-select
              v-model:value="filterActive"
              :options="activeFilterOptions"
              placeholder="Статус"
              style="width: 150px"
              clearable
              @update:value="loadStockItems"
            />
            <n-checkbox v-model:checked="filterLowStock" @update:checked="loadStockItems">
              Только низкий остаток
            </n-checkbox>
            <n-button @click="loadStockItems">
              <template #icon>
                <n-icon :component="RefreshIcon" />
              </template>
              Обновить
            </n-button>
          </n-space>

          <n-data-table
            :columns="nomenclatureColumns"
            :data="items"
            :loading="loading"
            :pagination="paginationConfig"
            :row-key="(row) => row.id"
          />
        </n-space>
      </n-tab-pane>

      <!-- Партии товара -->
      <n-tab-pane name="batches" tab="Партии товара">
        <n-space vertical :size="16">
          <n-space>
            <n-select
              v-model:value="filterWarehouse"
              :options="warehouseFilterOptions"
              placeholder="Фильтр по складу"
              style="width: 200px"
              clearable
              @update:value="loadBatches"
            />
            <n-select
              v-model:value="filterStockItem"
              :options="stockItemFilterOptions"
              placeholder="Фильтр по номенклатуре"
              style="width: 250px"
              clearable
              filterable
              @update:value="loadBatches"
            />
            <n-checkbox v-model:checked="filterExpired" @update:checked="loadBatches">
              Только просроченные
            </n-checkbox>
            <n-button @click="loadBatches">
              <template #icon>
                <n-icon :component="RefreshIcon" />
              </template>
              Обновить
            </n-button>
          </n-space>

          <n-data-table
            :columns="batchColumns"
            :data="batches"
            :loading="loadingBatches"
            :pagination="paginationConfig"
            :row-key="(row) => row.id"
          />
        </n-space>
      </n-tab-pane>

      <!-- Движения -->
      <n-tab-pane name="movements" tab="Движения товара">
        <n-space vertical :size="16">
          <n-space>
            <n-select
              v-model:value="filterMoveType"
              :options="moveTypeOptions"
              placeholder="Тип движения"
              style="width: 180px"
              clearable
              @update:value="loadMoves"
            />
            <n-button @click="loadMoves">
              <template #icon>
                <n-icon :component="RefreshIcon" />
              </template>
              Обновить
            </n-button>
          </n-space>

          <n-data-table
            :columns="movementColumns"
            :data="movements"
            :loading="loadingMoves"
            :pagination="paginationConfig"
            :row-key="(row) => row.id"
          />
        </n-space>
      </n-tab-pane>

      <!-- Остатки -->
      <n-tab-pane name="inventory" tab="Остатки на складах">
        <n-space vertical :size="16">
          <n-button @click="loadInventory">
            <template #icon>
              <n-icon :component="RefreshIcon" />
            </template>
            Обновить
          </n-button>

          <n-data-table
            :columns="inventoryColumns"
            :data="inventory"
            :loading="loadingInventory"
            :pagination="paginationConfig"
          />
        </n-space>
      </n-tab-pane>

      <!-- Склады -->
      <n-tab-pane name="warehouses" tab="Склады">
        <n-space vertical :size="16">
          <n-button @click="loadWarehouses">
            <template #icon>
              <n-icon :component="RefreshIcon" />
            </template>
            Обновить
          </n-button>

          <n-data-table
            :columns="warehouseColumns"
            :data="warehouses"
            :loading="loadingWarehouses"
            :pagination="paginationConfig"
            :row-key="(row) => row.id"
          />
        </n-space>
      </n-tab-pane>
    </n-tabs>

    <!-- Модалки -->
    <WarehouseStockItemModal
      v-model="showItemModal"
      :item="currentItem"
      @success="handleItemSuccess"
    />

    <WarehouseModal
      v-model="showWarehouseModal"
      :warehouse="currentWarehouse"
      @success="handleWarehouseSuccess"
    />

    <WarehouseBatchModal
      v-model="showBatchModal"
      :batch="currentBatch"
      @success="handleBatchSuccess"
    />

    <WarehouseMoveModal
      v-model="showMoveModal"
      :move-type="currentMoveType"
      @success="handleMoveSuccess"
    />
  </div>
</template>

<script setup>
import { ref, h, onMounted, reactive } from 'vue'
import { NButton, NTag, NIcon, useMessage, useDialog } from 'naive-ui'
import { Search as SearchIcon, Refresh as RefreshIcon, Edit as EditIcon, Trash as TrashIcon } from '@vicons/tabler'
import warehouseAPI from '@/api/warehouse'
import WarehouseStockItemModal from '@/components/WarehouseStockItemModal.vue'
import WarehouseModal from '@/components/WarehouseModal.vue'
import WarehouseBatchModal from '@/components/WarehouseBatchModal.vue'
import WarehouseMoveModal from '@/components/WarehouseMoveModal.vue'

const message = useMessage()
const dialog = useDialog()

// State
const activeTab = ref('nomenclature')
const loading = ref(false)
const loadingBatches = ref(false)
const loadingMoves = ref(false)
const loadingInventory = ref(false)
const loadingWarehouses = ref(false)

const items = ref([])
const batches = ref([])
const movements = ref([])
const inventory = ref([])
const warehouses = ref([])

// Filters
const searchQuery = ref('')
const filterActive = ref(null)
const filterLowStock = ref(false)
const filterWarehouse = ref(null)
const filterStockItem = ref(null)
const filterExpired = ref(false)
const filterMoveType = ref(null)

// Modals
const showItemModal = ref(false)
const showWarehouseModal = ref(false)
const showBatchModal = ref(false)
const showMoveModal = ref(false)
const currentItem = ref(null)
const currentWarehouse = ref(null)
const currentBatch = ref(null)
const currentMoveType = ref('in')

// Filter options
const warehouseFilterOptions = ref([])
const stockItemFilterOptions = ref([])

const activeFilterOptions = [
  { label: 'Активные', value: true },
  { label: 'Неактивные', value: false }
]

const moveTypeOptions = [
  { label: 'Приход', value: 'in' },
  { label: 'Расход', value: 'out' },
  { label: 'Перемещение', value: 'transfer' }
]

const paginationConfig = reactive({
  page: 1,
  pageSize: 20,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100]
})

// Columns
const nomenclatureColumns = [
  { title: 'ID', key: 'id', width: 70 },
  { title: 'Наименование', key: 'name', ellipsis: { tooltip: true } },
  { title: 'Ед. изм.', key: 'unit', width: 100 },
  { 
    title: 'Остаток', 
    key: 'current_quantity', 
    width: 100,
    render: (row) => row.current_quantity?.toFixed(2) || '0.00'
  },
  { 
    title: 'Мин. остаток', 
    key: 'min_quantity', 
    width: 120,
    render: (row) => row.min_quantity?.toFixed(2) || '0.00'
  },
  {
    title: 'Статус',
    key: 'low_stock',
    width: 120,
    render: (row) => {
      if (row.low_stock) {
        return h(NTag, { type: 'error' }, { default: () => 'Низкий остаток' })
      }
      return h(NTag, { type: 'success' }, { default: () => 'В наличии' })
    }
  },
  {
    title: 'Активен',
    key: 'is_active',
    width: 100,
    render: (row) => h(NTag, { type: row.is_active ? 'success' : 'default' }, 
      { default: () => row.is_active ? 'Да' : 'Нет' })
  },
  {
    title: 'Действия',
    key: 'actions',
    width: 150,
    render: (row) => h('div', { style: { display: 'flex', gap: '8px' } }, [
      h(NButton, {
        size: 'small',
        onClick: () => editItem(row)
      }, { default: () => 'Изменить' }),
      h(NButton, {
        size: 'small',
        type: 'error',
        onClick: () => deleteItem(row)
      }, { default: () => 'Удалить' })
    ])
  }
]

const batchColumns = [
  { title: 'ID', key: 'id', width: 70 },
  { title: 'Номенклатура', key: 'stockitem_name', ellipsis: { tooltip: true } },
  { title: 'Склад', key: 'warehouse_name', width: 150 },
  { title: 'Партия/Лот', key: 'lot', width: 120 },
  { 
    title: 'Срок годности', 
    key: 'exp_date', 
    width: 130,
    render: (row) => row.exp_date || '-'
  },
  { 
    title: 'Количество', 
    key: 'quantity', 
    width: 120,
    render: (row) => `${row.quantity} ${row.stockitem_unit}`
  },
  {
    title: 'Статус',
    key: 'is_expired',
    width: 120,
    render: (row) => {
      if (row.is_expired) {
        return h(NTag, { type: 'error' }, { default: () => 'Просрочено' })
      }
      return h(NTag, { type: 'success' }, { default: () => 'Годен' })
    }
  },
  {
    title: 'Действия',
    key: 'actions',
    width: 150,
    render: (row) => h('div', { style: { display: 'flex', gap: '8px' } }, [
      h(NButton, {
        size: 'small',
        onClick: () => editBatch(row)
      }, { default: () => 'Изменить' }),
      h(NButton, {
        size: 'small',
        type: 'error',
        onClick: () => deleteBatch(row)
      }, { default: () => 'Удалить' })
    ])
  }
]

const movementColumns = [
  { title: 'ID', key: 'id', width: 70 },
  { 
    title: 'Дата', 
    key: 'created_at', 
    width: 160,
    render: (row) => new Date(row.created_at).toLocaleString('ru-RU')
  },
  { 
    title: 'Тип', 
    key: 'type_display', 
    width: 120,
    render: (row) => {
      const typeMap = {
        'in': 'success',
        'out': 'error',
        'transfer': 'info'
      }
      return h(NTag, { type: typeMap[row.type] || 'default' }, 
        { default: () => row.type_display })
    }
  },
  { title: 'Номенклатура', key: 'stockitem_name', ellipsis: { tooltip: true } },
  { title: 'Филиал', key: 'branch_name', width: 150 },
  { 
    title: 'Количество', 
    key: 'qty', 
    width: 120,
    render: (row) => row.qty?.toFixed(2) || '0.00'
  }
]

const inventoryColumns = [
  { title: 'Номенклатура', key: 'stockitem__name', ellipsis: { tooltip: true } },
  { title: 'Склад', key: 'warehouse__name', width: 180 },
  { title: 'Ед. изм.', key: 'stockitem__unit', width: 100 },
  { 
    title: 'Остаток', 
    key: 'total_quantity', 
    width: 120,
    render: (row) => row.total_quantity?.toFixed(2) || '0.00'
  },
  { 
    title: 'Мин. остаток', 
    key: 'stockitem__min_quantity', 
    width: 130,
    render: (row) => row.stockitem__min_quantity?.toFixed(2) || '0.00'
  },
  {
    title: 'Статус',
    key: 'status',
    width: 140,
    render: (row) => {
      const isLow = (row.total_quantity || 0) < (row.stockitem__min_quantity || 0)
      return h(NTag, { type: isLow ? 'error' : 'success' }, 
        { default: () => isLow ? 'Низкий остаток' : 'В наличии' })
    }
  }
]

const warehouseColumns = [
  { title: 'ID', key: 'id', width: 70 },
  { title: 'Название', key: 'name' },
  { title: 'Филиал', key: 'branch_name', width: 200 },
  { 
    title: 'Партий', 
    key: 'batches_count', 
    width: 100,
    render: (row) => row.batches_count || 0
  },
  {
    title: 'Активен',
    key: 'is_active',
    width: 100,
    render: (row) => h(NTag, { type: row.is_active ? 'success' : 'default' }, 
      { default: () => row.is_active ? 'Да' : 'Нет' })
  },
  { 
    title: 'Создан', 
    key: 'created_at', 
    width: 160,
    render: (row) => new Date(row.created_at).toLocaleString('ru-RU')
  },
  {
    title: 'Действия',
    key: 'actions',
    width: 150,
    render: (row) => h('div', { style: { display: 'flex', gap: '8px' } }, [
      h(NButton, {
        size: 'small',
        onClick: () => editWarehouse(row)
      }, { default: () => 'Изменить' }),
      h(NButton, {
        size: 'small',
        type: 'error',
        onClick: () => deleteWarehouse(row)
      }, { default: () => 'Удалить' })
    ])
  }
]

// Methods
const handleTabChange = (value) => {
  switch (value) {
    case 'nomenclature':
      loadStockItems()
      break
    case 'batches':
      loadBatches()
      loadFilterOptions()
      break
    case 'movements':
      loadMoves()
      break
    case 'inventory':
      loadInventory()
      break
    case 'warehouses':
      loadWarehouses()
      break
  }
}

const handleSearch = () => {
  loadStockItems()
}

const loadStockItems = async () => {
  try {
    loading.value = true
    const params = {
      search: searchQuery.value || undefined,
      is_active: filterActive.value !== null ? filterActive.value : undefined
    }
    const response = await warehouseAPI.getStockItems(params)
    items.value = response.data.results || response.data
    
    if (filterLowStock.value) {
      items.value = items.value.filter(item => item.low_stock)
    }
  } catch (error) {
    message.error('Ошибка загрузки номенклатуры')
  } finally {
    loading.value = false
  }
}

const loadBatches = async () => {
  try {
    loadingBatches.value = true
    const params = {
      warehouse: filterWarehouse.value || undefined,
      stockitem: filterStockItem.value || undefined,
      expired: filterExpired.value || undefined
    }
    const response = await warehouseAPI.getStockBatches(params)
    batches.value = response.data.results || response.data
  } catch (error) {
    message.error('Ошибка загрузки партий')
  } finally {
    loadingBatches.value = false
  }
}

const loadMoves = async () => {
  try {
    loadingMoves.value = true
    const params = {
      type: filterMoveType.value || undefined
    }
    const response = await warehouseAPI.getStockMoves(params)
    movements.value = response.data.results || response.data
  } catch (error) {
    message.error('Ошибка загрузки движений')
  } finally {
    loadingMoves.value = false
  }
}

const loadInventory = async () => {
  try {
    loadingInventory.value = true
    const response = await warehouseAPI.getInventory()
    inventory.value = response.data.results || response.data
  } catch (error) {
    message.error('Ошибка загрузки остатков')
  } finally {
    loadingInventory.value = false
  }
}

const loadWarehouses = async () => {
  try {
    loadingWarehouses.value = true
    const response = await warehouseAPI.getWarehouses()
    warehouses.value = response.data.results || response.data
  } catch (error) {
    message.error('Ошибка загрузки складов')
  } finally {
    loadingWarehouses.value = false
  }
}

const loadFilterOptions = async () => {
  try {
    const [whResponse, itemsResponse] = await Promise.all([
      warehouseAPI.getWarehouses({ is_active: true }),
      warehouseAPI.getStockItemsSimple()
    ])
    
    const warehouses = whResponse.data.results || whResponse.data
    warehouseFilterOptions.value = warehouses.map(wh => ({
      label: wh.name,
      value: wh.id
    }))
    
    const items = itemsResponse.data.results || itemsResponse.data
    stockItemFilterOptions.value = items.map(item => ({
      label: `${item.name} (${item.unit})`,
      value: item.id
    }))
  } catch (error) {
    console.error('Ошибка загрузки опций фильтров:', error)
  }
}

// CRUD operations
const editItem = (item) => {
  currentItem.value = item
  showItemModal.value = true
}

const deleteItem = (item) => {
  dialog.warning({
    title: 'Удалить номенклатуру?',
    content: `Вы уверены, что хотите удалить "${item.name}"?`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await warehouseAPI.deleteStockItem(item.id)
        message.success('Номенклатура удалена')
        loadStockItems()
      } catch (error) {
        message.error('Ошибка удаления номенклатуры')
      }
    }
  })
}

const editWarehouse = (warehouse) => {
  currentWarehouse.value = warehouse
  showWarehouseModal.value = true
}

const deleteWarehouse = (warehouse) => {
  dialog.warning({
    title: 'Удалить склад?',
    content: `Вы уверены, что хотите удалить склад "${warehouse.name}"?`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await warehouseAPI.deleteWarehouse(warehouse.id)
        message.success('Склад удален')
        loadWarehouses()
      } catch (error) {
        message.error('Ошибка удаления склада')
      }
    }
  })
}

const editBatch = (batch) => {
  currentBatch.value = batch
  showBatchModal.value = true
}

const deleteBatch = (batch) => {
  dialog.warning({
    title: 'Удалить партию?',
    content: `Вы уверены, что хотите удалить партию "${batch.lot || 'без номера'}"?`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await warehouseAPI.deleteStockBatch(batch.id)
        message.success('Партия удалена')
        loadBatches()
      } catch (error) {
        message.error('Ошибка удаления партии')
      }
    }
  })
}

const openMoveModal = (type) => {
  currentMoveType.value = type
  showMoveModal.value = true
}

// Success handlers
const handleItemSuccess = () => {
  currentItem.value = null
  loadStockItems()
}

const handleWarehouseSuccess = () => {
  currentWarehouse.value = null
  loadWarehouses()
}

const handleBatchSuccess = () => {
  currentBatch.value = null
  loadBatches()
  loadInventory()
}

const handleMoveSuccess = () => {
  loadMoves()
  loadBatches()
  loadInventory()
}

onMounted(() => {
  loadStockItems()
})
</script>

<style scoped>
.warehouse-page {
  padding: 24px;
  background: #121212;
  min-height: 100vh;
}

:deep(.n-page-header) {
  color: #e0e0e0;
}

:deep(.n-tabs) {
  color: #e0e0e0;
}

:deep(.n-data-table) {
  background-color: #1e1e1e;
}

:deep(.n-data-table-th) {
  background-color: #2d2d2d;
  color: #e0e0e0;
}

:deep(.n-data-table-td) {
  background-color: #1e1e1e;
  color: #e0e0e0;
  border-color: #333;
}

:deep(.n-input) {
  background-color: #2d2d2d;
}

:deep(.n-input__input-el) {
  color: #e0e0e0;
}

:deep(.n-base-selection) {
  background-color: #2d2d2d;
}

:deep(.n-base-selection-label) {
  background-color: #2d2d2d;
  color: #e0e0e0;
}
</style>
