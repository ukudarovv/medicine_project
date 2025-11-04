<template>
  <div class="billing-page">
    <n-page-header title="Финансы">
      <template #extra>
        <n-space>
          <n-date-picker
            v-model:value="dateRange"
            type="daterange"
            clearable
            @update:value="handleDateRangeChange"
          />
          <n-button 
            type="primary" 
            @click="showPaymentModal = true"
            :disabled="!currentShift"
          >
            💰 Новый платёж
          </n-button>
          <n-button 
            @click="showCashShiftModal = true"
            :type="currentShift ? 'default' : 'warning'"
          >
            {{ currentShift ? '🔓 Смена открыта' : '🔒 Открыть смену' }}
          </n-button>
          <n-button @click="exportReport">
            📊 Экспорт 1C
          </n-button>
        </n-space>
      </template>
    </n-page-header>

    <!-- Financial summary cards -->
    <n-grid :cols="4" :x-gap="16" style="margin-top: 24px">
      <n-grid-item>
        <n-card>
          <n-statistic 
            label="Доход за период" 
            :value="formatMoney(statistics.total_income || 0)"
          >
            <template #suffix>₸</template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic 
            label="Расход за период" 
            :value="formatMoney(statistics.total_expense || 0)"
          >
            <template #suffix>₸</template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic 
            label="Прибыль" 
            :value="formatMoney(statistics.total_profit || 0)"
            :class="(statistics.total_profit || 0) >= 0 ? 'profit-positive' : 'profit-negative'"
          >
            <template #suffix>₸</template>
          </n-statistic>
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card>
          <n-statistic 
            label="Касса (наличные)" 
            :value="formatMoney(statistics.cash_balance || 0)"
          >
            <template #suffix>₸</template>
          </n-statistic>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- Payment methods breakdown -->
    <n-card title="Статистика по способам оплаты" style="margin-top: 24px" v-if="statistics.payment_methods?.length">
      <n-space>
        <n-tag 
          v-for="method in statistics.payment_methods" 
          :key="method.method"
          size="large"
          :bordered="false"
        >
          {{ getMethodName(method.method) }}: {{ formatMoney(method.total) }} ₸ ({{ method.count }})
        </n-tag>
      </n-space>
    </n-card>

    <!-- Transactions table -->
    <n-card title="Транзакции" :bordered="false" style="margin-top: 24px">
      <template #header-extra>
        <n-space>
          <n-input 
            v-model:value="searchQuery" 
            placeholder="Поиск..."
            clearable
            style="width: 200px"
          >
            <template #prefix>
              🔍
            </template>
          </n-input>
        </n-space>
      </template>
      <n-data-table
        :columns="columns"
        :data="filteredTransactions"
        :loading="loading"
        :pagination="pagination"
        :row-key="(row) => row.id"
      />
    </n-card>

    <!-- Payment Modal -->
    <n-modal 
      v-model:show="showPaymentModal" 
      preset="card"
      title="Новый платёж"
      style="width: 600px"
      :mask-closable="false"
    >
      <n-form 
        ref="paymentFormRef"
        :model="paymentForm"
        :rules="paymentRules"
        label-placement="top"
      >
        <n-form-item label="Счёт (Invoice ID)" path="invoice">
          <n-input-number 
            v-model:value="paymentForm.invoice" 
            placeholder="ID счёта"
            style="width: 100%"
            :min="1"
          />
        </n-form-item>
        
        <n-form-item label="Способ оплаты" path="method">
          <n-select 
            v-model:value="paymentForm.method" 
            :options="paymentMethodOptions"
            placeholder="Выберите способ оплаты"
          />
        </n-form-item>

        <n-form-item label="Сумма (₸)" path="amount">
          <n-input-number 
            v-model:value="paymentForm.amount" 
            placeholder="0.00"
            style="width: 100%"
            :min="0"
            :precision="2"
            :step="100"
          >
            <template #suffix>₸</template>
          </n-input-number>
        </n-form-item>

        <n-form-item label="Примечание" path="provider">
          <n-input 
            v-model:value="paymentForm.provider" 
            placeholder="Дополнительная информация"
            type="textarea"
            :rows="2"
          />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showPaymentModal = false">Отмена</n-button>
          <n-button 
            type="primary" 
            @click="handleCreatePayment"
            :loading="paymentSubmitting"
          >
            Создать платёж
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- Cash Shift Modal -->
    <n-modal 
      v-model:show="showCashShiftModal" 
      preset="card"
      :title="currentShift ? 'Закрыть кассовую смену' : 'Открыть кассовую смену'"
      style="width: 500px"
      :mask-closable="false"
    >
      <n-form 
        ref="shiftFormRef"
        :model="shiftForm"
        :rules="shiftRules"
        label-placement="top"
      >
        <n-form-item label="Филиал" path="branch" v-if="!currentShift">
          <n-select 
            v-model:value="shiftForm.branch" 
            :options="branchOptions"
            placeholder="Выберите филиал"
          />
        </n-form-item>

        <n-form-item 
          :label="currentShift ? 'Сумма закрытия (₸)' : 'Сумма открытия (₸)'" 
          :path="currentShift ? 'closing_balance' : 'opening_balance'"
        >
          <n-input-number 
            v-model:value="currentShift ? shiftForm.closing_balance : shiftForm.opening_balance" 
            placeholder="0.00"
            style="width: 100%"
            :min="0"
            :precision="2"
            :step="100"
          >
            <template #suffix>₸</template>
          </n-input-number>
        </n-form-item>

        <n-alert 
          v-if="currentShift" 
          type="info" 
          title="Текущая смена"
          style="margin-top: 16px"
        >
          Открыта: {{ formatDateTime(currentShift.opened_at) }}<br>
          Кассир: {{ currentShift.opened_by_name }}<br>
          Начальный остаток: {{ formatMoney(currentShift.opening_balance) }} ₸
        </n-alert>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showCashShiftModal = false">Отмена</n-button>
          <n-button 
            :type="currentShift ? 'error' : 'primary'"
            @click="currentShift ? handleCloseShift() : handleOpenShift()"
            :loading="shiftSubmitting"
          >
            {{ currentShift ? 'Закрыть смену' : 'Открыть смену' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h, watch } from 'vue'
import { NButton, NTag, useMessage, useDialog } from 'naive-ui'
import { format, parseISO } from 'date-fns'
import { ru } from 'date-fns/locale'
import * as billingApi from '@/api/billing'

const message = useMessage()
const dialog = useDialog()

// State
const transactions = ref([])
const statistics = ref({})
const loading = ref(false)
const dateRange = ref(null)
const searchQuery = ref('')
const currentShift = ref(null)

// Modals
const showPaymentModal = ref(false)
const showCashShiftModal = ref(false)

// Forms
const paymentFormRef = ref(null)
const shiftFormRef = ref(null)
const paymentSubmitting = ref(false)
const shiftSubmitting = ref(false)

const paymentForm = ref({
  invoice: null,
  method: 'cash',
  amount: 0,
  provider: ''
})

const shiftForm = ref({
  branch: null,
  opening_balance: 0,
  closing_balance: 0
})

const branchOptions = ref([])

// Payment methods
const paymentMethodOptions = [
  { label: '💵 Наличные', value: 'cash' },
  { label: '💳 Карта', value: 'card' },
  { label: '🏦 Kaspi', value: 'kaspi' },
  { label: '📱 Kaspi QR', value: 'kaspi_qr' },
  { label: '💼 Halyk Pay', value: 'halyk_pay' },
  { label: '💰 Paybox', value: 'paybox' },
  { label: '☁️ Cloud Payments', value: 'cloud' }
]

// Validation rules
const paymentRules = {
  invoice: [
    { required: true, type: 'number', message: 'Укажите ID счёта', trigger: 'blur' }
  ],
  method: [
    { required: true, message: 'Выберите способ оплаты', trigger: 'change' }
  ],
  amount: [
    { required: true, type: 'number', message: 'Укажите сумму', trigger: 'blur' },
    { type: 'number', min: 0.01, message: 'Сумма должна быть больше 0', trigger: 'blur' }
  ]
}

const shiftRules = {
  branch: [
    { required: true, type: 'number', message: 'Выберите филиал', trigger: 'change' }
  ],
  opening_balance: [
    { required: true, type: 'number', message: 'Укажите начальную сумму', trigger: 'blur' }
  ],
  closing_balance: [
    { required: true, type: 'number', message: 'Укажите сумму закрытия', trigger: 'blur' }
  ]
}

// Computed
const filteredTransactions = computed(() => {
  if (!searchQuery.value) return transactions.value
  
  const query = searchQuery.value.toLowerCase()
  return transactions.value.filter(t => 
    t.description?.toLowerCase().includes(query) ||
    t.patient?.toLowerCase().includes(query) ||
    t.invoice_number?.toLowerCase().includes(query) ||
    t.category?.toLowerCase().includes(query)
  )
})

const pagination = {
  page: 1,
  pageSize: 20,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100]
}

const columns = [
  { 
    title: 'Дата', 
    key: 'date', 
    width: 160,
    render: (row) => formatDateTime(row.date)
  },
  { 
    title: 'Тип', 
    key: 'type', 
    width: 100,
    render: (row) => h(
      NTag, 
      { type: row.type === 'income' ? 'success' : 'error', size: 'small' }, 
      { default: () => row.type === 'income' ? 'Доход' : 'Расход' }
    )
  },
  { title: 'Категория', key: 'category', width: 150 },
  { title: 'Описание', key: 'description', ellipsis: { tooltip: true } },
  { title: 'Пациент', key: 'patient', width: 180, ellipsis: { tooltip: true } },
  { 
    title: 'Способ', 
    key: 'method', 
    width: 130,
    render: (row) => h(NTag, { size: 'small', bordered: false }, { default: () => row.method })
  },
  { 
    title: 'Сумма', 
    key: 'amount', 
    width: 120, 
    align: 'right',
    render: (row) => h(
      'span',
      { style: { fontWeight: 'bold', color: row.type === 'income' ? '#18a058' : '#d03050' } },
      `${row.type === 'income' ? '+' : '-'} ${formatMoney(row.amount)} ₸`
    )
  },
  { 
    title: 'Статус', 
    key: 'status', 
    width: 120,
    render: (row) => h(NTag, { size: 'small', type: 'info' }, { default: () => row.status })
  }
]

// Methods
const formatMoney = (value) => {
  return Number(value || 0).toLocaleString('ru-RU', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  })
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const date = typeof dateStr === 'string' ? parseISO(dateStr) : dateStr
    return format(date, 'dd.MM.yyyy HH:mm', { locale: ru })
  } catch {
    return dateStr
  }
}

const getMethodName = (method) => {
  const option = paymentMethodOptions.find(o => o.value === method)
  return option ? option.label : method
}

const loadStatistics = async () => {
  try {
    const params = getDateRangeParams()
    const response = await billingApi.getBillingStatistics(params.start_date, params.end_date)
    statistics.value = response.data
  } catch (error) {
    console.error('Failed to load statistics:', error)
    message.error('Ошибка загрузки статистики')
  }
}

const loadTransactions = async () => {
  loading.value = true
  try {
    const params = getDateRangeParams()
    const response = await billingApi.getTransactions(params.start_date, params.end_date)
    transactions.value = response.data
  } catch (error) {
    console.error('Failed to load transactions:', error)
    message.error('Ошибка загрузки транзакций')
  } finally {
    loading.value = false
  }
}

const loadCurrentShift = async () => {
  try {
    // Get user's branch (you'll need to get this from auth store or settings)
    const branchId = shiftForm.value.branch || 1 // Default to 1 for now
    const response = await billingApi.getCurrentCashShift(branchId)
    currentShift.value = response.data.shift || null
  } catch (error) {
    console.error('Failed to load current shift:', error)
  }
}

const loadBranches = async () => {
  try {
    // This should come from organization API
    // For now, mock data
    branchOptions.value = [
      { label: 'Главный филиал', value: 1 }
    ]
    shiftForm.value.branch = 1
  } catch (error) {
    console.error('Failed to load branches:', error)
  }
}

const getDateRangeParams = () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    return {}
  }
  
  return {
    start_date: new Date(dateRange.value[0]).toISOString(),
    end_date: new Date(dateRange.value[1]).toISOString()
  }
}

const handleDateRangeChange = () => {
  loadStatistics()
  loadTransactions()
}

const handleCreatePayment = async () => {
  try {
    await paymentFormRef.value?.validate()
    paymentSubmitting.value = true
    
    await billingApi.createPayment(paymentForm.value)
    message.success('Платёж успешно создан')
    showPaymentModal.value = false
    
    // Reset form
    paymentForm.value = {
      invoice: null,
      method: 'cash',
      amount: 0,
      provider: ''
    }
    
    // Reload data
    await Promise.all([loadStatistics(), loadTransactions()])
  } catch (error) {
    if (error?.response?.data) {
      message.error(`Ошибка: ${JSON.stringify(error.response.data)}`)
    } else {
      message.error('Ошибка создания платежа')
    }
    console.error('Failed to create payment:', error)
  } finally {
    paymentSubmitting.value = false
  }
}

const handleOpenShift = async () => {
  try {
    await shiftFormRef.value?.validate()
    shiftSubmitting.value = true
    
    await billingApi.openCashShift({
      branch: shiftForm.value.branch,
      opening_balance: shiftForm.value.opening_balance
    })
    
    message.success('Кассовая смена открыта')
    showCashShiftModal.value = false
    await loadCurrentShift()
  } catch (error) {
    console.error('Failed to open shift:', error)
    message.error('Ошибка открытия смены')
  } finally {
    shiftSubmitting.value = false
  }
}

const handleCloseShift = async () => {
  dialog.warning({
    title: 'Закрыть смену?',
    content: 'Вы уверены, что хотите закрыть текущую кассовую смену?',
    positiveText: 'Закрыть',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await shiftFormRef.value?.validate()
        shiftSubmitting.value = true
        
        await billingApi.closeCashShift(
          currentShift.value.id,
          shiftForm.value.closing_balance
        )
        
        message.success('Кассовая смена закрыта')
        showCashShiftModal.value = false
        currentShift.value = null
        shiftForm.value.closing_balance = 0
      } catch (error) {
        console.error('Failed to close shift:', error)
        message.error('Ошибка закрытия смены')
      } finally {
        shiftSubmitting.value = false
      }
    }
  })
}

const exportReport = async () => {
  try {
    const params = getDateRangeParams()
    if (!params.start_date || !params.end_date) {
      message.warning('Выберите период для экспорта')
      return
    }
    
    const response = await billingApi.export1C(params.start_date, params.end_date)
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `1c_export_${format(new Date(), 'yyyy-MM-dd')}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    
    message.success('Отчёт экспортирован')
  } catch (error) {
    console.error('Failed to export report:', error)
    message.error('Ошибка экспорта отчёта')
  }
}

// Lifecycle
onMounted(async () => {
  await loadBranches()
  await loadCurrentShift()
  await loadStatistics()
  await loadTransactions()
})

// Watch for modal close to reset forms
watch(showPaymentModal, (val) => {
  if (!val) {
    paymentFormRef.value?.restoreValidation()
  }
})

watch(showCashShiftModal, (val) => {
  if (!val) {
    shiftFormRef.value?.restoreValidation()
  }
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
  border: 1px solid #2a2a2a;
}

:deep(.n-statistic) {
  color: #e0e0e0;
}

:deep(.n-statistic-value) {
  color: #18a058 !important;
  font-weight: 600;
  font-size: 28px;
}

:deep(.n-statistic-value__suffix) {
  color: #18a058 !important;
}

.profit-positive :deep(.n-statistic-value) {
  color: #18a058 !important;
}

.profit-negative :deep(.n-statistic-value) {
  color: #d03050 !important;
}

:deep(.n-data-table) {
  background-color: transparent;
}

:deep(.n-data-table-th) {
  background-color: #1e1e1e;
  color: #a0a0a0;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.5px;
}

:deep(.n-data-table-td) {
  background-color: #1e1e1e;
  color: #e0e0e0;
  border-bottom: 1px solid #2a2a2a;
}

:deep(.n-data-table-tr:hover .n-data-table-td) {
  background-color: #252525;
}

:deep(.n-page-header) {
  color: #e0e0e0;
}

:deep(.n-page-header__title) {
  color: #e0e0e0;
  font-size: 24px;
  font-weight: 600;
}

:deep(.n-button) {
  font-weight: 500;
}

:deep(.n-modal) {
  background-color: #1e1e1e;
}

:deep(.n-card-header) {
  border-bottom: 1px solid #2a2a2a;
  color: #e0e0e0;
}

:deep(.n-input),
:deep(.n-input-number),
:deep(.n-select),
:deep(.n-date-picker) {
  background-color: #252525;
  color: #e0e0e0;
}

:deep(.n-input__input-el),
:deep(.n-input-number__input-el) {
  color: #e0e0e0;
}

:deep(.n-base-selection) {
  background-color: #252525;
}

:deep(.n-tag) {
  font-weight: 500;
}

:deep(.n-alert) {
  background-color: #1a2332;
  border: 1px solid #2a3d5a;
}
</style>
