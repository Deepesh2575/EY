import { useRef } from 'react'
import { Paperclip } from 'lucide-react'

interface FileUploadProps {
  onFileSelect: (file: File) => void;
}

function FileUpload({ onFileSelect }: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Validate file type (optional - adjust as needed)
      const allowedTypes = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      ]
      
      if (allowedTypes.includes(file.type)) {
        onFileSelect(file)
      } else {
        alert('Please upload a PDF, image, or Word document')
      }
    }
    // Reset input so same file can be selected again
    e.target.value = ''
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileChange}
        className="hidden"
        accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
      />
      <button
        type="button"
        onClick={handleClick}
        className="p-3 bg-background-lighter hover:bg-background-light rounded-lg transition-colors"
        aria-label="Upload file"
      >
        <Paperclip className="w-5 h-5 text-gray-300" />
      </button>
    </>
  )
}

export default FileUpload


