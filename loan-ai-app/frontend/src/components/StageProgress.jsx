import { Check } from 'lucide-react'

const stages = [
  { key: 'GREETING', label: 'Welcome', icon: '👋' },
  { key: 'INFO_GATHERING', label: 'Details', icon: '📝' },
  { key: 'VERIFICATION', label: 'Verification', icon: '✓' },
  { key: 'UNDERWRITING', label: 'Review', icon: '🔍' },
  { key: 'SANCTION', label: 'Decision', icon: '✅' },
  { key: 'COMPLETED', label: 'Complete', icon: '🎉' },
]

function StageProgress({ currentStage }) {
  const getStageIndex = (stage) => {
    return stages.findIndex(s => s.key === stage)
  }
  
  const currentIndex = getStageIndex(currentStage)
  
  const isPastStage = (index) => {
    return index < currentIndex
  }
  
  const isCurrentStage = (index) => {
    return index === currentIndex
  }
  
  return (
    <div className="w-full py-4 px-2 bg-dark-800/50 rounded-lg">
      <div className="flex items-center justify-between relative">
        {/* Connection lines */}
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-dark-700 -z-0">
          <div 
            className="h-full bg-primary-500 transition-all duration-500"
            style={{ width: `${(currentIndex / (stages.length - 1)) * 100}%` }}
          />
        </div>
        
        {stages.map((stage, index) => {
          const isPast = isPastStage(index)
          const isCurrent = isCurrentStage(index)
          
          return (
            <div key={stage.key} className="flex flex-col items-center relative z-10">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-lg transition-all duration-300 ${
                  isPast
                    ? 'bg-success-500 text-white'
                    : isCurrent
                    ? 'bg-primary-500 text-white ring-4 ring-primary-500/30'
                    : 'bg-dark-700 text-gray-500'
                }`}
              >
                {isPast ? (
                  <Check className="w-5 h-5" />
                ) : (
                  <span>{stage.icon}</span>
                )}
              </div>
              <span
                className={`text-xs mt-2 hidden sm:block transition-colors ${
                  isCurrent ? 'text-primary-400 font-semibold' : isPast ? 'text-success-400' : 'text-gray-500'
                }`}
              >
                {stage.label}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default StageProgress


