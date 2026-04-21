import { useEffect, useRef, useState } from 'react'
import { Play, CheckCircle, Loader2, AlertCircle, Linkedin, Mail, Search, Globe } from 'lucide-react'
import toast from 'react-hot-toast'
import { runApi } from '../services/api'

type Log = { agent: string; action: string; result?: string; event?: string; status?: string; timestamp: string }

const agentColors: Record<string, string> = {
  'Priya': 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  'Arjun': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  'Neha': 'bg-green-500/20 text-green-300 border-green-500/30',
  'Vikram': 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  'DailyRunner': 'bg-slate-500/20 text-slate-300 border-slate-500/30',
}
function agentColor(name = '') {
  for (const [k, v] of Object.entries(agentColors)) if (name.includes(k)) return v
  return 'bg-slate-700 text-slate-300 border-slate-600'
}

export function DailyRun() {
  const [running, setRunning] = useState(false)
  const [runId, setRunId] = useState<string | null>(null)
  const [logs, setLogs] = useState<Log[]>([])
  const [steps, setSteps] = useState<{name: string; status: string; summary?: string}[]>([])
  const [activeAgent, setActiveAgent] = useState<string | null>(null)
  const [result, setResult] = useState<any>(null)
  const [focus, setFocus] = useState('')
  const [mode, setMode] = useState('manual')
  const wsRef = useRef<WebSocket | null>(null)
  const logsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const connect = (rid: string) => {
    const ws = new WebSocket('ws://localhost:8001/ws')
    wsRef.current = ws
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      if (msg.run_id && msg.run_id !== rid) return
      if (msg.event === 'step') setSteps(p => {
        const i = p.findIndex(s => s.name === msg.name)
        if (i >= 0) { const n = [...p]; n[i] = msg; return n }
        return [...p, msg]
      })
      else if (msg.event === 'agent_working') setActiveAgent(msg.agent)
      else if (msg.agent) setLogs(p => [...p, msg])
      else if (msg.event === 'completed') {
        setRunning(false); setActiveAgent(null)
        toast.success('Daily run completed!')
        runApi.getRun(rid).then(r => setResult(r.result))
      } else if (msg.event === 'error') {
        setRunning(false); toast.error(msg.message)
      }
    }
  }

  const start = async () => {
    setRunning(true); setLogs([]); setSteps([]); setResult(null); setActiveAgent(null)
    try {
      const { run_id } = await runApi.triggerDaily({ day_focus: focus || undefined, posting_mode: mode })
      setRunId(run_id)
      connect(run_id)
    } catch { toast.error('Failed to start'); setRunning(false) }
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-2">Daily Marketing Run</h1>
      <p className="text-slate-400 mb-6">Runs all 4 agents: Lead scan → Content creation → Email drafts → Post or queue</p>

      {/* Config */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 mb-6 space-y-4">
        <div>
          <label className="text-sm font-medium text-slate-300 block mb-1.5">Today's Focus (optional)</label>
          <input value={focus} onChange={e => setFocus(e.target.value)}
            placeholder="e.g., Push SatyaDocAI for banking, highlight govt tender opportunity"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm" />
        </div>
        <div>
          <label className="text-sm font-medium text-slate-300 block mb-2">Posting Mode</label>
          <div className="flex gap-3">
            {['manual', 'auto'].map(m => (
              <button key={m} onClick={() => setMode(m)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors border ${
                  mode === m ? 'bg-blue-600 border-blue-500 text-white' : 'bg-slate-800 border-slate-700 text-slate-400'
                }`}>
                {m === 'manual' ? '✋ Manual Approval' : '⚡ Auto Post'}
              </button>
            ))}
          </div>
          <p className="text-slate-500 text-xs mt-2">Manual = content queued for your review. Auto = posts directly to social media.</p>
        </div>
        <button onClick={start} disabled={running}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-colors w-full justify-center">
          {running ? <><Loader2 size={18} className="animate-spin" /> Running...</> : <><Play size={18} /> Start Daily Run</>}
        </button>
      </div>

      {/* What runs */}
      {!running && !result && (
        <div className="grid grid-cols-2 gap-3 mb-6">
          {[
            { icon: Search, label: 'Lead Intelligence', desc: 'News scan, govt tenders, competitor analysis', color: 'text-yellow-400' },
            { icon: Linkedin, label: 'Social Content', desc: 'LinkedIn, Instagram, Facebook posts created', color: 'text-blue-400' },
            { icon: Mail, label: 'Nurture Emails', desc: 'Domain-personalized emails for each lead', color: 'text-green-400' },
            { icon: Globe, label: 'Opportunities', desc: 'New leads and tenders flagged for action', color: 'text-purple-400' },
          ].map(({ icon: Icon, label, desc, color }) => (
            <div key={label} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <Icon className={`${color} mb-2`} size={18} />
              <div className="font-medium text-white text-sm">{label}</div>
              <div className="text-slate-500 text-xs mt-0.5">{desc}</div>
            </div>
          ))}
        </div>
      )}

      {/* Steps */}
      {steps.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 mb-4">
          <h2 className="font-semibold text-white mb-3">Progress</h2>
          <div className="space-y-2">
            {steps.map((s, i) => (
              <div key={i} className="flex items-center gap-3 text-sm py-1.5 border-b border-slate-800 last:border-0">
                {s.status === 'complete' ? <CheckCircle size={15} className="text-green-400 shrink-0" /> :
                 s.status === 'started' ? <Loader2 size={15} className="text-blue-400 animate-spin shrink-0" /> :
                 <div className="w-3.5 h-3.5 rounded-full border border-slate-600 shrink-0" />}
                <span className="text-slate-300 font-medium">{s.name}</span>
                {s.summary && <span className="text-slate-500 text-xs ml-auto">{s.summary}</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {activeAgent && (
        <div className="bg-blue-600/10 border border-blue-500/30 rounded-xl p-3 mb-4 flex items-center gap-2 text-sm text-blue-300">
          <Loader2 size={14} className="animate-spin" /> {activeAgent} is working...
        </div>
      )}

      {/* Result summary */}
      {result && (
        <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-5 mb-4">
          <div className="flex items-center gap-2 text-green-400 font-semibold mb-3">
            <CheckCircle size={18} /> Run Completed
          </div>
          <div className="grid grid-cols-3 gap-4">
            {[
              { label: 'Posts Created', value: result.content_created?.length || 0 },
              { label: 'Emails Queued', value: result.emails_queued?.length || 0 },
              { label: 'Opportunities', value: result.opportunities_found?.length || 0 },
            ].map(({ label, value }) => (
              <div key={label} className="bg-slate-900 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-white">{value}</div>
                <div className="text-slate-400 text-xs mt-1">{label}</div>
              </div>
            ))}
          </div>
          {result.opportunities_found?.length > 0 && (
            <div className="mt-4">
              <div className="text-sm font-medium text-white mb-2">Top Opportunities Found:</div>
              {result.opportunities_found.slice(0, 3).map((o: any, i: number) => (
                <div key={i} className="text-sm text-slate-400 py-1 border-b border-slate-800 last:border-0">
                  <span className={`text-xs px-2 py-0.5 rounded mr-2 ${o.priority === 'High' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                    {o.priority}
                  </span>
                  {o.title} — <span className="text-slate-500">{o.relevant_product}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Agent log */}
      {logs.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="font-semibold text-white mb-3">Agent Log ({logs.length})</h2>
          <div className="space-y-1.5 max-h-64 overflow-y-auto">
            {logs.map((log, i) => (
              <div key={i} className="flex items-start gap-2 text-xs py-1 border-b border-slate-800/50 last:border-0">
                <span className={`px-2 py-0.5 rounded border text-xs font-medium shrink-0 ${agentColor(log.agent)}`}>
                  {log.agent?.split('(')[0]?.trim()}
                </span>
                <span className="text-slate-400 flex-1">{log.action}</span>
                <span className="text-slate-600 shrink-0">{log.timestamp?.slice(11, 19)}</span>
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>
      )}
    </div>
  )
}
