<template>
  <div class="main-layout">
    <aside class="sidebar">
      <div class="logo">
        <h2>Medicine ERP</h2>
      </div>
      <nav class="menu">
        <router-link to="/" class="menu-item">
          📅 Расписание
        </router-link>
        <router-link to="/patients" class="menu-item">
          👥 Пациенты
        </router-link>
        <router-link to="/services" class="menu-item">
          🦷 Услуги
        </router-link>
        <router-link to="/staff" class="menu-item">
          👨‍⚕️ Сотрудники
        </router-link>
        <router-link to="/visits" class="menu-item">
          📋 Визиты
        </router-link>
        <router-link to="/billing" class="menu-item">
          💰 Финансы
        </router-link>
        <router-link to="/warehouse" class="menu-item">
          📦 Склад
        </router-link>
        <router-link to="/marketing" class="menu-item">
          📧 Маркетинг
        </router-link>
        <router-link to="/reports" class="menu-item">
          📊 Отчёты
        </router-link>
        <router-link to="/settings/clinic" class="menu-item">
          ⚙️ Настройки
        </router-link>
      </nav>
      <div class="user-section">
        <n-button text @click="handleLogout">
          🚪 Выход
        </n-button>
      </div>
    </aside>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped lang="scss">
@import '@/styles/tokens.scss';

.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 260px;
  background: $bg-secondary;
  border-right: 1px solid $border-color;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.logo {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color;
  
  h2 {
    margin: 0;
    font-size: 20px;
    color: $primary-color;
  }
}

.menu {
  flex: 1;
  padding: $spacing-md 0;
  overflow-y: auto;
}

.menu-item {
  display: block;
  padding: $spacing-md $spacing-lg;
  color: $text-secondary;
  text-decoration: none;
  transition: all $transition-fast;
  
  &:hover {
    background: $bg-tertiary;
    color: $text-primary;
    text-decoration: none;
  }
  
  &.router-link-active {
    background: $bg-tertiary;
    color: $primary-color;
    border-left: 3px solid $primary-color;
  }
}

.user-section {
  padding: $spacing-lg;
  border-top: 1px solid $border-color;
}

.content {
  flex: 1;
  overflow-y: auto;
  background: $bg-primary;
}
</style>

