<template>
  <div class="data-table">
    <div class="table-header" v-if="$slots.header || showSearch">
      <div class="table-actions">
        <slot name="header"></slot>
      </div>
      <n-input
        v-if="showSearch"
        v-model:value="searchQuery"
        placeholder="Поиск..."
        clearable
        class="search-input"
      >
        <template #prefix>
          <span>🔍</span>
        </template>
      </n-input>
    </div>

    <n-data-table
      :columns="columns"
      :data="filteredData"
      :loading="loading"
      :pagination="paginationProps"
      :row-key="rowKey"
      @update:page="handlePageChange"
      @update:page-size="handlePageSizeChange"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  columns: {
    type: Array,
    required: true
  },
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  showSearch: {
    type: Boolean,
    default: true
  },
  rowKey: {
    type: String,
    default: 'id'
  },
  pageSize: {
    type: Number,
    default: 25
  }
})

const searchQuery = ref('')
const currentPage = ref(1)
const currentPageSize = ref(props.pageSize)

const filteredData = computed(() => {
  if (!searchQuery.value) return props.data
  
  const query = searchQuery.value.toLowerCase()
  return props.data.filter(row => {
    return Object.values(row).some(value => {
      return String(value).toLowerCase().includes(query)
    })
  })
})

const paginationProps = computed(() => ({
  page: currentPage.value,
  pageSize: currentPageSize.value,
  pageSizes: [25, 50, 100],
  showSizePicker: true,
  prefix: ({ itemCount }) => `Всего: ${itemCount}`
}))

function handlePageChange(page) {
  currentPage.value = page
}

function handlePageSizeChange(pageSize) {
  currentPageSize.value = pageSize
  currentPage.value = 1
}
</script>

<style scoped lang="scss">
.data-table {
  width: 100%;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 16px;
}

.table-actions {
  display: flex;
  gap: 8px;
  flex: 1;
}

.search-input {
  width: 300px;
}
</style>

