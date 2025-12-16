import { Clock, Shield, Zap, ArrowRight } from 'lucide-react'

function WelcomeScreen({ onQuickStart }) {
  const quickActions = [
    { id: 'personal', label: 'Personal Loan', icon: '💳', description: 'For personal needs' },
    { id: 'business', label: 'Business Loan', icon: '🏢', description: 'Grow your business' },
    { id: 'home', label: 'Home Loan', icon: '🏠', description: 'Buy your dream home' },
  ]
  
  return (
    <div className="flex flex-col items-center justify-center h-full px-4 py-8 animate-fade-in">
      <div className="text-center mb-8">
        <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
          <span className="text-4xl">🤖</span>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
          AI Loan Assistant
        </h1>
        <p className="text-lg text-gray-400 mb-6">
          Get instant loan approval in just 5 minutes
        </p>
      </div>
      
      <div className="w-full max-w-md mb-8">
        <h3 className="text-lg font-semibold text-white mb-4 text-center">
          What would you like to do?
        </h3>
        <div className="space-y-3">
          {quickActions.map((action) => (
            <button
              key={action.id}
              onClick={() => onQuickStart(action.id)}
              className="w-full p-4 bg-dark-800 hover:bg-dark-700 border border-dark-700 hover:border-primary-500 rounded-lg transition-all duration-200 flex items-center justify-between group"
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{action.icon}</span>
                <div className="text-left">
                  <div className="text-white font-semibold">{action.label}</div>
                  <div className="text-sm text-gray-400">{action.description}</div>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-500 transition-colors" />
            </button>
          ))}
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-2xl mt-8">
        <div className="flex flex-col items-center p-4 bg-dark-800/50 rounded-lg">
          <Clock className="w-6 h-6 text-success-500 mb-2" />
          <span className="text-sm text-gray-300 font-medium">5-min approval</span>
        </div>
        <div className="flex flex-col items-center p-4 bg-dark-800/50 rounded-lg">
          <Shield className="w-6 h-6 text-primary-500 mb-2" />
          <span className="text-sm text-gray-300 font-medium">100% Secure</span>
        </div>
        <div className="flex flex-col items-center p-4 bg-dark-800/50 rounded-lg">
          <Zap className="w-6 h-6 text-warning-500 mb-2" />
          <span className="text-sm text-gray-300 font-medium">24/7 Available</span>
        </div>
      </div>
    </div>
  )
}

export default WelcomeScreen


