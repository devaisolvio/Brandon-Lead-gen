import { useState, useEffect } from 'react'

const STATUS_COLORS = {
  running: {
    bg: 'bg-blue-900/20',
    border: 'border-blue-500/50',
    text: 'text-blue-400',
    button: 'bg-blue-600 hover:bg-blue-700',
    spinner: 'border-blue-400'
  },
  completed: {
    bg: 'bg-green-900/20',
    border: 'border-green-500/50',
    text: 'text-green-400',
    button: 'bg-green-600 hover:bg-green-700',
    spinner: 'border-green-400'
  },
  failed: {
    bg: 'bg-red-900/20',
    border: 'border-red-500/50',
    text: 'text-red-400',
    button: 'bg-red-600 hover:bg-red-700',
    spinner: 'border-red-400'
  },
  default: {
    bg: 'bg-gray-800/50',
    border: 'border-gray-700/50',
    text: 'text-gray-300',
    button: 'bg-indigo-600 hover:bg-indigo-700',
    spinner: 'border-indigo-400'
  }
}

function PipelineCard({ pipeline, status, onStart, loading }) {
  const [localStatus, setLocalStatus] = useState(status?.status || 'idle')
  const [elapsedTime, setElapsedTime] = useState(null)

  useEffect(() => {
    setLocalStatus(status?.status || 'idle')
    
    if (status?.started_at && status?.status === 'running') {
      const interval = setInterval(() => {
        const start = new Date(status.started_at)
        const now = new Date()
        const diff = Math.floor((now - start) / 1000)
        const minutes = Math.floor(diff / 60)
        const seconds = diff % 60
        setElapsedTime(`${minutes}m ${seconds}s`)
      }, 1000)
      
      return () => clearInterval(interval)
    } else {
      setElapsedTime(null)
    }
  }, [status])

  const statusConfig = STATUS_COLORS[localStatus] || STATUS_COLORS.default
  const isRunning = localStatus === 'running'
  const isCompleted = localStatus === 'completed'
  const isFailed = localStatus === 'failed'

  const formatDate = (dateString) => {
    if (!dateString) return null
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className={`${statusConfig.bg} ${statusConfig.border} border-2 rounded-2xl shadow-2xl backdrop-blur-md p-6 transition-all duration-300 hover:shadow-[0_0_30px_rgba(59,130,246,0.3)] hover:scale-[1.02] hover:border-opacity-100 relative overflow-hidden group`}>
      {/* Animated gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/0 via-white/0 to-white/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      
      {/* Header */}
      <div className="flex items-start justify-between mb-5 relative z-10">
        <div className="flex items-center gap-4">
          <div className="text-4xl transform group-hover:scale-110 transition-transform duration-300">
            {pipeline.icon}
          </div>
          <div>
            <h3 className="text-xl font-bold text-white mb-1">{pipeline.name}</h3>
            <p className="text-sm text-gray-400 leading-relaxed">{pipeline.description}</p>
          </div>
        </div>
      </div>

      {/* Status Badge */}
      <div className="mb-5 relative z-10">
        <div className="flex items-center gap-3">
          <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold ${statusConfig.text} ${statusConfig.bg} ${statusConfig.border} border backdrop-blur-sm shadow-lg`}>
            {isRunning && (
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            )}
            {localStatus.charAt(0).toUpperCase() + localStatus.slice(1)}
          </span>
          {elapsedTime && (
            <span className="text-sm text-gray-400 font-medium bg-gray-800/50 px-3 py-1 rounded-full">
              ⏱️ {elapsedTime}
            </span>
          )}
        </div>
      </div>

      {/* Status Details */}
      {status && (
        <div className="mb-5 space-y-2.5 text-sm relative z-10">
          {status.started_at && (
            <div className="flex justify-between items-center bg-gray-800/30 px-3 py-2 rounded-lg">
              <span className="text-gray-400 flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Started:
              </span>
              <span className="text-gray-200 font-semibold">{formatDate(status.started_at)}</span>
            </div>
          )}
          {status.completed_at && (
            <div className="flex justify-between items-center bg-gray-800/30 px-3 py-2 rounded-lg">
              <span className="text-gray-400 flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Completed:
              </span>
              <span className="text-gray-200 font-semibold">{formatDate(status.completed_at)}</span>
            </div>
          )}
          {status.error && (
            <div className="mt-2 p-3 bg-red-900/40 border border-red-700/50 rounded-lg text-red-300 text-xs backdrop-blur-sm">
              <div className="flex items-start gap-2">
                <svg className="w-4 h-4 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div>
                  <strong className="font-semibold">Error:</strong> {status.error}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Action Button */}
      <button
        onClick={onStart}
        disabled={isRunning || loading}
        className={`w-full ${statusConfig.button} text-white font-bold py-3.5 px-4 rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] relative z-10 group/btn`}
      >
        {isRunning ? (
          <>
            <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Running...
          </>
        ) : isCompleted ? (
          <>
            <svg className="w-5 h-5 group-hover/btn:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Run Again
          </>
        ) : isFailed ? (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Retry
          </>
        ) : (
          <>
            <svg className="w-5 h-5 group-hover/btn:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Start Pipeline
          </>
        )}
      </button>
    </div>
  )
}

export default PipelineCard

