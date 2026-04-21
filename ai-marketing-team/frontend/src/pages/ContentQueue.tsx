import { useEffect, useState } from 'react'
import { CheckCircle, Send, Clock, RefreshCw, Linkedin, Instagram, Facebook } from 'lucide-react'
import toast from 'react-hot-toast'
import { postsApi } from '../services/api'

const platformIcon = (p: string) => {
  if (p === 'linkedin') return <Linkedin size={14} className="text-blue-400" />
  if (p === 'instagram') return <Instagram size={14} className="text-pink-400" />
  return <Facebook size={14} className="text-blue-600" />
}

const statusConfig: Record<string, { label: string; color: string }> = {
  draft: { label: 'Draft', color: 'bg-slate-700 text-slate-300' },
  queued_for_approval: { label: 'Pending', color: 'bg-yellow-500/20 text-yellow-400' },
  approved: { label: 'Approved', color: 'bg-green-500/20 text-green-400' },
  posted: { label: 'Posted', color: 'bg-blue-500/20 text-blue-400' },
  dry_run: { label: 'Queued', color: 'bg-yellow-500/20 text-yellow-400' },
}

export function ContentQueue() {
  const [posts, setPosts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<string | null>(null)
  const [filter, setFilter] = useState('all')

  const load = () => { setLoading(true); postsApi.getAll().then(setPosts).finally(() => setLoading(false)) }
  useEffect(() => { load() }, [])

  const approve = async (id: string) => {
    await postsApi.approve(id)
    toast.success('Approved!')
    load()
  }

  const publish = async (id: string) => {
    const r = await postsApi.publish(id)
    toast[r.status === 'posted' || r.status === 'dry_run' ? 'success' : 'error'](
      r.status === 'posted' ? 'Published!' : r.message || 'Check social credentials'
    )
    load()
  }

  const filtered = filter === 'all' ? posts : posts.filter(p => p.platform === filter || p.status === filter)

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Content Queue</h1>
          <p className="text-slate-400 text-sm mt-1">{posts.length} posts · Review and publish to social media</p>
        </div>
        <button onClick={load} className="p-2 text-slate-400 hover:text-white transition-colors">
          <RefreshCw size={16} />
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {['all', 'linkedin', 'instagram', 'facebook', 'draft', 'approved', 'posted'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors capitalize ${
              filter === f ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}>{f}</button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-16 text-slate-500">Loading posts...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 text-slate-500">
          <Clock size={32} className="mx-auto mb-3 opacity-30" />
          <p>No posts yet. Run the daily workflow to generate content.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((post: any) => {
            const sc = statusConfig[post.status] || statusConfig.draft
            const isOpen = expanded === post.id
            return (
              <div key={post.id} className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                <div className="p-4 flex items-start gap-3">
                  <div className="mt-0.5">{platformIcon(post.platform)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs text-slate-500 capitalize">{post.platform}</span>
                      <span className="text-slate-700">·</span>
                      <span className="text-xs text-slate-500 capitalize">{post.content_type?.replace('_', ' ')}</span>
                      <span className={`ml-auto text-xs px-2 py-0.5 rounded-full ${sc.color}`}>{sc.label}</span>
                    </div>
                    <p className="text-slate-300 text-sm line-clamp-2">{post.title || post.body?.slice(0, 120)}</p>
                    {post.hashtags?.length > 0 && (
                      <div className="flex gap-1 flex-wrap mt-2">
                        {post.hashtags.slice(0, 4).map((h: string) => (
                          <span key={h} className="text-xs text-blue-400/70 bg-blue-500/10 px-2 py-0.5 rounded">{h}</span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Expand */}
                <div className="px-4 pb-3 flex items-center gap-2">
                  <button onClick={() => setExpanded(isOpen ? null : post.id)}
                    className="text-xs text-slate-500 hover:text-slate-300 transition-colors">
                    {isOpen ? '▲ Collapse' : '▼ View full post'}
                  </button>
                  <div className="flex-1" />
                  {['draft', 'queued_for_approval', 'dry_run'].includes(post.status) && (
                    <button onClick={() => approve(post.id)}
                      className="flex items-center gap-1.5 bg-green-600/20 hover:bg-green-600/30 text-green-400 border border-green-500/30 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors">
                      <CheckCircle size={12} /> Approve
                    </button>
                  )}
                  {post.status === 'approved' && (
                    <button onClick={() => publish(post.id)}
                      className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors">
                      <Send size={12} /> Publish Now
                    </button>
                  )}
                </div>

                {isOpen && (
                  <div className="px-4 pb-4 border-t border-slate-800 pt-3">
                    <pre className="text-sm text-slate-300 whitespace-pre-wrap font-sans leading-relaxed">{post.body}</pre>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
