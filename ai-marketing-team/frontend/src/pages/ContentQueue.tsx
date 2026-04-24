import { useEffect, useState } from 'react'
import { CheckCircle, Send, Clock, RefreshCw, Zap, Image, ExternalLink, Download } from 'lucide-react'
import toast from 'react-hot-toast'
import { postsApi } from '../services/api'
import { exportPosts } from '../utils/export'

const platformDot = (p: string) => {
  const bg: Record<string, string> = {
    linkedin: 'bg-blue-500',
    instagram: 'bg-pink-500',
    facebook: 'bg-blue-700',
  }
  const label: Record<string, string> = { linkedin: 'in', instagram: 'ig', facebook: 'fb' }
  return (
    <span className={`inline-flex items-center justify-center w-5 h-5 rounded text-white text-[9px] font-bold ${bg[p] || 'bg-slate-600'}`}>
      {label[p] || p[0]?.toUpperCase()}
    </span>
  )
}

const statusConfig: Record<string, { label: string; color: string }> = {
  draft: { label: 'Draft', color: 'bg-slate-700 text-slate-300' },
  queued_for_approval: { label: 'Pending', color: 'bg-yellow-500/20 text-yellow-400' },
  approved: { label: 'Approved', color: 'bg-green-500/20 text-green-400' },
  posted: { label: 'Posted', color: 'bg-blue-500/20 text-blue-400' },
  dry_run: { label: 'Queued (no creds)', color: 'bg-yellow-500/20 text-yellow-400' },
}

export function ContentQueue() {
  const [posts, setPosts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<string | null>(null)
  const [filter, setFilter] = useState('all')
  const [imageUrls, setImageUrls] = useState<Record<string, string>>({})
  const [posting, setPosting] = useState<string | null>(null)

  const load = () => {
    setLoading(true)
    postsApi.getAll().then(setPosts).finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [])

  const approve = async (id: string) => {
    await postsApi.approve(id)
    toast.success('Approved!')
    load()
  }

  const publish = async (id: string) => {
    setPosting(id)
    try {
      const r = await postsApi.publish(id)
      toast[r.status === 'posted' || r.status === 'dry_run' ? 'success' : 'error'](
        r.status === 'posted' ? 'Published!' :
        r.status === 'dry_run' ? 'Queued (add social credentials to post live)' :
        r.message || 'Check social credentials'
      )
      load()
    } finally { setPosting(null) }
  }

  const postLive = async (id: string) => {
    setPosting(id)
    try {
      const imageUrl = imageUrls[id] || undefined
      const r = await postsApi.postLive(id, imageUrl)
      if (r.status === 'posted') {
        toast.success('Posted live!')
        if (r.image_url) toast.success('Image attached!')
      } else if (r.status === 'dry_run') {
        toast('Queued — add social media credentials in .env to post live', { icon: '🔑' })
      } else {
        toast.error(r.message || r.detail || 'Posting failed')
      }
      load()
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to post')
    } finally { setPosting(null) }
  }

  const filtered = filter === 'all' ? posts : posts.filter(p => p.platform === filter || p.status === filter)

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Content Queue</h1>
          <p className="text-slate-400 text-sm mt-1">{posts.length} posts · Review and publish to social media</p>
        </div>
        <div className="flex gap-2 items-center">
          <div className="flex gap-1 bg-slate-800 border border-slate-700 rounded-lg p-1">
            {(['csv','json','md'] as const).map(fmt => (
              <button key={fmt} onClick={() => exportPosts(posts, fmt)}
                className="flex items-center gap-1 text-slate-400 hover:text-white px-2 py-1 rounded text-xs transition-colors">
                <Download size={11} /> .{fmt}
              </button>
            ))}
          </div>
          <button onClick={load} className="p-2 text-slate-400 hover:text-white transition-colors">
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {/* Credentials hint */}
      <div className="mb-4 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-xs text-slate-400 flex items-center gap-2">
        <span className="text-yellow-400">💡</span>
        To post live: add <code className="bg-slate-800 px-1 rounded">LINKEDIN_ACCESS_TOKEN</code>, <code className="bg-slate-800 px-1 rounded">FACEBOOK_PAGE_ACCESS_TOKEN</code>, or <code className="bg-slate-800 px-1 rounded">PEXELS_API_KEY</code> in <code className="bg-slate-800 px-1 rounded">ai-marketing-team/backend/.env</code>
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
          <p>No posts yet. Use the Content Calendar to generate posts.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((post: any) => {
            const sc = statusConfig[post.status] || statusConfig.draft
            const isOpen = expanded === post.id
            const isPosting = posting === post.id
            return (
              <div key={post.id} className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                <div className="p-4 flex items-start gap-3">
                  <div className="mt-0.5">{platformDot(post.platform)}</div>
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

                {/* Expanded view */}
                {isOpen && (
                  <div className="px-4 pb-4 border-t border-slate-800 pt-3 space-y-3">
                    <pre className="text-sm text-slate-300 whitespace-pre-wrap font-sans leading-relaxed">{post.body}</pre>

                    {/* Image section */}
                    {post.image_url ? (
                      <div className="rounded-lg overflow-hidden border border-slate-700">
                        <img src={post.image_url} alt="Post image" className="w-full max-h-64 object-cover" />
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800">
                          <Image size={12} className="text-slate-500" />
                          <a href={post.image_url} target="_blank" rel="noreferrer" className="text-xs text-blue-400 hover:underline truncate flex items-center gap-1">
                            View image <ExternalLink size={10} />
                          </a>
                        </div>
                      </div>
                    ) : post.image_prompt ? (
                      <div className="bg-slate-800 border border-slate-700 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-1">
                          <Image size={12} className="text-slate-500" />
                          <span className="text-xs text-slate-400 font-medium">Image Prompt (AI-generated suggestion)</span>
                        </div>
                        <p className="text-xs text-slate-500 italic">{post.image_prompt}</p>
                      </div>
                    ) : null}

                    {/* Custom image URL input */}
                    {post.status !== 'posted' && (
                      <div>
                        <label className="text-xs text-slate-500 block mb-1">Optional: Provide image URL to attach when posting</label>
                        <input
                          type="url"
                          placeholder="https://your-image-url.jpg  (or leave blank)"
                          value={imageUrls[post.id] || ''}
                          onChange={e => setImageUrls(prev => ({ ...prev, [post.id]: e.target.value }))}
                          className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500"
                        />
                      </div>
                    )}
                  </div>
                )}

                {/* Actions */}
                <div className="px-4 pb-3 flex items-center gap-2">
                  <button onClick={() => setExpanded(isOpen ? null : post.id)}
                    className="text-xs text-slate-500 hover:text-slate-300 transition-colors">
                    {isOpen ? '▲ Collapse' : '▼ View full post'}
                  </button>
                  <div className="flex-1" />

                  {/* Approve */}
                  {['draft', 'queued_for_approval', 'dry_run'].includes(post.status) && (
                    <button onClick={() => approve(post.id)} disabled={isPosting}
                      className="flex items-center gap-1.5 bg-green-600/20 hover:bg-green-600/30 text-green-400 border border-green-500/30 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors disabled:opacity-50">
                      <CheckCircle size={12} /> Approve
                    </button>
                  )}

                  {/* Publish Now (approved → post) */}
                  {post.status === 'approved' && (
                    <button onClick={() => publish(post.id)} disabled={isPosting}
                      className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors disabled:opacity-50">
                      <Send size={12} /> {isPosting ? 'Posting...' : 'Publish Now'}
                    </button>
                  )}

                  {/* Post This Live — bypass approval */}
                  {post.status !== 'posted' && (
                    <button onClick={() => postLive(post.id)} disabled={isPosting}
                      className="flex items-center gap-1.5 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-3 py-1.5 rounded-lg text-xs font-semibold transition-all disabled:opacity-50 shadow-lg shadow-purple-900/30">
                      <Zap size={12} /> {isPosting ? 'Posting...' : 'Post This Live'}
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
