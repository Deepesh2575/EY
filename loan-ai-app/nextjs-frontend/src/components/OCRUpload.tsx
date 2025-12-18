import { useState, ChangeEvent } from 'react'
import { ocrDocument } from '../services/api'

interface OCRUploadProps {
  onSend: (message: string) => void;
}

interface OCRResult {
  text?: string;
  fields?: { [key: string]: string };
}

export default function OCRUpload({ onSend }: OCRUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [result, setResult] = useState<OCRResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFile = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] || null
    setFile(f)
    setResult(null)
    setError(null)
  }

  const upload = async () => {
    if (!file) return
    setLoading(true)
    try {
      const res = await ocrDocument('', file) // Assuming ocrDocument can handle empty conversationId for now
      setResult(res as OCRResult)
    } catch (err: any) {
      setError(err.message || 'OCR failed')
    } finally {
      setLoading(false)
    }
  }

  const sendToChat = () => {
    if (result && onSend) {
      const text = result.text || Object.values(result.fields || {}).join('\n')
      onSend(text)
    }
  }

  return (
    <div className="p-4 border-b border-dark-700">
      <div className="flex items-center space-x-2">
        <input type="file" accept="image/*,application/pdf" onChange={handleFile} />
        <button onClick={upload} className="px-3 py-1 bg-primary-500 rounded text-white" disabled={loading || !file}>
          {loading ? 'Scanning...' : 'Scan Document'}
        </button>
        {result && (
          <button onClick={sendToChat} className="px-3 py-1 bg-success-500 rounded text-white">
            Send to chat
          </button>
        )}
      </div>

      {error && <div className="mt-2 text-danger-400">{error}</div>}

      {result && (
        <div className="mt-2 text-sm bg-dark-800 p-2 rounded">
          <div className="font-medium">Extracted Text</div>
          <pre className="whitespace-pre-wrap text-xs">{result.text}</pre>
          {result.fields && (
            <div className="mt-2">
              <div className="font-medium">Parsed Fields</div>
              <pre className="text-xs">{JSON.stringify(result.fields, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
