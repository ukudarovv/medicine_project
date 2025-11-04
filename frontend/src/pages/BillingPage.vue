<template>
  <div class="billing-page">
    <n-page-header title="Финансы">
      <template #extra>
        <n-space>
          <n-date-picker
            v-model:value="dateRange"
            type="daterange"
            clearable
          />
          <n-button type="primary">
            + Новая транзакция
          </n-button>
          <n-button>
            📊 Отчёт
          </n-button>
        </n-space>
      </template>
    </n-page-header>

    <!-- Financial summary cards -->
    <n-grid :cols="4" :x-gap="16" style="margin-top: 24px">
      <n-grid-item>
        <n-card>
          <n-statistic label="Доход за период" :value="totalIncome">
            <template #suffix>₸</template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="Расход за период" :value="totalExpense">
            <template #suffix>₸</template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="Прибыль" :value="totalProfit">
            <template #suffix>₸</template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic label="Касса" :value="cashBalance">
            <template #suffix>₸</template>
          </n-statistic>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- Transactions table -->
    <n-card title="Транзакции" :bordered="false" style="margin-top: 24px">
      <n-data-table
        :columns="columns"
        :data="transactions"
        :loading="loading"
        :pagination="pagination"
      />
    </n-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { NButton, NTag, useMessage } from 'naive-ui'
import { format } from 'date-fns'

const message = useMessage()
const transactions = ref([])
const loading = ref(false)
const dateRange = ref(null)

const totalIncome = computed(() => 
  transactions.value
    .filter(t => t.type === 'income')
    .reduce((sum, t) => sum + t.amount, 0)
)

const totalExpense = computed(() =>
  transactions.value
    .filter(t => t.type === 'expense')
    .reduce((sum, t) => sum + t.amount, 0)
)

const totalProfit = computed(() => totalIncome.value - totalExpense.value)
const cashBalance = ref(0)

const pagination = {
  page: 1,
  pageSize: 20
}

const columns = [
  { title: 'Дата', key: 'date', width: 120 },
  { title: 'Тип', key: 'type', width: 100,
    render: (row) => h(NTag, { type: row.type === 'income' ? 'success' : 'error' }, 
      { default: () => row.type === 'income' ? 'Доход' : 'Расход' })
  },
  { title: 'Категория', key: 'category' },
  { title: 'Описание', key: 'description' },
  { title: 'Сумма', key: 'amount', width: 120, render: (row) => `${row.amount} ₸` }
]

onMounted(() => {
  // Mock data
  transactions.value = []
  cashBalance.value = 0
})
</script>

<style scoped>
.billing-page {
  padding: 24px;
  background: #121212;
  min-height: 100vh;
}

:deep(.n-card) {
  background-color: #1e1e1e;
  color: #e0e0e0;
}

:deep(.n-statistic) {
  color: #e0e0e0;
}

:deep(.n-statistic-value) {
  color: #18a058 !important;
}
</style>
