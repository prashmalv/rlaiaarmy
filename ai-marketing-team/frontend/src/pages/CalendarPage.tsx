import { useState } from 'react'
import { Loader2, RefreshCw, Calendar } from 'lucide-react'
import toast from 'react-hot-toast'
import { generateApi } from '../services/api'

const platformColors: Record<string, string> = {
  linkedin: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  instagram: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
  email: 'bg-green-500/20 text-green-400 border-green-500/30',
}

export function CalendarPage() {
  const [calendar, setCalendar] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [focus, setFocus] = useState('')

  const generate = async () => {
    setLoading(true)
    try {
      const data = await generateApi.weeklyCalendar(focus || undefined)
      setCalendar(data)
    } catch { toast.error('Failed to generate calendar') }
    finally { setLoading(false) }
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-2">Content Calendar</h1>
      <p className="text-slate-400 mb-6">Priya (CMO) plans your week — what to post, when, and why</p>

      <div className="flex gap-3 mb-6">
        <input value={focus} onChange={e => setFocus(e.target.value)}
          placeholder="Optional focus (e.g., SatyaDocAI for BFSI, government tenders)"
          className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500" />
        <button onClick={generate} disabled={loading}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-5 py-2.5 rounded-lg font-medium text-sm transition-colors">
          {loading ? <Loader2 size={15} className="animate-spin" /> : <RefreshCw size={15} />}
          Generate Week
        </button>
      </div>

      {!calendar && !loading && (
        <div className="text-center py-16 text-slate-500 bg-slate-900 border border-slate-800 rounded-xl">
          <Calendar size={40} className="mx-auto mb-3 opacity-30" />
          <p>Click "Generate Week" to plan your content calendar</p>
        </div>
      )}

      {loading && (
        <div className="text-center py-16 text-slate-500">
          <Loader2 size={32} className="animate-spin mx-auto mb-3 text-blue-400" />
          <p>Priya is planning your week...</p>
        </div>
      )}

      {calendar && (
        <div className="space-y-4">
          <div className="bg-blue-600/10 border border-blue-500/30 rounded-xl p-4">
            <div className="font-semibold text-white">{calendar.week_theme}</div>
            {calendar.cmo_notes && <div className="text-slate-400 text-sm mt-1">{calendar.cmo_notes}</div>}
          </div>

          <div className="space-y-3">
            {calendar.days?.map((day: any, i: number) => (
              <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                <div className="bg-slate-800 px-5 py-3 flex items-center justify-between">
                  <span className="font-semibold text-white">{day.day}</span>
                  <span className="text-slate-500 text-sm">{day.date}</span>
                </div>
                <div className="p-5 grid grid-cols-3 gap-4">
                  {/* LinkedIn */}
                  <div>
                    <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${platformColors.linkedin}`}>LinkedIn</span>
                    <div className="mt-2 text-sm font-medium text-white">{day.linkedin?.title}</div>
                    <div className="text-xs text-slate-500 mt-1 capitalize">{day.linkedin?.content_type?.replace('_', ' ')}</div>
                    {day.linkedin?.product_featured && day.linkedin.product_featured !== 'none' && (
                      <div className="text-xs text-blue-400 mt-1">{day.linkedin.product_featured}</div>
                    )}
                    <div className="text-xs text-slate-400 mt-1">{day.linkedin?.angle}</div>
                    {day.linkedin?.cta && <div className="text-xs text-green-400 mt-1 italic">{day.linkedin.cta}</div>}
                  </div>

                  {/* Instagram */}
                  <div>
                    <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${platformColors.instagram}`}>Instagram</span>
                    <div className="mt-2 text-sm text-slate-300">{day.instagram?.caption_angle}</div>
                    <div className="text-xs text-slate-500 mt-1 capitalize">{day.instagram?.content_type}</div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {day.instagram?.hashtags?.slice(0, 4).map((h: string) => (
                        <span key={h} className="text-xs text-pink-400/70">{h}</span>
                      ))}
                    </div>
                  </div>

                  {/* Email */}
                  <div>
                    <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${platformColors.email}`}>Email</span>
                    <div className="mt-2 text-sm font-medium text-white">{day.email_idea?.subject_line}</div>
                    <div className="text-xs text-slate-500 mt-1 capitalize">{day.email_idea?.target_domain}</div>
                    <div className="text-xs text-slate-400 mt-1">{day.email_idea?.angle}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {calendar.weekly_thought_leadership_topic && (
            <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-4">
              <div className="text-xs text-purple-400 font-medium mb-1">This Week's Thought Leadership Article</div>
              <div className="text-white font-semibold">{calendar.weekly_thought_leadership_topic}</div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
