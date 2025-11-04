# Frontend Implementation TODO

**Status:** Backend Complete ✅ | Frontend Partial ⏳  
**Estimated Time:** 40-60 hours  
**Priority:** Medium (Backend can be used independently)

---

## ОСТАВШИЕСЯ ЗАДАЧИ

### 1. VisitDiaryEditor Component (Sprint 2) 
**Priority:** HIGH  
**Time:** 8-10 hours  
**File:** `frontend/src/components/VisitDiaryEditor.vue`

**Требования:**
- Структурированные поля:
  - Жалобы (complaints)
  - Анамнез (anamnesis)
  - Осмотр (examination)
  - Заключение (conclusion)
  - Рекомендации (recommendations)
- Rich-text редактор для каждого поля (TinyMCE или Quill)
- Dropdown "Выбрать шаблон" по специальности врача
- Автосохранение черновика (useAutosave)
- Привязка к Visit.diary_structured (JSONField)

**API Integration:**
```javascript
// Save diary
await apiClient.patch(`/api/visits/visits/${visitId}`, {
  diary_structured: {
    complaints: '...',
    anamnesis: '...',
    examination: '...',
    conclusion: '...',
    recommendations: '...'
  }
})
```

---

### 2. WaitlistModal Component (Sprint 2)
**Priority:** MEDIUM  
**Time:** 4-6 hours  
**File:** `frontend/src/components/WaitlistModal.vue`

**Требования:**
- Форма полей:
  - Patient (select/autocomplete)
  - Service (optional)
  - Employee (optional - желаемый врач)
  - Preferred date (или период start/end)
  - Time window (morning/afternoon/evening/any)
  - Priority (number input)
  - Comment (textarea)
- Status tracking (waiting/contacted/scheduled/cancelled)
- Contact result field
- Integration с Waitlist API

**API Integration:**
```javascript
// Create waitlist entry
await apiClient.post('/api/calendar/waitlist/', waitlistData)

// Mark contacted
await apiClient.post(`/api/calendar/waitlist/${id}/mark-contacted/`, {
  contact_result: 'Записался на прием'
})
```

---

### 3. MedicalExaminationModal Component (Sprint 3)
**Priority:** HIGH  
**Time:** 12-15 hours  
**File:** `frontend/src/components/MedicalExaminationModal.vue`

**Требования:**
- Основная информация:
  - Type (preliminary/periodic/extraordinary)
  - Date, work profile
  - Conclusion, fit_for_work (checkbox)
  - Restrictions, next_exam_date
- **Табличные блоки:**
  1. Past Diseases (table: disease, ICD-10, year, note)
  2. Vaccinations (table: vaccine, date, revaccination, serial)
  3. Lab Tests (table: type, name, result, date, file)
- Commission members (JSONField editor)
- Кнопка "Печать заключения" → API print endpoint

**API Integration:**
```javascript
// Create examination
await apiClient.post('/api/patients/examinations/', examData)

// Add past disease
await apiClient.post('/api/patients/exam-past-diseases/', {
  examination: examId,
  icd_code: icdId,
  disease_name: 'Грипп',
  year: 2020
})

// Print
window.open(`/api/patients/examinations/${id}/print/`)
```

---

### 4. TreatmentPlanModal Component (Sprint 3)
**Priority:** HIGH  
**Time:** 15-20 hours  
**File:** `frontend/src/components/TreatmentPlanModal.vue`

**Требования:**
- Header: title, description, dates, status
- **Stages** (accordion/expandable list):
  - Each stage: title, description, dates, status
  - **Items table** (inline editable):
    - Service/Description
    - Qty planned / Qty completed
    - Unit price, discount %
    - Total (calculated)
    - Tooth number (dental)
  - Progress bar: completed/planned
- Footer:
  - Total cost (all stages)
  - Checkbox "Prices frozen"
  - Button "Freeze prices" → API call
  - Button "Save as template" → API call
- Button "Create appointments from plan" → modal with dates selection

**API Integration:**
```javascript
// Create plan
const plan = await apiClient.post('/api/patients/treatment-plans/', planData)

// Add stage
const stage = await apiClient.post('/api/patients/treatment-stages/', stageData)

// Add item to stage
await apiClient.post('/api/patients/treatment-stage-items/', itemData)

// Freeze prices
await apiClient.post(`/api/patients/treatment-plans/${id}/freeze-prices/`)

// Save as template
await apiClient.post(`/api/patients/treatment-plans/${id}/save-as-template/`, {
  name: 'Template name'
})
```

---

### 5. TreatmentPlanFromTemplate Component (Sprint 3)
**Priority:** MEDIUM  
**Time:** 4-5 hours  
**File:** `frontend/src/components/TreatmentPlanFromTemplate.vue`

**Требования:**
- Select template from list
- Display template structure (stages & items)
- Fetch current prices for services
- Allow editing before creating plan
- Button "Create plan from template"

**API Integration:**
```javascript
// Get templates
const templates = await apiClient.get('/api/patients/treatment-plan-templates/')

// Use template data to create new plan
```

---

### 6. Payment UI Updates (Sprint 4)
**Priority:** MEDIUM  
**Time:** 6-8 hours  
**Files:** 
- `frontend/src/components/PaymentModal.vue` (update existing)
- `frontend/src/pages/PatientsPage.vue` (add statistics tab)

**Требования:**

**PaymentModal:**
- Add buttons for "Kaspi QR" and "Halyk Pay"
- On Kaspi QR click → show QR code image (from API response)
- On Halyk Pay click → redirect to payment URL
- Show payment status (pending/completed/failed)

**Patient Statistics Tab:**
- Dashboard with metrics:
  - Total visits (number)
  - Total revenue (chart over time)
  - Average check
  - Current balance (colored indicator)
- Button "Выдать справку для налогового вычета"

**API Integration:**
```javascript
// Get statistics
const stats = await apiClient.get(`/api/patients/patients/${id}/statistics/`)

// Create tax certificate
await apiClient.post('/api/billing/tax-certificates/', {
  patient: patientId,
  year: 2025
})
```

---

### 7. Inline Editing in Tables (Sprint 5)
**Priority:** LOW  
**Time:** 8-10 hours  
**Files:** Multiple tables across application

**Требования:**
- Click на ячейку → edit mode
- Tab для навигации
- Enter для сохранения
- Esc для отмены
- Автосохранение при blur

**Usage in:**
- Visit services table
- Medical exam diseases/vaccinations/tests tables
- Treatment plan items table

**Implementation Example:**
```vue
<template>
  <td @dblclick="startEdit">
    <n-input v-if="isEditing" v-model:value="localValue" @blur="save" />
    <span v-else>{{ value }}</span>
  </td>
</template>
```

---

### 8. ICD-10 KZ Data Loading (Sprint 2)
**Priority:** MEDIUM  
**Time:** 2-3 hours  
**File:** `backend/apps/services/fixtures/icd10_kz.json` or CSV

**Требования:**
- Найти официальный справочник МКБ-10 РК
- Конвертировать в JSON/CSV
- Создать management command для загрузки
- Обновить существующую таблицу icd_codes

**Management Command:**
```python
# backend/apps/services/management/commands/load_icd10_kz.py
class Command(BaseCommand):
    help = 'Load ICD-10 KZ edition'
    
    def handle(self, *args, **options):
        # Load from CSV/JSON
        # Update ICDCode model
        pass
```

---

## ПРИОРИТИЗАЦИЯ

### Must Have (для production):
1. VisitDiaryEditor (критично для врачей)
2. MedicalExaminationModal (обязательно для медосмотров)
3. ICD-10 KZ data loading

### Should Have (желательно):
4. TreatmentPlanModal (важно, но можно через API/admin)
5. Payment UI updates (можно использовать существующий payment modal)
6. Patient statistics dashboard

### Nice to Have (можно позже):
7. WaitlistModal (можно управлять через admin)
8. Inline editing (улучшение UX)

---

## DEVELOPMENT WORKFLOW

### Setup:
```bash
cd frontend
npm install
npm run dev
```

### Testing:
```bash
npm run test  # If tests configured
npm run build # Check for build errors
```

### Integration:
1. Ensure backend is running on `http://localhost:8000`
2. Update `VITE_API_URL` in `.env` if needed
3. Test API calls with browser DevTools

---

## HELPER CODE SNIPPETS

### 1. Using IIN Mask:
```vue
<script setup>
import { masks, validateIINFormat, extractBirthDateFromIIN } from '@/utils/masks'

const iinValue = ref('')

const handleIINChange = () => {
  const validation = validateIINFormat(iinValue.value)
  if (!validation.valid) {
    message.error(validation.error)
    return
  }
  
  const birthDate = extractBirthDateFromIIN(iinValue.value)
  // Auto-fill birth date
}
</script>

<template>
  <n-input 
    v-model:value="iinValue" 
    placeholder="000000000000"
    maxlength="12"
    @change="handleIINChange"
  />
</template>
```

### 2. Using Permissions:
```vue
<script setup>
import { usePermissions } from '@/composables/usePermissions'

const { canEditPatients, canViewFinancial, canDelete } = usePermissions()
</script>

<template>
  <n-form-item v-if="canViewFinancial" label="Баланс">
    <n-input-number v-model:value="balance" :disabled="!canEditFinancial" />
  </n-form-item>
  
  <n-button v-if="canDelete" type="error" @click="deletePatient">
    Удалить
  </n-button>
</template>
```

### 3. Using Hotkeys:
```vue
<script setup>
import { useHotkeys } from '@/composables/useHotkeys'

useHotkeys({
  'ctrl+s': () => {
    console.log('Saving...')
    save()
  },
  'ctrl+p': () => {
    console.log('Printing...')
    printForm()
  },
  'escape': () => {
    closeModal()
  }
})
</script>
```

### 4. Using Autosave:
```vue
<script setup>
import { useAutosave } from '@/composables/useAutosave'

const formData = ref({...})

const { isDirty, loadDraft, clearDraft } = useAutosave(formData, {
  draftKey: 'visit_diary_draft_' + visitId,
  debounceMs: 2000,
  enableLocalStorage: true,
  saveCallback: async (data) => {
    await apiClient.patch(`/api/visits/visits/${visitId}/`, {
      diary_structured: data
    })
  }
})

// On component mount
onMounted(() => {
  const draft = loadDraft()
  if (draft) {
    // Ask user to restore
    if (confirm('Восстановить несохраненные изменения?')) {
      formData.value = draft
    } else {
      clearDraft()
    }
  }
})
</script>
```

---

## RESOURCES

### UI Libraries (Already Installed):
- Naive UI - https://www.naiveui.com/
- Vue 3 - https://vuejs.org/
- Vite - https://vitejs.dev/

### Recommended Additions:
- TinyMCE or Quill for rich text editing
- VueUse for utility composables (already partially used)
- Chart.js or ECharts for statistics charts

### Reference:
- Backend API: `http://localhost:8000/api/`
- API Schema: `http://localhost:8000/api/schema/`
- Django Admin: `http://localhost:8000/admin/`

---

**Created:** November 4, 2025  
**For:** Frontend Developers  
**Project:** Medicine ERP - KZ Adaptation

