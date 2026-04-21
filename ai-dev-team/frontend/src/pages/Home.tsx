import { Link } from 'react-router-dom'
import { Bot, Zap, Shield, BarChart3, FileText, Clock } from 'lucide-react'

const features = [
  { icon: Bot, title: 'BA Agent', desc: 'Analyses requirements, creates agile backlog, user stories with acceptance criteria', color: 'text-green-400' },
  { icon: FileText, title: 'Tech Architect', desc: 'Designs system architecture, defines module boundaries, API contracts, coding standards', color: 'text-purple-400' },
  { icon: Zap, title: '3x AI Engineers + 3x Full Stack', desc: 'Parallel development with integration — backend APIs + React frontend', color: 'text-blue-400' },
  { icon: Shield, title: 'Security Agent', desc: 'OWASP Top 10 analysis, security test scripts, vulnerability reporting', color: 'text-red-400' },
  { icon: BarChart3, title: 'Performance Agent', desc: 'Load testing, stress testing, P95 latency, RPS benchmarks via Locust', color: 'text-yellow-400' },
  { icon: Clock, title: '2-Hour Sprints', desc: 'Complete dev cycle in hours not weeks. Email approval for production deploy', color: 'text-cyan-400' },
]

export function Home() {
  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 bg-blue-600/20 text-blue-400 px-4 py-1.5 rounded-full text-sm font-medium mb-6 border border-blue-500/30">
          <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
          Autonomous AI Development Team
        </div>
        <h1 className="text-4xl font-bold text-white mb-4">
          From Requirements to Production
          <br />
          <span className="text-blue-400">in Hours, Not Months</span>
        </h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          An AI team of specialised agents — BA, Architect, Engineers, Security, Performance — working together to deliver production-ready software with full testing and approval workflow.
        </p>
        <div className="mt-8 flex gap-4 justify-center">
          <Link to="/new" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2">
            <Zap size={18} />
            Start New Project
          </Link>
          <Link to="/projects" className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-6 py-3 rounded-lg font-medium transition-colors border border-slate-700">
            View Projects
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {features.map(({ icon: Icon, title, desc, color }) => (
          <div key={title} className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-600 transition-colors">
            <Icon className={`${color} mb-3`} size={24} />
            <h3 className="font-semibold text-white mb-2">{title}</h3>
            <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
          </div>
        ))}
      </div>

      <div className="mt-10 bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h2 className="font-semibold text-white mb-4">Workflow</h2>
        <div className="flex flex-wrap gap-2 items-center text-sm">
          {['Requirements Input', '→', 'BA Analysis', '→', 'Architecture Design', '→', 'Poker Planning', '→', 'Sprint Execution (2hr)', '→', 'Security Test', '→', 'Performance Test', '→', 'Email Approval', '→', 'Production / Dev Hold'].map((step, i) => (
            <span key={i} className={step === '→' ? 'text-slate-600' : 'bg-slate-800 text-slate-300 px-3 py-1 rounded-md border border-slate-700'}>
              {step}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
