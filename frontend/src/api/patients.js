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

