import { CheckCircle, XCircle, Loader, Circle } from 'lucide-react'

interface StatusIndicatorProps {
  status: 'idle' | 'processing' | 'success' | 'error';
}

function StatusIndicator({ status }: StatusIndicatorProps) {
  const statusConfig = {
    idle: {
      icon: Circle,
      color: 'text-gray-400',
      label: 'Ready',
    },
    processing: {
      icon: Loader,
      color: 'text-accent animate-spin',
      label: 'Processing',
    },
    success: {
      icon: CheckCircle,
      color: 'text-secondary',
      label: 'Success',
    },
    error: {
      icon: XCircle,
      color: 'text-danger',
      label: 'Error',
    },
  }

  const config = statusConfig[status] || statusConfig.idle
  const Icon = config.icon

  return (
    <div className="flex items-center space-x-2">
      <Icon className={`w-4 h-4 ${config.color}`} />
      <span className="text-sm text-gray-400">{config.label}</span>
    </div>
  )
}

export default StatusIndicator


