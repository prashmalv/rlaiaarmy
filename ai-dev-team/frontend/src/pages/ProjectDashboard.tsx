import { useEffect, useState, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { CheckCircle, XCircle, Clock, Loader2, ExternalLink, Shield, Zap, FileCode2, Activity } from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'

type Phase = { name: string; status: string; summary?: string; result?: string; score?: number }
type Log = { timestamp: string; agent: string; action: string; output_summary: string; status: string; event?: string }

const agentColors: Record<string, string> = {
  'Alex': 'bg-green-500/20 text-green-400 border-green-500/30',
  'Morgan': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  'Dev-E': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  'Dev-F': 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  'Sam': 'bg-red-500/20 text-red-400 border-red-500/30',
  'Perry': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
}

function agentColor(name: string) {
  for (const [key, cls] of Object.entries(agentColors)) {
    if (name.startsWith(key)) return cls
  }
  return 'bg-slate-700 text-slate-300 border-slate-600'
}

export function ProjectDashboard() {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<any>(null)
  const [phases, setPhases] = useState<Phase[]>([])
  const [logs, setLogs] = useState<Log[]>([])
  const [activeAgent, setActiveAgent] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const logsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchProject()
    connectWS()
    return () => wsRef.current?.close()
  }, [id])

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const fetchProject = async () => {
    try {
      const { data } = await axios.get(`/api/projects/${id}`)
      setProject(data)
      if (data.phases) setPhases(data.phases)
      if (data.logs) setLogs(data.logs.filter((l: Log) => l.agent))
    } catch (err) {
      toast.error('Failed to load project')
    }
  }

  const connectWS = () => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${id}`)
    wsRef.current = ws

    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      if (msg.event === 'phase') {
        setPhases(prev => {
          const existing = prev.findIndex(p => p.name === msg.name)
          if (existing >= 0) {
            const updated = [...prev]
            updated[existing] = { ...updated[existing], ...msg }
            return updated
          }
          return [...prev, msg]
        })
      } else if (msg.event === 'agent_working') {
        setActiveAgent(msg.agent)
      } else if (msg.event === 'log' || msg.agent) {
        setLogs(prev => [...prev, msg])
      } else if (msg.event === 'completed') {
        setActiveAgent(null)
        fetchProject()
        toast.success('AI Dev Team completed!')
      } else if (msg.event === 'error') {
        setActiveAgent(null)
        toast.error(`Error: ${msg.message}`)
        fetchProject()
      }
    }
    ws.onerror = () => { /* silently reconnect */ }
  }

  const handleApprove = async () => {
    await axios.post(`/api/projects/${id}/approve`)
    toast.success('Project approved for production!')
    fetchProject()
  }

  const handleReject = async () => {
    const reason = prompt('Rejection reason:')
    if (reason !== null) {
      await axios.post(`/api/projects/${id}/reject?reason=${encodeURIComponent(reason)}`)
      toast.error('Project rejected')
      fetchProject()
    }
  }

  if (!project) {
    return <div className="flex items-center justify-center h-full"><Loader2 className="animate-spin text-blue-400" size={32} /></div>
  }

  const isRunning = project.status === 'in_progress' || project.status === 'created'
  const isPendingApproval = project.status === 'pending_approval'
  const isApproved = project.status === 'approved'
  const isRejected = project.status === 'rejected'

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">{project.name}</h1>
          <p className="text-slate-400 text-sm mt-1">Project ID: {project.id} · Started: {project.created_at?.slice(0, 16).replace('T', ' ')} UTC</p>
        </div>
        <div className="flex gap-3 items-center">
          {isRunning && (
            <span className="flex items-center gap-2 text-blue-400 text-sm">
              <Loader2 size={14} className="animate-spin" />
              Running...
            </span>
          )}
          {isPendingApproval && (
            <>
              <button onClick={handleApprove} className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                ✅ Approve Production
              </button>
              <button onClick={handleReject} className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                ❌ Reject
              </button>
            </>
          )}
          {project.report_path && (
            <a href={`/api/projects/${id}/report`} target="_blank" rel="noreferrer"
              className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 border border-slate-700">
              <ExternalLink size={14} /> Full Report
            </a>
          )}
        </div>
      </div>

      {/* Status Banner */}
      {(isPendingApproval || isApproved || isRejected) && (
        <div className={`rounded-xl p-4 flex items-center gap-3 border ${
          isPendingApproval ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400' :
          isApproved ? 'bg-green-500/10 border-green-500/30 text-green-400' :
          'bg-red-500/10 border-red-500/30 text-red-400'
        }`}>
          {isPendingApproval ? <Clock size={20} /> : isApproved ? <CheckCircle size={20} /> : <XCircle size={20} />}
          <div>
            <div className="font-semibold">
              {isPendingApproval ? 'Pending Senior Management Approval' :
               isApproved ? 'Approved — Ready for Production Deployment' :
               `Rejected — ${project.rejection_reason || 'No reason given'}`}
            </div>
            {isPendingApproval && <div className="text-sm opacity-80">Approval email sent · Application running on Dev environment</div>}
          </div>
        </div>
      )}

      {/* Stats */}
      {project.sprints_completed && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Sprints', value: project.sprints_completed, icon: Activity },
            { label: 'Stories Done', value: project.total_stories, icon: CheckCircle },
            { label: 'Files Generated', value: project.total_files, icon: FileCode2 },
            { label: 'Security Score', value: `${project.security?.score || 0}/100`, icon: Shield },
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <Icon className="text-blue-400 mb-2" size={18} />
              <div className="text-2xl font-bold text-white">{value}</div>
              <div className="text-slate-400 text-xs mt-1">{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Test Results */}
      {project.security && project.performance && (
        <div className="grid grid-cols-2 gap-4">
          {[
            { label: 'Security Tests', data: project.security, icon: Shield },
            { label: 'Performance Tests', data: project.performance, icon: Zap },
          ].map(({ label, data, icon: Icon }) => (
            <div key={label} className={`border rounded-xl p-5 ${data.status === 'PASSED' ? 'bg-green-500/5 border-green-500/20' : 'bg-red-500/5 border-red-500/20'}`}>
              <div className="flex items-center gap-2 mb-3">
                <Icon size={18} className={data.status === 'PASSED' ? 'text-green-400' : 'text-red-400'} />
                <span className="font-medium text-white">{label}</span>
              </div>
              <div className={`text-2xl font-bold ${data.status === 'PASSED' ? 'text-green-400' : 'text-red-400'}`}>
                {data.status === 'PASSED' ? '✅ PASSED' : '❌ FAILED'}
              </div>
              <div className="text-slate-400 text-sm mt-1">Score: {data.score}/100</div>
            </div>
          ))}
        </div>
      )}

      {/* Phases */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h2 className="font-semibold text-white mb-4">Execution Phases</h2>
        <div className="space-y-2">
          {phases.map((phase, i) => (
            <div key={i} className="flex items-center gap-3 py-2 border-b border-slate-800 last:border-0">
              {phase.status === 'complete' ? <CheckCircle size={16} className="text-green-400 shrink-0" /> :
               phase.status === 'started' ? <Loader2 size={16} className="text-blue-400 animate-spin shrink-0" /> :
               <Clock size={16} className="text-slate-600 shrink-0" />}
              <span className="text-slate-300 text-sm font-medium">{phase.name}</span>
              {phase.summary && <span className="text-slate-500 text-xs ml-auto">{phase.summary}</span>}
              {phase.result && (
                <span className={`text-xs px-2 py-0.5 rounded-full ${phase.result === 'PASSED' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                  {phase.result} {phase.score && `· ${phase.score}/100`}
                </span>
              )}
            </div>
          ))}
          {isRunning && phases.length === 0 && (
            <div className="text-slate-500 text-sm py-4 text-center">Waiting for agents to start...</div>
          )}
        </div>
      </div>

      {/* Active Agent */}
      {activeAgent && (
        <div className="bg-blue-600/10 border border-blue-500/30 rounded-xl p-4 flex items-center gap-3">
          <Loader2 size={16} className="text-blue-400 animate-spin" />
          <span className="text-blue-300 text-sm font-medium">{activeAgent} is working...</span>
        </div>
      )}

      {/* Agent Action Log */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h2 className="font-semibold text-white mb-4">Agent Action Log <span className="text-slate-500 font-normal text-sm">({logs.length} actions)</span></h2>
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {logs.map((log, i) => (
            <div key={i} className="flex items-start gap-3 py-2 border-b border-slate-800/50 last:border-0 text-sm">
              <span className={`px-2 py-0.5 rounded border text-xs font-medium shrink-0 ${agentColor(log.agent || '')}`}>
                {log.agent}
              </span>
              <div className="flex-1 min-w-0">
                <span className="text-slate-300">{log.action}</span>
                {log.output_summary && (
                  <div className="text-slate-500 text-xs mt-0.5 truncate">{log.output_summary}</div>
                )}
              </div>
              <span className="text-slate-600 text-xs shrink-0">{log.timestamp?.slice(11, 19)}</span>
            </div>
          ))}
          <div ref={logsEndRef} />
          {logs.length === 0 && <div className="text-slate-500 text-sm py-4 text-center">No logs yet</div>}
        </div>
      </div>
    </div>
  )
}
