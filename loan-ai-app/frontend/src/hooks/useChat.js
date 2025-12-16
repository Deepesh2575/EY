import { useState, useEffect, useRef, useCallback } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { sendMessage, uploadDocument, getConversation } from '../services/api'

const STORAGE_PREFIX = 'loan_chat_'

export const useChat = () => {
  const [messages, setMessages] = useState([])
  const [conversationId, setConversationId] = useState(null)
  const [currentStage, setCurrentStage] = useState('GREETING')
  const [isTyping, setIsTyping] = useState(false)
  const [error, setError] = useState(null)
  const [uploadedFiles, setUploadedFiles] = useState({})
  const [isApproved, setIsApproved] = useState(null)
  const [sanctionLetterUrl, setSanctionLetterUrl] = useState(null)
  const [retryCount, setRetryCount] = useState(0)
  
  const messagesEndRef = useRef(null)
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
        .then(data => {
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
  const handleSendMessage = useCallback(async (messageText, retryAttempt = 0) => {
    if (!messageText.trim()) return

    const userMessage = {
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

      const botMessage = {
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
    } catch (err) {
      console.error('Error sending message:', err)
      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id ? { ...msg, status: 'failed' } : msg
      ))

      if (retryAttempt < MAX_RETRIES && (err.message?.includes('connect') || err.status >= 500)) {
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

  const handleFileUpload = useCallback(async (docType, file, retryAttempt = 0) => {
    const maxSize = 5 * 1024 * 1024
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']

    if (file.size > maxSize) throw new Error('File size must be less than 5MB')
    if (!allowedTypes.includes(file.type)) throw new Error('Only JPG, PNG, and PDF files are allowed')

    const fileMessage = {
      id: uuidv4(),
      role: 'user',
      content: `Uploading ${docType.replace('_', ' ')}: ${file.name}...`,
      timestamp: new Date().toISOString(),
      file: file.name,
      status: 'pending',
    }
    setMessages(prev => [...prev, fileMessage])
    setIsTyping(true)
    setError(null)

    try {
      const response = await uploadDocument(conversationId, docType, file, (progress) => {
        setMessages(prev => prev.map(msg =>
          msg.id === fileMessage.id ? { ...msg, uploadProgress: progress } : msg
        ))
      })

      setMessages(prev => prev.map(msg =>
        msg.id === fileMessage.id ? { 
          ...msg, 
          status: 'sent', 
          content: `Uploaded ${docType.replace('_', ' ')}: ${file.name}` 
        } : msg
      ))

      if (response.conversation_id && response.conversation_id !== conversationId) {
        setConversationId(response.conversation_id)
        window.history.replaceState({}, '', `?conversation_id=${response.conversation_id}`)
      }

      setUploadedFiles(prev => ({
        ...prev,
        [docType]: { name: file.name, uploaded: true }
      }))

      setMessages(prev => [...prev, {
        id: uuidv4(),
        role: 'assistant',
        content: `✅ ${docType.replace('_', ' ')} uploaded successfully! We're processing it now.`,
        timestamp: new Date().toISOString(),
      }])

      if (response.metadata?.stage) {
        setCurrentStage(response.metadata.stage)
      }

      return response
    } catch (err) {
      console.error('Error uploading file:', err)
      setError(err.message || 'Failed to upload file. Please try again.')
      setMessages(prev => prev.map(msg =>
        msg.id === fileMessage.id ? { ...msg, status: 'failed', content: `❌ Failed to upload ${file.name}` } : msg
      ))
      if (retryAttempt < MAX_RETRIES && (err.message?.includes('connect') || err.status >= 500)) {
        setRetryCount(prev => prev + 1)
        setTimeout(() => {
          handleFileUpload(docType, file, retryAttempt + 1)
        }, 2000 * (retryAttempt + 1))
        return
      }
      throw err
    } finally {
      setIsTyping(false)
    }
  }, [conversationId, MAX_RETRIES])
  
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


