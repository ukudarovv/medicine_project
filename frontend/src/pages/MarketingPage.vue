<template>
  <div class="marketing-page">
    <div class="page-header">
      <h1>Маркетинг</h1>
      <div class="header-actions">
        <button @click="showReminderModal = true" class="btn-primary">
          + Напоминание
        </button>
        <button class="btn-secondary">+ Звонок-напоминание</button>
        <button @click="showSendMessageModal = true" class="btn-secondary">
          Отправить сообщение
        </button>
      </div>
    </div>

    <div class="tabs">
      <button
        class="tab"
        :class="{ active: activeTab === 'reminders' }"
        @click="activeTab = 'reminders'"
      >
        Напоминания
      </button>
      <button
        class="tab"
        :class="{ active: activeTab === 'campaigns' }"
        @click="activeTab = 'campaigns'"
      >
        Пользовательские рассылки
      </button>
    </div>

    <!-- Reminders Tab -->
    <div v-if="activeTab === 'reminders'" class="tab-content">
      <div class="filters">
        <div class="filter-group">
          <label>Период отчёта:</label>
          <input type="date" v-model="filters.period_from" />
          <span>—</span>
          <input type="date" v-model="filters.period_to" />
        </div>
        <button @click="loadReminders" class="btn-secondary">Применить</button>
        <button @click="resetFilters" class="btn-secondary">Сбросить</button>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Наименование</th>
              <th>Включено</th>
              <th>Тип</th>
              <th>Пациентов пришло</th>
              <th>Онлайн-записей</th>
              <th>Визитов всего</th>
              <th>Визитов на сумму</th>
              <th>Конверсия</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="9" class="loading-cell">Загрузка...</td>
            </tr>
            <tr v-else-if="validReminders.length === 0">
              <td colspan="9" class="empty-cell">Нет данных</td>
            </tr>
            <tr v-else v-for="reminder in validReminders" :key="reminder.id">
              <td class="name-cell">
                {{ reminder.name }}
                <small v-if="reminder.link_service_name">
                  {{ reminder.link_service_name }}
                </small>
              </td>
              <td>
                <label class="toggle-switch" @click.stop="toggleReminder(reminder)">
                  <input type="checkbox" :checked="reminder.enabled" />
                  <span class="slider"></span>
                </label>
              </td>
              <td>
                <span class="type-badge">{{ reminder.type_display }}</span>
              </td>
              <td class="number-cell">{{ reminder.sent_count }}</td>
              <td class="number-cell">{{ reminder.online_bookings_count }}</td>
              <td class="number-cell">{{ reminder.visit_count }}</td>
              <td class="number-cell">{{ formatMoney(reminder.visit_amount) }}</td>
              <td class="number-cell">
                <span
                  class="conversion-badge"
                  :class="getConversionClass(reminder.conversion_rate)"
                >
                  {{ reminder.conversion_rate }}%
                </span>
              </td>
              <td class="actions-cell">
                <button @click="editReminder(reminder)" class="btn-icon" title="Редактировать">
                  ✏️
                </button>
                <button @click="duplicateReminder(reminder)" class="btn-icon" title="Копировать">
                  📋
                </button>
                <button @click="deleteReminder(reminder)" class="btn-icon" title="Удалить">
                  🗑️
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Campaigns Tab -->
    <div v-if="activeTab === 'campaigns'" class="tab-content">
      <div class="filters">
        <div class="filter-group">
          <label>Статус:</label>
          <select v-model="campaignFilters.status" class="filter-select">
            <option value="">Все</option>
            <option value="draft">Черновик</option>
            <option value="scheduled">Запланирована</option>
            <option value="running">Выполняется</option>
            <option value="paused">Приостановлена</option>
            <option value="finished">Завершена</option>
            <option value="failed">Ошибка</option>
          </select>
        </div>
        <button @click="loadCampaigns" class="btn-secondary">Применить</button>
        <button @click="resetCampaignFilters" class="btn-secondary">Сбросить</button>
        <button @click="showCampaignModal = true" class="btn-primary">+ Новая рассылка</button>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Наименование</th>
              <th>Статус</th>
              <th>Канал</th>
              <th>Получателей</th>
              <th>Отправлено</th>
              <th>Доставлено</th>
              <th>Визитов</th>
              <th>Сумма</th>
              <th>Конверсия</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="campaignsLoading">
              <td colspan="10" class="loading-cell">Загрузка...</td>
            </tr>
            <tr v-else-if="validCampaigns.length === 0">
              <td colspan="10" class="empty-cell">Нет данных</td>
            </tr>
            <tr v-else v-for="campaign in validCampaigns" :key="campaign.id">
              <td class="name-cell">{{ campaign.title }}</td>
              <td>
                <span class="status-badge" :class="campaign.status">
                  {{ getStatusLabel(campaign.status) }}
                </span>
              </td>
              <td>{{ campaign.channel.toUpperCase() }}</td>
              <td class="number-cell">{{ campaign.total_recipients }}</td>
              <td class="number-cell">{{ campaign.sent_count }}</td>
              <td class="number-cell">{{ campaign.delivered_count }}</td>
              <td class="number-cell">{{ campaign.visit_count }}</td>
              <td class="number-cell">{{ formatMoney(campaign.visit_amount) }}</td>
              <td class="number-cell">
                <span
                  class="conversion-badge"
                  :class="getConversionClass(campaign.conversion_rate)"
                >
                  {{ campaign.conversion_rate }}%
                </span>
              </td>
              <td class="actions-cell">
                <button @click="exportCampaign(campaign)" class="btn-icon" title="Экспорт">
                  📥
                </button>
                <button
                  v-if="campaign.status === 'running'"
                  @click="pauseCampaign(campaign)"
                  class="btn-icon"
                  title="Приостановить"
                >
                  ⏸
                </button>
                <button
                  v-if="campaign.status === 'paused'"
                  @click="resumeCampaign(campaign)"
                  class="btn-icon"
                  title="Продолжить"
                >
                  ▶
                </button>
                <button @click="deleteCampaign(campaign)" class="btn-icon" title="Удалить">
                  🗑️
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modals -->
    <ReminderModal
      :visible="showReminderModal"
      :reminder="currentReminder"
      @close="closeReminderModal"
      @success="handleSuccess"
      @error="handleError"
    />
    
    <CampaignModal
      :visible="showCampaignModal"
      :campaign="currentCampaign"
      @close="closeCampaignModal"
      @success="handleSuccess"
      @error="handleError"
      @campaign-created="handleCampaignCreated"
    />
    
    <SendMessageModal
      :visible="showSendMessageModal"
      @close="showSendMessageModal = false"
      @success="handleSuccess"
      @error="handleError"
    />

    <!-- Notifications -->
    <div v-if="notification" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>
  </div>
</template>

<script>
import ReminderModal from '@/components/ReminderModal.vue'
import CampaignModal from '@/components/CampaignModal.vue'
import SendMessageModal from '@/components/SendMessageModal.vue'
import { 
  getReminders, deleteReminder as deleteReminderApi, toggleReminder,
  getCampaigns, deleteCampaign as deleteCampaignApi, pauseCampaign as pauseCampaignApi,
  resumeCampaign as resumeCampaignApi, exportCampaign as exportCampaignApi
} from '@/api/marketing'

export default {
  name: 'MarketingPage',
  components: {
    ReminderModal,
    CampaignModal,
    SendMessageModal,
  },
  data() {
    return {
      activeTab: 'reminders',
      loading: false,
      reminders: [],
      campaigns: [],
      campaignsLoading: false,
      showReminderModal: false,
      showCampaignModal: false,
      showSendMessageModal: false,
      currentReminder: null,
      currentCampaign: null,
      notification: null,
      filters: {
        period_from: '',
        period_to: '',
      },
      campaignFilters: {
        status: '',
      },
    }
  },
  computed: {
    validReminders() {
      return this.reminders.filter(r => r && r.id)
    },
    validCampaigns() {
      return this.campaigns.filter(c => c && c.id)
    },
  },
  mounted() {
    this.loadReminders()
    this.loadCampaigns()
  },
  watch: {
    activeTab(val) {
      if (val === 'campaigns') {
        this.loadCampaigns()
      } else if (val === 'reminders') {
        this.loadReminders()
      }
    },
  },
  methods: {
    async loadReminders() {
      this.loading = true
      try {
        const params = {}
        if (this.filters.period_from) params.period_from = this.filters.period_from
        if (this.filters.period_to) params.period_to = this.filters.period_to

        const response = await getReminders(params)
        // Handle both paginated and non-paginated responses
        this.reminders = Array.isArray(response.data) 
          ? response.data 
          : (response.data?.results || [])
      } catch (error) {
        console.error('Error loading reminders:', error)
        this.handleError('Ошибка загрузки напоминаний')
        this.reminders = []
      } finally {
        this.loading = false
      }
    },
    resetFilters() {
      this.filters = {
        period_from: '',
        period_to: '',
      }
      this.loadReminders()
    },
    async toggleReminder(reminder) {
      try {
        const response = await toggleReminder(reminder.id)
        reminder.enabled = response.data.enabled
        this.handleSuccess('Статус изменён')
      } catch (error) {
        console.error('Error toggling reminder:', error)
        this.handleError('Ошибка изменения статуса')
      }
    },
    editReminder(reminder) {
      this.currentReminder = reminder
      this.showReminderModal = true
    },
    duplicateReminder(reminder) {
      this.currentReminder = {
        ...reminder,
        id: null,
        name: `${reminder.name} (копия)`,
      }
      this.showReminderModal = true
    },
    async deleteReminder(reminder) {
      if (!confirm(`Удалить напоминание "${reminder.name}"?`)) return

      try {
        await deleteReminderApi(reminder.id)
        this.handleSuccess('Напоминание удалено')
        this.loadReminders()
      } catch (error) {
        console.error('Error deleting reminder:', error)
        this.handleError('Ошибка удаления')
      }
    },
    closeReminderModal() {
      this.showReminderModal = false
      this.currentReminder = null
    },
    
    // Campaign methods
    async loadCampaigns() {
      this.campaignsLoading = true
      try {
        const params = {}
        if (this.campaignFilters.status) params.status = this.campaignFilters.status

        const response = await getCampaigns(params)
        // Handle both paginated and non-paginated responses
        this.campaigns = Array.isArray(response.data) 
          ? response.data 
          : (response.data?.results || [])
      } catch (error) {
        console.error('Error loading campaigns:', error)
        this.handleError('Ошибка загрузки кампаний')
        this.campaigns = []
      } finally {
        this.campaignsLoading = false
      }
    },
    resetCampaignFilters() {
      this.campaignFilters = { status: '' }
      this.loadCampaigns()
    },
    async pauseCampaign(campaign) {
      try {
        await pauseCampaignApi(campaign.id)
        campaign.status = 'paused'
        this.handleSuccess('Кампания приостановлена')
      } catch (error) {
        console.error('Error pausing campaign:', error)
        this.handleError('Ошибка приостановки')
      }
    },
    async resumeCampaign(campaign) {
      try {
        await resumeCampaignApi(campaign.id)
        campaign.status = 'running'
        this.handleSuccess('Кампания возобновлена')
      } catch (error) {
        console.error('Error resuming campaign:', error)
        this.handleError('Ошибка возобновления')
      }
    },
    async exportCampaign(campaign) {
      try {
        const response = await exportCampaignApi(campaign.id)
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `campaign_${campaign.id}_results.xlsx`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        this.handleSuccess('Экспорт завершён')
      } catch (error) {
        console.error('Error exporting campaign:', error)
        this.handleError('Ошибка экспорта')
      }
    },
    async deleteCampaign(campaign) {
      if (!confirm(`Удалить кампанию "${campaign.title}"?`)) return

      try {
        await deleteCampaignApi(campaign.id)
        this.handleSuccess('Кампания удалена')
        this.loadCampaigns()
      } catch (error) {
        console.error('Error deleting campaign:', error)
        this.handleError('Ошибка удаления')
      }
    },
    closeCampaignModal() {
      this.showCampaignModal = false
      this.currentCampaign = null
    },
    handleCampaignCreated(campaign) {
      this.currentCampaign = campaign
    },
    
    // Common methods
    handleSuccess(message) {
      this.notification = { type: 'success', message }
      setTimeout(() => (this.notification = null), 3000)
      if (this.activeTab === 'reminders') {
        this.loadReminders()
      } else if (this.activeTab === 'campaigns') {
        this.loadCampaigns()
      }
    },
    handleError(message) {
      this.notification = { type: 'error', message }
      setTimeout(() => (this.notification = null), 5000)
    },
    formatMoney(amount) {
      if (!amount) return '0 ₸'
      return `${Number(amount).toLocaleString()} ₸`
    },
    getConversionClass(rate) {
      if (rate >= 10) return 'high'
      if (rate >= 5) return 'medium'
      return 'low'
    },
    getStatusLabel(status) {
      const labels = {
        draft: 'Черновик',
        scheduled: 'Запланирована',
        running: 'Выполняется',
        paused: 'Приостановлена',
        finished: 'Завершена',
        failed: 'Ошибка',
      }
      return labels[status] || status
    },
  },
}
</script>

<style scoped lang="scss">
@import '@/styles/tokens.scss';

.marketing-page {
  padding: $spacing-lg;
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-lg;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: $text-primary;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: $radius-md;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: $primary-color;
  color: #fff;
}

.btn-primary:hover {
  background: darken($primary-color, 10%);
}

.btn-secondary {
  background: $bg-tertiary;
  color: $text-primary;
  border: 1px solid $border-color;
}

.btn-secondary:hover {
  background: lighten($bg-tertiary, 5%);
}

.tabs {
  display: flex;
  gap: 0;
  border-bottom: 2px solid $border-color;
  margin-bottom: $spacing-lg;
}

.tab {
  padding: 12px 24px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 500;
  color: $text-secondary;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}

.tab:hover {
  color: $primary-color;
}

.tab.active {
  color: $primary-color;
  border-bottom-color: $primary-color;
}

.filters {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 16px;
  background: $bg-secondary;
  border-radius: $radius-md;
  margin-bottom: $spacing-lg;
  border: 1px solid $border-color;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 14px;
  font-weight: 500;
  color: $text-primary;
}

.filter-group input[type="date"],
.filter-group .filter-select {
  padding: 6px 12px;
  border: 1px solid $border-color;
  border-radius: $radius-sm;
  font-size: 14px;
  min-width: 180px;
  background: $bg-tertiary;
  color: $text-primary;
}

.table-container {
  background: $bg-secondary;
  border-radius: $radius-md;
  overflow: hidden;
  box-shadow: $shadow-sm;
  border: 1px solid $border-color;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: $bg-tertiary;
  border-bottom: 2px solid $border-color;
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: $text-secondary;
  text-transform: uppercase;
}

.data-table td {
  padding: 16px;
  border-bottom: 1px solid $border-color;
  font-size: 14px;
  color: $text-primary;
}

.data-table tbody tr:hover {
  background: $bg-tertiary;
}

.name-cell {
  font-weight: 500;
}

.name-cell small {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: $text-secondary;
}

.number-cell {
  text-align: right;
}

.type-badge {
  display: inline-block;
  padding: 4px 12px;
  background: $bg-tertiary;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  color: $text-primary;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.draft {
  background: $status-draft;
  color: #fff;
}

.status-badge.scheduled {
  background: $status-in-progress;
  color: #fff;
}

.status-badge.running {
  background: $status-booked;
  color: #fff;
}

.status-badge.paused {
  background: $status-in-progress;
  color: #fff;
}

.status-badge.finished {
  background: $status-done;
  color: #fff;
}

.status-badge.failed {
  background: $status-no-show;
  color: #fff;
}

.conversion-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.conversion-badge.high {
  background: rgba(76, 175, 80, 0.2);
  color: $status-done;
}

.conversion-badge.medium {
  background: rgba(255, 152, 0, 0.2);
  color: $status-in-progress;
}

.conversion-badge.low {
  background: rgba(244, 67, 54, 0.2);
  color: $status-no-show;
}

.actions-cell {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.btn-icon {
  padding: 4px 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 16px;
  transition: transform 0.2s;
}

.btn-icon:hover {
  transform: scale(1.2);
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  cursor: pointer;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: $border-color;
  transition: 0.3s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: '';
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: $status-done;
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.loading-cell,
.empty-cell {
  text-align: center;
  padding: 48px;
  color: $text-secondary;
  font-style: italic;
}

.coming-soon {
  text-align: center;
  padding: 64px;
  color: $text-secondary;
  font-size: 16px;
}

.notification {
  position: fixed;
  top: 24px;
  right: 24px;
  padding: 16px 24px;
  border-radius: $radius-md;
  font-size: 14px;
  font-weight: 500;
  box-shadow: $shadow-md;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

.notification.success {
  background: rgba(76, 175, 80, 0.9);
  color: #fff;
}

.notification.error {
  background: rgba(244, 67, 54, 0.9);
  color: #fff;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
