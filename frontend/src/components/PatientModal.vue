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
            <n-card :bordered="false">
              <template #header>
                <n-space align="center" justify="space-between">
                  <span>Медицинская карта пациента № {{ formData.id || 'новая' }} от {{ currentDate }}</span>
                  <n-space>
                    <n-button size="small">Изменить</n-button>
                    <n-button size="small" type="primary">🖨️ Печать</n-button>
                  </n-space>
                </n-space>
              </template>
              
              <n-upload
                multiple
                directory-dnd
                :max="12"
                :show-file-list="true"
              >
                <n-upload-dragger>
                  <div style="margin-bottom: 12px">
                    📎 Добавить вложения
                  </div>
                  <n-text style="font-size: 12px">
                    Перетащите файлы в эту область или нажмите сюда (не более 12 Мб)
                  </n-text>
                </n-upload-dragger>
              </n-upload>
            </n-card>

            <!-- Основные данные -->
            <n-card title="Основные данные" :bordered="false" style="margin-top: 16px">
              <n-form-item label="id">
                <n-input :value="formData.id || 'автоматически'" disabled />
              </n-form-item>

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
                  placeholder="дд.мм.гггг"
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

              <n-space>
                <n-button text type="primary">
                  Категория
                </n-button>
                <n-button text type="primary">
                  + Добавить представителя
                </n-button>
              </n-space>
            </n-card>

            <!-- Контакты -->
            <n-card title="Контакты" :bordered="false" style="margin-top: 16px">
              <n-space vertical size="large">
                <n-form-item label="Телефон" path="phone">
                  <n-space>
                    <n-input v-model:value="formData.phone" placeholder="Телефон" style="width: 250px" />
                    <n-button text type="primary">+ Телефон</n-button>
                  </n-space>
                </n-form-item>

                <n-form-item label="MAX" help="Идентификатор MAX">
                  <n-input v-model:value="formData.max_id" placeholder="MAX ID" style="width: 250px" />
                </n-form-item>

                <n-grid :cols="2" :x-gap="12">
                  <n-grid-item>
                    <n-form-item label="Никнейм в Telegram">
                      <n-input v-model:value="formData.telegram_nickname" placeholder="Никнейм в Telegram" />
                    </n-form-item>
                  </n-grid-item>
                  <n-grid-item>
                    <n-form-item label="Telegram ID">
                      <n-input v-model:value="formData.telegram_id" placeholder="Telegram ID" />
                    </n-form-item>
                  </n-grid-item>
                </n-grid>

                <n-form-item label="E-mail" path="email">
                  <n-input v-model:value="formData.email" placeholder="email@example.com" />
                </n-form-item>

                <n-space vertical>
                  <n-checkbox v-model:checked="formData.consent_newsletters">
                    Согласен на получение рассылки
                  </n-checkbox>
                  <n-checkbox v-model:checked="formData.consent_egisz">
                    Согласен на хранение и отправку данных в ЕГИСЗ
                  </n-checkbox>
                </n-space>

                <n-space>
                  <n-button text type="primary">Соц. сети - Добавить</n-button>
                  <n-button text type="primary">Контактное лицо - Добавить</n-button>
                </n-space>
              </n-space>
            </n-card>

            <!-- Документы -->
            <n-card title="Документы" :bordered="false" style="margin-top: 16px">
              <n-space vertical size="large">
                <n-form-item label="Полис ОМС">
                  <n-input v-model:value="formData.oms_policy" placeholder="Номер полиса" />
                </n-form-item>

                <n-form-item label="Дата выдачи полиса ОМС">
                  <n-date-picker
                    v-model:value="formData.oms_policy_date"
                    type="date"
                    placeholder="дд.мм.гггг"
                    style="width: 100%"
                  />
                </n-form-item>

                <n-form-item label="Код организации выдавшей документ">
                  <n-input v-model:value="formData.oms_org_code" placeholder="Код организации" />
                </n-form-item>

                <n-form-item label="СНИЛС">
                  <n-input v-model:value="formData.snils" placeholder="XXX-XXX-XXX XX" />
                </n-form-item>

                <n-form-item label="Мед. страховая организация">
                  <n-input v-model:value="formData.insurance_org" placeholder="Название организации" />
                </n-form-item>

                <n-form-item label="Код меры социальной поддержки">
                  <n-input v-model:value="formData.social_support_code" placeholder="Код" />
                </n-form-item>
              </n-space>

              <n-divider title-placement="left">Удостоверение личности</n-divider>

              <n-space vertical size="large">
                <n-form-item label="Гражданство">
                  <n-input v-model:value="formData.citizenship" placeholder="Гражданство" />
                </n-form-item>

                <n-form-item label="Тип документа">
                  <n-input v-model:value="formData.doc_type" placeholder="Найти..." />
                </n-form-item>

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

                <n-grid :cols="2" :x-gap="12">
                  <n-grid-item>
                    <n-form-item label="Код подразделения">
                      <n-input v-model:value="formData.dept_code" placeholder="Код" />
                    </n-form-item>
                  </n-grid-item>
                  <n-grid-item>
                    <n-form-item label="ИНН Пациента" path="iin">
                      <n-input v-model:value="formData.iin" placeholder="ИИН/ИНН" />
                    </n-form-item>
                  </n-grid-item>
                </n-grid>
              </n-space>
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
              <n-space vertical size="large">
                <n-form-item label="Идентификатор типа адреса">
                  <n-input v-model:value="formData.address_type" placeholder="Найти..." />
                </n-form-item>

                <n-form-item label="Субъект РФ">
                  <n-input v-model:value="formData.region" placeholder="Выбрать субъект РФ" />
                </n-form-item>

                <n-grid :cols="2" :x-gap="12">
                  <n-grid-item>
                    <n-form-item label="Район">
                      <n-input v-model:value="formData.district" placeholder="Найти..." />
                    </n-form-item>
                  </n-grid-item>
                  <n-grid-item>
                    <n-form-item label="Город">
                      <n-input v-model:value="formData.city" placeholder="Найти..." />
                    </n-form-item>
                  </n-grid-item>
                </n-grid>

                <n-grid :cols="2" :x-gap="12">
                  <n-grid-item>
                    <n-form-item label="Населенный пункт">
                      <n-input v-model:value="formData.locality" placeholder="Найти..." />
                    </n-form-item>
                  </n-grid-item>
                  <n-grid-item>
                    <n-form-item label="Улица">
                      <n-input v-model:value="formData.street" placeholder="Найти..." />
                    </n-form-item>
                  </n-grid-item>
                </n-grid>

                <n-grid :cols="4" :x-gap="12">
                  <n-grid-item>
                    <n-form-item label="Дом">
                      <n-input v-model:value="formData.house" placeholder="Дом" />
                    </n-form-item>
                  </n-grid-item>
                  <n-grid-item>
                    <n-form-item label="Местность">
                      <n-select v-model:value="formData.area_type" :options="areaTypeOptions" />
                    </n-form-item>
                  </n-grid-item>
                  <n-grid-item>
                    <n-form-item label="Квартира">
                      <n-input v-model:value="formData.apartment" placeholder="Кв." />
                    </n-form-item>
                  </n-grid-item>
                  <n-grid-item>
                    <n-form-item label="Индекс">
                      <n-input v-model:value="formData.postal_code" placeholder="Индекс" />
                    </n-form-item>
                  </n-grid-item>
                </n-grid>

                <n-form-item label="Геокоординаты объекта">
                  <n-input v-model:value="formData.geocoords" placeholder="Координаты" />
                </n-form-item>

                <n-button text type="primary">
                  Изменение места регистрации - Добавить
                </n-button>
              </n-space>
            </n-card>

            <!-- Заболевания диспансерного наблюдения -->
            <n-card title="Заболевания, по поводу которых осуществляется диспансерное наблюдение" :bordered="false" style="margin-top: 16px">
              <n-data-table
                :columns="diseaseColumns"
                :data="[]"
                :pagination="false"
                size="small"
              />
              <n-button text type="primary" style="margin-top: 8px">
                + Заболевание
              </n-button>
            </n-card>

            <!-- Лист диагнозов -->
            <n-card title="Лист записи заключительных (уточненных) диагнозов" :bordered="false" style="margin-top: 16px">
              <n-data-table
                :columns="diagnosisColumns"
                :data="[]"
                :pagination="false"
                size="small"
              />
              <n-button text type="primary" style="margin-top: 8px">
                + Диагноз
              </n-button>
            </n-card>

            <!-- Личные данные -->
            <n-card title="Личные данные" :bordered="false" style="margin-top: 16px">
              <n-space vertical size="large">
                <n-form-item label="Семейное положение">
                  <n-select v-model:value="formData.marital_status" :options="maritalStatusOptions" />
                </n-form-item>

                <n-form-item label="Образование">
                  <n-select v-model:value="formData.education" :options="educationOptions" />
                </n-form-item>

                <n-form-item label="Занятость">
                  <n-select v-model:value="formData.employment" :options="employmentOptions" />
                </n-form-item>

                <n-form-item label="Место работы">
                  <n-input v-model:value="formData.workplace" placeholder="Место работы" />
                </n-form-item>

                <n-form-item label="Должность">
                  <n-input v-model:value="formData.job_position" placeholder="Должность" />
                </n-form-item>

                <n-button text type="primary">
                  Изменение места работы - Добавить
                </n-button>
              </n-space>
            </n-card>

            <!-- Инвалидность -->
            <n-card title="Инвалидность" :bordered="false" style="margin-top: 16px">
              <n-space vertical size="large">
                <n-checkbox v-model:checked="formData.has_disability">
                  Пациент с инвалидностью
                </n-checkbox>

                <template v-if="formData.has_disability">
                  <n-form-item label="Срок инвалидности">
                    <n-space>
                      <n-date-picker
                        v-model:value="formData.disability_from"
                        type="date"
                        placeholder="с"
                      />
                      <n-date-picker
                        v-model:value="formData.disability_to"
                        type="date"
                        placeholder="по"
                      />
                      <n-checkbox v-model:checked="formData.disability_permanent">
                        Бессрочно
                      </n-checkbox>
                    </n-space>
                  </n-form-item>

                  <n-grid :cols="2" :x-gap="12">
                    <n-grid-item>
                      <n-form-item label="Группа инвалидности">
                        <n-select v-model:value="formData.disability_group" :options="disabilityGroupOptions" />
                      </n-form-item>
                    </n-grid-item>
                    <n-grid-item>
                      <n-form-item label="Тип инвалидности">
                        <n-select v-model:value="formData.disability_type" :options="disabilityTypeOptions" />
                      </n-form-item>
                    </n-grid-item>
                  </n-grid>

                  <n-radio-group v-model:value="formData.disability_status">
                    <n-radio value="primary">Первичная</n-radio>
                    <n-radio value="secondary">Вторичная</n-radio>
                  </n-radio-group>
                </template>
              </n-space>
            </n-card>

            <!-- Анамнез -->
            <n-card title="Анамнез" :bordered="false" style="margin-top: 16px">
              <n-space vertical size="large">
                <n-form-item label="Инвалидность">
                  <n-input v-model:value="formData.disability_notes" placeholder="Первичная, повторная, группа, дата" />
                </n-form-item>

                <n-grid :cols="3" :x-gap="12">
                  <n-grid-item>
                    <n-form-item label="Группа крови">
                      <n-select v-model:value="formData.blood_type" :options="bloodTypeOptions" />
                    </n-form-item>
                  </n-grid-item>
                  <n-grid-item>
                    <n-form-item label="Rh-фактор">
                      <n-select v-model:value="formData.rh_factor" :options="rhFactorOptions" />
                    </n-form-item>
                  </n-grid-item>
                  <n-grid-item>
                    <n-form-item label="Антиген К1 системы Kell">
                      <n-input v-model:value="formData.kell_antigen" placeholder="К1" />
                    </n-form-item>
                  </n-grid-item>
                </n-grid>

                <n-form-item label="Иные сведения групповой принадлежности крови">
                  <n-input v-model:value="formData.blood_info_other" placeholder="Дополнительная информация" />
                </n-form-item>

                <n-form-item label="Аллергические реакции">
                  <n-input
                    v-model:value="formData.allergies"
                    type="textarea"
                    :rows="4"
                    placeholder="Опишите аллергии и реакции"
                  />
                </n-form-item>
              </n-space>
            </n-card>

            <!-- Учет дозовых нагрузок -->
            <n-card title="Учет дозовых нагрузок" :bordered="false" style="margin-top: 16px">
              <n-data-table
                :columns="doseColumns"
                :data="[]"
                :pagination="false"
                size="small"
              />
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

const currentDate = computed(() => {
  const now = new Date()
  return `${now.getDate().toString().padStart(2, '0')}.${(now.getMonth() + 1).toString().padStart(2, '0')}.${now.getFullYear()}`
})

// Table columns for diseases
const diseaseColumns = [
  { title: 'Дата начала наблюдения', key: 'start_date', width: 150 },
  { title: 'Дата прекращения наблюдения', key: 'end_date', width: 150 },
  { title: 'Диагноз', key: 'diagnosis' },
  { title: 'Код МКБ', key: 'icd_code', width: 100 },
  { title: 'Врач', key: 'doctor', width: 200 }
]

// Table columns for diagnoses
const diagnosisColumns = [
  { title: 'Дата', key: 'date', width: 120 },
  { title: 'Заключительные (уточненные) диагнозы', key: 'diagnosis' },
  { title: 'Код МКБ', key: 'icd_code', width: 100 },
  { title: 'Первичный - 1, Повторный - 2', key: 'type', width: 150 },
  { title: 'ФИО врача', key: 'doctor', width: 200 },
  { title: 'Должность', key: 'position', width: 150 },
  { title: 'Специальность', key: 'specialty', width: 150 }
]

// Table columns for dose tracking
const doseColumns = [
  { title: '№', key: 'number', width: 60 },
  { title: 'Дата', key: 'date', width: 120 },
  { title: 'Вид исследования', key: 'study_type' },
  { title: 'Эффективная доза, мЗв', key: 'dose', width: 150 },
  { title: 'Примечание', key: 'note' }
]

// Select options
const areaTypeOptions = [
  { label: '- все -', value: '' },
  { label: 'Городская', value: 'urban' },
  { label: 'Сельская', value: 'rural' }
]

const maritalStatusOptions = [
  { label: '- все -', value: '' },
  { label: 'Не женат/Не замужем', value: 'single' },
  { label: 'Женат/Замужем', value: 'married' },
  { label: 'Разведен(а)', value: 'divorced' },
  { label: 'Вдовец/Вдова', value: 'widowed' }
]

const educationOptions = [
  { label: '- все -', value: '' },
  { label: 'Среднее', value: 'secondary' },
  { label: 'Среднее специальное', value: 'vocational' },
  { label: 'Высшее', value: 'higher' }
]

const employmentOptions = [
  { label: '- все -', value: '' },
  { label: 'Работает', value: 'employed' },
  { label: 'Не работает', value: 'unemployed' },
  { label: 'Пенсионер', value: 'retired' },
  { label: 'Студент', value: 'student' }
]

const disabilityGroupOptions = [
  { label: '- все -', value: '' },
  { label: 'I группа', value: '1' },
  { label: 'II группа', value: '2' },
  { label: 'III группа', value: '3' }
]

const disabilityTypeOptions = [
  { label: '- все -', value: '' },
  { label: 'Общее заболевание', value: 'general' },
  { label: 'Профессиональное заболевание', value: 'occupational' },
  { label: 'Инвалид с детства', value: 'childhood' }
]

const bloodTypeOptions = [
  { label: 'Не указано', value: '' },
  { label: 'O (I)', value: 'O' },
  { label: 'A (II)', value: 'A' },
  { label: 'B (III)', value: 'B' },
  { label: 'AB (IV)', value: 'AB' }
]

const rhFactorOptions = [
  { label: 'Не указано', value: '' },
  { label: 'Положительный (+)', value: 'positive' },
  { label: 'Отрицательный (-)', value: 'negative' }
]

// Form data
const formData = ref({
  id: null,
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
  // Контакты
  max_id: '',
  telegram_nickname: '',
  telegram_id: '',
  consent_newsletters: false,
  consent_egisz: false,
  // Документы
  oms_policy: '',
  oms_policy_date: null,
  oms_org_code: '',
  snils: '',
  insurance_org: '',
  social_support_code: '',
  citizenship: '',
  doc_type: '',
  dept_code: '',
  // Адрес детализированный
  address_type: '',
  region: '',
  district: '',
  city: '',
  locality: '',
  street: '',
  house: '',
  area_type: '',
  apartment: '',
  postal_code: '',
  geocoords: '',
  // Личные данные
  marital_status: '',
  education: '',
  employment: '',
  workplace: '',
  job_position: '',
  // Инвалидность
  has_disability: false,
  disability_from: null,
  disability_to: null,
  disability_permanent: false,
  disability_group: '',
  disability_type: '',
  disability_status: '',
  disability_notes: '',
  // Анамнез
  blood_type: '',
  rh_factor: '',
  kell_antigen: '',
  blood_info_other: ''
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
    id: null,
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
    max_id: '',
    telegram_nickname: '',
    telegram_id: '',
    consent_newsletters: false,
    consent_egisz: false,
    oms_policy: '',
    oms_policy_date: null,
    oms_org_code: '',
    snils: '',
    insurance_org: '',
    social_support_code: '',
    citizenship: '',
    doc_type: '',
    dept_code: '',
    address_type: '',
    region: '',
    district: '',
    city: '',
    locality: '',
    street: '',
    house: '',
    area_type: '',
    apartment: '',
    postal_code: '',
    geocoords: '',
    marital_status: '',
    education: '',
    employment: '',
    workplace: '',
    job_position: '',
    has_disability: false,
    disability_from: null,
    disability_to: null,
    disability_permanent: false,
    disability_group: '',
    disability_type: '',
    disability_status: '',
    disability_notes: '',
    blood_type: '',
    rh_factor: '',
    kell_antigen: '',
    blood_info_other: ''
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

