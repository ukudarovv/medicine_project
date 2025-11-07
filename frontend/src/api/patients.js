import apiClient from './axios'

// Patient CRUD
export const getPatients = (params) => apiClient.get('/patients/', { params })
export const getPatient = (id) => apiClient.get(`/patients/${id}/`)
export const createPatient = (data) => apiClient.post('/patients/', data)
export const updatePatient = (id, data) => apiClient.put(`/patients/${id}/`, data)
export const deletePatient = (id) => apiClient.delete(`/patients/${id}/`)
export const searchPatient = (params) => apiClient.get('/patients/search/', { params })

// Representatives
export const getRepresentatives = (patientId) => apiClient.get('/patients/representatives/', { params: { patient: patientId } })
export const createRepresentative = (data) => apiClient.post('/patients/representatives/', data)
export const updateRepresentative = (id, data) => apiClient.put(`/patients/representatives/${id}/`, data)
export const deleteRepresentative = (id) => apiClient.delete(`/patients/representatives/${id}/`)

// Additional phones
export const getPatientPhones = (patientId) => apiClient.get('/patients/phones/', { params: { patient: patientId } })
export const createPatientPhone = (data) => apiClient.post('/patients/phones/', data)
export const updatePatientPhone = (id, data) => apiClient.put(`/patients/phones/${id}/`, data)
export const deletePatientPhone = (id) => apiClient.delete(`/patients/phones/${id}/`)

// Social networks
export const getPatientSocialNetworks = (patientId) => apiClient.get('/patients/social-networks/', { params: { patient: patientId } })
export const createPatientSocialNetwork = (data) => apiClient.post('/patients/social-networks/', data)
export const updatePatientSocialNetwork = (id, data) => apiClient.put(`/patients/social-networks/${id}/`, data)
export const deletePatientSocialNetwork = (id) => apiClient.delete(`/patients/social-networks/${id}/`)

// Contact persons
export const getPatientContactPersons = (patientId) => apiClient.get('/patients/contact-persons/', { params: { patient: patientId } })
export const createPatientContactPerson = (data) => apiClient.post('/patients/contact-persons/', data)
export const updatePatientContactPerson = (id, data) => apiClient.put(`/patients/contact-persons/${id}/`, data)
export const deletePatientContactPerson = (id) => apiClient.delete(`/patients/contact-persons/${id}/`)

// Diseases
export const getPatientDiseases = (patientId) => apiClient.get('/patients/diseases/', { params: { patient: patientId } })
export const createPatientDisease = (data) => apiClient.post('/patients/diseases/', data)
export const updatePatientDisease = (id, data) => apiClient.put(`/patients/diseases/${id}/`, data)
export const deletePatientDisease = (id) => apiClient.delete(`/patients/diseases/${id}/`)

// Diagnoses
export const getPatientDiagnoses = (patientId) => apiClient.get('/patients/diagnoses/', { params: { patient: patientId } })
export const createPatientDiagnosis = (data) => apiClient.post('/patients/diagnoses/', data)
export const updatePatientDiagnosis = (id, data) => apiClient.put(`/patients/diagnoses/${id}/`, data)
export const deletePatientDiagnosis = (id) => apiClient.delete(`/patients/diagnoses/${id}/`)

// Files
export const getPatientFiles = (patientId) => apiClient.get('/patients/files/', { params: { patient: patientId } })
export const uploadPatientFile = (data) => {
  const formData = new FormData()
  Object.keys(data).forEach((key) => {
    formData.append(key, data[key])
  })
  return apiClient.post('/patients/files/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
export const deletePatientFile = (id) => apiClient.delete(`/patients/files/${id}/`)

// Medical Examinations
export const getMedicalExaminations = (patientId) => apiClient.get('/patients/examinations/', { params: { patient: patientId } })
export const getMedicalExamination = (id) => apiClient.get(`/patients/examinations/${id}/`)
export const createMedicalExamination = (data) => apiClient.post('/patients/examinations/', data)
export const updateMedicalExamination = (id, data) => apiClient.patch(`/patients/examinations/${id}/`, data)
export const deleteMedicalExamination = (id) => apiClient.delete(`/patients/examinations/${id}/`)

// Medical Examination - Past Diseases
export const getMedExamPastDiseases = (examinationId) => apiClient.get('/patients/exam-past-diseases/', { params: { examination: examinationId } })
export const createMedExamPastDisease = (data) => apiClient.post('/patients/exam-past-diseases/', data)
export const updateMedExamPastDisease = (id, data) => apiClient.patch(`/patients/exam-past-diseases/${id}/`, data)
export const deleteMedExamPastDisease = (id) => apiClient.delete(`/patients/exam-past-diseases/${id}/`)

// Medical Examination - Vaccinations
export const getMedExamVaccinations = (examinationId) => apiClient.get('/patients/exam-vaccinations/', { params: { examination: examinationId } })
export const createMedExamVaccination = (data) => apiClient.post('/patients/exam-vaccinations/', data)
export const updateMedExamVaccination = (id, data) => apiClient.patch(`/patients/exam-vaccinations/${id}/`, data)
export const deleteMedExamVaccination = (id) => apiClient.delete(`/patients/exam-vaccinations/${id}/`)

// Medical Examination - Lab Tests
export const getMedExamLabTests = (examinationId) => apiClient.get('/patients/exam-lab-tests/', { params: { examination: examinationId } })
export const createMedExamLabTest = (data) => apiClient.post('/patients/exam-lab-tests/', data)
export const updateMedExamLabTest = (id, data) => apiClient.patch(`/patients/exam-lab-tests/${id}/`, data)
export const deleteMedExamLabTest = (id) => apiClient.delete(`/patients/exam-lab-tests/${id}/`)

// Treatment Plans
export const getTreatmentPlans = (patientId) => apiClient.get('/patients/treatment-plans/', { params: { patient: patientId } })
export const getTreatmentPlan = (id) => apiClient.get(`/patients/treatment-plans/${id}/`)
export const createTreatmentPlan = (data) => apiClient.post('/patients/treatment-plans/', data)
export const updateTreatmentPlan = (id, data) => apiClient.patch(`/patients/treatment-plans/${id}/`, data)
export const deleteTreatmentPlan = (id) => apiClient.delete(`/patients/treatment-plans/${id}/`)
export const freezeTreatmentPlanPrices = (id) => apiClient.post(`/patients/treatment-plans/${id}/freeze_prices/`)
export const saveTreatmentPlanAsTemplate = (id, data) => apiClient.post(`/patients/treatment-plans/${id}/save_as_template/`, data)

// Treatment Plan Stages
export const getTreatmentStages = (planId) => apiClient.get('/patients/treatment-stages/', { params: { plan: planId } })
export const createTreatmentStage = (data) => apiClient.post('/patients/treatment-stages/', data)
export const updateTreatmentStage = (id, data) => apiClient.patch(`/patients/treatment-stages/${id}/`, data)
export const deleteTreatmentStage = (id) => apiClient.delete(`/patients/treatment-stages/${id}/`)

// Treatment Plan Stage Items
export const getTreatmentStageItems = (stageId) => apiClient.get('/patients/treatment-stage-items/', { params: { stage: stageId } })
export const createTreatmentStageItem = (data) => apiClient.post('/patients/treatment-stage-items/', data)
export const updateTreatmentStageItem = (id, data) => apiClient.patch(`/patients/treatment-stage-items/${id}/`, data)
export const deleteTreatmentStageItem = (id) => apiClient.delete(`/patients/treatment-stage-items/${id}/`)

// Treatment Plan Templates
export const getTreatmentPlanTemplates = () => apiClient.get('/patients/treatment-plan-templates/')
export const createTreatmentPlanTemplate = (data) => apiClient.post('/patients/treatment-plan-templates/', data)
export const updateTreatmentPlanTemplate = (id, data) => apiClient.patch(`/patients/treatment-plan-templates/${id}/`, data)
export const deleteTreatmentPlanTemplate = (id) => apiClient.delete(`/patients/treatment-plan-templates/${id}/`)

// AI Analysis
export const getPatientAIAnalysis = (patientId) => apiClient.post(`/patients/patients/${patientId}/ai-analysis/`)

