/**
 * Composable for consent system
 */
import { ref } from 'vue'
import { useMessage } from 'naive-ui'
import { getAccessRequests, getAccessGrants, getAuditLogs } from '@/api/consent'

export function useConsent() {
  const message = useMessage()
  const loading = ref(false)
  const accessRequests = ref([])
  const accessGrants = ref([])
  const auditLogs = ref([])

  /**
   * Load access requests for patient
   */
  const loadAccessRequests = async (patientId) => {
    loading.value = true
    try {
      const data = await getAccessRequests({ patient_id: patientId })
      accessRequests.value = data.results || data
      return accessRequests.value
    } catch (error) {
      console.error('Error loading access requests:', error)
      message.error('Ошибка загрузки запросов доступа')
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Load access grants for patient
   */
  const loadAccessGrants = async (patientId) => {
    loading.value = true
    try {
      const data = await getAccessGrants({
        patient_id: patientId,
        active_only: true
      })
      accessGrants.value = data.results || data
      return accessGrants.value
    } catch (error) {
      console.error('Error loading access grants:', error)
      message.error('Ошибка загрузки доступов')
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Load audit logs for patient
   */
  const loadAuditLogs = async (patientId) => {
    loading.value = true
    try {
      const data = await getAuditLogs({ patient_id: patientId })
      auditLogs.value = data.results || data
      return auditLogs.value
    } catch (error) {
      console.error('Error loading audit logs:', error)
      message.error('Ошибка загрузки истории')
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Check if current user has access to patient
   */
  const hasAccessToPatient = (patientId) => {
    return accessGrants.value.some(
      grant => grant.patient === patientId && grant.is_active
    )
  }

  /**
   * Check if current user has specific scope for patient
   */
  const hasScope = (patientId, scope) => {
    const grant = accessGrants.value.find(
      g => g.patient === patientId && g.is_active
    )
    return grant?.scopes?.includes(scope) || false
  }

  return {
    loading,
    accessRequests,
    accessGrants,
    auditLogs,
    loadAccessRequests,
    loadAccessGrants,
    loadAuditLogs,
    hasAccessToPatient,
    hasScope
  }
}

