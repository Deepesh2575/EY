import ReactMarkdown from 'react-markdown'
import { User, Bot, Check, Clock, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const isDecision = message.metadata?.decision === 'APPROVED' || 
                     message.metadata?.decision === 'REJECTED' ||
                     message.metadata?.is_decision
  const isApproved = message.metadata?.decision === 'APPROVED'
  const isError = message.isError || message.error || message.status === 'failed'

  const formatTime = (timestamp) => {
    try {
      const date = new Date(timestamp)
      const now = new Date()
      const diffMs = now - date
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)
      
      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins}m ago`
      if (diffHours < 24) return `${diffHours}h ago`
      if (diffDays < 7) return `${diffDays}d ago`
      return date.toLocaleDateString()
    } catch {
      return 'Just now'
    }
  }

  const statusIcon = () => {
    switch (message.status) {
      case 'pending': return <Clock className="w-3 h-3 text-gray-400" />
      case 'sent': return <Check className="w-3 h-3 text-green-400" />
      case 'failed': return <AlertTriangle className="w-3 h-3 text-red-400" />
      default: return null
    }
  }
  
  if (isDecision) {
    return (
      <div className="flex justify-center my-6 animate-fade-in">
        <div
          className={`max-w-md px-6 py-4 rounded-xl shadow-lg ${
            isApproved
              ? 'bg-gradient-to-r from-success-500 to-success-600 text-white'
              : 'bg-gradient-to-r from-danger-500 to-danger-600 text-white'
          }`}
        >
          <div className="flex items-center space-x-3 mb-2">
            {isApproved ? <CheckCircle className="w-6 h-6" /> : <XCircle className="w-6 h-6" />}
            <h3 className="text-lg font-bold">
              {isApproved ? 'Loan Approved!' : 'Loan Application Status'}
            </h3>
          </div>
          <ReactMarkdown className="prose prose-invert max-w-none text-white/90">
            {message.content}
          </ReactMarkdown>
          <div className="text-xs text-white/70 mt-2">
            {formatTime(message.timestamp)}
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <div
      className={`flex items-start space-x-3 mb-4 ${
        isUser ? 'flex-row-reverse space-x-reverse' : ''
      } animate-${isUser ? 'slide-in-right' : 'slide-in-left'}`}
    >
      <div
        className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          isUser
            ? 'bg-primary-600'
            : 'bg-gradient-to-br from-primary-500 to-primary-700'
        } shadow-lg`}
      >
        {isUser ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
      </div>

      <div className={`flex-1 ${isUser ? 'flex flex-col items-end' : ''}`}>
        <div
          className={`inline-block max-w-[70%] px-4 py-3 rounded-2xl ${
            isUser
              ? 'bg-primary-600 text-white rounded-br-sm'
              : 'bg-dark-800 text-gray-100 rounded-bl-sm border border-dark-700'
          } ${isError ? 'border-2 border-danger-500' : ''}`}
        >
          {message.file && (
            <div className="mb-2 text-sm opacity-75 flex items-center space-x-1">
              <span>📎</span>
              <span>{message.file}</span>
            </div>
          )}
          <ReactMarkdown className="prose prose-invert max-w-none prose-sm">
            {message.content}
          </ReactMarkdown>
          {message.uploadProgress && message.status === 'pending' && (
            <div className="w-full bg-gray-200 rounded-full h-1 mt-2">
              <div className="bg-blue-600 h-1 rounded-full" style={{ width: `${message.uploadProgress}%` }}></div>
            </div>
          )}
        </div>
        <div
          className={`flex items-center space-x-1 text-xs text-gray-500 mt-1 px-2 ${
            isUser ? 'justify-end' : 'justify-start'
          }`}
        >
          <span>{formatTime(message.timestamp)}</span>
          {isUser && statusIcon()}
        </div>
      </div>
    </div>
  )
}

export default MessageBubble
