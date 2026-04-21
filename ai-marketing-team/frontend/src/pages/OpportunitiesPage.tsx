import { useEffect, useState } from 'react'
import { Lightbulb, CheckCircle, XCircle, RefreshCw, ExternalLink } from 'lucide-react'
import toast from 'react-hot-toast'
import { opportunitiesApi } from '../services/api'

const priorityConfig: Record<string, string> = {
  High: 'bg-red-500/20 text-red-400 border-red-500/30',
  Medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  Low: 'bg-slate-700 text-slate-400 border-slate-600',
}

const productColor: Record<string, string> = {
  LOVAIC: 'text-cyan-400', SatyaDocAI: 'text-purple-400',
  SalesBuddy: 'text-green-400', VoiceBuddy: 'text-green-400',
  EvalBuddy: 'text-green-400', 'AI Avatar': 'text-orange-400', Multiple: 'text-blue-400',
}

export function OpportunitiesPage() {
  const [opps, setOpps] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  const load = () => { setLoading(true); opportunitiesApi.getAll().then(setOpps).finally(() => setLoading(false)) }
  useEffect(() => { load() }, [])

  const updateStatus = async (id: string, status: string) => {
    await opportunitiesApi.updateStatus(id, status)
    toast.success(`Marked as ${status}`)
    load()
  }

  const filtered = filter === 'all' ? opps : opps.filter(o => o.status === filter || o.priority === filter)

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Opportunities</h1>
          <p className="text-slate-400 text-sm mt-1">{opps.filter(o => o.status === 'new').length} new opportunities discovered by Vikram (Intel)</p>
        </div>
        <button onClick={load} className="p-2 text-slate-400 hover:text-white transition-colors">
          <RefreshCw size={16} />
        </button>
      </div>

      <div className="flex gap-2 mb-6 flex-wrap">
        {['all', 'new', 'reviewed', 'actioned', 'High', 'Medium'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors capitalize ${
              filter === f ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}>{f}</button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-16 text-slate-500">Scanning for opportunities...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 text-slate-500">
          <Lightbulb size={32} className="mx-auto mb-3 opacity-30" />
          <p>No opportunities yet. Run daily scan to discover new ones.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((opp: any) => (
            <div key={opp.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-start gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${priorityConfig[opp.priority] || priorityConfig.Low}`}>
                      {opp.priority} Priority
                    </span>
                    <span className={`text-xs font-semibold ${productColor[opp.relevant_product] || 'text-slate-400'}`}>
                      {opp.relevant_product}
                    </span>
                    <span className="text-xs text-slate-500 capitalize">{opp.domain}</span>
                    <span className="text-xs text-slate-600 ml-auto">{opp.discovered_at?.slice(0, 10)}</span>
                  </div>
                  <h3 className="font-semibold text-white">{opp.title}</h3>
                  <p className="text-slate-400 text-sm mt-1 leading-relaxed">{opp.summary}</p>

                  {opp.action_suggested && (
                    <div className="mt-3 bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
                      <div className="text-xs text-blue-400 font-medium mb-1">Suggested Action</div>
                      <div className="text-sm text-slate-300">{opp.action_suggested}</div>
                    </div>
                  )}

                  <div className="flex items-center gap-2 mt-3">
                    {opp.source_url && (
                      <a href={opp.source_url} target="_blank" rel="noreferrer"
                        className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-300 transition-colors">
                        <ExternalLink size={11} /> Source
                      </a>
                    )}
                    <div className="flex-1" />
                    {opp.status === 'new' && (
                      <>
                        <button onClick={() => updateStatus(opp.id, 'actioned')}
                          className="flex items-center gap-1.5 bg-green-600/20 hover:bg-green-600/30 text-green-400 border border-green-500/30 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors">
                          <CheckCircle size={12} /> Action Taken
                        </button>
                        <button onClick={() => updateStatus(opp.id, 'dismissed')}
                          className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-500 px-3 py-1.5 rounded-lg text-xs transition-colors">
                          <XCircle size={12} /> Dismiss
                        </button>
                      </>
                    )}
                    {opp.status !== 'new' && (
                      <span className="text-xs text-slate-500 capitalize">{opp.status}</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
