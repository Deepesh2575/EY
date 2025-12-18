import { useState, useRef, useEffect } from 'react'
import { Send, Paperclip, X, FileCheck, Lightbulb } from 'lucide-react'

interface UploadedFile {
  name: string;
  file?: File;
}

interface ChatInputProps {
  onSend: (message: string) => void;
  onFileUpload: (docType: string, file: File, onProgress?: (progress: number) => void) => Promise<void>;
  isLoading: boolean;
  uploadedFiles?: { [key: string]: UploadedFile };
  disabled?: boolean;
}

function ChatInput({ onSend, onFileUpload, isLoading, uploadedFiles: externalUploadedFiles = {} }: ChatInputProps) {
  const [inputValue, setInputValue] = useState('')
  const [uploadedFiles, setUploadedFiles] = useState<{[key: string]: UploadedFile}>(externalUploadedFiles)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const MAX_CHARS = 2000

  
  // Sync external uploaded files
  useEffect(() => {
    setUploadedFiles(externalUploadedFiles)
  }, [externalUploadedFiles])
  
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value
    if (text.length <= MAX_CHARS) {
      setInputValue(text)
    }
  }
  
  const handleSend = (e?: React.FormEvent<HTMLFormElement>) => {
    e?.preventDefault()
    if (!inputValue.trim() || isLoading) return
    
    onSend(inputValue)
    setInputValue('')
  }
  
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }
  
  const handleQuickMessage = (msg: string) => {
    onSend(msg)
  }
  
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    // Determine doc type from filename or default
    let docType = 'salary_slip'
    const filename = file.name.toLowerCase()
    if (filename.includes('pan') || filename.includes('id')) {
      docType = 'pan_card'
    } else if (filename.includes('aadhaar')) {
      docType = 'aadhaar'
    } else if (filename.includes('bank') || filename.includes('statement')) {
      docType = 'bank_statement'
    }
    
    // Show file in UI immediately
    setUploadedFiles(prev => ({
      ...prev,
      [docType]: { name: file.name, file }
    }))
    
    // Upload file
    try {
      await onFileUpload(docType, file)
      // File uploaded successfully
    } catch {
      // Remove file on error
      setUploadedFiles(prev => {
        const newFiles = { ...prev }
        delete newFiles[docType]
        return newFiles
      })
    }
    
    // Reset input
    e.target.value = ''
  }
  
  const removeFile = (docType: string) => {
    setUploadedFiles(prev => {
      const newFiles = { ...prev }
      delete newFiles[docType]
      return newFiles
    })
  }
  
  const docTypeLabels: {[key: string]: string} = {
    salary_slip: 'Salary Slip',
    pan_card: 'PAN Card',
    aadhaar: 'Aadhaar',
    bank_statement: 'Bank Statement',
  }
  
  return (
    <div className="border-t border-dark-700 bg-dark-800/80 backdrop-blur-sm">
      {/* Uploaded files preview */}
      {Object.keys(uploadedFiles).length > 0 && (
        <div className="px-4 pt-3 pb-2 flex flex-wrap gap-2">
          {Object.entries(uploadedFiles).map(([docType]) => (
            <div
              key={docType}
              className="flex items-center space-x-2 px-3 py-1.5 bg-success-500/20 border border-success-500/30 rounded-lg text-sm"
            >
              <FileCheck className="w-4 h-4 text-success-500" />
              <span className="text-success-400">{docTypeLabels[docType] || docType}</span>
              <button
                onClick={() => removeFile(docType)}
                className="text-success-400 hover:text-success-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
      
      {/* Input area */}
      <form onSubmit={handleSend} className="flex items-end space-x-2 px-4 py-4">
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
          onChange={handleFileSelect}
        />
        
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="p-3 bg-dark-700 hover:bg-dark-600 rounded-lg transition-colors flex-shrink-0"
          disabled={isLoading}
          aria-label="Upload file"
        >
          <Paperclip className="w-5 h-5 text-gray-300" />
        </button>
        
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
          className="flex-1 px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none min-h-[48px] max-h-32"
          rows={1}
          maxLength={MAX_CHARS}
          disabled={isLoading}
          onInput={(e: React.FormEvent<HTMLTextAreaElement>) => {
            const target = e.target as HTMLTextAreaElement
            target.style.height = 'auto'
            target.style.height = target.scrollHeight + 'px'
          }}
        />
        
        <button
          type="submit"
          disabled={isLoading || !inputValue.trim()}
          className="p-3 bg-primary-600 hover:bg-primary-700 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0 hover:shadow-lg hover:shadow-primary-500/30 hover:-translate-y-0.5"
          aria-label="Send message"
        >
          <Send className="w-5 h-5 text-white" />
        </button>
      </form>

      {/* Quick suggestions */}
      {inputValue === '' && !isLoading && Object.keys(uploadedFiles).length === 0 && (
        <div className="px-4 pb-3 space-y-2">
          <div className="flex items-center space-x-1 text-xs text-dark-500 mb-2">
            <Lightbulb className="w-4 h-4" />
            <span>Quick options:</span>
          </div>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => handleQuickMessage('I need a personal loan')}
              className="bg-primary-500/20 hover:bg-primary-500/30 text-primary-300 px-3 py-1.5 rounded-full text-sm transition-colors"
            >
              💰 Personal Loan
            </button>
            <button
              onClick={() => handleQuickMessage('What documents do I need?')}
              className="bg-primary-500/20 hover:bg-primary-500/30 text-primary-300 px-3 py-1.5 rounded-full text-sm transition-colors"
            >
              📋 Required Docs
            </button>
            <button
              onClick={() => handleQuickMessage('Tell me about your loan products')}
              className="bg-primary-500/20 hover:bg-primary-500/30 text-primary-300 px-3 py-1.5 rounded-full text-sm transition-colors"
            >
              ℹ️ Loan Products
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default ChatInput