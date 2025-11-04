import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/LoginPage.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'schedule',
          component: () => import('@/pages/SchedulePage.vue')
        },
        {
          path: '/visits',
          name: 'visits',
          component: () => import('@/pages/VisitsPage.vue')
        },
        {
          path: '/patients',
          name: 'patients',
          component: () => import('@/pages/PatientsPage.vue')
        },
        {
          path: '/services',
          name: 'services',
          component: () => import('@/pages/ServicesPage.vue')
        },
        {
          path: '/staff',
          name: 'staff',
          component: () => import('@/pages/StaffPage.vue')
        },
        {
          path: '/warehouse',
          name: 'warehouse',
          component: () => import('@/pages/WarehousePage.vue')
        },
        {
          path: '/billing',
          name: 'billing',
          component: () => import('@/pages/BillingPage.vue')
        },
        {
          path: '/marketing',
          name: 'marketing',
          component: () => import('@/pages/MarketingPage.vue')
        },
        {
          path: '/reports',
          name: 'reports',
          component: () => import('@/pages/ReportsPage.vue')
        },
        {
          path: '/settings',
          name: 'settings',
          component: () => import('@/pages/SettingsPage.vue'),
          children: [
            {
              path: 'clinic',
              name: 'settings-clinic',
              component: () => import('@/pages/SettingsClinicPage.vue')
            }
          ]
        }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router

