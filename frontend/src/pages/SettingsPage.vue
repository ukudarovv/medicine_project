<template>
  <div class="settings-page">
    <div class="page-header">
      <h1>Настройки</h1>
    </div>

    <div class="page-content">
      <n-space vertical :size="24">
        <!-- Regional Settings -->
        <n-card title="Региональные настройки" :bordered="false">
          <n-form label-placement="left" label-width="200px">
            <n-form-item label="Страна">
              <n-input value="Казахстан" disabled />
            </n-form-item>
            
            <n-form-item label="Валюта">
              <n-space>
                <n-input value="KZT" disabled style="width: 100px" />
                <n-tag type="success">₸ Тенге</n-tag>
              </n-space>
            </n-form-item>
            
            <n-form-item label="Часовой пояс">
              <n-input value="Asia/Almaty" disabled />
            </n-form-item>
            
            <n-form-item label="Формат даты">
              <n-input value="dd.mm.yyyy" disabled />
            </n-form-item>
            
            <n-form-item label="Маска телефона">
              <n-input value="+7 7XX XXX-XX-XX" disabled />
            </n-form-item>
          </n-form>
        </n-card>

        <!-- Field Visibility -->
        <n-card title="Видимость полей" :bordered="false">
          <n-form label-placement="left" label-width="200px">
            <n-form-item label="Скрыть РФ-поля">
              <n-space vertical>
                <n-checkbox v-model:checked="hideRFFields">
                  Скрыть российские поля (ОМС, СНИЛС)
                </n-checkbox>
                <n-text depth="3" style="font-size: 12px;">
                  При включении данной опции поля специфичные для России будут скрыты в интерфейсе
                </n-text>
              </n-space>
            </n-form-item>
          </n-form>
        </n-card>

        <!-- System Info -->
        <n-card title="Информация о системе" :bordered="false">
          <n-descriptions label-placement="left" :column="1">
            <n-descriptions-item label="Версия">
              v1.2.0 (KZ Adaptation)
            </n-descriptions-item>
            <n-descriptions-item label="Backend API">
              {{ apiUrl }}
            </n-descriptions-item>
            <n-descriptions-item label="Адаптация">
              Казахстан (KZ Market)
            </n-descriptions-item>
            <n-descriptions-item label="Функции">
              <n-space size="small">
                <n-tag size="small" type="success">ИИН валидация</n-tag>
                <n-tag size="small" type="success">КАТО адреса</n-tag>
                <n-tag size="small" type="success">ОСМС</n-tag>
                <n-tag size="small" type="success">Медосмотры</n-tag>
                <n-tag size="small" type="success">Планы лечения</n-tag>
              </n-space>
            </n-descriptions-item>
          </n-descriptions>
        </n-card>

        <!-- Save Button -->
        <n-space justify="end">
          <n-button @click="handleReset">Сбросить</n-button>
          <n-button type="primary" @click="handleSave">Сохранить</n-button>
        </n-space>
      </n-space>
    </div>
    
    <router-view />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useMessage } from 'naive-ui'

const message = useMessage()

// Settings
const hideRFFields = ref(true)
const apiUrl = ref(import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1')

function handleSave() {
  // Save to localStorage
  localStorage.setItem('settings', JSON.stringify({
    hideRFFields: hideRFFields.value
  }))
  
  message.success('Настройки сохранены')
}

function handleReset() {
  hideRFFields.value = true
  message.info('Настройки сброшены')
}

// Load settings
function loadSettings() {
  try {
    const saved = localStorage.getItem('settings')
    if (saved) {
      const settings = JSON.parse(saved)
      hideRFFields.value = settings.hideRFFields ?? true
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}

loadSettings()
</script>

<style scoped lang="scss">
@import '@/styles/tokens.scss';

.settings-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: $bg-primary;
}

.page-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color;
  background: $bg-secondary;

  h1 {
    margin: 0;
    font-size: 24px;
    color: $text-primary;
  }
}

.page-content {
  flex: 1;
  padding: $spacing-lg;
  overflow: auto;
}
</style>

