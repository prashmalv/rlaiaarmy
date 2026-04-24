import { useEffect, useState } from 'react'
import { Plus, Trash2, Mail, ExternalLink, RefreshCw, Download } from 'lucide-react'
import toast from 'react-hot-toast'
import { leadsApi, generateApi } from '../services/api'
import { exportLeads } from '../utils/export'

const DOMAINS = ['banking', 'healthcare', 'insurance', 'manufacturing', 'retail', 'government', 'hr', 'education', 'ecommerce', 'telecom', 'fmcg', 'technology']
const domainColor: Record<string, string> = {
  banking: 'bg-blue-500/20 text-blue-400', healthcare: 'bg-green-500/20 text-green-400',
  insurance: 'bg-purple-500/20 text-purple-400', manufacturing: 'bg-orange-500/20 text-orange-400',
  government: 'bg-red-500/20 text-red-400', hr: 'bg-pink-500/20 text-pink-400',
}
function getDomainColor(d: string) { return domainColor[d] || 'bg-slate-700 text-slate-300' }

export function LeadsPage() {
  const [leads, setLeads] = useState<any[]>([])
  const [showAdd, setShowAdd] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [suggestions, setSuggestions] = useState<any[]>([])
  const [form, setForm] = useState({ name: '', email: '', company: '', designation: '', domain: 'banking', linkedin_url: '', notes: '' })

  const load = () => leadsApi.getAll().then(setLeads)
  useEffect(() => { load() }, [])

  const add = async () => {
    if (!form.name || !form.email) { toast.error('Name and email required'); return }
    await leadsApi.create(form)
    toast.success('Lead added!')
    setShowAdd(false)
    setForm({ name: '', email: '', company: '', designation: '', domain: 'banking', linkedin_url: '', notes: '' })
    load()
  }

  const remove = async (id: string) => {
    if (!confirm('Remove this lead?')) return
    await leadsApi.delete(id)
    toast.success('Lead removed')
    load()
  }

  const getSuggestions = async () => {
    setGenerating(true)
    try {
      const r = await generateApi.leadSuggestions()
      setSuggestions(r.suggestions || [])
    } catch { toast.error('Failed') }
    finally { setGenerating(false) }
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Leads</h1>
          <p className="text-slate-400 text-sm mt-1">{leads.length} contacts · Nurture emails sent daily</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <div className="flex gap-1 bg-slate-800 border border-slate-700 rounded-lg p-1">
            {(['csv','json','md'] as const).map(fmt => (
              <button key={fmt} onClick={() => exportLeads(leads, fmt)}
                className="flex items-center gap-1 text-slate-400 hover:text-white px-2 py-1 rounded text-xs transition-colors">
                <Download size={11} /> .{fmt}
              </button>
            ))}
          </div>
          <button onClick={getSuggestions} disabled={generating}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 px-4 py-2 rounded-lg text-sm transition-colors">
            {generating ? <RefreshCw size={14} className="animate-spin" /> : <RefreshCw size={14} />}
            AI Suggest Leads
          </button>
          <button onClick={() => setShowAdd(!showAdd)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
            <Plus size={14} /> Add Lead
          </button>
        </div>
      </div>

      {/* Add form */}
      {showAdd && (
        <div className="bg-slate-900 border border-slate-700 rounded-xl p-5 mb-6">
          <h3 className="font-semibold text-white mb-4">Add New Lead</h3>
          <div className="grid grid-cols-2 gap-3">
            {[
              { key: 'name', label: 'Full Name', placeholder: 'Rajesh Kumar' },
              { key: 'email', label: 'Email', placeholder: 'rajesh@company.com' },
              { key: 'company', label: 'Company', placeholder: 'HDFC Bank' },
              { key: 'designation', label: 'Designation', placeholder: 'CTO' },
              { key: 'linkedin_url', label: 'LinkedIn URL', placeholder: 'https://linkedin.com/in/...' },
            ].map(({ key, label, placeholder }) => (
              <div key={key}>
                <label className="text-xs text-slate-400 block mb-1">{label}</label>
                <input value={(form as any)[key]} onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
                  placeholder={placeholder}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500" />
              </div>
            ))}
            <div>
              <label className="text-xs text-slate-400 block mb-1">Domain/Industry</label>
              <select value={form.domain} onChange={e => setForm(f => ({ ...f, domain: e.target.value }))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
                {DOMAINS.map(d => <option key={d} value={d} className="capitalize">{d}</option>)}
              </select>
            </div>
          </div>
          <div className="mt-3">
            <label className="text-xs text-slate-400 block mb-1">Notes</label>
            <textarea value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
              rows={2} placeholder="Any context about this lead..."
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 resize-none" />
          </div>
          <div className="flex gap-2 mt-4">
            <button onClick={add} className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg text-sm font-medium">Save Lead</button>
            <button onClick={() => setShowAdd(false)} className="bg-slate-800 text-slate-400 px-5 py-2 rounded-lg text-sm">Cancel</button>
          </div>
        </div>
      )}

      {/* AI Suggestions */}
      {suggestions.length > 0 && (
        <div className="bg-slate-900 border border-yellow-500/20 rounded-xl p-5 mb-6">
          <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
            <span className="text-yellow-400">💡</span> AI-Suggested Leads to Reach Out
          </h3>
          <div className="space-y-3">
            {suggestions.map((s: any, i: number) => (
              <div key={i} className="bg-slate-800 rounded-lg p-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="font-medium text-white text-sm">{s.company}</div>
                    <div className="text-slate-400 text-xs mt-0.5">{s.why_now}</div>
                    <div className="text-slate-500 text-xs mt-1 italic">"{s.opening_angle}"</div>
                  </div>
                  <div className="text-right shrink-0">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${getDomainColor(s.industry)}`}>{s.industry}</span>
                    <div className="text-xs text-slate-500 mt-1">{s.relevant_product}</div>
                    <div className="text-xs text-slate-600 mt-0.5">{s.suggested_contact}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Leads list */}
      <div className="space-y-2">
        {leads.map((lead: any) => (
          <div key={lead.id} className="bg-slate-900 border border-slate-800 hover:border-slate-600 rounded-xl p-4 flex items-center gap-4 transition-colors">
            <div className="w-9 h-9 rounded-full bg-slate-700 flex items-center justify-center text-white font-semibold text-sm shrink-0">
              {lead.name?.charAt(0)?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-medium text-white text-sm">{lead.name}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${getDomainColor(lead.domain)}`}>{lead.domain}</span>
              </div>
              <div className="text-slate-400 text-xs mt-0.5">{lead.designation} {lead.company && `@ ${lead.company}`}</div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              {lead.email && (
                <a href={`mailto:${lead.email}`}
                  className="p-1.5 text-slate-500 hover:text-blue-400 transition-colors">
                  <Mail size={14} />
                </a>
              )}
              {lead.linkedin_url && (
                <a href={lead.linkedin_url} target="_blank" rel="noreferrer"
                  className="p-1.5 text-slate-500 hover:text-blue-400 transition-colors">
                  <ExternalLink size={14} />
                </a>
              )}
              <button onClick={() => remove(lead.id)} className="p-1.5 text-slate-600 hover:text-red-400 transition-colors">
                <Trash2 size={14} />
              </button>
            </div>
          </div>
        ))}
        {leads.length === 0 && (
          <div className="text-center py-16 text-slate-500">
            <p>No leads yet. Add your first lead or use AI suggestions.</p>
          </div>
        )}
      </div>
    </div>
  )
}
