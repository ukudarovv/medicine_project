<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    :title="isEdit ? 'Редактировать медосмотр' : 'Новый медосмотр'"
    style="width: 900px"
    :segmented="{ content: 'soft' }"
  >
    <n-scrollbar style="max-height: 70vh">
      <n-form ref="formRef" :model="formData" :rules="rules" label-placement="top">
        <!-- Основная информация -->
        <n-card title="Основная информация" :bordered="false">
          <n-grid :cols="2" :x-gap="12">
            <n-grid-item>
              <n-form-item label="Вид медицинского осмотра *" path="exam_type">
                <n-select
                  v-model:value="formData.exam_type"
                  :options="examTypeOptions"
                  placeholder="Выберите вид"
                />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="Дата осмотра *" path="exam_date">
                <n-date-picker
                  v-model:value="formData.exam_date"
                  type="date"
                  placeholder="Выберите дату"
                  style="width: 100%"
                />
              </n-form-item>
            </n-grid-item>
          </n-grid>

          <n-form-item label="Профиль работы" path="work_profile">
            <n-input
              v-model:value="formData.work_profile"
              type="textarea"
              placeholder="Опишите условия труда и профиль работы"
              :autosize="{ minRows: 2, maxRows: 4 }"
            />
          </n-form-item>

          <n-form-item label="Заключение комиссии" path="conclusion">
            <n-input
              v-model:value="formData.conclusion"
              type="textarea"
              placeholder="Заключение медицинской комиссии"
              :autosize="{ minRows: 3, maxRows: 6 }"
            />
          </n-form-item>

          <n-grid :cols="2" :x-gap="12">
            <n-grid-item>
              <n-form-item label="Годен к работе">
                <n-switch v-model:value="formData.fit_for_work" />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="Дата следующего осмотра" path="next_exam_date">
                <n-date-picker
                  v-model:value="formData.next_exam_date"
                  type="date"
                  placeholder="Выберите дату"
                  style="width: 100%"
                />
              </n-form-item>
            </n-grid-item>
          </n-grid>

          <n-form-item label="Ограничения и рекомендации" path="restrictions">
            <n-input
              v-model:value="formData.restrictions"
              type="textarea"
              placeholder="Укажите ограничения и рекомендации для работника"
              :autosize="{ minRows: 2, maxRows: 4 }"
            />
          </n-form-item>
        </n-card>

        <!-- Члены комиссии -->
        <n-card title="Члены врачебной комиссии" :bordered="false" style="margin-top: 16px">
          <n-dynamic-input
            v-model:value="formData.commission_members"
            :on-create="onCreateCommissionMember"
          >
            <template #default="{ value }">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; width: 100%">
                <n-input v-model:value="value.specialty" placeholder="Специальность врача" />
                <n-input v-model:value="value.conclusion" placeholder="Заключение" />
              </div>
            </template>
          </n-dynamic-input>
        </n-card>

        <!-- Перенесенные заболевания -->
        <n-card title="Перенесенные заболевания" :bordered="false" style="margin-top: 16px">
          <template #header-extra>
            <n-button
              size="small"
              type="primary"
              @click="addPastDisease"
            >
              + Добавить
            </n-button>
          </template>
          <n-list v-if="pastDiseases.length > 0" bordered>
            <n-list-item v-for="(disease, idx) in pastDiseases" :key="idx">
              <n-thing>
                <template #header>{{ disease.disease_name }} ({{ disease.year }})</template>
                <template #description>{{ disease.note }}</template>
                <template #action>
                  <n-button
                    size="small"
                    type="error"
                    @click="removePastDisease(idx)"
                  >
                    Удалить
                  </n-button>
                </template>
              </n-thing>
            </n-list-item>
          </n-list>
          <n-empty v-else description="Нет данных о перенесенных заболеваниях" size="small" />
        </n-card>

        <!-- Профилактические прививки -->
        <n-card title="Профилактические прививки" :bordered="false" style="margin-top: 16px">
          <template #header-extra>
            <n-button
              size="small"
              type="primary"
              @click="addVaccination"
            >
              + Добавить
            </n-button>
          </template>
          <n-list v-if="vaccinations.length > 0" bordered>
            <n-list-item v-for="(vaccination, idx) in vaccinations" :key="idx">
              <n-thing>
                <template #header>{{ vaccination.vaccine_type }}</template>
                <template #description>
                  Дата: {{ formatDate(vaccination.date) }}
                  <span v-if="vaccination.revaccination_date">
                    | Ревакцинация: {{ formatDate(vaccination.revaccination_date) }}
                  </span>
                </template>
                <template #action>
                  <n-button
                    size="small"
                    type="error"
                    @click="removeVaccination(idx)"
                  >
                    Удалить
                  </n-button>
                </template>
              </n-thing>
            </n-list-item>
          </n-list>
          <n-empty v-else description="Нет данных о прививках" size="small" />
        </n-card>

        <!-- Лабораторные исследования -->
        <n-card title="Лабораторные исследования" :bordered="false" style="margin-top: 16px">
          <template #header-extra>
            <n-button
              size="small"
              type="primary"
              @click="addLabTest"
            >
              + Добавить
            </n-button>
          </template>
          <n-list v-if="labTests.length > 0" bordered>
            <n-list-item v-for="(test, idx) in labTests" :key="idx">
              <n-thing>
                <template #header>{{ test.test_name || test.test_type }}</template>
                <template #description>
                  Дата: {{ formatDate(test.performed_date) }} | Результат: {{ test.result }}
                </template>
                <template #action>
                  <n-button
                    size="small"
                    type="error"
                    @click="removeLabTest(idx)"
                  >
                    Удалить
                  </n-button>
                </template>
              </n-thing>
            </n-list-item>
          </n-list>
          <n-empty v-else description="Нет данных о лабораторных исследованиях" size="small" />
        </n-card>
      </n-form>
    </n-scrollbar>

    <template #footer>
      <n-space justify="end">
        <n-button @click="handleClose">Отмена</n-button>
        <n-button type="primary" @click="handleSave" :loading="saving">
          {{ isEdit ? 'Обновить' : 'Создать' }}
        </n-button>
      </n-space>
    </template>

    <!-- Sub-modals for adding detailed data -->
    <n-modal v-model:show="showPastDiseaseModal" preset="dialog" title="Добавить перенесенное заболевание">
      <n-form :model="newPastDisease">
        <n-form-item label="Название заболевания">
          <n-input v-model:value="newPastDisease.disease_name" placeholder="Введите название" />
        </n-form-item>
        <n-form-item label="Год">
          <n-input-number v-model:value="newPastDisease.year" :min="1900" :max="new Date().getFullYear()" style="width: 100%" />
        </n-form-item>
        <n-form-item label="Примечание">
          <n-input v-model:value="newPastDisease.note" type="textarea" placeholder="Дополнительная информация" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space justify="end">
          <n-button @click="showPastDiseaseModal = false">Отмена</n-button>
          <n-button type="primary" @click="savePastDisease">Добавить</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal v-model:show="showVaccinationModal" preset="dialog" title="Добавить прививку">
      <n-form :model="newVaccination">
        <n-form-item label="Тип вакцины">
          <n-input v-model:value="newVaccination.vaccine_type" placeholder="Введите тип вакцины" />
        </n-form-item>
        <n-form-item label="Дата прививки">
          <n-date-picker v-model:value="newVaccination.date" type="date" style="width: 100%" />
        </n-form-item>
        <n-form-item label="Дата ревакцинации">
          <n-date-picker v-model:value="newVaccination.revaccination_date" type="date" style="width: 100%" />
        </n-form-item>
        <n-form-item label="Серия и номер">
          <n-input v-model:value="newVaccination.serial_number" placeholder="Серия и номер вакцины" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space justify="end">
          <n-button @click="showVaccinationModal = false">Отмена</n-button>
          <n-button type="primary" @click="saveVaccination">Добавить</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal v-model:show="showLabTestModal" preset="dialog" title="Добавить лабораторное исследование">
      <n-form :model="newLabTest">
        <n-form-item label="Тип исследования">
          <n-select v-model:value="newLabTest.test_type" :options="labTestTypeOptions" />
        </n-form-item>
        <n-form-item label="Название исследования">
          <n-input v-model:value="newLabTest.test_name" placeholder="Введите название" />
        </n-form-item>
        <n-form-item label="Результат">
          <n-input v-model:value="newLabTest.result" type="textarea" placeholder="Результат исследования" />
        </n-form-item>
        <n-form-item label="Дата проведения">
          <n-date-picker v-model:value="newLabTest.performed_date" type="date" style="width: 100%" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space justify="end">
          <n-button @click="showLabTestModal = false">Отмена</n-button>
          <n-button type="primary" @click="saveLabTest">Добавить</n-button>
        </n-space>
      </template>
    </n-modal>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { format } from 'date-fns'
import {
  createMedicalExamination,
  updateMedicalExamination,
  createMedExamPastDisease,
  createMedExamVaccination,
  createMedExamLabTest
} from '@/api/patients'

const props = defineProps({
  show: Boolean,
  examination: {
    type: Object,
    default: null
  },
  patientId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update:show', 'saved'])

const message = useMessage()
const formRef = ref(null)
const saving = ref(false)

const visible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

const isEdit = computed(() => !!props.examination)

// Form data
const formData = ref({
  patient: props.patientId,
  exam_type: 'periodic',
  exam_date: null,
  work_profile: '',
  conclusion: '',
  fit_for_work: true,
  restrictions: '',
  next_exam_date: null,
  commission_members: []
})

// Related data
const pastDiseases = ref([])
const vaccinations = ref([])
const labTests = ref([])

// Sub-modal states
const showPastDiseaseModal = ref(false)
const showVaccinationModal = ref(false)
const showLabTestModal = ref(false)

// New item forms
const newPastDisease = ref({ disease_name: '', year: new Date().getFullYear(), note: '' })
const newVaccination = ref({ vaccine_type: '', date: null, revaccination_date: null, serial_number: '' })
const newLabTest = ref({ test_type: 'blood_general', test_name: '', result: '', performed_date: null })

// Options
const examTypeOptions = [
  { label: 'Предварительный', value: 'preliminary' },
  { label: 'Периодический', value: 'periodic' },
  { label: 'Внеочередной', value: 'extraordinary' }
]

const labTestTypeOptions = [
  { label: 'ОАК (Общий анализ крови)', value: 'blood_general' },
  { label: 'Биохимия крови', value: 'blood_biochem' },
  { label: 'ОАМ (Общий анализ мочи)', value: 'urine' },
  { label: 'ЭКГ', value: 'ecg' },
  { label: 'Рентгенография', value: 'xray' },
  { label: 'Флюорография', value: 'fluorography' },
  { label: 'Спирометрия', value: 'spirometry' },
  { label: 'Аудиометрия', value: 'audiometry' },
  { label: 'Проверка зрения', value: 'vision_test' },
  { label: 'Другое', value: 'other' }
]

// Rules
const rules = {
  exam_type: { required: true, message: 'Выберите вид осмотра', trigger: 'change' },
  exam_date: { required: true, type: 'number', message: 'Выберите дату осмотра', trigger: 'change' }
}

// Methods
function onCreateCommissionMember() {
  return {
    specialty: '',
    conclusion: ''
  }
}

function addPastDisease() {
  newPastDisease.value = { disease_name: '', year: new Date().getFullYear(), note: '' }
  showPastDiseaseModal.value = true
}

function savePastDisease() {
  if (!newPastDisease.value.disease_name) {
    message.error('Введите название заболевания')
    return
  }
  pastDiseases.value.push({ ...newPastDisease.value })
  showPastDiseaseModal.value = false
  message.success('Заболевание добавлено')
}

function removePastDisease(index) {
  pastDiseases.value.splice(index, 1)
}

function addVaccination() {
  newVaccination.value = { vaccine_type: '', date: null, revaccination_date: null, serial_number: '' }
  showVaccinationModal.value = true
}

function saveVaccination() {
  if (!newVaccination.value.vaccine_type || !newVaccination.value.date) {
    message.error('Заполните обязательные поля')
    return
  }
  vaccinations.value.push({ ...newVaccination.value })
  showVaccinationModal.value = false
  message.success('Прививка добавлена')
}

function removeVaccination(index) {
  vaccinations.value.splice(index, 1)
}

function addLabTest() {
  newLabTest.value = { test_type: 'blood_general', test_name: '', result: '', performed_date: null }
  showLabTestModal.value = true
}

function saveLabTest() {
  if (!newLabTest.value.result || !newLabTest.value.performed_date) {
    message.error('Заполните обязательные поля')
    return
  }
  labTests.value.push({ ...newLabTest.value })
  showLabTestModal.value = false
  message.success('Исследование добавлено')
}

function removeLabTest(index) {
  labTests.value.splice(index, 1)
}

function formatDate(timestamp) {
  if (!timestamp) return ''
  return format(new Date(timestamp), 'dd.MM.yyyy')
}

function handleClose() {
  visible.value = false
  resetForm()
}

function resetForm() {
  formData.value = {
    patient: props.patientId,
    exam_type: 'periodic',
    exam_date: null,
    work_profile: '',
    conclusion: '',
    fit_for_work: true,
    restrictions: '',
    next_exam_date: null,
    commission_members: []
  }
  pastDiseases.value = []
  vaccinations.value = []
  labTests.value = []
}

async function handleSave() {
  try {
    await formRef.value?.validate()
    saving.value = true

    const data = {
      patient: props.patientId,
      exam_type: formData.value.exam_type,
      exam_date: formData.value.exam_date ? new Date(formData.value.exam_date).toISOString().split('T')[0] : null,
      work_profile: formData.value.work_profile,
      conclusion: formData.value.conclusion,
      fit_for_work: formData.value.fit_for_work,
      restrictions: formData.value.restrictions,
      next_exam_date: formData.value.next_exam_date ? new Date(formData.value.next_exam_date).toISOString().split('T')[0] : null,
      commission_members: formData.value.commission_members
    }

    let examinationId

    if (isEdit.value) {
      await updateMedicalExamination(props.examination.id, data)
      examinationId = props.examination.id
      message.success('Медосмотр обновлен')
    } else {
      const response = await createMedicalExamination(data)
      examinationId = response.data.id
      message.success('Медосмотр создан')

      // Save related data
      for (const disease of pastDiseases.value) {
        await createMedExamPastDisease({
          examination: examinationId,
          ...disease
        })
      }

      for (const vaccination of vaccinations.value) {
        await createMedExamVaccination({
          examination: examinationId,
          vaccine_type: vaccination.vaccine_type,
          date: vaccination.date ? new Date(vaccination.date).toISOString().split('T')[0] : null,
          revaccination_date: vaccination.revaccination_date ? new Date(vaccination.revaccination_date).toISOString().split('T')[0] : null,
          serial_number: vaccination.serial_number,
          note: vaccination.note || ''
        })
      }

      for (const test of labTests.value) {
        await createMedExamLabTest({
          examination: examinationId,
          test_type: test.test_type,
          test_name: test.test_name,
          result: test.result,
          performed_date: test.performed_date ? new Date(test.performed_date).toISOString().split('T')[0] : null
        })
      }
    }

    emit('saved')
    handleClose()
  } catch (error) {
    console.error('Error saving medical examination:', error)
    if (error.response?.data) {
      const errors = Object.values(error.response.data).flat()
      message.error('Ошибка: ' + errors.join(', '))
    } else {
      message.error('Ошибка сохранения медосмотра')
    }
  } finally {
    saving.value = false
  }
}

// Watch for examination prop changes
watch(
  () => props.examination,
  (newVal) => {
    if (newVal) {
      formData.value = {
        patient: props.patientId,
        exam_type: newVal.exam_type || 'periodic',
        exam_date: newVal.exam_date ? new Date(newVal.exam_date).getTime() : null,
        work_profile: newVal.work_profile || '',
        conclusion: newVal.conclusion || '',
        fit_for_work: newVal.fit_for_work !== undefined ? newVal.fit_for_work : true,
        restrictions: newVal.restrictions || '',
        next_exam_date: newVal.next_exam_date ? new Date(newVal.next_exam_date).getTime() : null,
        commission_members: newVal.commission_members || []
      }
      // Load related data if editing
      pastDiseases.value = newVal.past_diseases || []
      vaccinations.value = newVal.vaccinations || []
      labTests.value = newVal.lab_tests || []
    }
  },
  { immediate: true }
)
</script>

<style scoped>
/* Component-specific styles can be added here */
</style>

