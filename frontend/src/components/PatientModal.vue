<template>
  <n-modal
    v-model:show="visible"
    :title="isEdit ? 'Редактировать пациента' : 'Новый пациент'"
    preset="card"
    style="width: 1100px"
    :segmented="{ content: 'soft' }"
  >
    <n-scrollbar style="max-height: 75vh">
      <!-- Tabs -->
      <n-tabs v-model:value="activeTab" type="line" animated>
        <!-- Общая информация -->
        <n-tab-pane name="general" tab="Общая информация">
          <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
            <!-- Медицинская карта -->
            <n-card title="Медицинская карта пациента № от дд.мм.гггг" :bordered="false">
              <n-button text type="primary">
                📎 Добавить вложения
              </n-button>
            </n-card>

            <!-- Основные данные -->
            <n-card title="Основные данные" :bordered="false" style="margin-top: 16px">
              <n-grid :cols="3" :x-gap="12">
                <n-grid-item>
                  <n-form-item label="Фамилия" path="last_name">
                    <n-input v-model:value="formData.last_name" placeholder="Фамилия" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item>
                  <n-form-item label="Имя" path="first_name">
                    <n-input v-model:value="formData.first_name" placeholder="Имя" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item>
                  <n-form-item label="Отчество" path="middle_name">
                    <n-input v-model:value="formData.middle_name" placeholder="Отчество" />
                  </n-form-item>
                </n-grid-item>
              </n-grid>

              <n-form-item label="Дата рождения" path="birth_date">
                <n-date-picker
                  v-model:value="formData.birth_date"
                  type="date"
                  placeholder="Выберите дату"
                  style="width: 100%"
                />
              </n-form-item>

              <n-form-item label="Пол" path="sex">
                <n-radio-group v-model:value="formData.sex">
                  <n-radio value="">Не указано</n-radio>
                  <n-radio value="M">Мужской</n-radio>
                  <n-radio value="F">Женский</n-radio>
                </n-radio-group>
              </n-form-item>

              <n-form-item label="Примечание к пациенту" path="notes">
                <n-input
                  v-model:value="formData.notes"
                  type="textarea"
                  :rows="3"
                  placeholder="Примечание"
                />
              </n-form-item>

              <n-button text type="primary">
                + Добавить представителя
              </n-button>
            </n-card>

            <!-- Контакты -->
            <n-card title="Контакты" :bordered="false" style="margin-top: 16px">
              <n-form-item label="Телефон" path="phone">
                <n-input v-model:value="formData.phone" placeholder="+7 (XXX) XXX-XX-XX" />
              </n-form-item>

              <n-form-item label="E-mail" path="email">
                <n-input v-model:value="formData.email" placeholder="email@example.com" />
              </n-form-item>

              <n-form-item label="Никнейм в Telegram">
                <n-input v-model:value="formData.telegram_nickname" placeholder="@username" />
              </n-form-item>

              <n-space vertical>
                <n-checkbox v-model:checked="formData.consent_newsletters">
                  Согласен на получение рассылки
                </n-checkbox>
                <n-checkbox v-model:checked="formData.consent_egisz">
                  Согласен на хранение и отправку данных в ЕГИСЗ
                </n-checkbox>
              </n-space>
            </n-card>

            <!-- Документы -->
            <n-card title="Документы" :bordered="false" style="margin-top: 16px">
              <n-form-item label="ИИН" path="iin">
                <n-input v-model:value="formData.iin" placeholder="Введите ИИН" />
              </n-form-item>

              <n-divider title-placement="left">Паспортные данные</n-divider>

              <n-grid :cols="2" :x-gap="12">
                <n-grid-item>
                  <n-form-item label="Серия">
                    <n-input v-model:value="formData.passport_series" placeholder="Серия" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item>
                  <n-form-item label="Номер">
                    <n-input v-model:value="formData.passport_number" placeholder="Номер" />
                  </n-form-item>
                </n-grid-item>
              </n-grid>

              <n-form-item label="Когда выдан">
                <n-date-picker
                  v-model:value="formData.passport_issued_date"
                  type="date"
                  style="width: 100%"
                />
              </n-form-item>

              <n-form-item label="Кем выдан">
                <n-input v-model:value="formData.passport_issued_by" placeholder="Орган выдачи" />
              </n-form-item>
            </n-card>

            <!-- Дисконтная карта -->
            <n-card title="Дисконтная карта" :bordered="false" style="margin-top: 16px">
              <n-grid :cols="2" :x-gap="12">
                <n-grid-item>
                  <n-form-item label="№ карты">
                    <n-input v-model:value="formData.discount_card" placeholder="Номер карты" />
                  </n-form-item>
                </n-grid-item>
                <n-grid-item>
                  <n-form-item label="Скидка, %">
                    <n-input-number
                      v-model:value="formData.discount_percent"
                      :min="0"
                      :max="100"
                      placeholder="0"
                      style="width: 100%"
                    />
                  </n-form-item>
                </n-grid-item>
              </n-grid>

              <n-text>Сумма покупок: {{ formData.balance || 0 }} ₸</n-text>
            </n-card>

            <!-- Адрес -->
            <n-card title="Адрес" :bordered="false" style="margin-top: 16px">
              <n-form-item label="Адрес" path="address">
                <n-input
                  v-model:value="formData.address"
                  type="textarea"
                  :rows="2"
                  placeholder="Введите адрес"
                />
              </n-form-item>
            </n-card>

            <!-- Анамнез -->
            <n-card title="Анамнез" :bordered="false" style="margin-top: 16px">
              <n-form-item label="Аллергические реакции">
                <n-input
                  v-model:value="formData.allergies"
                  type="textarea"
                  :rows="3"
                  placeholder="Опишите аллергии"
                />
              </n-form-item>

              <n-form-item label="Медицинская история">
                <n-input
                  v-model:value="formData.medical_history"
                  type="textarea"
                  :rows="4"
                  placeholder="Анамнез"
                />
              </n-form-item>
            </n-card>
          </n-form>
        </n-tab-pane>

        <!-- История болезни -->
        <n-tab-pane name="history" tab="История болезни">
          <n-card title="Визиты" :bordered="false">
            <template #header-extra>
              <n-button type="primary" size="small">
                + Новый визит
              </n-button>
            </template>
            <n-empty v-if="!isEdit" description="Пока ни одного визита не назначено">
              <template #extra>
                <n-text>
                  Вы можете создать первый визит пациента после сохранения карточки
                </n-text>
              </template>
            </n-empty>
          </n-card>
        </n-tab-pane>

        <!-- Медосмотры -->
        <n-tab-pane name="examinations" tab="Медосмотры">
          <n-card :bordered="false">
            <n-button type="primary">
              + Новый медосмотр
            </n-button>
            <n-empty
              style="margin-top: 24px"
              description="В этом разделе будут храниться карты медосмотра. Пока ни одной карты не добавлено."
            />
          </n-card>
        </n-tab-pane>

        <!-- Планы лечения -->
        <n-tab-pane name="plans" tab="Планы лечения">
          <n-empty description="Планы лечения будут добавлены позже" />
        </n-tab-pane>

        <!-- Статистика -->
        <n-tab-pane name="stats" tab="Статистика">
          <n-empty description="Статистика визитов и лечения" />
        </n-tab-pane>

        <!-- История контактов -->
        <n-tab-pane name="contacts" tab="История контактов">
          <n-empty description="История взаимодействий с пациентом" />
        </n-tab-pane>
      </n-tabs>
    </n-scrollbar>

    <template #footer>
      <n-space justify="end">
        <n-button @click="handleClose">Отмена</n-button>
        <n-button type="warning" @click="handleSave(false)" :loading="saving">
          Сохранить
        </n-button>
        <n-button type="primary" @click="handleSave(true)" :loading="saving">
          Сохранить и закрыть
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
  patient: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const authStore = useAuthStore()
const formRef = ref(null)
const saving = ref(false)
const activeTab = ref('general')

const isEdit = computed(() => !!props.patient)

const visible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

// Form data
const formData = ref({
  organization: null,
  first_name: '',
  last_name: '',
  middle_name: '',
  birth_date: null,
  sex: '',
  phone: '',
  email: '',
  address: '',
  iin: '',
  passport_series: '',
  passport_number: '',
  passport_issued_by: '',
  passport_issued_date: null,
  notes: '',
  allergies: '',
  medical_history: '',
  discount_card: '',
  discount_percent: 0,
  balance: 0,
  telegram_nickname: '',
  consent_newsletters: false,
  consent_egisz: false
})

const rules = {
  first_name: { required: true, message: 'Введите имя', trigger: 'blur' },
  last_name: { required: true, message: 'Введите фамилию', trigger: 'blur' },
  birth_date: { required: true, type: 'number', message: 'Выберите дату рождения', trigger: 'change' },
  phone: { required: true, message: 'Введите телефон', trigger: 'blur' },
  sex: { required: true, message: 'Выберите пол', trigger: 'change' }
}

// Watch for patient prop changes
watch(
  () => props.patient,
  (newVal) => {
    if (newVal) {
      formData.value = {
        organization: newVal.organization,
        first_name: newVal.first_name || '',
        last_name: newVal.last_name || '',
        middle_name: newVal.middle_name || '',
        birth_date: newVal.birth_date ? new Date(newVal.birth_date).getTime() : null,
        sex: newVal.sex || '',
        phone: newVal.phone || '',
        email: newVal.email || '',
        address: newVal.address || '',
        iin: newVal.iin || '',
        passport_series: newVal.documents?.passport_series || '',
        passport_number: newVal.documents?.passport_number || '',
        passport_issued_by: newVal.documents?.passport_issued_by || '',
        passport_issued_date: newVal.documents?.passport_issued_date ? new Date(newVal.documents.passport_issued_date).getTime() : null,
        notes: newVal.notes || '',
        allergies: newVal.allergies || '',
        medical_history: newVal.medical_history || '',
        discount_card: '',
        discount_percent: newVal.discount_percent || 0,
        balance: newVal.balance || 0,
        telegram_nickname: '',
        consent_newsletters: newVal.consents?.newsletters || false,
        consent_egisz: newVal.consents?.egisz || false
      }
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

function resetForm() {
  formData.value = {
    organization: authStore.user?.organization || null,
    first_name: '',
    last_name: '',
    middle_name: '',
    birth_date: null,
    sex: '',
    phone: '',
    email: '',
    address: '',
    iin: '',
    passport_series: '',
    passport_number: '',
    passport_issued_by: '',
    passport_issued_date: null,
    notes: '',
    allergies: '',
    medical_history: '',
    discount_card: '',
    discount_percent: 0,
    balance: 0,
    telegram_nickname: '',
    consent_newsletters: false,
    consent_egisz: false
  }
  activeTab.value = 'general'
}

function handleClose() {
  visible.value = false
  resetForm()
}

async function handleSave(closeAfter = false) {
  try {
    await formRef.value?.validate()
    saving.value = true

    const data = {
      organization: formData.value.organization || authStore.user?.organization,
      first_name: formData.value.first_name,
      last_name: formData.value.last_name,
      middle_name: formData.value.middle_name,
      birth_date: formData.value.birth_date ? new Date(formData.value.birth_date).toISOString().split('T')[0] : null,
      sex: formData.value.sex,
      phone: formData.value.phone,
      email: formData.value.email,
      address: formData.value.address,
      iin: formData.value.iin,
      documents: {
        passport_series: formData.value.passport_series,
        passport_number: formData.value.passport_number,
        passport_issued_by: formData.value.passport_issued_by,
        passport_issued_date: formData.value.passport_issued_date ? new Date(formData.value.passport_issued_date).toISOString().split('T')[0] : null
      },
      notes: formData.value.notes,
      allergies: formData.value.allergies,
      medical_history: formData.value.medical_history,
      discount_percent: formData.value.discount_percent,
      consents: {
        newsletters: formData.value.consent_newsletters,
        egisz: formData.value.consent_egisz
      }
    }

    if (isEdit.value) {
      await apiClient.patch(`/patients/patients/${props.patient.id}`, data)
      message.success('Пациент обновлён')
    } else {
      await apiClient.post('/patients/patients', data)
      message.success('Пациент создан')
    }

    emit('saved')

    if (closeAfter) {
      handleClose()
    } else {
      resetForm()
    }
  } catch (error) {
    console.error('Error saving patient:', error)
    if (error.response?.data) {
      const errors = error.response.data
      const errorMsg = typeof errors === 'string' ? errors : JSON.stringify(errors)
      message.error('Ошибка: ' + errorMsg)
    } else {
      message.error('Ошибка сохранения пациента')
    }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/tokens.scss';

:deep(.n-card) {
  margin-bottom: 16px;
}

:deep(.n-card__header) {
  font-weight: 600;
  font-size: 16px;
}
</style>

