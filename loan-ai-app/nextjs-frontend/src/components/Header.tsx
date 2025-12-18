import { Shield, Clock, Zap } from 'lucide-react'

function Header() {
  return (
    <header className="sticky top-0 z-50 bg-dark-800/80 backdrop-blur-md border-b border-dark-700">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">AI</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">AI Loan Assistant</h1>
              <p className="text-sm text-gray-400">Get instant loan approval in 5 minutes</p>
            </div>
          </div>
          
          <div className="hidden md:flex items-center space-x-6">
            <div className="flex items-center space-x-2 text-sm text-gray-300">
              <Clock className="w-4 h-4 text-success-500" />
              <span>24/7 Available</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-300">
              <Zap className="w-4 h-4 text-warning-500" />
              <span>Instant Decisions</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-300">
              <Shield className="w-4 h-4 text-primary-500" />
              <span>Secure & Fast</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header


