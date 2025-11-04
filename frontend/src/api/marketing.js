import api from './axios'

// Reminders
export const getReminders = (params) => api.get('/comms/marketing/reminders/', { params })
export const getReminder = (id) => api.get(`/comms/marketing/reminders/${id}/`)
export const createReminder = (data) => api.post('/comms/marketing/reminders/', data)
export const updateReminder = (id, data) => api.patch(`/comms/marketing/reminders/${id}/`, data)
export const deleteReminder = (id) => api.delete(`/comms/marketing/reminders/${id}/`)
export const toggleReminder = (id) => api.patch(`/comms/marketing/reminders/${id}/toggle/`)
export const testReminder = (id, phone) => api.post(`/comms/marketing/reminders/${id}/test/`, { phone })

// Campaigns
export const getCampaigns = (params) => api.get('/comms/marketing/campaigns/', { params })
export const getCampaign = (id) => api.get(`/comms/marketing/campaigns/${id}/`)
export const createCampaign = (data) => api.post('/comms/marketing/campaigns/', data)
export const updateCampaign = (id, data) => api.patch(`/comms/marketing/campaigns/${id}/`, data)
export const deleteCampaign = (id) => api.delete(`/comms/marketing/campaigns/${id}/`)
export const prepareCampaign = (id, filters) => api.post(`/comms/marketing/campaigns/${id}/prepare/`, { filters })
export const scheduleCampaign = (id, data) => api.post(`/comms/marketing/campaigns/${id}/schedule/`, data)
export const pauseCampaign = (id) => api.post(`/comms/marketing/campaigns/${id}/pause/`)
export const resumeCampaign = (id) => api.post(`/comms/marketing/campaigns/${id}/resume/`)
export const exportCampaign = (id) => api.get(`/comms/marketing/campaigns/${id}/export/`)

// Manual message
export const sendManualMessage = (data) => api.post('/comms/marketing/message-log/send_manual/', data)

// Contact log (reports)
export const getContactLogs = (params) => api.get('/comms/marketing/contact-log/', { params })

// SMS balance
export const getSmsBalance = (params) => api.get('/comms/marketing/sms-balance/', { params })
export const getCurrentBalance = () => api.get('/comms/marketing/sms-balance/current/')

// SMS Providers
export const getSmsProviders = () => api.get('/comms/marketing/providers/')
export const getSmsProvider = (id) => api.get(`/comms/marketing/providers/${id}/`)
export const createSmsProvider = (data) => api.post('/comms/marketing/providers/', data)
export const updateSmsProvider = (id, data) => api.patch(`/comms/marketing/providers/${id}/`, data)
export const deleteSmsProvider = (id) => api.delete(`/comms/marketing/providers/${id}/`)

export default {
  // Reminders
  getReminders,
  getReminder,
  createReminder,
  updateReminder,
  deleteReminder,
  toggleReminder,
  testReminder,
  
  // Campaigns
  getCampaigns,
  getCampaign,
  createCampaign,
  updateCampaign,
  deleteCampaign,
  prepareCampaign,
  scheduleCampaign,
  pauseCampaign,
  resumeCampaign,
  exportCampaign,
  
  // Manual message
  sendManualMessage,
  
  // Reports
  getContactLogs,
  getSmsBalance,
  getCurrentBalance,
  
  // Providers
  getSmsProviders,
  getSmsProvider,
  createSmsProvider,
  updateSmsProvider,
  deleteSmsProvider,
}

