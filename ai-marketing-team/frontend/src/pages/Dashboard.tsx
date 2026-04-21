import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Users, FileText, Lightbulb, Play, TrendingUp, Clock, CheckCircle } from 'lucide-react'
import { statsApi } from '../services/api'

export function Dashboard() {
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    statsApi.get().then(setStats).catch(() => {})
    const t = setInterval(() => statsApi.get().then(setStats).catch(() => {}), 15000)
    return () => clearInterval(t)
  }, [])

  const cards = stats ? [
    { label: 'Total Leads', value: stats.total_leads, sub: `${stats.active_leads} active`, icon: Users, color: 'text-blue-400', link: '/leads' },
    { label: 'Content Posts', value: stats.total_posts, sub: `${stats.posts_by_status?.approved || 0} approved`, icon: FileText, color: 'text-purple-400', link: '/content' },
    { label: 'Opportunities', value: stats.total_opportunities, sub: `${stats.new_opportunities} new`, icon: Lightbulb, color: 'text-yellow-400', link: '/opportunities' },
    { label: 'Runs Today', value: stats.total_runs, sub: `Next: ${stats.next_scheduled_run}`, icon: Play, color: 'text-green-400', link: '/run' },
  ] : []

  const products = [
    { name: 'LOVAIC', desc: 'Computer Vision · Pixel-level analytics', color: 'from-blue-600 to-cyan-600' },
    { name: 'SatyaDocAI', desc: 'Document Forgery Detection', color: 'from-violet-600 to-purple-600' },
    { name: 'SalesBuddy / VoiceBuddy', desc: 'AI Voice Agent Suite', color: 'from-green-600 to-teal-600' },
    { name: 'AI Avatar L&D', desc: 'Training & Marketing Ads', color: 'from-orange-600 to-red-600' },
  ]

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Marketing Command Center</h1>
        <p className="text-slate-400 mt-1">RightLeftAI — AI-powered autonomous marketing team</p>
      </div>

      {/* Quick Action */}
      <div className="bg-gradient-to-r from-blue-600/20 to-violet-600/20 border border-blue-500/30 rounded-xl p-5 mb-6 flex items-center justify-between">
        <div>
          <div className="font-semibold text-white">Run Today's Marketing</div>
          <div className="text-slate-400 text-sm mt-0.5">Generate posts, scan leads, create nurture emails — all in one click</div>
        </div>
        <Link to="/run"
          className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg font-medium text-sm flex items-center gap-2 transition-colors shrink-0">
          <Play size={16} /> Launch Daily Run
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {cards.map(({ label, value, sub, icon: Icon, color, link }) => (
          <Link key={label} to={link}
            className="bg-slate-900 border border-slate-800 hover:border-slate-600 rounded-xl p-5 transition-colors">
            <Icon className={`${color} mb-3`} size={20} />
            <div className="text-2xl font-bold text-white">{value ?? '—'}</div>
            <div className="text-slate-400 text-sm mt-0.5">{label}</div>
            <div className="text-slate-600 text-xs mt-1">{sub}</div>
          </Link>
        ))}
      </div>

      {/* Products */}
      <div className="mb-8">
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Our Products to Market</h2>
        <div className="grid grid-cols-2 gap-3">
          {products.map(p => (
            <div key={p.name} className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-3">
              <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${p.color} shrink-0`} />
              <div>
                <div className="font-semibold text-white text-sm">{p.name}</div>
                <div className="text-slate-500 text-xs">{p.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Team */}
      <div>
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Your AI Marketing Team</h2>
        <div className="grid grid-cols-2 gap-3">
          {[
            { name: 'Priya (CMO)', role: 'Strategy, calendar, weekly reports', color: 'bg-purple-500/10 border-purple-500/20 text-purple-400' },
            { name: 'Arjun (Content)', role: 'LinkedIn, Instagram, Facebook, articles', color: 'bg-blue-500/10 border-blue-500/20 text-blue-400' },
            { name: 'Neha (Email)', role: 'Nurture sequences, news digests, cold outreach', color: 'bg-green-500/10 border-green-500/20 text-green-400' },
            { name: 'Vikram (Intel)', role: 'Tenders, opportunities, competitor analysis', color: 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400' },
          ].map(a => (
            <div key={a.name} className={`border rounded-xl p-4 ${a.color}`}>
              <div className="font-semibold text-sm">{a.name}</div>
              <div className="text-xs mt-1 opacity-70">{a.role}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
