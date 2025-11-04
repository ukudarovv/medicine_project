/**
 * Input masks for KZ-specific fields - Sprint 5
 */

export const masks = {
  // IIN: 12 digits
  iin: '############',
  
  // Phone KZ: +7 7XX XXX-XX-XX
  phoneKZ: '+# ### ###-##-##',
  
  // Date: dd.mm.yyyy
  date: '##.##.####',
  
  // Postal code KZ: 6 digits
  postalCode: '######',
}

/**
 * Validate IIN format (12 digits)
 */
export function validateIINFormat(iin) {
  if (!iin) return { valid: false, error: 'ИИН обязателен' }
  
  const cleaned = iin.replace(/\D/g, '')
  if (cleaned.length !== 12) {
    return { valid: false, error: 'ИИН должен содержать 12 цифр' }
  }
  
  return { valid: true }
}

/**
 * Validate KZ phone format
 */
export function validatePhoneKZ(phone) {
  if (!phone) return { valid: false, error: 'Телефон обязателен' }
  
  const cleaned = phone.replace(/\D/g, '')
  
  // Should start with 77
  if (!cleaned.startsWith('77')) {
    return { valid: false, error: 'Телефон должен начинаться с +7 7XX' }
  }
  
  if (cleaned.length !== 11) {
    return { valid: false, error: 'Неверный формат телефона' }
  }
  
  return { valid: true }
}

/**
 * Format phone number for display
 */
export function formatPhoneKZ(phone) {
  if (!phone) return ''
  
  const cleaned = phone.replace(/\D/g, '')
  
  if (cleaned.length === 11) {
    // +7 7XX XXX-XX-XX
    return `+${cleaned[0]} ${cleaned.slice(1, 4)} ${cleaned.slice(4, 7)}-${cleaned.slice(7, 9)}-${cleaned.slice(9, 11)}`
  }
  
  return phone
}

/**
 * Format IIN for display
 */
export function formatIIN(iin) {
  if (!iin) return ''
  
  const cleaned = iin.replace(/\D/g, '')
  
  if (cleaned.length === 12) {
    // YYMMDD XXXX CY format
    return `${cleaned.slice(0, 6)} ${cleaned.slice(6, 10)} ${cleaned.slice(10, 12)}`
  }
  
  return iin
}

/**
 * Extract birth date from IIN
 */
export function extractBirthDateFromIIN(iin) {
  if (!iin) return null
  
  const cleaned = iin.replace(/\D/g, '')
  if (cleaned.length !== 12) return null
  
  const yy = parseInt(cleaned.slice(0, 2))
  const mm = parseInt(cleaned.slice(2, 4))
  const dd = parseInt(cleaned.slice(4, 6))
  const centuryIndicator = parseInt(cleaned[6])
  
  // Determine century
  let year
  if (centuryIndicator === 1 || centuryIndicator === 2) {
    year = 1800 + yy
  } else if (centuryIndicator === 3 || centuryIndicator === 4) {
    year = 1900 + yy
  } else if (centuryIndicator === 5 || centuryIndicator === 6) {
    year = 2000 + yy
  } else {
    return null
  }
  
  try {
    return new Date(year, mm - 1, dd)
  } catch {
    return null
  }
}

/**
 * Extract sex from IIN
 */
export function extractSexFromIIN(iin) {
  if (!iin) return null
  
  const cleaned = iin.replace(/\D/g, '')
  if (cleaned.length !== 12) return null
  
  const centuryIndicator = parseInt(cleaned[6])
  
  // Odd = male, even = female
  return centuryIndicator % 2 === 1 ? 'M' : 'F'
}

