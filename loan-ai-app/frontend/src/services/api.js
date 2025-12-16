import axios from 'axios'

import { API_BASE_URL } from '../constants'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,  // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Enhanced error handling
api.interceptors.response.use(
  (response) => response.data,  // Return data directly
  (error) => {
    console.error('API Error:', error)
    
    if (error.response) {
      // Server responded with error
      const data = error.response.data
      const message = data?.message || data?.detail || 'Something went wrong'
      const errorObj = new Error(message)
      errorObj.status = error.response.status
      errorObj.data = data
      return Promise.reject(errorObj)
    } else if (error.request) {
      // Request made but no response
      return Promise.reject(new Error('Cannot connect to server. Please check your connection.'))
    } else {
      return Promise.reject(error)
    }
  }
)

// API Methods
export const sendMessage = async (conversationId, message) => {
  return await api.post('/api/chat', {
    conversation_id: conversationId,
    message: message,
  })
}

export const uploadDocument = async (conversationId, docType, file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const config = {
    params: { 
      conversation_id: conversationId, 
      doc_type: docType 
    },
    headers: { 
      'Content-Type': 'multipart/form-data' 
    },
  }
  
  if (onProgress) {
    config.onUploadProgress = (progressEvent) => {
      const progress = (progressEvent.loaded / progressEvent.total) * 100
      onProgress(progress)
    }
  }
  
  return await api.post('/api/upload', formData, config)
}

export const ocrDocument = async (conversationId, file) => {
  const formData = new FormData()
  formData.append('file', file)

  const config = {
    params: { conversation_id: conversationId },
    headers: { 'Content-Type': 'multipart/form-data' }
  }

  return await api.post('/api/ocr', formData, config)
}

export const getConversation = async (conversationId) => {
  return await api.get(`/api/conversation/${conversationId}`)
}

export const createConversation = async () => {
  return await api.post('/api/conversation')
}

export const downloadSanctionLetter = async (filename) => {
  return await api.get(`/api/download/${filename}`, {
    responseType: 'blob'
  })
}

export const getStats = async () => {
  return await api.get('/api/stats')
}

export const checkHealth = async () => {
  return await api.get('/health')
}

// Legacy methods for backward compatibility
export const uploadFile = async (file, conversationId = null) => {
  return uploadDocument(conversationId, 'salary_slip', file)
}

export const getConversationHistory = async (conversationId) => {
  return getConversation(conversationId)
}

export default api
