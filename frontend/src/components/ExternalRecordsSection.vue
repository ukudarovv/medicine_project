<template>
  <div class="external-records-section">
    <div class="section-header">
      <h3>📋 Записи из других медицинских организаций</h3>
      <n-button @click="loadRecords" :loading="loading" size="small">
        <template #icon>
          <n-icon><svg viewBox="0 0 24 24"><path fill="currentColor" d="M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z" /></svg></n-icon>
        </template>
        Обновить
      </n-button>
    </div>

    <div v-if="loading" class="loading-state">
      <n-spin size="large" />
      <p>Загрузка записей...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <n-alert type="error" :title="error" />
    </div>

    <div v-else-if="!hasRecords" class="empty-state">
      <div class="empty-icon">📄</div>
      <p>Нет записей из других организаций</p>
      <small>Записи появятся здесь, когда другие клиники внесут данные по согласованному доступу</small>
    </div>

    <div v-else class="records-content">
      <!-- Summary -->
      <div v-if="summary" class="summary-card">
        <div class="summary-item">
          <span class="label">Всего записей:</span>
          <span class="value">{{ summary.external_records }}</span>
        </div>
        <div class="summary-item">
          <span class="label">Организации:</span>
          <span class="value">{{ summary.organizations.length }}</span>
        </div>
        <div class="summary-item">
          <span class="label">Последнее обновление:</span>
          <span class="value">{{ formatDate(summary.last_updated) }}</span>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-bar">
        <n-select
          v-model:value="selectedOrganization"
          :options="organizationOptions"
          placeholder="Фильтр по организации"
          clearable
          style="width: 250px"
        />
        <n-select
          v-model:value="selectedRecordType"
          :options="recordTypeOptions"
          placeholder="Тип записи"
          clearable
          style="width: 200px"
        />
      </div>

      <!-- Records grouped by organization -->
      <div class="records-list">
        <div
          v-for="(orgRecords, orgName) in groupedRecords"
          :key="orgName"
          class="org-group"
        >
          <div class="org-header">
            <h4>🏥 {{ orgName }}</h4>
            <n-tag type="info" size="small">
              {{ orgRecords.length }} {{ pluralize(orgRecords.length, 'запись', 'записи', 'записей') }}
            </n-tag>
          </div>

          <div class="records-grid">
            <div
              v-for="record in orgRecords"
              :key="record.id"
              class="record-card"
              :class="{ 'is-external': record.is_external }"
              @click="openRecord(record)"
            >
              <div class="record-header">
                <span class="record-type-badge" :class="`type-${record.record_type}`">
                  {{ record.record_type_display }}
                </span>
                <span class="record-date">{{ formatDate(record.created_at) }}</span>
              </div>
              
              <div class="record-title">{{ record.title }}</div>
              
              <div class="record-meta">
                <span class="meta-item">
                  <n-icon size="14"><svg viewBox="0 0 24 24"><path fill="currentColor" d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z" /></svg></n-icon>
                  {{ record.author_name || 'Не указан' }}
                </span>
                <span class="meta-item external-badge">
                  <n-icon size="14"><svg viewBox="0 0 24 24"><path fill="currentColor" d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,16.5L6.5,12L7.91,10.59L11,13.67L16.59,8.09L18,9.5L11,16.5Z" /></svg></n-icon>
                  Внешняя запись
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Record Detail Modal -->
    <n-modal
      v-model:show="showDetailModal"
      preset="card"
      title="Медицинская запись"
      style="width: 800px"
    >
      <div v-if="selectedRecord" class="record-detail">
        <div class="detail-header">
          <n-tag :type="selectedRecord.is_external ? 'warning' : 'default'">
            {{ selectedRecord.record_type_display }}
          </n-tag>
          <span class="detail-date">{{ formatDateTime(selectedRecord.created_at) }}</span>
        </div>

        <div class="detail-section">
          <h4>Заголовок</h4>
          <p>{{ selectedRecord.title }}</p>
        </div>

        <div class="detail-section">
          <h4>Организация</h4>
          <p>{{ selectedRecord.organization_name }}</p>
        </div>

        <div class="detail-section" v-if="selectedRecord.author_name">
          <h4>Автор</h4>
          <p>{{ selectedRecord.author_name }}</p>
        </div>

        <div class="detail-section" v-if="selectedRecord.payload">
          <h4>Детали записи</h4>
          <pre class="payload-content">{{ JSON.stringify(selectedRecord.payload, null, 2) }}</pre>
        </div>

        <div class="detail-watermark" v-if="selectedRecord.is_external">
          🔒 Внешняя запись от {{ selectedRecord.organization_name }} • Только для чтения
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { format, parseISO } from 'date-fns'
import { ru } from 'date-fns/locale'
import { getEHRRecords, getPatientEHRSummary } from '@/api/ehr'

export default {
  name: 'ExternalRecordsSection',
  props: {
    patientId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const message = useMessage()
    
    const loading = ref(false)
    const error = ref(null)
    const records = ref([])
    const summary = ref(null)
    const selectedOrganization = ref(null)
    const selectedRecordType = ref(null)
    const showDetailModal = ref(false)
    const selectedRecord = ref(null)

    const recordTypeOptions = [
      { label: 'Запись визита', value: 'visit_note' },
      { label: 'Диагноз', value: 'diagnosis' },
      { label: 'Рецепт', value: 'prescription' },
      { label: 'Результат анализа', value: 'lab_result' },
      { label: 'Изображение', value: 'image' },
      { label: 'Документ', value: 'document' },
      { label: 'Процедура', value: 'procedure' },
      { label: 'Аллергия', value: 'allergy' },
      { label: 'Прививка', value: 'vaccination' }
    ]

    const hasRecords = computed(() => {
      return records.value.length > 0
    })

    const organizationOptions = computed(() => {
      const orgs = new Set(records.value.map(r => r.organization_name))
      return Array.from(orgs).map(name => ({
        label: name,
        value: name
      }))
    })

    const filteredRecords = computed(() => {
      let filtered = records.value

      if (selectedOrganization.value) {
        filtered = filtered.filter(r => r.organization_name === selectedOrganization.value)
      }

      if (selectedRecordType.value) {
        filtered = filtered.filter(r => r.record_type === selectedRecordType.value)
      }

      return filtered
    })

    const groupedRecords = computed(() => {
      const groups = {}
      
      filteredRecords.value.forEach(record => {
        const orgName = record.organization_name
        if (!groups[orgName]) {
          groups[orgName] = []
        }
        groups[orgName].push(record)
      })

      return groups
    })

    const loadRecords = async () => {
      loading.value = true
      error.value = null

      try {
        // Load summary
        const summaryData = await getPatientEHRSummary(props.patientId)
        summary.value = summaryData

        // Load external records only
        const recordsData = await getEHRRecords({
          patient_id: props.patientId,
          include_external: true
        })

        // Filter only external records
        records.value = (recordsData.results || recordsData).filter(r => r.is_external)
      } catch (err) {
        console.error('Error loading external records:', err)
        error.value = err.response?.data?.error || 'Ошибка загрузки записей'
        message.error(error.value)
      } finally {
        loading.value = false
      }
    }

    const openRecord = (record) => {
      selectedRecord.value = record
      showDetailModal.value = true
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      try {
        return format(parseISO(dateStr), 'dd.MM.yyyy', { locale: ru })
      } catch {
        return dateStr
      }
    }

    const formatDateTime = (dateStr) => {
      if (!dateStr) return '-'
      try {
        return format(parseISO(dateStr), 'dd.MM.yyyy HH:mm', { locale: ru })
      } catch {
        return dateStr
      }
    }

    const pluralize = (count, one, two, five) => {
      const n = Math.abs(count) % 100
      const n1 = n % 10
      if (n > 10 && n < 20) return five
      if (n1 > 1 && n1 < 5) return two
      if (n1 === 1) return one
      return five
    }

    onMounted(() => {
      loadRecords()
    })

    return {
      loading,
      error,
      records,
      summary,
      hasRecords,
      selectedOrganization,
      selectedRecordType,
      recordTypeOptions,
      organizationOptions,
      groupedRecords,
      showDetailModal,
      selectedRecord,
      loadRecords,
      openRecord,
      formatDate,
      formatDateTime,
      pluralize
    }
  }
}
</script>

<style scoped lang="scss">
.external-records-section {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h3 {
    margin: 0;
    color: #2c3e50;
    font-size: 18px;
  }
}

.loading-state,
.empty-state,
.error-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.summary-card {
  display: flex;
  gap: 30px;
  padding: 15px 20px;
  background: white;
  border-radius: 6px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 5px;

  .label {
    font-size: 13px;
    color: #7f8c8d;
  }

  .value {
    font-size: 20px;
    font-weight: 600;
    color: #2c3e50;
  }
}

.filters-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.org-group {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.org-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 12px;
  border-bottom: 2px solid #ecf0f1;

  h4 {
    margin: 0;
    color: #2c3e50;
    font-size: 16px;
  }
}

.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.record-card {
  padding: 15px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border-color: #3498db;
  }

  &.is-external {
    border-left: 3px solid #f39c12;
  }
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.record-type-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  color: white;

  &.type-visit_note { background: #3498db; }
  &.type-diagnosis { background: #e74c3c; }
  &.type-prescription { background: #9b59b6; }
  &.type-lab_result { background: #1abc9c; }
  &.type-image { background: #34495e; }
  &.type-document { background: #95a5a6; }
}

.record-date {
  font-size: 12px;
  color: #7f8c8d;
}

.record-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.record-meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 12px;
  color: #7f8c8d;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.external-badge {
  color: #f39c12;
  font-weight: 600;
}

.record-detail {
  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid #ecf0f1;
  }

  .detail-date {
    color: #7f8c8d;
    font-size: 14px;
  }

  .detail-section {
    margin-bottom: 20px;

    h4 {
      margin: 0 0 8px 0;
      color: #7f8c8d;
      font-size: 13px;
      font-weight: 600;
      text-transform: uppercase;
    }

    p {
      margin: 0;
      color: #2c3e50;
    }
  }

  .payload-content {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 13px;
    line-height: 1.6;
  }

  .detail-watermark {
    margin-top: 20px;
    padding: 12px;
    background: #fff3cd;
    border-left: 4px solid #f39c12;
    color: #856404;
    font-size: 13px;
    font-weight: 600;
    border-radius: 4px;
  }
}
</style>

