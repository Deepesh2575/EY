import { useState, useEffect, useRef, useCallback } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { sendMessage, uploadDocument, getConversation } from '../services/api'
// import { AxiosError } from 'axios' // Reverted import due to build issue

const STORAGE_PREFIX = 'loan_chat_'

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  status?: 'pending' | 'sent' | 'failed';
  file?: string; // for uploaded files
  uploadProgress?: number; // for file uploads
  metadata?: { [key: string]: any }; // for assistant messages
  isError?: boolean; // Added for error messages
  error?: string; // Added for error messages
}

interface ConversationData {
  messages?: Message[];
  stage?: string;
  decision?: 'APPROVED' | 'REJECTED';
}

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [currentStage, setCurrentStage] = useState<string>('GREETING')
  const [isTyping, setIsTyping] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadedFiles, setUploadedFiles] = useState<{[key: string]: { name: string, file?: File, uploaded?: boolean }}>({})
  const [isApproved, setIsApproved] = useState<boolean | null>(null)
  const [sanctionLetterUrl, setSanctionLetterUrl] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState<number>(0)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const MAX_RETRIES = 3
  
  
  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])
  
  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])
  
  // Initialize conversation or recover from storage
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const savedConvId = urlParams.get('conversation_id')
    
    if (savedConvId) {
      // Try to recover conversation
      const saved = localStorage.getItem(`${STORAGE_PREFIX}${savedConvId}`)
      if (saved) {
        try {
          const data = JSON.parse(saved)
          setConversationId(savedConvId)
          setMessages(data.messages || [])
          setCurrentStage(data.currentStage || 'GREETING')
          setUploadedFiles(data.uploadedFiles || {})
          setIsApproved(data.isApproved || null)
          return
        } catch (e) {
          console.error('Error recovering conversation:', e)
        }
      }
      
      // Try to fetch from API
      getConversation(savedConvId)
        .then((data: ConversationData) => {
          setConversationId(savedConvId)
          if (data.messages) {
            setMessages(data.messages.map(msg => ({
              id: uuidv4(),
              role: msg.role,
              content: msg.content,
              timestamp: msg.timestamp,
            })))
          }
          setCurrentStage(data.stage || 'GREETING')
          setIsApproved(data.decision === 'APPROVED')
        })
        .catch(() => {
          // Create new conversation if recovery fails
          initializeNewConversation()
        })
    } else {
      initializeNewConversation()
    }
  }, [])
  
  const initializeNewConversation = () => {
    const newConvId = uuidv4()
    setConversationId(newConvId)
    
    // Add welcome message
    setMessages([{
      id: uuidv4(),
      role: 'assistant',
      content: '👋 Welcome! I\'m your AI Loan Officer. I can help you get instant loan approval. How can I assist you today?',
      timestamp: new Date().toISOString(),
    }])
    
    // Update URL
    window.history.replaceState({}, '', `?conversation_id=${newConvId}`)
  }
  
  // Save conversation to localStorage
  useEffect(() => {
    if (conversationId && messages.length > 0) {
      const data = {
        messages,
        currentStage,
        uploadedFiles,
        isApproved,
        timestamp: new Date().toISOString(),
      }
      localStorage.setItem(`${STORAGE_PREFIX}${conversationId}`, JSON.stringify(data))
    }
  }, [messages, conversationId, currentStage, uploadedFiles, isApproved])
  
  // Send message with retry logic
  const handleSendMessage = useCallback(async (messageText: string, retryAttempt: number = 0) => {
    if (!messageText.trim()) return

    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
      status: 'pending',
    }
    setMessages(prev => [...prev, userMessage])
    setError(null)
    setIsTyping(true)

    try {
      const response = await sendMessage(conversationId, messageText)

      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id ? { ...msg, status: 'sent' } : msg
      ))

      if (response.conversation_id && response.conversation_id !== conversationId) {
        setConversationId(response.conversation_id)
        window.history.replaceState({}, '', `?conversation_id=${response.conversation_id}`)
      }

      const botMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: response.message || response.response || 'I apologize, but I could not generate a response.',
        timestamp: response.timestamp || new Date().toISOString(),
        metadata: response.metadata || {},
      }
      setMessages(prev => [...prev, botMessage])

      if (response.stage || response.metadata?.stage) {
        setCurrentStage(response.stage || response.metadata?.stage)
      }

      const decision = response.metadata?.decision
      if (decision === 'APPROVED' || decision === 'REJECTED') {
        setIsApproved(decision === 'APPROVED')
        if (response.metadata?.sanction_letter_url) {
          setSanctionLetterUrl(response.metadata.sanction_letter_url)
        }
      }

      setRetryCount(0)
    } catch (err: any) {
      console.error('Error sending message:', err)
      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id ? { ...msg, status: 'failed' } : msg
      ))

      if (retryAttempt < MAX_RETRIES && ((err as any).message?.includes('connect') || (err as any).response?.status >= 500)) {
        setRetryCount(prev => prev + 1)
        setTimeout(() => {
          handleSendMessage(messageText, retryAttempt + 1)
        }, 2000 * (retryAttempt + 1))
        return
      }

      setError(err.message || 'Failed to send message. Please try again.')
    } finally {
      setIsTyping(false)
    }
  }, [conversationId, MAX_RETRIES])

  const handleFileUpload = useCallback(async (docType: string, file: File, onProgress?: (progress: number) => void) => {
    const MAX_RETRIES_FILE_UPLOAD = 3; // Define max retries specifically for file upload if needed
    let currentRetryAttempt = 0;

    const executeUpload = async (currentFile: File, currentDocType: string) => {
      const maxSize = 5 * 1024 * 1024
      const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']

      if (currentFile.size > maxSize) throw new Error('File size must be less than 5MB')
      if (!allowedTypes.includes(currentFile.type)) throw new Error('Only JPG, PNG, and PDF files are allowed')

      const fileMessage: Message = {
        id: uuidv4(),
        role: 'user',
        content: `Uploading ${currentDocType.replace('_', ' ')}: ${currentFile.name}...`,
        timestamp: new Date().toISOString(),
        file: currentFile.name,
        status: 'pending',
      }
      setMessages(prev => [...prev, fileMessage])
      setIsTyping(true)
      setError(null)

      try {
        const response = await uploadDocument(conversationId, currentDocType, currentFile, (progress) => {
          setMessages(prev => prev.map(msg =>
            msg.id === fileMessage.id ? { ...msg, uploadProgress: progress } : msg
          ))
          if (onProgress) onProgress(progress);
        })

        setMessages(prev => prev.map(msg =>
          msg.id === fileMessage.id ? { 
            ...msg, 
            status: 'sent', 
            content: `Uploaded ${currentDocType.replace('_', ' ')}: ${currentFile.name}` 
          } : msg
        ))

        if (response.conversation_id && response.conversation_id !== conversationId) {
          setConversationId(response.conversation_id)
          window.history.replaceState({}, '', `?conversation_id=${response.conversation_id}`)
        }

        setUploadedFiles(prev => ({
          ...prev,
          [currentDocType]: { name: currentFile.name, uploaded: true }
        }))

        setMessages(prev => [...prev, {
          id: uuidv4(),
          role: 'assistant',
          content: `✅ ${currentDocType.replace('_', ' ')} uploaded successfully! We're processing it now.`,
          timestamp: new Date().toISOString(),
        }])

        if (response.metadata?.stage) {
          setCurrentStage(response.metadata.stage)
        }

        return; // Do not return the response, thus making the promise resolve to void
      } catch (err: any) {
        console.error('Error uploading file:', err)
        setMessages(prev => prev.map(msg =>
          msg.id === fileMessage.id ? { ...msg, status: 'failed', content: `❌ Failed to upload ${file.name}` } : msg
        ))

        if (currentRetryAttempt < MAX_RETRIES_FILE_UPLOAD && (err.message?.includes('connect') || err.status >= 500)) {
          currentRetryAttempt++;
          setRetryCount(prev => prev + 1)
          setTimeout(() => executeUpload(currentFile, currentDocType), 2000 * currentRetryAttempt)
          return;
        }
        setError(err.message || 'Failed to upload file. Please try again.')
        throw err
      } finally {
        setIsTyping(false)
      }
    };
    
    await executeUpload(file, docType); // Await the execution but don't return its result
  }, [conversationId])
  
  return {
    messages,
    conversationId,
    currentStage,
    isTyping,
    error,
    uploadedFiles,
    isApproved,
    sanctionLetterUrl,
    retryCount,
    messagesEndRef,
    handleSendMessage,
    handleFileUpload,
    setError,
  }
}


