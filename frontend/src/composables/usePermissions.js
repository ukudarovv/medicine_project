/**
 * Role-based permissions composable - Sprint 5
 */
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function usePermissions() {
  const authStore = useAuthStore()
  
  const user = computed(() => authStore.user)
  const userRole = computed(() => user.value?.role || 'readonly')
  
  // Can edit patient data
  const canEditPatients = computed(() => 
    ['owner', 'branch_admin', 'doctor', 'registrar'].includes(userRole.value)
  )
  
  // Can view financial data
  const canViewFinancial = computed(() => 
    ['owner', 'branch_admin', 'cashier'].includes(userRole.value)
  )
  
  // Can edit financial data
  const canEditFinancial = computed(() => 
    ['owner', 'branch_admin', 'cashier'].includes(userRole.value)
  )
  
  // Can manage staff
  const canManageStaff = computed(() => 
    ['owner', 'branch_admin'].includes(userRole.value)
  )
  
  // Can view reports
  const canViewReports = computed(() => 
    ['owner', 'branch_admin', 'cashier'].includes(userRole.value)
  )
  
  // Can delete records
  const canDelete = computed(() => 
    ['owner', 'branch_admin'].includes(userRole.value)
  )
  
  // Can manage services/prices
  const canManageServices = computed(() => 
    ['owner', 'branch_admin'].includes(userRole.value)
  )
  
  // Can conduct visits
  const canConductVisits = computed(() => 
    ['owner', 'branch_admin', 'doctor'].includes(userRole.value)
  )
  
  // Can manage calendar
  const canManageCalendar = computed(() => 
    ['owner', 'branch_admin', 'doctor', 'registrar'].includes(userRole.value)
  )
  
  // Can issue tax certificates
  const canIssueTaxCertificates = computed(() => 
    ['owner', 'branch_admin', 'cashier'].includes(userRole.value)
  )
  
  // Can configure payment providers
  const canConfigurePayments = computed(() => 
    ['owner', 'branch_admin'].includes(userRole.value)
  )
  
  return {
    user,
    userRole,
    canEditPatients,
    canViewFinancial,
    canEditFinancial,
    canManageStaff,
    canViewReports,
    canDelete,
    canManageServices,
    canConductVisits,
    canManageCalendar,
    canIssueTaxCertificates,
    canConfigurePayments,
  }
}

