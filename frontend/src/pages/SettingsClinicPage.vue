<template>
  <div class="settings-clinic">
    <n-card title="Информация о клинике">
      <n-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-placement="left"
        label-width="180"
      >
        <n-divider title-placement="left">Реквизиты</n-divider>
        
        <n-form-item label="Юридическое название" path="legal_name">
          <n-input v-model:value="formData.legal_name" placeholder="ООО «Название»" />
        </n-form-item>
        
        <n-form-item label="ИНН" path="inn">
          <n-input v-model:value="formData.inn" placeholder="1234567890" />
        </n-form-item>
        
        <n-form-item label="КПП" path="kpp">
          <n-input v-model:value="formData.kpp" placeholder="123456789" />
        </n-form-item>
        
        <n-form-item label="ОГРН" path="ogrn">
          <n-input v-model:value="formData.ogrn" placeholder="1234567890123" />
        </n-form-item>
        
        <n-form-item label="Юридический адрес" path="legal_address">
          <n-input
            v-model:value="formData.legal_address"
            type="textarea"
            :rows="2"
            placeholder="Адрес"
          />
        </n-form-item>
        
        <n-divider title-placement="left">Контакты</n-divider>
        
        <n-form-item label="Веб-сайт" path="website">
          <n-input v-model:value="formData.website" placeholder="https://example.com" />
        </n-form-item>
        
        <n-form-item label="Email поддержки" path="support_email">
          <n-input v-model:value="formData.support_email" placeholder="support@example.com" />
        </n-form-item>
        
        <n-form-item label="Телефон поддержки" path="support_phone">
          <n-input v-model:value="formData.support_phone" placeholder="+7 (XXX) XXX-XX-XX" />
        </n-form-item>
        
        <n-divider title-placement="left">Лицензия</n-divider>
        
        <n-form-item label="Номер лицензии" path="license_number">
          <n-input v-model:value="formData.license_number" placeholder="№ XXXXX" />
        </n-form-item>
        
        <n-form-item label="Дата выдачи" path="license_issued_date">
          <n-date-picker v-model:value="formData.license_issued_date" type="date" />
        </n-form-item>
        
        <n-form-item label="Кем выдана" path="license_issued_by">
          <n-input
            v-model:value="formData.license_issued_by"
            type="textarea"
            :rows="2"
            placeholder="Орган выдачи"
          />
        </n-form-item>
        
        <n-form-item>
          <n-space>
            <n-button type="primary" @click="handleSave" :loading="loading">
              Сохранить
            </n-button>
            <n-button @click="handleReset">
              Сбросить
            </n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import apiClient from '@/api/axios'

const message = useMessage()
const formRef = ref(null)
const loading = ref(false)

const formData = ref({
  legal_name: '',
  inn: '',
  kpp: '',
  ogrn: '',
  legal_address: '',
  website: '',
  support_email: '',
  support_phone: '',
  license_number: '',
  license_issued_date: null,
  license_issued_by: ''
})

const rules = {
  legal_name: { required: true, message: 'Введите юридическое название', trigger: 'blur' },
  inn: { required: true, message: 'Введите ИНН', trigger: 'blur' },
  support_email: { type: 'email', message: 'Некорректный email', trigger: 'blur' }
}

async function loadData() {
  try {
    loading.value = true
    const response = await apiClient.get('/org/clinic-info')
    if (response.data) {
      Object.assign(formData.value, response.data)
      if (response.data.license_issued_date) {
        formData.value.license_issued_date = new Date(response.data.license_issued_date).getTime()
      }
    }
  } catch (error) {
    console.error('Error loading clinic info:', error)
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  try {
    await formRef.value?.validate()
    loading.value = true
    
    const data = { ...formData.value }
    if (data.license_issued_date) {
      data.license_issued_date = new Date(data.license_issued_date).toISOString().split('T')[0]
    }
    
    await apiClient.patch('/org/clinic-info', data)
    message.success('Информация сохранена')
  } catch (error) {
    if (error.response) {
      message.error('Ошибка сохранения: ' + JSON.stringify(error.response.data))
    } else {
      console.error('Save error:', error)
    }
  } finally {
    loading.value = false
  }
}

function handleReset() {
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.settings-clinic {
  margin-top: 16px;
}
</style>
