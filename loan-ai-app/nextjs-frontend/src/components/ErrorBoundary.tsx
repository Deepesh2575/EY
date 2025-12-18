import { Component, ReactNode } from 'react'
import { AlertCircle } from 'lucide-react'

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-dark-900 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-dark-800 rounded-lg p-6 border border-danger-500/30">
            <div className="flex items-center space-x-3 mb-4">
              <AlertCircle className="w-6 h-6 text-danger-500" />
              <h2 className="text-xl font-bold text-white">Something went wrong</h2>
            </div>
            <p className="text-gray-300 mb-4">
              We encountered an unexpected error. Please refresh the page to continue.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="w-full px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg text-white transition-colors"
            >
              Refresh Page
            </button>
            {process.env.NODE_ENV === 'development' && ( // Changed import.meta.env.MODE to process.env.NODE_ENV
              <details className="mt-4">
                <summary className="text-sm text-gray-400 cursor-pointer">Error Details</summary>
                <pre className="mt-2 text-xs text-gray-500 overflow-auto">
                  {this.state.error?.toString()}
                </pre>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary


