import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Play, FileText, Users, Lightbulb,
  Calendar, Wand2, ExternalLink
} from 'lucide-react'

const nav = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/run', icon: Play, label: 'Daily Run' },
  { to: '/content', icon: FileText, label: 'Content Queue' },
  { to: '/leads', icon: Users, label: 'Leads' },
  { to: '/opportunities', icon: Lightbulb, label: 'Opportunities' },
  { to: '/calendar', icon: Calendar, label: 'Content Calendar' },
  { to: '/generate', icon: Wand2, label: 'Generate' },
]

const agents = [
  { name: 'Priya (CMO)', color: 'bg-purple-400' },
  { name: 'Arjun (Content)', color: 'bg-blue-400' },
  { name: 'Neha (Email)', color: 'bg-green-400' },
  { name: 'Vikram (Intel)', color: 'bg-yellow-400' },
]

export function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0">
      {/* Brand */}
      <div className="p-5 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center font-bold text-white text-sm">
            RL
          </div>
          <div>
            <div className="font-bold text-white text-sm leading-tight">RightLeftAI</div>
            <div className="text-slate-400 text-xs">Marketing Command Center</div>
          </div>
        </div>
        <a href="https://rightleft.ai" target="_blank" rel="noreferrer"
          className="mt-3 flex items-center gap-1 text-xs text-slate-500 hover:text-slate-300 transition-colors">
          <ExternalLink size={10} /> rightleft.ai
        </a>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-0.5">
        {nav.map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to} end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-blue-600/20 text-blue-400 font-medium'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`
            }>
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Agents */}
      <div className="p-4 border-t border-slate-800">
        <div className="text-xs text-slate-600 font-medium uppercase tracking-wider mb-2">AI Team</div>
        <div className="space-y-1.5">
          {agents.map(a => (
            <div key={a.name} className="flex items-center gap-2 text-xs text-slate-500">
              <span className={`w-1.5 h-1.5 rounded-full ${a.color}`}></span>
              {a.name}
            </div>
          ))}
        </div>
      </div>
    </aside>
  )
}
