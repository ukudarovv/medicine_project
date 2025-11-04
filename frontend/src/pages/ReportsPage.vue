<template>
  <div class="reports-page">
    <n-page-header title="Отчёты">
      <template #extra>
        <n-space>
          <n-date-picker
            v-model:value="dateRange"
            type="daterange"
            clearable
          />
          <n-button type="primary">
            📊 Сформировать отчёт
          </n-button>
        </n-space>
      </template>
    </n-page-header>

    <n-grid :cols="3" :x-gap="16" :y-gap="16" style="margin-top: 24px">
      <!-- Financial reports -->
      <n-grid-item>
        <n-card title="📈 Финансовые отчёты" hoverable @click="selectReport('financial')">
          <n-text depth="3">Доходы, расходы, прибыль</n-text>
        </n-card>
      </n-grid-item>

      <!-- Patient reports -->
      <n-grid-item>
        <n-card title="👥 Отчёты по пациентам" hoverable @click="selectReport('patients')">
          <n-text depth="3">Новые пациенты, активность, демография</n-text>
        </n-card>
      </n-grid-item>

      <!-- Service reports -->
      <n-grid-item>
        <n-card title="🦷 Отчёты по услугам" hoverable @click="selectReport('services')">
          <n-text depth="3">Популярные услуги, выручка по услугам</n-text>
        </n-card>
      </n-grid-item>

      <!-- Staff reports -->
      <n-grid-item>
        <n-card title="👨‍⚕️ Отчёты по персоналу" hoverable @click="selectReport('staff')">
          <n-text depth="3">Загрузка врачей, эффективность</n-text>
        </n-card>
      </n-grid-item>

      <!-- Warehouse reports -->
      <n-grid-item>
        <n-card title="📦 Складские отчёты" hoverable @click="selectReport('warehouse')">
          <n-text depth="3">Остатки, движение, себестоимость</n-text>
        </n-card>
      </n-grid-item>

      <!-- Marketing reports -->
      <n-grid-item>
        <n-card title="📢 Маркетинговые отчёты" hoverable @click="selectReport('marketing')">
          <n-text depth="3">Источники, конверсия, ROI</n-text>
        </n-card>
      </n-grid-item>
    </n-grid>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useMessage } from 'naive-ui'

const message = useMessage()
const dateRange = ref(null)

function selectReport(type) {
  message.info(`Формирование отчёта: ${type}`)
  // TODO: Open report builder
}
</script>

<style scoped>
.reports-page {
  padding: 24px;
  background: #121212;
  min-height: 100vh;
}

:deep(.n-page-header) {
  color: #e0e0e0;
}

:deep(.n-card) {
  background-color: #1e1e1e;
  color: #e0e0e0;
  cursor: pointer;
  transition: all 0.3s;
}

:deep(.n-card:hover) {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
  background-color: #252525;
}
</style>
