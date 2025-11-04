/**
 * Autosave composable - Sprint 5
 * Provides debounced autosave functionality for forms
 */
import { watch, onMounted, onUnmounted, ref } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { useMessage } from 'naive-ui'

export function useAutosave(formData, options = {}) {
  const {
    saveCallback,           // Function to call for saving to API
    draftKey,              // localStorage key for draft
    interval = 30000,      // Autosave interval (30 seconds)
    debounceMs = 2000,     // Debounce for localStorage (2 seconds)
    enableLocalStorage = true,
    enableApiSave = false,
  } = options
  
  const message = useMessage()
  const isDirty = ref(false)
  const lastSaved = ref(null)
  const isSaving = ref(false)
  
  // Debounced save to localStorage
  const saveToLocalStorage = useDebounceFn(() => {
    if (!enableLocalStorage || !draftKey) return
    
    try {
      localStorage.setItem(draftKey, JSON.stringify(formData.value))
      lastSaved.value = new Date()
      isDirty.value = false
    } catch (error) {
      console.error('Failed to save draft:', error)
    }
  }, debounceMs)
  
  // Periodic save to API
  let apiSaveInterval = null
  
  const saveToAPI = async () => {
    if (!enableApiSave || !saveCallback || !isDirty.value) return
    
    try {
      isSaving.value = true
      await saveCallback(formData.value)
      lastSaved.value = new Date()
      isDirty.value = false
    } catch (error) {
      console.error('Failed to autosave to API:', error)
    } finally {
      isSaving.value = false
    }
  }
  
  // Load draft from localStorage
  const loadDraft = () => {
    if (!enableLocalStorage || !draftKey) return null
    
    try {
      const draft = localStorage.getItem(draftKey)
      return draft ? JSON.parse(draft) : null
    } catch (error) {
      console.error('Failed to load draft:', error)
      return null
    }
  }
  
  // Clear draft
  const clearDraft = () => {
    if (!draftKey) return
    
    try {
      localStorage.removeItem(draftKey)
      isDirty.value = false
    } catch (error) {
      console.error('Failed to clear draft:', error)
    }
  }
  
  // Watch formData for changes
  watch(
    formData,
    () => {
      isDirty.value = true
      saveToLocalStorage()
    },
    { deep: true }
  )
  
  // Setup periodic API save
  onMounted(() => {
    if (enableApiSave && saveCallback) {
      apiSaveInterval = setInterval(saveToAPI, interval)
    }
  })
  
  onUnmounted(() => {
    if (apiSaveInterval) {
      clearInterval(apiSaveInterval)
    }
  })
  
  return {
    isDirty,
    lastSaved,
    isSaving,
    loadDraft,
    clearDraft,
    saveToAPI,
  }
}

