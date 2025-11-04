<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    title="Поиск"
    style="width: 700px"
    :segmented="{ content: 'soft' }"
  >
    <n-input
      ref="searchInputRef"
      v-model:value="searchQuery"
      placeholder="Поиск пациентов, услуг, диагнозов..."
      clearable
      autofocus
      @keydown.down="focusNextResult"
      @keydown.up="focusPrevResult"
      @keydown.enter="selectResult"
    >
      <template #prefix>
        <span>🔍</span>
      </template>
    </n-input>

    <n-tabs v-model:value="activeTab" type="segment" style="margin-top: 20px">
      <n-tab-pane name="patients" tab="Пациенты">
        <n-list v-if="patientResults.length > 0" hoverable clickable>
          <n-list-item
            v-for="(patient, idx) in patientResults"
            :key="patient.id"
            @click="goToPatient(patient)"
          >
            <n-space justify="space-between" align="center">
              <div>
                <strong>{{ patient.full_name }}</strong>
                <div style="font-size: 12px; color: #999;">
                  {{ patient.phone }} | {{ patient.iin || 'ИИН не указан' }}
                </div>
              </div>
              <n-tag size="small" :type="patient.is_active ? 'success' : 'default'">
                {{ patient.is_active ? 'Активен' : 'Архив' }}
              </n-tag>
            </n-space>
          </n-list-item>
        </n-list>
        <n-empty v-else description="Пациенты не найдены" />
      </n-tab-pane>

      <n-tab-pane name="services" tab="Услуги">
        <n-list v-if="serviceResults.length > 0" hoverable clickable>
          <n-list-item
            v-for="service in serviceResults"
            :key="service.id"
            @click="selectService(service)"
          >
            <n-space justify="space-between" align="center">
              <div>
                <strong>{{ service.name }}</strong>
                <div style="font-size: 12px; color: #999;">
                  Код: {{ service.code }} | Цена: {{ service.base_price }} ₸
                </div>
              </div>
            </n-space>
          </n-list-item>
        </n-list>
        <n-empty v-else description="Услуги не найдены" />
      </n-tab-pane>

      <n-tab-pane name="actions" tab="Действия">
        <n-list hoverable clickable>
          <n-list-item @click="createPatient">
            <n-space>
              <span>➕</span>
              <strong>Создать нового пациента</strong>
            </n-space>
          </n-list-item>
          <n-list-item @click="openCalendar">
            <n-space>
              <span>📅</span>
              <strong>Открыть календарь</strong>
            </n-space>
          </n-list-item>
          <n-list-item @click="createVisit">
            <n-space>
              <span>🏥</span>
              <strong>Создать визит</strong>
            </n-space>
          </n-list-item>
        </n-list>
      </n-tab-pane>
    </n-tabs>

    <template #footer>
      <n-text depth="3" style="font-size: 11px;">
        Используйте ↑↓ для навигации, Enter для выбора, Esc для закрытия
      </n-text>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import apiClient from '@/api/axios'
import { useDebounceFn } from '@vueuse/core'

const router = useRouter()
const message = useMessage()

// Props & Emits
const props = defineProps({
  show: Boolean
})

const emit = defineEmits(['update:show', 'patientSelected', 'serviceSelected'])

const visible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val)
})

// State
const searchQuery = ref('')
const activeTab = ref('patients')
const searchInputRef = ref(null)

const patientResults = ref([])
const serviceResults = ref([])
const selectedIndex = ref(0)

// Debounced search
const performSearch = useDebounceFn(async () => {
  if (!searchQuery.value || searchQuery.value.length < 2) {
    patientResults.value = []
    serviceResults.value = []
    return
  }
  
  try {
    // Search patients
    const patientsResponse = await apiClient.get('/patients/patients', {
      params: { search: searchQuery.value, page_size: 10 }
    })
    patientResults.value = patientsResponse.data.results || patientsResponse.data || []
    
    // Search services
    const servicesResponse = await apiClient.get('/services/services', {
      params: { search: searchQuery.value, page_size: 10 }
    })
    serviceResults.value = servicesResponse.data.results || servicesResponse.data || []
  } catch (error) {
    console.error('Search error:', error)
  }
}, 300)

// Watch search query
watch(searchQuery, () => {
  performSearch()
})

// Actions
function goToPatient(patient) {
  emit('patientSelected', patient)
  router.push({ name: 'patients', query: { id: patient.id } })
  visible.value = false
}

function selectService(service) {
  emit('serviceSelected', service)
  visible.value = false
}

function createPatient() {
  router.push({ name: 'patients', query: { action: 'new' } })
  visible.value = false
}

function openCalendar() {
  router.push({ name: 'schedule' })
  visible.value = false
}

function createVisit() {
  router.push({ name: 'visits', query: { action: 'new' } })
  visible.value = false
}

function focusNextResult() {
  // TODO: Implement keyboard navigation
}

function focusPrevResult() {
  // TODO: Implement keyboard navigation
}

function selectResult() {
  // TODO: Implement selection with Enter
}
</script>

<style scoped lang="scss">
.n-list-item {
  cursor: pointer;
  
  &:hover {
    background-color: #f5f5f5;
  }
}
</style>

