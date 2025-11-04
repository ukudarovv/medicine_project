<template>
  <n-modal
    v-model:show="visible"
    :title="isEdit ? 'Редактировать шаблон ЗП' : 'Новый шаблон ЗП'"
    preset="card"
    style="width: 700px"
  >
    <n-scrollbar style="max-height: 70vh">
      <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
        <n-form-item label="Название шаблона" path="name">
          <n-input v-model:value="formData.name" placeholder="Например: Врач-стоматолог базовая ставка" />
        </n-form-item>

        <n-divider title-placement="left">Комиссии</n-divider>

        <n-space vertical>
          <n-checkbox v-model:checked="formData.pct_of_own_sales">
            Процент от собственных продаж
          </n-checkbox>
          <n-form-item v-if="formData.pct_of_own_sales" label="Процент комиссии, %">
            <n-input-number
              v-model:value="formData.pct_value"
              :min="0"
              :max="100"
              placeholder="0"
              style="width: 100%"
            />
          </n-form-item>

          <n-checkbox v-model:checked="formData.direction_bonus_enabled">
            Бонус за направление
          </n-checkbox>
          <n-form-item v-if="formData.direction_bonus_enabled" label="Процент бонуса, %">
            <n-input-number
              v-model:value="formData.direction_bonus_pct"
              :min="0"
              :max="100"
              placeholder="0"
              style="width: 100%"
            />
          </n-form-item>

          <n-checkbox v-model:checked="formData.pct_per_created_visits_enabled">
            Процент за созданные визиты
          </n-checkbox>
          <n-form-item v-if="formData.pct_per_created_visits_enabled" label="Процент за визит, %">
            <n-input-number
              v-model:value="formData.pct_per_visit"
              :min="0"
              :max="100"
              placeholder="0"
              style="width: 100%"
            />
          </n-form-item>
        </n-space>

        <n-divider title-placement="left">Фиксированная ЗП и минимум</n-divider>

        <n-space vertical>
          <n-checkbox v-model:checked="formData.fixed_salary_enabled">
            Фиксированный оклад
          </n-checkbox>
          <n-grid :cols="2" :x-gap="12" v-if="formData.fixed_salary_enabled">
            <n-grid-item>
              <n-form-item label="Сумма оклада">
                <n-input-number
                  v-model:value="formData.fixed_amount"
                  :min="0"
                  placeholder="0"
                  style="width: 100%"
                />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="Валюта">
                <n-select
                  v-model:value="formData.currency"
                  :options="currencyOptions"
                  placeholder="Валюта"
                />
              </n-form-item>
            </n-grid-item>
          </n-grid>

          <n-checkbox v-model:checked="formData.min_rate_enabled">
            Минимальная ставка
          </n-checkbox>
          <n-form-item v-if="formData.min_rate_enabled" label="Минимальная сумма">
            <n-input-number
              v-model:value="formData.min_rate_amount"
              :min="0"
              placeholder="0"
              style="width: 100%"
            />
          </n-form-item>
        </n-space>

        <n-divider title-placement="left">Дополнительные настройки</n-divider>

        <n-space vertical>
          <n-checkbox v-model:checked="formData.honor_patient_discount_enabled">
            Учитывать скидку пациенту
          </n-checkbox>

          <n-checkbox v-model:checked="formData.subscription_services_pct_enabled">
            Процент от услуг по абонементам
          </n-checkbox>
          <n-form-item v-if="formData.subscription_services_pct_enabled" label="Процент от абонементов, %">
            <n-input-number
              v-model:value="formData.subscription_pct"
              :min="0"
              :max="100"
              placeholder="0"
              style="width: 100%"
            />
          </n-form-item>

          <n-checkbox v-model:checked="formData.calc_from_profit_instead_of_revenue">
            Расчёт от прибыли вместо выручки
          </n-checkbox>
        </n-space>
      </n-form>
    </n-scrollbar>

    <template #footer>
      <n-space justify="end">
        <n-button @click="handleClose">Отмена</n-button>
        <n-button type="primary" @click="handleSave" :loading="saving">
          Сохранить
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import apiClient from '@/api/axios'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  template: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const authStore = useAuthStore()
const formRef = ref(null)
const saving = ref(false)

const isEdit = computed(() => !!props.template)

const visible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

const formData = ref({
  name: '',
  pct_of_own_sales: false,
  pct_value: null,
  direction_bonus_enabled: false,
  direction_bonus_pct: null,
  pct_per_created_visits_enabled: false,
  pct_per_visit: null,
  fixed_salary_enabled: false,
  fixed_amount: null,
  currency: 'KZT',
  min_rate_enabled: false,
  min_rate_amount: null,
  honor_patient_discount_enabled: false,
  subscription_services_pct_enabled: false,
  subscription_pct: null,
  calc_from_profit_instead_of_revenue: false
})

const rules = {
  name: { required: true, message: 'Введите название шаблона', trigger: 'blur' }
}

const currencyOptions = [
  { label: '₸ Тенге (KZT)', value: 'KZT' },
  { label: '₽ Рубль (RUB)', value: 'RUB' },
  { label: '$ Доллар (USD)', value: 'USD' },
  { label: '€ Евро (EUR)', value: 'EUR' }
]

watch(
  () => props.template,
  (newVal) => {
    if (newVal) {
      formData.value = {
        name: newVal.name || '',
        pct_of_own_sales: newVal.pct_of_own_sales || false,
        pct_value: newVal.pct_value || null,
        direction_bonus_enabled: newVal.direction_bonus_enabled || false,
        direction_bonus_pct: newVal.direction_bonus_pct || null,
        pct_per_created_visits_enabled: newVal.pct_per_created_visits_enabled || false,
        pct_per_visit: newVal.pct_per_visit || null,
        fixed_salary_enabled: newVal.fixed_salary_enabled || false,
        fixed_amount: newVal.fixed_amount || null,
        currency: newVal.currency || 'KZT',
        min_rate_enabled: newVal.min_rate_enabled || false,
        min_rate_amount: newVal.min_rate_amount || null,
        honor_patient_discount_enabled: newVal.honor_patient_discount_enabled || false,
        subscription_services_pct_enabled: newVal.subscription_services_pct_enabled || false,
        subscription_pct: newVal.subscription_pct || null,
        calc_from_profit_instead_of_revenue: newVal.calc_from_profit_instead_of_revenue || false
      }
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

function resetForm() {
  formData.value = {
    name: '',
    pct_of_own_sales: false,
    pct_value: null,
    direction_bonus_enabled: false,
    direction_bonus_pct: null,
    pct_per_created_visits_enabled: false,
    pct_per_visit: null,
    fixed_salary_enabled: false,
    fixed_amount: null,
    currency: 'KZT',
    min_rate_enabled: false,
    min_rate_amount: null,
    honor_patient_discount_enabled: false,
    subscription_services_pct_enabled: false,
    subscription_pct: null,
    calc_from_profit_instead_of_revenue: false
  }
}

function handleClose() {
  visible.value = false
  resetForm()
}

async function handleSave() {
  try {
    await formRef.value?.validate()
    saving.value = true

    const data = {
      organization: authStore.user?.organization,
      ...formData.value
    }

    if (isEdit.value) {
      await apiClient.patch(`/staff/salary-templates/${props.template.id}`, data)
      message.success('Шаблон ЗП обновлён')
    } else {
      await apiClient.post('/staff/salary-templates', data)
      message.success('Шаблон ЗП создан')
    }

    emit('saved')
    handleClose()
  } catch (error) {
    console.error('Error saving salary template:', error)
    message.error('Ошибка сохранения шаблона ЗП')
  } finally {
    saving.value = false
  }
}
</script>

