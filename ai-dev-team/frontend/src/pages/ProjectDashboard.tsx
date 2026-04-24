import { useEffect, useState, useRef } from 'react'
import { useParams } from 'react-router-dom'
import {
  CheckCircle, XCircle, Clock, Loader2, ExternalLink, Shield, Zap,
  FileCode2, Activity, Download, ChevronRight, ChevronDown, Eye, Printer,
  Terminal, FolderOpen
} from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'

type Phase = { name: string; status: string; summary?: string; result?: string; score?: number }
type Log   = { timestamp: string; agent: string; action: string; output_summary: string; status: string; event?: string }
type FileMeta = { path: string; size: number; ext: string }

const agentColors: Record<string, string> = {
  'Alex':  'bg-green-500/20 text-green-400 border-green-500/30',
  'Morgan':'bg-purple-500/20 text-purple-400 border-purple-500/30',
  'Dev-E': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  'Dev-F': 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  'Sam':   'bg-red-500/20 text-red-400 border-red-500/30',
  'Perry': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  'Jordan':'bg-orange-500/20 text-orange-400 border-orange-500/30',
}
function agentColor(name: string) {
  for (const [key, cls] of Object.entries(agentColors)) {
    if (name?.startsWith(key)) return cls
  }
  return 'bg-slate-700 text-slate-300 border-slate-600'
}

const EXT_COLORS: Record<string, string> = {
  py: 'text-blue-400', ts: 'text-cyan-400', tsx: 'text-cyan-300',
  js: 'text-yellow-400', jsx: 'text-yellow-300', json: 'text-green-400',
  md: 'text-slate-300', html: 'text-orange-400', css: 'text-pink-400',
  sql: 'text-purple-400', sh: 'text-green-300', txt: 'text-slate-400',
}

function buildFileTree(files: FileMeta[]) {
  const tree: Record<string, any> = {}
  for (const f of files) {
    const parts = f.path.split(/[/\\]/)
    let node = tree
    for (let i = 0; i < parts.length - 1; i++) {
      if (!node[parts[i]]) node[parts[i]] = { __dir: true }
      node = node[parts[i]]
    }
    node[parts[parts.length - 1]] = f
  }
  return tree
}

function FileNode({ name, node, projectId, depth = 0 }: { name: string; node: any; projectId: string; depth?: number }) {
  const [open, setOpen] = useState(depth < 2)
  const [content, setContent] = useState<string | null>(null)
  const [loadingContent, setLoadingContent] = useState(false)

  const isDir = node.__dir || (typeof node === 'object' && !node.path)
  const indent = depth * 12

  if (isDir) {
    const children = Object.entries(node).filter(([k]) => k !== '__dir')
    return (
      <div>
        <button onClick={() => setOpen(o => !o)}
          className="flex items-center gap-1.5 w-full text-left py-0.5 hover:bg-slate-800 rounded px-1 group"
          style={{ paddingLeft: `${indent + 4}px` }}>
          {open ? <ChevronDown size={12} className="text-slate-500" /> : <ChevronRight size={12} className="text-slate-500" />}
          <FolderOpen size={12} className="text-yellow-400/70" />
          <span className="text-slate-400 text-xs font-medium">{name}</span>
        </button>
        {open && children.map(([k, v]) => <FileNode key={k} name={k} node={v} projectId={projectId} depth={depth + 1} />)}
      </div>
    )
  }

  const ext = node.ext || ''
  const viewFile = async () => {
    if (content !== null) { setContent(null); return }
    setLoadingContent(true)
    try {
      const { data } = await axios.get(`/api/projects/${projectId}/files/view?path=${encodeURIComponent(node.path)}`)
      setContent(data.content)
    } catch { toast.error('Failed to load file') }
    finally { setLoadingContent(false) }
  }

  return (
    <div>
      <div className="flex items-center gap-1.5 py-0.5 hover:bg-slate-800 rounded px-1 group"
        style={{ paddingLeft: `${indent + 4}px` }}>
        <span className="w-3" />
        <FileCode2 size={11} className={EXT_COLORS[ext] || 'text-slate-500'} />
        <span className="text-slate-300 text-xs flex-1 truncate">{name}</span>
        <span className="text-slate-600 text-[10px] mr-1">{(node.size / 1024).toFixed(1)}KB</span>
        <button onClick={viewFile} className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-white transition-all">
          <Eye size={11} />
        </button>
      </div>
      {loadingContent && <div className="text-xs text-slate-500 pl-10 py-1">Loading...</div>}
      {content !== null && (
        <div className="mx-2 my-1 rounded border border-slate-700 bg-slate-950 overflow-x-auto">
          <pre className="text-xs text-slate-300 p-3 leading-relaxed max-h-64 overflow-y-auto">{content}</pre>
        </div>
      )}
    </div>
  )
}

export function ProjectDashboard() {
  const { id } = useParams<{ id: string }>()
  const [project, setProject]     = useState<any>(null)
  const [phases, setPhases]       = useState<Phase[]>([])
  const [logs, setLogs]           = useState<Log[]>([])
  const [activeAgent, setActiveAgent] = useState<string | null>(null)
  const [files, setFiles]         = useState<FileMeta[]>([])
  const [showFiles, setShowFiles] = useState(false)
  const wsRef     = useRef<WebSocket | null>(null)
  const logsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => { fetchProject(); connectWS(); return () => wsRef.current?.close() }, [id])
  useEffect(() => { logsEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [logs])

  const fetchProject = async () => {
    try {
      const { data } = await axios.get(`/api/projects/${id}`)
      setProject(data)
      if (data.phases) setPhases(data.phases)
      if (data.logs)   setLogs(data.logs.filter((l: Log) => l.agent))
    } catch { toast.error('Failed to load project') }
  }

  const fetchFiles = async () => {
    try {
      const { data } = await axios.get(`/api/projects/${id}/files`)
      setFiles(data.files || [])
      setShowFiles(true)
    } catch { toast.error('Failed to load files') }
  }

  const connectWS = () => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${id}`)
    wsRef.current = ws
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      if (msg.event === 'phase') {
        setPhases(prev => {
          const idx = prev.findIndex(p => p.name === msg.name)
          if (idx >= 0) { const u = [...prev]; u[idx] = { ...u[idx], ...msg }; return u }
          return [...prev, msg]
        })
      } else if (msg.event === 'agent_working') {
        setActiveAgent(msg.agent)
      } else if (msg.event === 'log' || msg.agent) {
        setLogs(prev => [...prev, msg])
      } else if (msg.event === 'completed') {
        setActiveAgent(null); fetchProject(); toast.success('AI Dev Team completed!')
      } else if (msg.event === 'error') {
        setActiveAgent(null); toast.error(`Error: ${msg.message}`); fetchProject()
      }
    }
    ws.onerror = () => {}
  }

  const handleApprove = async () => {
    await axios.post(`/api/projects/${id}/approve`)
    toast.success('Approved for production!'); fetchProject()
  }
  const handleReject = async () => {
    const reason = prompt('Rejection reason:')
    if (reason !== null) {
      await axios.post(`/api/projects/${id}/reject?reason=${encodeURIComponent(reason)}`)
      toast.error('Project rejected'); fetchProject()
    }
  }

  if (!project) return (
    <div className="flex items-center justify-center h-full">
      <Loader2 className="animate-spin text-blue-400" size={32} />
    </div>
  )

  const isRunning          = ['in_progress', 'created'].includes(project.status)
  const isPendingApproval  = project.status === 'pending_approval'
  const isApproved         = project.status === 'approved'
  const isRejected         = project.status === 'rejected'
  const isError            = project.status === 'error'
  const isDone             = !isRunning

  // Detect tech stack from architecture for run instructions
  const arch = project.architecture || {}
  const techStack = arch.tech_stack || {}
  const deployment = arch.deployment || {}
  const backendPort  = deployment?.ports?.backend || 8000
  const frontendPort = deployment?.ports?.frontend || 3000
  const isDocker = (deployment?.local || '').toLowerCase().includes('docker')
  const dbTech = techStack.database || ''

  const fileTree = buildFileTree(files)

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">

      {/* ── Header ── */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">{project.name}</h1>
          <p className="text-slate-400 text-sm mt-1">ID: {project.id} · Started: {project.created_at?.slice(0, 16).replace('T', ' ')} UTC</p>
        </div>
        <div className="flex gap-2 items-center flex-wrap justify-end">
          {isRunning && (
            <span className="flex items-center gap-2 text-blue-400 text-sm">
              <Loader2 size={14} className="animate-spin" /> Running...
            </span>
          )}
          {isPendingApproval && <>
            <button onClick={handleApprove} className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium">✅ Approve</button>
            <button onClick={handleReject}  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium">❌ Reject</button>
          </>}
          {isDone && project.output_dir && (
            <a href={`/api/projects/${id}/download`}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
              <Download size={14} /> Download Code (ZIP)
            </a>
          )}
          {project.report_path && (
            <>
              <a href={`/api/projects/${id}/report`} target="_blank" rel="noreferrer"
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 border border-slate-700">
                <ExternalLink size={14} /> Full Report
              </a>
              <button onClick={() => {
                const w = window.open(`/api/projects/${id}/report`, '_blank')
                w?.addEventListener('load', () => w.print())
              }} className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-2 rounded-lg text-sm border border-slate-700" title="Save report as PDF">
                <Printer size={14} />
              </button>
            </>
          )}
        </div>
      </div>

      {/* ── Status Banner ── */}
      {(isPendingApproval || isApproved || isRejected || isError) && (
        <div className={`rounded-xl p-4 flex items-start gap-3 border ${
          isPendingApproval ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400' :
          isApproved        ? 'bg-green-500/10 border-green-500/30 text-green-400' :
                              'bg-red-500/10 border-red-500/30 text-red-400'}`}>
          {isPendingApproval ? <Clock size={20} /> : isApproved ? <CheckCircle size={20} /> : <XCircle size={20} />}
          <div>
            <div className="font-semibold">
              {isPendingApproval ? 'Pending Senior Management Approval' :
               isApproved        ? 'Approved — Ready for Production Deployment' :
               isError           ? `Error: ${project.error || 'Unexpected failure'}` :
               `Rejected — ${project.rejection_reason || 'No reason given'}`}
            </div>
            {isPendingApproval && <div className="text-sm opacity-80 mt-0.5">Approval email sent · App running in Dev environment</div>}
            {isError && <div className="text-sm opacity-80 mt-0.5">Restart the backend and try again. The agent pipeline is more resilient now after the latest fix.</div>}
          </div>
        </div>
      )}

      {/* ── Stats ── */}
      {project.sprints_completed !== undefined && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Sprints',          value: project.sprints_completed, icon: Activity },
            { label: 'Stories Done',     value: project.total_stories,     icon: CheckCircle },
            { label: 'Files Generated',  value: project.total_files,       icon: FileCode2 },
            { label: 'Security Score',   value: `${project.security?.score ?? 0}/100`, icon: Shield },
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <Icon className="text-blue-400 mb-2" size={18} />
              <div className="text-2xl font-bold text-white">{value ?? '—'}</div>
              <div className="text-slate-400 text-xs mt-1">{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* ── Test Results ── */}
      {project.security && project.performance && (
        <div className="grid grid-cols-2 gap-4">
          {[
            { label: 'Security Tests',    data: project.security,    icon: Shield },
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
              <div className="text-slate-400 text-sm mt-1">Score: {data.score ?? 0}/100</div>
            </div>
          ))}
        </div>
      )}

      {/* ── Phases ── */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h2 className="font-semibold text-white mb-4">Execution Phases</h2>
        <div className="space-y-2">
          {phases.map((phase, i) => (
            <div key={i} className="flex items-center gap-3 py-2 border-b border-slate-800 last:border-0">
              {phase.status === 'complete' ? <CheckCircle size={16} className="text-green-400 shrink-0" /> :
               phase.status === 'started'  ? <Loader2 size={16} className="text-blue-400 animate-spin shrink-0" /> :
               <Clock size={16} className="text-slate-600 shrink-0" />}
              <span className="text-slate-300 text-sm font-medium">{phase.name}</span>
              {phase.summary && <span className="text-slate-500 text-xs ml-auto">{phase.summary}</span>}
              {phase.result && (
                <span className={`text-xs px-2 py-0.5 rounded-full ${phase.result === 'PASSED' || phase.result === 'GO' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                  {phase.result}{phase.score ? ` · ${phase.score}/100` : ''}
                </span>
              )}
            </div>
          ))}
          {isRunning && phases.length === 0 && <div className="text-slate-500 text-sm py-4 text-center">Waiting for agents to start...</div>}
        </div>
      </div>

      {/* ── Active Agent ── */}
      {activeAgent && (
        <div className="bg-blue-600/10 border border-blue-500/30 rounded-xl p-4 flex items-center gap-3">
          <Loader2 size={16} className="text-blue-400 animate-spin" />
          <span className="text-blue-300 text-sm font-medium">{activeAgent} is working...</span>
        </div>
      )}

      {/* ── How to Run ── */}
      {isDone && project.output_dir && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <Terminal size={16} className="text-green-400" />
            <h2 className="font-semibold text-white">How to Run the Generated Application</h2>
          </div>
          <div className="space-y-3 text-sm">
            <div className="bg-slate-950 rounded-lg p-3 font-mono text-xs text-slate-300 space-y-1">
              <div className="text-slate-500"># 1. Download the ZIP and extract it</div>
              <div className="text-green-400">curl -O "/api/projects/{id}/download"</div>
              {dbTech.toLowerCase().includes('postgres') && <>
                <div className="text-slate-500 mt-2"># 2. Start PostgreSQL and create DB</div>
                <div>createdb {project.name?.toLowerCase().replace(/\s+/g, '_')}_db</div>
              </>}
              {isDocker ? <>
                <div className="text-slate-500 mt-2"># 2. Run with Docker Compose</div>
                <div>docker-compose up --build</div>
                <div className="text-slate-500 mt-1"># App will be at:</div>
                <div>Frontend → <span className="text-blue-400">http://localhost:{frontendPort}</span></div>
                <div>Backend  → <span className="text-blue-400">http://localhost:{backendPort}</span></div>
              </> : <>
                <div className="text-slate-500 mt-2"># 2. Install backend dependencies</div>
                <div>cd backend && pip install -r requirements.txt</div>
                <div className="text-slate-500 mt-1"># 3. Run backend</div>
                <div>uvicorn main:app --reload --port {backendPort}</div>
                <div className="text-slate-500 mt-1"># 4. Install frontend dependencies (new terminal)</div>
                <div>cd frontend && npm install && npm run dev</div>
                <div className="text-slate-500 mt-1"># App will be at:</div>
                <div>Frontend → <span className="text-blue-400">http://localhost:{frontendPort}</span></div>
                <div>Backend  → <span className="text-blue-400">http://localhost:{backendPort}/docs</span></div>
              </>}
            </div>
            <div className="text-xs text-slate-500">
              Tech stack: <span className="text-slate-300">{Object.values(techStack).filter(Boolean).join(' · ')}</span>
            </div>
            {project.security?.score < 70 || project.performance?.score < 70 ? (
              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 text-yellow-400 text-xs">
                ⚠ Before going live: fix the issues flagged in the Full Report.
                Security issues: check OWASP findings. Performance: review Locust test results.
                Re-run security tests with <code className="bg-slate-800 px-1 rounded">pytest tests/security/</code>
              </div>
            ) : null}
          </div>
        </div>
      )}

      {/* ── Generated Files Browser ── */}
      {isDone && project.output_dir && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <FolderOpen size={16} className="text-yellow-400" />
              <h2 className="font-semibold text-white">Generated Files</h2>
              {files.length > 0 && <span className="text-slate-500 text-sm">({files.length} files)</span>}
            </div>
            <div className="flex gap-2">
              {!showFiles ? (
                <button onClick={fetchFiles}
                  className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1.5 border border-blue-500/30 px-3 py-1.5 rounded-lg transition-colors">
                  <Eye size={13} /> Browse Files
                </button>
              ) : (
                <button onClick={() => setShowFiles(false)}
                  className="text-sm text-slate-400 hover:text-white px-3 py-1.5 rounded-lg transition-colors">
                  Collapse
                </button>
              )}
              <a href={`/api/projects/${id}/download`}
                className="text-sm text-green-400 hover:text-green-300 flex items-center gap-1.5 border border-green-500/30 px-3 py-1.5 rounded-lg transition-colors">
                <Download size={13} /> Download ZIP
              </a>
            </div>
          </div>

          {showFiles && files.length > 0 && (
            <div className="bg-slate-950 rounded-lg border border-slate-800 p-2 max-h-96 overflow-y-auto">
              {Object.entries(fileTree).map(([k, v]) => (
                <FileNode key={k} name={k} node={v} projectId={id!} depth={0} />
              ))}
            </div>
          )}
          {showFiles && files.length === 0 && (
            <div className="text-slate-500 text-sm py-4 text-center">No files generated yet</div>
          )}
        </div>
      )}

      {/* ── Agent Log ── */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h2 className="font-semibold text-white mb-4">
          Agent Action Log <span className="text-slate-500 font-normal text-sm">({logs.length} actions)</span>
        </h2>
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {logs.map((log, i) => (
            <div key={i} className="flex items-start gap-3 py-2 border-b border-slate-800/50 last:border-0 text-sm">
              <span className={`px-2 py-0.5 rounded border text-xs font-medium shrink-0 ${agentColor(log.agent || '')}`}>
                {log.agent}
              </span>
              <div className="flex-1 min-w-0">
                <span className="text-slate-300">{log.action}</span>
                {log.output_summary && <div className="text-slate-500 text-xs mt-0.5 truncate">{log.output_summary}</div>}
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
