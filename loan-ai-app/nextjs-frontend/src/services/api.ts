import axios from 'axios'

// Define interfaces for API response types
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  status?: 'pending' | 'sent' | 'failed';
  file?: string;
  uploadProgress?: number;
  metadata?: { [key: string]: any };
  isError?: boolean;
  error?: string;
}

interface ConversationData {
  messages?: Message[];
  stage?: string;
  decision?: 'APPROVED' | 'REJECTED';
  conversation_id?: string;
  metadata?: { [key: string]: any };
  sanction_letter_url?: string;
}

interface StatsData {
  approved_loans: number;
  rejected_loans: number;
  pending: number;
  total_conversations: number;
}

interface SendMessageResponse {
  conversation_id?: string;
  message?: string; // The bot's response message
  response?: string; // Alternative for bot's response message
  timestamp?: string;
  metadata?: { [key: string]: any };
  stage?: string;
}

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  timeout: 30000,  // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config: any) => { // Using any as fallback
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: any) => { // Using any as fallback
    return Promise.reject(error)
  }
)

// Response interceptor - Enhanced error handling
api.interceptors.response.use(
  (response: any) => response.data,  // Using any as fallback
  (error: any) => { // Using any as fallback
    console.error('API Error:', error)
    
    if (error.response) {
      // Server responded with error
      const data = error.response.data
      const message = (data as any)?.message || (data as any)?.detail || 'Something went wrong'
      const errorObj: any = new Error(message)
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
export const sendMessage = async (conversationId: string | null, message: string): Promise<any> => {
  return await api.post('/api/chat', {
    conversation_id: conversationId,
    message: message,
  })
}

export const uploadDocument = async (
  conversationId: string | null, 
  docType: string, 
  file: File, 
  onProgress?: (progress: number) => void
): Promise<any> => {
  const formData = new FormData()
  formData.append('file', file)
  
  const config: any = { // Using any as fallback
    params: { 
      conversation_id: conversationId, 
      doc_type: docType 
    },
    headers: { 
      'Content-Type': 'multipart/form-data' 
    },
    onUploadProgress: (progressEvent: ProgressEvent) => {
        if (onProgress) {
            const progress = (progressEvent.loaded / (progressEvent.total || file.size)) * 100
            onProgress(progress)
        }
    }
  }
  
  return await api.post('/api/upload', formData, config)
}

export const ocrDocument = async (conversationId: string | null, file: File): Promise<any> => {
  const formData = new FormData()
  formData.append('file', file)

  const config: any = { // Using any as fallback
    params: { conversation_id: conversationId },
    headers: { 'Content-Type': 'multipart/form-data' }
  }

  return await api.post('/api/ocr', formData, config)
}

export const getConversation = async (conversationId: string): Promise<any> => {
  return await api.get(`/api/conversation/${conversationId}`)
}

export const createConversation = async (): Promise<any> => {
  return await api.post('/api/conversation')
}

export const downloadSanctionLetter = async (filename: string): Promise<any> => {
  return await api.get(`/api/download/${filename}`, {
    responseType: 'blob'
  })
}

export const getStats = async (): Promise<any> => {
  return await api.get('/api/stats')
}

export const checkHealth = async (): Promise<any> => {
  return await api.get('/health')
}

// Legacy methods for backward compatibility
export const uploadFile = async (file: File, conversationId: string | null = null): Promise<any> => {
  return uploadDocument(conversationId, 'salary_slip', file)
}

export const getConversationHistory = async (conversationId: string): Promise<any> => {
  return getConversation(conversationId)
}

export default api