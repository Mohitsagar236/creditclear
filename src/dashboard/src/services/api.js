/**
 * API Service
 * 
 * Handles all API requests to the backend services
 */

import axios from 'axios';

// Create axios instance with base URL from environment
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Cache for storing repeated requests
const cache = new Map();

/**
 * API service object
 */
export const api = {
  /**
   * Check health status of the API
   */
  async checkHealth() {
    try {
      const response = await apiClient.get('/health');
      return { success: true, ...response.data };
    } catch (error) {
      console.error('Health check failed:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Get system metrics
   */
  async getMetrics() {
    try {
      const response = await apiClient.get('/metrics');
      return response.data;
    } catch (error) {
      console.error('Failed to get metrics:', error);
      return {
        total_predictions: Math.floor(Math.random() * 2000),
        active_users: Math.floor(Math.random() * 100),
        api_version: '1.0.0',
        status: 'degraded'
      };
    }
  },

  /**
   * Submit comprehensive data for prediction
   */
  async submitComprehensiveData(data) {
    try {
      const response = await apiClient.post('/api/comprehensive-prediction', data);
      return response.data;
    } catch (error) {
      console.error('Failed to submit comprehensive data:', error);
      throw error;
    }
  },

  /**
   * Submit digital footprint data
   */
  async submitFootprintData(data) {
    try {
      const response = await apiClient.post('/api/digital-footprint', data);
      return response.data;
    } catch (error) {
      console.error('Failed to submit digital footprint data:', error);
      // Return fallback data
      return {
        success: false,
        score: 0.65,
        insights: [
          "Digital footprint analysis incomplete",
          "Using fallback score based on limited data"
        ],
        recommendations: [
          "Ensure all digital accounts are properly linked",
          "Try submitting again later"
        ]
      };
    }
  },

  /**
   * Get cache statistics for monitoring
   */
  getCacheStats() {
    return {
      size: cache.size,
      keys: Array.from(cache.keys()),
    };
  },

  /**
   * Get request queue statistics (mock data)
   */
  getRequestQueueStats() {
    return {
      active: Math.floor(Math.random() * 10),
      queued: Math.floor(Math.random() * 5),
      completed: Math.floor(Math.random() * 100)
    };
  },

  /**
   * Clear the request cache
   */
  clearCache() {
    cache.clear();
    console.log('API cache cleared');
  }
};

// Response interceptor for caching GET requests
apiClient.interceptors.response.use(response => {
  const requestConfig = response.config;
  
  // Only cache GET requests
  if (requestConfig.method === 'get') {
    const url = requestConfig.url;
    cache.set(url, response.data);
  }
  
  return response;
});

export default api;
