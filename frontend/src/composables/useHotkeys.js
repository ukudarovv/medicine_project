/**
 * Global hotkeys composable - Sprint 5
 */
import { onMounted, onUnmounted } from 'vue'

export function useHotkeys(handlers = {}) {
  /**
   * Usage:
   * useHotkeys({
   *   'ctrl+s': () => save(),
   *   'ctrl+p': () => print(),
   *   'esc': () => closeModal(),
   * })
   */
  
  const handleKeyDown = (e) => {
    const key = e.key.toLowerCase()
    const ctrl = e.ctrlKey || e.metaKey
    const alt = e.altKey
    const shift = e.shiftKey
    
    // Build key combination string
    let combo = ''
    if (ctrl) combo += 'ctrl+'
    if (alt) combo += 'alt+'
    if (shift) combo += 'shift+'
    combo += key
    
    // Check if handler exists for this combination
    const handler = handlers[combo]
    if (handler) {
      e.preventDefault()
      handler(e)
    }
  }
  
  onMounted(() => {
    document.addEventListener('keydown', handleKeyDown)
  })
  
  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeyDown)
  })
  
  return {
    // Can expose methods if needed
  }
}

/**
 * Common hotkey presets
 */
export const commonHotkeys = {
  save: 'ctrl+s',
  print: 'ctrl+p',
  search: 'ctrl+f',
  globalSearch: 'ctrl+k',
  close: 'escape',
  newItem: 'ctrl+n',
  delete: 'delete',
}

