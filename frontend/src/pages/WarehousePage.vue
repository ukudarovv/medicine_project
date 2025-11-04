<template>
  <div class="warehouse-page">
    <n-page-header title="Склад">
      <template #extra>
        <n-space>
          <n-button type="primary">
            + Новая номенклатура
          </n-button>
          <n-button type="primary">
            📦 Поступление
          </n-button>
          <n-button>
            📤 Списание
          </n-button>
          <n-button>
            📊 Инвентаризация
          </n-button>
        </n-space>
      </template>
    </n-page-header>

    <n-tabs type="line" animated style="margin-top: 16px">
      <n-tab-pane name="nomenclature" tab="Номенклатура">
        <n-data-table
          :columns="nomenclatureColumns"
          :data="items"
          :loading="loading"
          :pagination="pagination"
        />
      </n-tab-pane>

      <n-tab-pane name="movements" tab="Движения">
        <n-data-table
          :columns="movementColumns"
          :data="movements"
          :loading="loading"
          :pagination="pagination"
        />
      </n-tab-pane>

      <n-tab-pane name="inventory" tab="Остатки">
        <n-data-table
          :columns="inventoryColumns"
          :data="inventory"
          :loading="loading"
          :pagination="pagination"
        />
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup>
import { ref, h } from 'vue'
import { NButton, NTag } from 'naive-ui'

const items = ref([])
const movements = ref([])
const inventory = ref([])
const loading = ref(false)

const pagination = {
  page: 1,
  pageSize: 20
}

const nomenclatureColumns = [
  { title: 'Код', key: 'code', width: 100 },
  { title: 'Наименование', key: 'name' },
  { title: 'Категория', key: 'category', width: 150 },
  { title: 'Ед. изм.', key: 'unit', width: 100 },
  { title: 'Цена закупки', key: 'purchase_price', width: 120 },
  { title: 'Цена продажи', key: 'sale_price', width: 120 },
  { title: 'На складе', key: 'quantity', width: 100 }
]

const movementColumns = [
  { title: 'Дата', key: 'date', width: 120 },
  { title: 'Тип', key: 'type', width: 120 },
  { title: 'Номенклатура', key: 'item_name' },
  { title: 'Количество', key: 'quantity', width: 100 },
  { title: 'Сумма', key: 'amount', width: 120 }
]

const inventoryColumns = [
  { title: 'Наименование', key: 'name' },
  { title: 'Остаток', key: 'quantity', width: 100 },
  { title: 'Мин. остаток', key: 'min_quantity', width: 120 },
  { title: 'Статус', key: 'status', width: 120,
    render: (row) => {
      const isLow = row.quantity < row.min_quantity
      return h(NTag, { type: isLow ? 'error' : 'success' }, 
        { default: () => isLow ? 'Недостаток' : 'В наличии' })
    }
  }
]
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
</style>
