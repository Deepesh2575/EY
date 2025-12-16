import { useEffect } from 'react'
import OCRUpload from './OCRUpload'
import VideoKYC from './VideoKYC'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'
import TypingIndicator from './TypingIndicator'
import StageProgress from './StageProgress'
import WelcomeScreen from './WelcomeScreen'
import { useChat } from '../hooks/useChat'
import { AlertCircle, Download } from 'lucide-react'

function ChatInterface() {
  const {
    messages,
    conversationId,
    currentStage,
    isTyping,
    error,
    uploadedFiles,
    sanctionLetterUrl,
    messagesEndRef,
    handleSendMessage,
    handleFileUpload,
    setError,
  } = useChat()

  const handleQuickStart = async (loanType) => {
    const loanTypeMessages = {
      personal: "I'm interested in a personal loan",
      business: "I need a business loan",
      home: "I want to apply for a home loan",
    }

    await handleSendMessage(loanTypeMessages[loanType] || "I need a loan")
  }

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      // Cmd/Ctrl + K to focus input (handled in ChatInput)
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        const input = document.querySelector('textarea[placeholder*="Type your message"]')
        input?.focus()
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [])

  return (
    <div className="flex flex-col h-full max-w-5xl mx-auto bg-dark-800 rounded-xl shadow-2xl border border-dark-700 overflow-hidden">
      {/* Stage Progress */}
      {messages.length > 0 && (
        <div className="px-4 pt-4 pb-2 border-b border-dark-700">
          <StageProgress currentStage={currentStage} />
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="mx-4 mt-4 p-3 bg-danger-500/20 border border-danger-500/30 rounded-lg flex items-center space-x-2 text-danger-400 text-sm animate-fade-in">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-danger-400 hover:text-danger-300"
          >
            ×
          </button>
        </div>
      )}

      {/* Messages Area */}
      <div
        className="flex-1 overflow-y-auto px-4 py-6 space-y-4 scroll-smooth"
        style={{ scrollBehavior: 'smooth' }}
      >
        {messages.length === 0 ? (
          <WelcomeScreen onQuickStart={handleQuickStart} />
        ) : (
          <>
            {/* Welcome message */}
            <div className="text-center mb-6 animate-fade-in">
              <div className="inline-block px-4 py-2 bg-primary-500/20 border border-primary-500/30 rounded-full">
                <p className="text-sm text-primary-300">
                  👋 Welcome! I&apos;m your AI Loan Officer. Let&apos;s get started!
                </p>
              </div>
            </div>

            {/* Messages */}
            {messages.map((message, index) => (
              <MessageBubble key={message.id || index} message={message} />
            ))}

            {/* Typing Indicator */}
            {isTyping && <TypingIndicator />}
          </>
        )}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Sanction Letter Download */}
      {sanctionLetterUrl && (
        <div className="mx-4 mb-2 p-3 bg-success-500/20 border border-success-500/30 rounded-lg flex items-center justify-between animate-fade-in">
          <div className="flex items-center space-x-2">
            <Download className="w-5 h-5 text-success-400" />
            <span className="text-success-400 font-medium">Sanction letter ready!</span>
          </div>
          <a
            href={sanctionLetterUrl}
            download
            className="px-4 py-2 bg-success-500 hover:bg-success-600 rounded-lg text-white text-sm transition-colors"
          >
            Download PDF
          </a>
        </div>
      )}

      {/* OCR Upload */}
      <OCRUpload onSend={handleSendMessage} />

      {/* Video KYC Overlay */}
      {currentStage === 'VIDEO_KYC' && !uploadedFiles['video_kyc_selfie'] && (
        <div className="absolute inset-0 z-50 bg-black/80 flex items-center justify-center p-4 backdrop-blur-sm animate-fade-in">
          <VideoKYC
            onCapture={(file) => {
              if (file) {
                handleFileUpload('video_kyc_selfie', file)
              }
            }}
          />
        </div>
      )}

      {/* Input Area */}
      <ChatInput
        onSend={handleSendMessage}
        onFileUpload={handleFileUpload}
        isLoading={isTyping}
        conversationId={conversationId}
        uploadedFiles={uploadedFiles}
        disabled={currentStage === 'VIDEO_KYC' && !uploadedFiles['video_kyc_selfie']} // Disable text input during KYC
      />
    </div>
  )
}

export default ChatInterface
