<template>
  <div class="login-page">
    <n-card class="login-card" title="Medicine ERP">
      <n-form ref="formRef" :model="formData" :rules="rules">
        <n-form-item label="Логин" path="username">
          <n-input v-model:value="formData.username" placeholder="Введите логин" />
        </n-form-item>
        <n-form-item label="Пароль" path="password">
          <n-input
            v-model:value="formData.password"
            type="password"
            placeholder="Введите пароль"
            @keyup.enter="handleLogin"
          />
        </n-form-item>
        <n-button type="primary" block :loading="loading" @click="handleLogin">
          Войти
        </n-button>
      </n-form>
    </n-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMessage } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()

const formRef = ref(null)
const loading = ref(false)

const formData = ref({
  username: '',
  password: ''
})

const rules = {
  username: { required: true, message: 'Введите логин', trigger: 'blur' },
  password: { required: true, message: 'Введите пароль', trigger: 'blur' }
}

async function handleLogin() {
  try {
    await formRef.value?.validate()
    loading.value = true
    
    await authStore.login(formData.value.username, formData.value.password)
    
    message.success('Успешный вход')
    router.push('/')
  } catch (error) {
    if (error.response) {
      message.error('Неверный логин или пароль')
    } else {
      console.error('Login error:', error)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #121212 0%, #1E1E1E 100%);
}

.login-card {
  width: 100%;
  max-width: 400px;
}
</style>

