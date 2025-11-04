<template>
  <div class="patient-card-header" :class="{ sticky: isSticky }">
    <n-card :bordered="false" size="small">
      <n-space justify="space-between" align="center">
        <!-- Left: Patient Info -->
        <n-space align="center" size="large">
          <n-avatar
            :size="64"
            :src="patient.photo_url"
            :style="{ backgroundColor: patient.sex === 'M' ? '#2196F3' : '#E91E63' }"
          >
            {{ patient.full_name?.charAt(0) || '?' }}
          </n-avatar>
          
          <div>
            <h2 style="margin: 0; font-size: 20px;">{{ patient.full_name }}</h2>
            <n-space size="small" style="margin-top: 4px;">
              <n-text depth="3">{{ patient.age }} лет</n-text>
              <n-divider vertical />
              <n-text depth="3">{{ patient.sex === 'M' ? 'Муж.' : 'Жен.' }}</n-text>
              <n-divider vertical />
              <n-text depth="3">
                ИИН: {{ patient.iin || 'не указан' }}
                <n-tag v-if="patient.iin_verified" type="success" size="tiny" style="margin-left: 4px;">
                  ✓
                </n-tag>
              </n-text>
            </n-space>
            <n-space size="small" style="margin-top: 4px;">
              <n-button text type="primary" size="small" @click="callPatient">
                📞 {{ patient.phone }}
              </n-button>
              <n-divider vertical />
              <n-tag v-if="patient.osms_status === 'insured'" type="success" size="small">
                ОСМС: Застрахован
              </n-tag>
              <n-tag v-else-if="patient.osms_status === 'not_insured'" type="warning" size="small">
                ОСМС: Не застрахован
              </n-tag>
            </n-space>
          </div>
        </n-space>

        <!-- Right: Actions -->
        <n-space>
          <n-tag :type="balanceType" size="large">
            Баланс: {{ patient.balance || 0 }} ₸
          </n-tag>
          <n-button type="primary" @click="$emit('edit')">
            ✏️ Редактировать
          </n-button>
        </n-space>
      </n-space>
    </n-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  patient: {
    type: Object,
    required: true
  },
  isSticky: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['edit', 'call'])

const balanceType = computed(() => {
  const balance = parseFloat(props.patient.balance) || 0
  if (balance > 0) return 'success'
  if (balance < 0) return 'error'
  return 'default'
})

function callPatient() {
  emit('call', props.patient.phone)
  // Could integrate with phone system
  window.open(`tel:${props.patient.phone}`)
}
</script>

<style scoped lang="scss">
.patient-card-header {
  &.sticky {
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
}

:deep(.n-card) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  
  .n-text {
    color: rgba(255, 255, 255, 0.9) !important;
  }
  
  h2 {
    color: white;
  }
}
</style>

