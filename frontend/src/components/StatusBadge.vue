<template>
  <span class="status-badge" :class="`status-${status}`">
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: ''
  }
})

const statusLabels = {
  draft: 'Черновик',
  booked: 'Забронировано',
  confirmed: 'Подтверждено',
  in_progress: 'В процессе',
  done: 'Выполнено',
  no_show: 'Не пришёл',
  canceled: 'Отменено',
  pending: 'Ожидает',
  paid: 'Оплачен',
  completed: 'Завершён'
}

const label = computed(() => props.label || statusLabels[props.status] || props.status)
</script>

<style scoped lang="scss">
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-draft {
  background: #9E9E9E;
  color: #FFFFFF;
}

.status-booked {
  background: #2196F3;
  color: #FFFFFF;
}

.status-confirmed {
  background: #00C2A8;
  color: #FFFFFF;
}

.status-in_progress {
  background: #FF9800;
  color: #FFFFFF;
}

.status-done, .status-completed {
  background: #4CAF50;
  color: #FFFFFF;
}

.status-no_show {
  background: #F44336;
  color: #FFFFFF;
}

.status-canceled {
  background: #FFCDD2;
  color: #D32F2F;
}

.status-pending {
  background: #FFC107;
  color: #000000;
}

.status-paid {
  background: #4CAF50;
  color: #FFFFFF;
}
</style>

