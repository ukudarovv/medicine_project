import apiClient from './axios'

/**
 * Calendar API module
 * Handles appointments, breaks, availability, and waitlist
 */

// ==================== Appointments ====================

export const getAppointments = (params) => apiClient.get('/calendar/appointments', { params })
export const getAppointment = (id) => apiClient.get(`/calendar/appointments/${id}`)
export const createAppointment = (data) => apiClient.post('/calendar/appointments', data)
export const updateAppointment = (id, data) => apiClient.patch(`/calendar/appointments/${id}`, data)
export const deleteAppointment = (id) => apiClient.delete(`/calendar/appointments/${id}`)

// ==================== Breaks ====================

export const getBreaks = (params) => apiClient.get('/calendar/breaks', { params })
export const getBreak = (id) => apiClient.get(`/calendar/breaks/${id}`)
export const createBreak = (data) => apiClient.post('/calendar/breaks', data)
export const updateBreak = (id, data) => apiClient.patch(`/calendar/breaks/${id}`, data)
export const deleteBreak = (id) => apiClient.delete(`/calendar/breaks/${id}`)
export const deleteRecurringBreaks = (params) => 
  apiClient.delete('/calendar/breaks/delete_recurring', { params })

// ==================== Availability ====================

export const getAvailability = (params) => apiClient.get('/calendar/availability', { params })
export const createAvailability = (data) => apiClient.post('/calendar/availability', data)
export const updateAvailability = (id, data) => apiClient.patch(`/calendar/availability/${id}`, data)
export const deleteAvailability = (id) => apiClient.delete(`/calendar/availability/${id}`)

// ==================== Waitlist ====================

export const getWaitlist = (params) => apiClient.get('/calendar/waitlist', { params })
export const createWaitlistEntry = (data) => apiClient.post('/calendar/waitlist', data)
export const updateWaitlistEntry = (id, data) => apiClient.patch(`/calendar/waitlist/${id}`, data)
export const deleteWaitlistEntry = (id) => apiClient.delete(`/calendar/waitlist/${id}`)
export const markWaitlistContacted = (id, data) => 
  apiClient.post(`/calendar/waitlist/${id}/mark_contacted`, data)

export default {
  getAppointments,
  getAppointment,
  createAppointment,
  updateAppointment,
  deleteAppointment,
  getBreaks,
  getBreak,
  createBreak,
  updateBreak,
  deleteBreak,
  deleteRecurringBreaks,
  getAvailability,
  createAvailability,
  updateAvailability,
  deleteAvailability,
  getWaitlist,
  createWaitlistEntry,
  updateWaitlistEntry,
  deleteWaitlistEntry,
  markWaitlistContacted
}

