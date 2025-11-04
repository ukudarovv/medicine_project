import api from './axios'

export const warehouseAPI = {
  // Склады (Warehouses)
  getWarehouses(params = {}) {
    return api.get('/warehouse/warehouses/', { params })
  },
  
  getWarehouse(id) {
    return api.get(`/warehouse/warehouses/${id}/`)
  },
  
  createWarehouse(data) {
    return api.post('/warehouse/warehouses/', data)
  },
  
  updateWarehouse(id, data) {
    return api.patch(`/warehouse/warehouses/${id}/`, data)
  },
  
  deleteWarehouse(id) {
    return api.delete(`/warehouse/warehouses/${id}/`)
  },
  
  // Номенклатура (Stock Items)
  getStockItems(params = {}) {
    return api.get('/warehouse/items/', { params })
  },
  
  getStockItem(id) {
    return api.get(`/warehouse/items/${id}/`)
  },
  
  getStockItemsSimple() {
    return api.get('/warehouse/items/list_simple/')
  },
  
  createStockItem(data) {
    return api.post('/warehouse/items/', data)
  },
  
  updateStockItem(id, data) {
    return api.patch(`/warehouse/items/${id}/`, data)
  },
  
  deleteStockItem(id) {
    return api.delete(`/warehouse/items/${id}/`)
  },
  
  // Партии (Stock Batches)
  getStockBatches(params = {}) {
    return api.get('/warehouse/batches/', { params })
  },
  
  getStockBatch(id) {
    return api.get(`/warehouse/batches/${id}/`)
  },
  
  createStockBatch(data) {
    return api.post('/warehouse/batches/', data)
  },
  
  updateStockBatch(id, data) {
    return api.patch(`/warehouse/batches/${id}/`, data)
  },
  
  deleteStockBatch(id) {
    return api.delete(`/warehouse/batches/${id}/`)
  },
  
  getInventory() {
    return api.get('/warehouse/batches/inventory/')
  },
  
  // Движения (Stock Moves)
  getStockMoves(params = {}) {
    return api.get('/warehouse/moves/', { params })
  },
  
  getStockMove(id) {
    return api.get(`/warehouse/moves/${id}/`)
  },
  
  createStockMove(data) {
    return api.post('/warehouse/moves/', data)
  },
  
  updateStockMove(id, data) {
    return api.patch(`/warehouse/moves/${id}/`, data)
  },
  
  deleteStockMove(id) {
    return api.delete(`/warehouse/moves/${id}/`)
  }
}

export default warehouseAPI

