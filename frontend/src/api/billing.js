import axios from './axios'

/**
 * Billing API module
 * Handles invoices, payments, cash shifts, and financial statistics
 */

// ==================== Statistics ====================

/**
 * Get billing statistics for dashboard
 * @param {string} startDate - Start date (ISO format)
 * @param {string} endDate - End date (ISO format)
 */
export const getBillingStatistics = (startDate = null, endDate = null) => {
  const params = {}
  if (startDate) params.start_date = startDate
  if (endDate) params.end_date = endDate
  
  return axios.get('/billing/invoices/statistics/', { params })
}

/**
 * Get all transactions (unified format for display)
 * @param {string} startDate - Start date (ISO format)
 * @param {string} endDate - End date (ISO format)
 */
export const getTransactions = (startDate = null, endDate = null) => {
  const params = {}
  if (startDate) params.start_date = startDate
  if (endDate) params.end_date = endDate
  
  return axios.get('/billing/invoices/transactions/', { params })
}

// ==================== Invoices ====================

/**
 * Get all invoices
 * @param {Object} params - Query parameters (status, start_date, end_date)
 */
export const getInvoices = (params = {}) => {
  return axios.get('/billing/invoices/', { params })
}

/**
 * Get invoice by ID
 * @param {number} id - Invoice ID
 */
export const getInvoice = (id) => {
  return axios.get(`/billing/invoices/${id}/`)
}

/**
 * Create new invoice
 * @param {Object} data - Invoice data
 */
export const createInvoice = (data) => {
  return axios.post('/billing/invoices/', data)
}

/**
 * Update invoice
 * @param {number} id - Invoice ID
 * @param {Object} data - Updated invoice data
 */
export const updateInvoice = (id, data) => {
  return axios.patch(`/billing/invoices/${id}/`, data)
}

/**
 * Delete invoice
 * @param {number} id - Invoice ID
 */
export const deleteInvoice = (id) => {
  return axios.delete(`/billing/invoices/${id}/`)
}

// ==================== Payments ====================

/**
 * Get all payments
 * @param {Object} params - Query parameters
 */
export const getPayments = (params = {}) => {
  return axios.get('/billing/payments/', { params })
}

/**
 * Get payment by ID
 * @param {number} id - Payment ID
 */
export const getPayment = (id) => {
  return axios.get(`/billing/payments/${id}/`)
}

/**
 * Create new payment
 * @param {Object} data - Payment data
 * @param {number} data.invoice - Invoice ID
 * @param {string} data.method - Payment method (cash, card, kaspi, kaspi_qr, halyk_pay, etc.)
 * @param {number} data.amount - Payment amount
 */
export const createPayment = (data) => {
  return axios.post('/billing/payments/', data)
}

/**
 * Update payment
 * @param {number} id - Payment ID
 * @param {Object} data - Updated payment data
 */
export const updatePayment = (id, data) => {
  return axios.patch(`/billing/payments/${id}/`, data)
}

/**
 * Delete payment
 * @param {number} id - Payment ID
 */
export const deletePayment = (id) => {
  return axios.delete(`/billing/payments/${id}/`)
}

// ==================== Cash Shifts ====================

/**
 * Get all cash shifts
 * @param {Object} params - Query parameters (active: true/false)
 */
export const getCashShifts = (params = {}) => {
  return axios.get('/billing/cashshifts/', { params })
}

/**
 * Get current open cash shift for a branch
 * @param {number} branchId - Branch ID
 */
export const getCurrentCashShift = (branchId) => {
  return axios.get('/billing/cashshifts/current/', {
    params: { branch: branchId }
  })
}

/**
 * Open new cash shift
 * @param {Object} data - Cash shift data
 * @param {number} data.branch - Branch ID
 * @param {number} data.opening_balance - Opening balance
 */
export const openCashShift = (data) => {
  return axios.post('/billing/cashshifts/', data)
}

/**
 * Close cash shift
 * @param {number} id - Cash shift ID
 * @param {number} closingBalance - Closing balance
 */
export const closeCashShift = (id, closingBalance) => {
  return axios.post(`/billing/cashshifts/${id}/close/`, {
    closing_balance: closingBalance
  })
}

/**
 * Export payments to 1C format
 * @param {string} startDate - Start date (ISO format)
 * @param {string} endDate - End date (ISO format)
 */
export const export1C = (startDate, endDate) => {
  return axios.get('/billing/cashshifts/export_1c/', {
    params: {
      start_date: startDate,
      end_date: endDate
    },
    responseType: 'blob'
  })
}

// ==================== Tax Certificates ====================

/**
 * Get tax deduction certificates
 * @param {Object} params - Query parameters (patient)
 */
export const getTaxCertificates = (params = {}) => {
  return axios.get('/billing/tax-certificates/', { params })
}

/**
 * Create tax deduction certificate
 * @param {Object} data - Certificate data
 */
export const createTaxCertificate = (data) => {
  return axios.post('/billing/tax-certificates/', data)
}

/**
 * Update tax certificate
 * @param {number} id - Certificate ID
 * @param {Object} data - Updated certificate data
 */
export const updateTaxCertificate = (id, data) => {
  return axios.patch(`/billing/tax-certificates/${id}/`, data)
}

/**
 * Delete tax certificate
 * @param {number} id - Certificate ID
 */
export const deleteTaxCertificate = (id) => {
  return axios.delete(`/billing/tax-certificates/${id}/`)
}

// ==================== Payment Providers ====================

/**
 * Get payment providers
 */
export const getPaymentProviders = () => {
  return axios.get('/billing/payment-providers/')
}

/**
 * Create payment provider configuration
 * @param {Object} data - Provider data
 */
export const createPaymentProvider = (data) => {
  return axios.post('/billing/payment-providers/', data)
}

/**
 * Update payment provider
 * @param {number} id - Provider ID
 * @param {Object} data - Updated provider data
 */
export const updatePaymentProvider = (id, data) => {
  return axios.patch(`/billing/payment-providers/${id}/`, data)
}

/**
 * Delete payment provider
 * @param {number} id - Provider ID
 */
export const deletePaymentProvider = (id) => {
  return axios.delete(`/billing/payment-providers/${id}/`)
}

