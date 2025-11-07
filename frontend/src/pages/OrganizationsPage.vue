<template>
  <div class="organizations-page">
    <n-page-header title="Управление организациями">
      <template #extra>
        <n-space>
          <n-button 
            v-if="isAdmin" 
            type="primary" 
            @click="openCreateModal"
          >
            + Новая организация
          </n-button>
          <n-button 
            v-if="currentOrg" 
            type="primary" 
            @click="openUsersModal"
          >
            👥 Пользователи
          </n-button>
        </n-space>
      </template>
    </n-page-header>

    <div class="page-content">
      <n-space vertical :size="16">
        <!-- Filters -->
        <n-space>
          <n-input
            v-model:value="searchQuery"
            placeholder="Поиск организаций..."
            clearable
            style="width: 300px"
          >
            <template #prefix>
              <span>🔍</span>
            </template>
          </n-input>
        </n-space>

        <!-- Organizations Table -->
        <n-data-table
          :columns="columns"
          :data="filteredOrganizations"
          :loading="loading"
          :pagination="paginationConfig"
          :row-key="(row) => row.id"
        />
      </n-space>
    </div>

    <!-- Create/Edit Organization Modal -->
    <n-modal
      v-model:show="showOrgModal"
      preset="card"
      :title="editingOrg ? 'Редактировать организацию' : 'Новая организация'"
      style="width: 700px"
      :segmented="{ content: 'soft' }"
    >
      <n-form
        ref="orgFormRef"
        :model="orgForm"
        :rules="orgRules"
        label-placement="left"
        label-width="180"
      >
        <n-divider title-placement="left">Информация об организации</n-divider>
        
        <n-form-item label="Название" path="name">
          <n-input v-model:value="orgForm.name" placeholder="Название организации" />
        </n-form-item>

        <n-form-item label="SMS отправитель" path="sms_sender">
          <n-input v-model:value="orgForm.sms_sender" placeholder="Имя отправителя SMS" />
        </n-form-item>

        <n-form-item label="Логотип">
          <n-upload
            :max="1"
            list-type="image-card"
            @change="handleLogoChange"
          >
            Загрузить логотип
          </n-upload>
        </n-form-item>

        <!-- Owner creation section - only for new organizations -->
        <template v-if="!editingOrg">
          <n-divider title-placement="left">Владелец организации (опционально)</n-divider>
          
          <n-form-item label="Создать владельца">
            <n-switch v-model:value="orgForm.createOwner" />
            <span style="margin-left: 12px; color: #999;">Создать пользователя с правами владельца</span>
          </n-form-item>

          <template v-if="orgForm.createOwner">
            <n-form-item label="Имя пользователя" path="owner_username">
              <n-input v-model:value="orgForm.owner_username" placeholder="username" />
            </n-form-item>

            <n-form-item label="Email" path="owner_email">
              <n-input v-model:value="orgForm.owner_email" type="email" placeholder="email@example.com" />
            </n-form-item>

            <n-form-item label="Имя" path="owner_first_name">
              <n-input v-model:value="orgForm.owner_first_name" placeholder="Имя" />
            </n-form-item>

            <n-form-item label="Фамилия" path="owner_last_name">
              <n-input v-model:value="orgForm.owner_last_name" placeholder="Фамилия" />
            </n-form-item>

            <n-form-item label="Телефон" path="owner_phone">
              <n-input v-model:value="orgForm.owner_phone" placeholder="+7 777 123 45 67" />
            </n-form-item>

            <n-form-item label="Пароль" path="owner_password">
              <n-input
                v-model:value="orgForm.owner_password"
                type="password"
                placeholder="Пароль"
                show-password-on="click"
              />
            </n-form-item>

            <n-form-item label="Подтверждение" path="owner_password2">
              <n-input
                v-model:value="orgForm.owner_password2"
                type="password"
                placeholder="Повторите пароль"
                show-password-on="click"
              />
            </n-form-item>
          </template>
        </template>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showOrgModal = false">Отмена</n-button>
          <n-button type="primary" @click="handleSaveOrg" :loading="saving">
            Сохранить
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- Users Management Modal -->
    <n-modal
      v-model:show="showUsersModal"
      preset="card"
      title="Пользователи организации"
      style="width: 900px"
      :segmented="{ content: 'soft' }"
    >
      <n-space vertical :size="16">
        <n-space justify="space-between">
          <n-input
            v-model:value="usersSearch"
            placeholder="Поиск пользователей..."
            clearable
            style="width: 300px"
          >
            <template #prefix>
              <span>🔍</span>
            </template>
          </n-input>
          <n-button type="primary" @click="openCreateUserModal">
            + Новый пользователь
          </n-button>
        </n-space>

        <n-data-table
          :columns="userColumns"
          :data="filteredUsers"
          :loading="loadingUsers"
          :pagination="{ pageSize: 10 }"
          :row-key="(row) => row.id"
        />
      </n-space>
    </n-modal>

    <!-- Create User Modal -->
    <n-modal
      v-model:show="showCreateUserModal"
      preset="card"
      :title="editingUser ? 'Редактировать пользователя' : 'Новый пользователь'"
      style="width: 600px"
      :segmented="{ content: 'soft' }"
    >
      <n-form
        ref="userFormRef"
        :model="userForm"
        :rules="userRules"
        label-placement="left"
        label-width="150"
      >
        <n-form-item label="Имя пользователя" path="username">
          <n-input v-model:value="userForm.username" placeholder="username" />
        </n-form-item>

        <n-form-item label="Email" path="email">
          <n-input v-model:value="userForm.email" type="email" placeholder="email@example.com" />
        </n-form-item>

        <n-form-item label="Имя" path="first_name">
          <n-input v-model:value="userForm.first_name" placeholder="Имя" />
        </n-form-item>

        <n-form-item label="Фамилия" path="last_name">
          <n-input v-model:value="userForm.last_name" placeholder="Фамилия" />
        </n-form-item>

        <n-form-item label="Телефон" path="phone">
          <n-input v-model:value="userForm.phone" placeholder="+7 777 123 45 67" />
        </n-form-item>

        <n-form-item label="Роль" path="role">
          <n-select
            v-model:value="userForm.role"
            :options="roleOptions"
            placeholder="Выберите роль"
          />
        </n-form-item>

        <n-form-item v-if="!editingUser" label="Пароль" path="password">
          <n-input
            v-model:value="userForm.password"
            type="password"
            placeholder="Пароль"
            show-password-on="click"
          />
        </n-form-item>

        <n-form-item v-if="!editingUser" label="Подтверждение" path="password2">
          <n-input
            v-model:value="userForm.password2"
            type="password"
            placeholder="Повторите пароль"
            show-password-on="click"
          />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreateUserModal = false">Отмена</n-button>
          <n-button type="primary" @click="handleSaveUser" :loading="savingUser">
            Сохранить
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { NButton, NSpace, NTag, NDivider, NSwitch, useMessage, useDialog } from 'naive-ui'
import organizationsAPI from '@/api/organizations'
import { useAuthStore } from '@/stores/auth'

const message = useMessage()
const dialog = useDialog()
const authStore = useAuthStore()

// Check if user is admin
const isAdmin = computed(() => authStore.user?.is_superuser)
const isOwner = computed(() => authStore.user?.role === 'owner')
const currentOrg = computed(() => authStore.user?.organization)

// State
const organizations = ref([])
const loading = ref(false)
const searchQuery = ref('')
const showOrgModal = ref(false)
const showUsersModal = ref(false)
const showCreateUserModal = ref(false)
const editingOrg = ref(null)
const saving = ref(false)

// Users state
const users = ref([])
const loadingUsers = ref(false)
const usersSearch = ref('')
const editingUser = ref(null)
const savingUser = ref(false)
const selectedOrgForUsers = ref(null)

// Forms
const orgFormRef = ref(null)
const userFormRef = ref(null)

const orgForm = ref({
  name: '',
  sms_sender: '',
  logo: null,
  createOwner: false,
  owner_username: '',
  owner_email: '',
  owner_first_name: '',
  owner_last_name: '',
  owner_phone: '',
  owner_password: '',
  owner_password2: ''
})

const userForm = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  role: 'readonly',
  password: '',
  password2: ''
})

// Validation rules
const orgRules = {
  name: [
    { required: true, message: 'Введите название организации', trigger: 'blur' }
  ]
}

const userRules = {
  username: [
    { required: true, message: 'Введите имя пользователя', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Введите email', trigger: 'blur' },
    { type: 'email', message: 'Введите корректный email', trigger: 'blur' }
  ],
  role: [
    { required: true, message: 'Выберите роль', trigger: 'change' }
  ],
  password: [
    { required: true, message: 'Введите пароль', trigger: 'blur' },
    { min: 8, message: 'Пароль должен быть не менее 8 символов', trigger: 'blur' }
  ],
  password2: [
    { required: true, message: 'Подтвердите пароль', trigger: 'blur' },
    {
      validator: (rule, value) => {
        return value === userForm.value.password
      },
      message: 'Пароли не совпадают',
      trigger: 'blur'
    }
  ]
}

// Role options
const roleOptions = [
  { label: 'Владелец', value: 'owner' },
  { label: 'Администратор филиала', value: 'branch_admin' },
  { label: 'Доктор', value: 'doctor' },
  { label: 'Регистратор', value: 'registrar' },
  { label: 'Кассир', value: 'cashier' },
  { label: 'Склад', value: 'warehouse' },
  { label: 'Маркетолог', value: 'marketer' },
  { label: 'Только чтение', value: 'readonly' }
]

// Computed
const filteredOrganizations = computed(() => {
  if (!searchQuery.value) return organizations.value
  const query = searchQuery.value.toLowerCase()
  return organizations.value.filter(org =>
    org.name.toLowerCase().includes(query)
  )
})

const filteredUsers = computed(() => {
  if (!usersSearch.value) return users.value
  const query = usersSearch.value.toLowerCase()
  return users.value.filter(user =>
    user.username?.toLowerCase().includes(query) ||
    user.email?.toLowerCase().includes(query) ||
    user.full_name?.toLowerCase().includes(query)
  )
})

// Pagination
const paginationConfig = {
  pageSize: 20
}

// Columns
const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 70
  },
  {
    title: 'Название',
    key: 'name',
    ellipsis: true
  },
  {
    title: 'SMS отправитель',
    key: 'sms_sender',
    width: 150
  },
  {
    title: 'Филиалов',
    key: 'branches_count',
    width: 100
  },
  {
    title: 'Пользователей',
    key: 'users_count',
    width: 120
  },
  {
    title: 'Создана',
    key: 'created_at',
    width: 110,
    render: (row) => {
      return new Date(row.created_at).toLocaleDateString('ru-RU')
    }
  },
  {
    title: 'Действия',
    key: 'actions',
    width: 200,
    render: (row) => {
      return h(NSpace, null, {
        default: () => [
          h(
            NButton,
            {
              size: 'small',
              onClick: () => openUsersModalForOrg(row)
            },
            { default: () => '👥 Пользователи' }
          ),
          isAdmin.value && h(
            NButton,
            {
              size: 'small',
              onClick: () => openEditModal(row)
            },
            { default: () => '✏️' }
          ),
          isAdmin.value && h(
            NButton,
            {
              size: 'small',
              type: 'error',
              onClick: () => handleDeleteOrg(row)
            },
            { default: () => '🗑️' }
          )
        ]
      })
    }
  }
]

const userColumns = [
  {
    title: 'ID',
    key: 'id',
    width: 70
  },
  {
    title: 'Пользователь',
    key: 'username'
  },
  {
    title: 'ФИО',
    key: 'full_name'
  },
  {
    title: 'Email',
    key: 'email'
  },
  {
    title: 'Роль',
    key: 'role',
    width: 150,
    render: (row) => {
      const roleMap = {
        owner: { text: 'Владелец', type: 'success' },
        branch_admin: { text: 'Админ филиала', type: 'info' },
        doctor: { text: 'Доктор', type: 'primary' },
        registrar: { text: 'Регистратор', type: 'default' },
        cashier: { text: 'Кассир', type: 'warning' },
        warehouse: { text: 'Склад', type: 'default' },
        marketer: { text: 'Маркетолог', type: 'default' },
        readonly: { text: 'Только чтение', type: 'default' }
      }
      const role = roleMap[row.role] || { text: row.role, type: 'default' }
      return h(NTag, { type: role.type }, { default: () => role.text })
    }
  },
  {
    title: 'Статус',
    key: 'is_active',
    width: 100,
    render: (row) => {
      return h(
        NTag,
        { type: row.is_active ? 'success' : 'error' },
        { default: () => row.is_active ? 'Активен' : 'Неактивен' }
      )
    }
  },
  {
    title: 'Действия',
    key: 'actions',
    width: 150,
    render: (row) => {
      return h(NSpace, null, {
        default: () => [
          h(
            NButton,
            {
              size: 'small',
              onClick: () => openEditUserModal(row)
            },
            { default: () => '✏️' }
          ),
          h(
            NButton,
            {
              size: 'small',
              type: 'error',
              onClick: () => handleDeleteUser(row)
            },
            { default: () => '🗑️' }
          )
        ]
      })
    }
  }
]

// Methods
async function loadOrganizations() {
  loading.value = true
  try {
    const response = await organizationsAPI.getAll()
    // API returns paginated response, extract results array
    organizations.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to load organizations:', error)
    message.error('Ошибка загрузки организаций')
  } finally {
    loading.value = false
  }
}

async function loadUsers(orgId) {
  loadingUsers.value = true
  try {
    const response = await organizationsAPI.getAllUsers(orgId)
    // API returns paginated response for users too, extract results array
    users.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (error) {
    console.error('Failed to load users:', error)
    message.error('Ошибка загрузки пользователей')
  } finally {
    loadingUsers.value = false
  }
}

function openCreateModal() {
  editingOrg.value = null
  orgForm.value = {
    name: '',
    sms_sender: '',
    logo: null,
    createOwner: false,
    owner_username: '',
    owner_email: '',
    owner_first_name: '',
    owner_last_name: '',
    owner_phone: '',
    owner_password: '',
    owner_password2: ''
  }
  showOrgModal.value = true
}

function openEditModal(org) {
  editingOrg.value = org
  orgForm.value = {
    name: org.name,
    sms_sender: org.sms_sender || '',
    logo: null
  }
  showOrgModal.value = true
}

function openUsersModal() {
  if (isOwner.value && currentOrg.value) {
    selectedOrgForUsers.value = currentOrg.value
    loadUsers(currentOrg.value.id)
    showUsersModal.value = true
  }
}

function openUsersModalForOrg(org) {
  selectedOrgForUsers.value = org
  loadUsers(org.id)
  showUsersModal.value = true
}

function openCreateUserModal() {
  editingUser.value = null
  userForm.value = {
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    role: 'readonly',
    password: '',
    password2: ''
  }
  showCreateUserModal.value = true
}

function openEditUserModal(user) {
  editingUser.value = user
  userForm.value = {
    username: user.username,
    email: user.email || '',
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    phone: user.phone || '',
    role: user.role,
    password: '',
    password2: ''
  }
  showCreateUserModal.value = true
}

async function handleSaveOrg() {
  try {
    await orgFormRef.value?.validate()
    
    // Validate owner data if createOwner is true
    if (!editingOrg.value && orgForm.value.createOwner) {
      if (!orgForm.value.owner_username || !orgForm.value.owner_password) {
        message.error('Заполните имя пользователя и пароль для владельца')
        return
      }
      if (orgForm.value.owner_password !== orgForm.value.owner_password2) {
        message.error('Пароли не совпадают')
        return
      }
    }
    
    saving.value = true

    const formData = new FormData()
    formData.append('name', orgForm.value.name)
    if (orgForm.value.sms_sender) {
      formData.append('sms_sender', orgForm.value.sms_sender)
    }
    if (orgForm.value.logo) {
      formData.append('logo', orgForm.value.logo)
    }

    let createdOrg = null
    
    if (editingOrg.value) {
      await organizationsAPI.update(editingOrg.value.id, formData)
      message.success('Организация обновлена')
    } else {
      const response = await organizationsAPI.create(formData)
      createdOrg = response.data
      message.success('Организация создана')
      
      // Create owner if requested
      if (orgForm.value.createOwner) {
        try {
          const ownerData = {
            username: orgForm.value.owner_username,
            email: orgForm.value.owner_email,
            first_name: orgForm.value.owner_first_name,
            last_name: orgForm.value.owner_last_name,
            phone: orgForm.value.owner_phone,
            password: orgForm.value.owner_password,
            password2: orgForm.value.owner_password2,
            role: 'owner'
          }
          await organizationsAPI.createUser(createdOrg.id, ownerData)
          message.success('Владелец организации создан')
        } catch (ownerError) {
          console.error('Failed to create owner:', ownerError)
          message.warning('Организация создана, но не удалось создать владельца')
        }
      }
    }

    showOrgModal.value = false
    await loadOrganizations()
  } catch (error) {
    console.error('Failed to save organization:', error)
    if (error.response?.data) {
      const errors = Object.values(error.response.data).flat()
      message.error(errors.join(', '))
    } else {
      message.error('Ошибка сохранения организации')
    }
  } finally {
    saving.value = false
  }
}

async function handleSaveUser() {
  try {
    await userFormRef.value?.validate()
    savingUser.value = true

    const data = { ...userForm.value }

    if (editingUser.value) {
      // Update user
      delete data.password
      delete data.password2
      await organizationsAPI.updateUser(editingUser.value.id, data)
      message.success('Пользователь обновлен')
    } else {
      // Create user
      if (isAdmin.value) {
        data.organization_id = selectedOrgForUsers.value.id
      }
      await organizationsAPI.createUser(selectedOrgForUsers.value.id, data)
      message.success('Пользователь создан')
    }

    showCreateUserModal.value = false
    await loadUsers(selectedOrgForUsers.value.id)
  } catch (error) {
    console.error('Failed to save user:', error)
    if (error.response?.data) {
      const errors = Object.values(error.response.data).flat()
      message.error(errors.join(', '))
    } else {
      message.error('Ошибка сохранения пользователя')
    }
  } finally {
    savingUser.value = false
  }
}

function handleDeleteOrg(org) {
  dialog.warning({
    title: 'Удалить организацию?',
    content: `Вы уверены, что хотите удалить организацию "${org.name}"? Это действие нельзя отменить!`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await organizationsAPI.delete(org.id)
        message.success('Организация удалена')
        await loadOrganizations()
      } catch (error) {
        console.error('Failed to delete organization:', error)
        message.error('Ошибка удаления организации')
      }
    }
  })
}

function handleDeleteUser(user) {
  dialog.warning({
    title: 'Удалить пользователя?',
    content: `Вы уверены, что хотите удалить пользователя "${user.username}"?`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await organizationsAPI.deleteUser(user.id)
        message.success('Пользователь удален')
        await loadUsers(selectedOrgForUsers.value.id)
      } catch (error) {
        console.error('Failed to delete user:', error)
        message.error('Ошибка удаления пользователя')
      }
    }
  })
}

function handleLogoChange({ file }) {
  if (file.status === 'finished') {
    orgForm.value.logo = file.file
  }
}

// Lifecycle
onMounted(() => {
  if (isAdmin.value) {
    loadOrganizations()
  } else if (isOwner.value && currentOrg.value) {
    // For owners, show only their organization
    // Check if currentOrg is a valid object (not just an ID)
    if (typeof currentOrg.value === 'object' && currentOrg.value.id) {
      organizations.value = [currentOrg.value]
    } else {
      // If organization is just an ID, we need to fetch the full data
      message.warning('Пожалуйста, перезайдите в систему для обновления данных')
      organizations.value = []
    }
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/tokens.scss';

.organizations-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: $bg-primary;
}

.page-content {
  flex: 1;
  padding: $spacing-lg;
  overflow: auto;
}
</style>

