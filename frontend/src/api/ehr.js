/**
 * API client for EHR (Electronic Health Records) system
 */
import axios from './axios'

/**
 * Get EHR records for a patient
 * @param {Object} params - Query parameters
 * @param {number} params.patient_id - Patient ID (required)
 * @param {boolean} params.include_external - Include external org records
 * @param {string} params.record_type - Filter by record type
 * @returns {Promise<Array>} List of EHR records
 */
export const getEHRRecords = async (params = {}) => {
  const response = await axios.get('/ehr/records/', { params })
  return response.data
}

/**
 * Get patient EHR summary
 * @param {number} patientId - Patient ID
 * @returns {Promise<Object>} Patient EHR summary
 */
export const getPatientEHRSummary = async (patientId) => {
  const response = await axios.get('/ehr/records/patient_summary/', {
    params: { patient_id: patientId }
  })
  return response.data
}

/**
 * Get single EHR record
 * @param {string} recordId - Record UUID
 * @returns {Promise<Object>} EHR record
 */
export const getEHRRecord = async (recordId) => {
  const response = await axios.get(`/ehr/records/${recordId}/`)
  return response.data
}

/**
 * Create new EHR record
 * @param {Object} data - Record data
 * @returns {Promise<Object>} Created record
 */
export const createEHRRecord = async (data) => {
  const response = await axios.post('/ehr/records/', data)
  return response.data
}

/**
 * Update EHR record (creates new version)
 * @param {string} recordId - Record UUID
 * @param {Object} data - Updated data
 * @returns {Promise<Object>} New version of record
 */
export const updateEHRRecord = async (recordId, data) => {
  const response = await axios.put(`/ehr/records/${recordId}/`, data)
  return response.data
}

/**
 * Delete EHR record (soft delete)
 * @param {string} recordId - Record UUID
 * @returns {Promise<void>}
 */
export const deleteEHRRecord = async (recordId) => {
  await axios.delete(`/ehr/records/${recordId}/`)
}

export default {
  getEHRRecords,
  getPatientEHRSummary,
  getEHRRecord,
  createEHRRecord,
  updateEHRRecord,
  deleteEHRRecord
}

