<template>
  <n-config-provider :theme="darkTheme" :locale="ruRU" :date-locale="dateRuRU">
    <n-message-provider>
      <n-notification-provider>
        <router-view />
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { darkTheme, ruRU, dateRuRU } from 'naive-ui'
</script>

<style scoped>
#app {
  width: 100%;
  height: 100vh;
}
</style>

