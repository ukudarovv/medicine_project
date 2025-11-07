/**
 * API client for Django backend
 */
const axios = require('axios');

const BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class APIClient {
  constructor() {
    this.token = null;
    this.grantId = null;
    
    // Create axios instance
    this.client = axios.create({
      baseURL: BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers['Authorization'] = `Bearer ${this.token}`;
        }
        if (this.grantId) {
          config.headers['X-Access-Grant-ID'] = this.grantId;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, need to re-login
          this.token = null;
          throw new Error('Session expired. Please login again.');
        }
        throw error;
      }
    );
  }
  
  setToken(token) {
    this.token = token;
  }
  
  setGrantId(grantId) {
    this.grantId = grantId;
  }
  
  clearAuth() {
    this.token = null;
    this.grantId = null;
  }
  
  // Auth endpoints
  async login(username, password) {
    const response = await this.client.post('/auth/login/', {
      username,
      password
    });
    this.setToken(response.data.access);
    return response.data;
  }
  
  async getMe() {
    const response = await this.client.get('/auth/me/');
    return response.data;
  }
  
  // Consent endpoints
  async searchPatientByIIN(iin) {
    const response = await this.client.post('/consent/search-patient/', { iin });
    return response.data;
  }
  
  async createAccessRequest(data) {
    const response = await this.client.post('/consent/access-requests/', data);
    return response.data;
  }
  
  async pollAccessRequestStatus(requestId) {
    const response = await this.client.get(`/consent/access-requests/${requestId}/status/`);
    return response.data;
  }
  
  async getPatientByGrant(grantId) {
    const response = await this.client.get(`/patients/by-grant/${grantId}/`);
    return response.data;
  }
  
  // Visit endpoints
  async createVisit(appointmentId) {
    const response = await this.client.post('/visits/visits/', {
      appointment: appointmentId,
      status: 'draft'
    });
    return response.data;
  }
  
  async getVisit(visitId) {
    const response = await this.client.get(`/visits/visits/${visitId}/`);
    return response.data;
  }
  
  async saveVisitNote(data) {
    const response = await this.client.post('/visits/notes/', data);
    return response.data;
  }
  
  // Appointment endpoints
  async createAppointment(data) {
    const response = await this.client.post('/calendar/appointments/', data);
    return response.data;
  }
}

// Export singleton instance
const apiClient = new APIClient();

module.exports = apiClient;

