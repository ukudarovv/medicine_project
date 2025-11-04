<template>
  <n-modal
    v-model:show="visible"
    :title="title"
    :preset="preset"
    :style="{ width: width }"
    @after-leave="handleAfterLeave"
  >
    <slot></slot>
    
    <template #footer v-if="$slots.footer || showDefaultFooter">
      <slot name="footer">
        <div class="modal-footer" v-if="showDefaultFooter">
          <n-button @click="handleCancel" :disabled="loading">
            Отмена
          </n-button>
          <n-button type="primary" @click="handleConfirm" :loading="loading">
            {{ confirmText }}
          </n-button>
        </div>
      </slot>
    </template>
  </n-modal>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    default: ''
  },
  width: {
    type: String,
    default: '960px'
  },
  preset: {
    type: String,
    default: 'card'
  },
  loading: {
    type: Boolean,
    default: false
  },
  showDefaultFooter: {
    type: Boolean,
    default: true
  },
  confirmText: {
    type: String,
    default: 'Сохранить'
  }
})

const emit = defineEmits(['update:show', 'confirm', 'cancel', 'after-leave'])

const visible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

function handleConfirm() {
  emit('confirm')
}

function handleCancel() {
  emit('cancel')
  visible.value = false
}

function handleAfterLeave() {
  emit('after-leave')
}
</script>

<style scoped lang="scss">
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>

