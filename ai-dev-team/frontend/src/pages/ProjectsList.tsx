import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle, XCircle, Clock, Loader2, Plus, FolderOpen } from 'lucide-react'
import axios from 'axios'

const statusConfig: Record<string, { label: string; color: string; icon: any }> = {
  created: { label: 'Starting', color: 'text-slate-400', icon: Clock },
  in_progress: { label: 'In Progress', color: 'text-blue-400', icon: Loader2 },
  pending_approval: { label: 'Pending Approval', color: 'text-yellow-400', icon: Clock },
  approved: { label: 'Approved', color: 'text-green-400', icon: CheckCircle },
  rejected: { label: 'Rejected', color: 'text-red-400', icon: XCircle },
  failed_testing: { label: 'Tests Failed', color: 'text-red-400', icon: XCircle },
  completed: { label: 'Completed', color: 'text-green-400', icon: CheckCircle },
  error: { label: 'Error', color: 'text-red-400', icon: XCircle },
}

export function ProjectsList() {
  const [projects, setProjects] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get('/api/projects').then(r => setProjects(r.data.projects)).finally(() => setLoading(false))
    const interval = setInterval(() => {
      axios.get('/api/projects').then(r => setProjects(r.data.projects))
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 className="animate-spin text-blue-400" size={32} /></div>

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">Projects</h1>
        <Link to="/new" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors">
          <Plus size={16} /> New Project
        </Link>
      </div>

      {projects.length === 0 ? (
        <div className="text-center py-16 text-slate-500">
          <FolderOpen size={48} className="mx-auto mb-4 opacity-30" />
          <p>No projects yet. Create your first one!</p>
          <Link to="/new" className="text-blue-400 hover:text-blue-300 mt-2 inline-block">+ New Project</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {projects.map((p: any) => {
            const cfg = statusConfig[p.status] || statusConfig.created
            const Icon = cfg.icon
            return (
              <Link key={p.id} to={`/projects/${p.id}`}
                className="block bg-slate-900 border border-slate-800 hover:border-slate-600 rounded-xl p-5 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-white truncate">{p.name}</h3>
                    <p className="text-slate-500 text-sm mt-1">ID: {p.id} · {p.created_at?.slice(0, 16).replace('T', ' ')} UTC</p>
                  </div>
                  <div className={`flex items-center gap-1.5 text-sm font-medium shrink-0 ml-4 ${cfg.color}`}>
                    <Icon size={14} className={p.status === 'in_progress' ? 'animate-spin' : ''} />
                    {cfg.label}
                  </div>
                </div>
                {(p.sprints_completed || p.total_stories) && (
                  <div className="mt-3 flex gap-4 text-xs text-slate-500">
                    {p.sprints_completed && <span>{p.sprints_completed} sprints</span>}
                    {p.total_stories && <span>{p.total_stories} stories</span>}
                    {p.total_files && <span>{p.total_files} files</span>}
                    {p.security?.score && <span className={p.security.status === 'PASSED' ? 'text-green-400' : 'text-red-400'}>Security: {p.security.score}/100</span>}
                    {p.performance?.score && <span className={p.performance.status === 'PASSED' ? 'text-green-400' : 'text-red-400'}>Perf: {p.performance.score}/100</span>}
                  </div>
                )}
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
