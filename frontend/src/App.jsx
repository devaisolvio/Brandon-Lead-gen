import { useState, useEffect, useCallback } from 'react'
import PipelineCard from './components/PipelineCard'
import { getPipelineStatus, getAllStatuses, startPipeline } from './services/api'

const PIPELINES = [
  {
    id: 'apollo',
    name: 'Apollo Lead Generation',
    description: 'Scrape and process leads from Apollo.io with AI-powered filtering',
    color: 'blue',
    icon: '🚀'
  },
  {
    id: 'googlemaps',
    name: 'Google Maps Scraper',
    description: 'Scrape businesses from Google Maps and qualify leads',
    color: 'green',
    icon: '📍'
  },
  {
    id: 'hubspot',
    name: 'HubSpot Leads',
    description: 'Pull and evaluate contacts from HubSpot CRM',
    color: 'purple',
    icon: '💼'
  }
]

function App() {
  const [statuses, setStatuses] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Fetch all pipeline statuses
  const fetchAllStatuses = useCallback(async () => {
    try {
      const data = await getAllStatuses()
      setStatuses(data)
      setError(null)
    } catch (err) {
      console.error('Error fetching statuses:', err)
      setError('Failed to connect to server. Make sure the Flask server is running on port 5000.')
    }
  }, [])

  // Fetch statuses on mount
  useEffect(() => {
    fetchAllStatuses()
  }, [fetchAllStatuses])

  // Smart polling: only poll when at least one pipeline is running
  useEffect(() => {
    // Check if any pipeline is currently running
    const isRunning = PIPELINES.some(pipeline => {
      const status = statuses[pipeline.id]
      return status?.status === 'running'
    })
    
    if (!isRunning) {
      // No pipelines running, don't poll
      return
    }

    // At least one pipeline is running, start polling
    const interval = setInterval(fetchAllStatuses, 3000)
    
    return () => clearInterval(interval)
  }, [statuses, fetchAllStatuses]) // Re-run when statuses change

  const handleStartPipeline = async (pipelineId) => {
    setLoading(true)
    setError(null)
    
    try {
      const result = await startPipeline(pipelineId)
      
      if (result.status === 'already_running') {
        setError(`${PIPELINES.find(p => p.id === pipelineId)?.name} is already running`)
      } else {
        // Refresh statuses after starting to trigger polling
        setTimeout(fetchAllStatuses, 500)
      }
    } catch (err) {
      console.error('Error starting pipeline:', err)
      setError(`Failed to start ${PIPELINES.find(p => p.id === pipelineId)?.name}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 relative overflow-hidden">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-900/10 via-purple-900/10 to-pink-900/10 animate-pulse"></div>
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl"></div>
      
      <div className="container mx-auto px-4 py-8 relative z-10">
        {/* Header */}
        <header className="mb-10">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-1 h-12 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full"></div>
            <div>
              <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white via-blue-100 to-purple-100 mb-2">
                Brandon Lead Generation
              </h1>
              <h2 className="text-2xl font-bold text-white">Dashboard</h2>
            </div>
          </div>
          <p className="text-gray-400 text-lg ml-4">
            Manage and monitor your lead generation pipelines
          </p>
        </header>

        {/* Error Banner */}
        {error && (
          <div className="mb-6 bg-gradient-to-r from-red-900/40 to-red-800/30 border-l-4 border-red-500 text-red-200 px-5 py-4 rounded-lg backdrop-blur-sm shadow-lg animate-slide-in">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="font-semibold">{error}</p>
            </div>
          </div>
        )}

        {/* Pipeline Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {PIPELINES.map((pipeline, index) => (
            <div 
              key={pipeline.id}
              className="animate-fade-in"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <PipelineCard
                pipeline={pipeline}
                status={statuses[pipeline.id]}
                onStart={() => handleStartPipeline(pipeline.id)}
                loading={loading}
              />
            </div>
          ))}
        </div>

        {/* Status Summary */}
        <div className="bg-gradient-to-br from-gray-800/60 to-gray-900/60 backdrop-blur-md rounded-2xl shadow-2xl border border-gray-700/50 p-8 hover:border-gray-600/50 transition-all duration-300">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-1 h-8 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full"></div>
            <h2 className="text-2xl font-bold text-white">System Status</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {PIPELINES.map((pipeline) => {
              const status = statuses[pipeline.id]
              const statusInfo = {
                running: { color: 'text-blue-400', border: 'border-blue-500', bg: 'bg-blue-500/10' },
                completed: { color: 'text-green-400', border: 'border-green-500', bg: 'bg-green-500/10' },
                failed: { color: 'text-red-400', border: 'border-red-500', bg: 'bg-red-500/10' },
                default: { color: 'text-gray-400', border: 'border-gray-600', bg: 'bg-gray-700/20' }
              }
              const currentStatus = statusInfo[status?.status] || statusInfo.default
              
              return (
                <div 
                  key={pipeline.id} 
                  className={`${currentStatus.bg} border-l-4 ${currentStatus.border} pl-5 py-4 rounded-r-lg transition-all duration-300 hover:translate-x-1`}
                >
                  <p className="text-sm font-semibold text-gray-300 mb-2">{pipeline.name}</p>
                  <p className={`text-xl font-bold ${currentStatus.color} capitalize mb-1`}>
                    {status?.status || 'Not Started'}
                  </p>
                  {status?.started_at && (
                    <p className="text-xs text-gray-500 mt-2">
                      Started: {new Date(status.started_at).toLocaleString()}
                    </p>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

