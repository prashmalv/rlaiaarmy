import { useState } from 'react'
import { Wand2, Loader2, Copy, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { generateApi } from '../services/api'

const PRODUCTS = ['LOVAIC', 'SatyaDocAI', 'SalesBuddy', 'EvalBuddy', 'VoiceBuddy', 'AI Avatar L&D']
const PLATFORMS = ['linkedin', 'instagram', 'facebook']
const LI_TYPES = ['thought_leadership', 'product_spotlight', 'case_study', 'news_commentary', 'tip_or_insight']
const IG_TYPES = ['carousel', 'quote_card', 'infographic', 'reel_script']
const INDUSTRIES = ['banking', 'healthcare', 'insurance', 'manufacturing', 'government', 'retail', 'hr', 'education']

export function GeneratePage() {
  const [platform, setPlatform] = useState('linkedin')
  const [contentType, setContentType] = useState('thought_leadership')
  const [product, setProduct] = useState('')
  const [topic, setTopic] = useState('')
  const [industry, setIndustry] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [copied, setCopied] = useState(false)

  const generate = async () => {
    setLoading(true); setResult(null)
    try {
      const r = await generateApi.content({ platform, content_type: contentType, product: product || undefined, topic: topic || undefined, industry: industry || undefined })
      setResult(r)
    } catch { toast.error('Generation failed') }
    finally { setLoading(false) }
  }

  const copy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    toast.success('Copied!')
  }

  const types = platform === 'instagram' ? IG_TYPES : LI_TYPES

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-2">Generate Content</h1>
      <p className="text-slate-400 mb-6">Arjun (Content) creates on-demand posts for any platform</p>

      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Platform */}
        <div>
          <label className="text-xs text-slate-400 font-medium block mb-2">Platform</label>
          <div className="flex gap-2">
            {PLATFORMS.map(p => (
              <button key={p} onClick={() => { setPlatform(p); setContentType(p === 'instagram' ? 'carousel' : 'thought_leadership') }}
                className={`flex-1 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${platform === p ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400'}`}>
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Content Type */}
        <div>
          <label className="text-xs text-slate-400 font-medium block mb-2">Content Type</label>
          <select value={contentType} onChange={e => setContentType(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
            {types.map(t => <option key={t} value={t} className="capitalize">{t.replace(/_/g, ' ')}</option>)}
          </select>
        </div>

        {/* Product */}
        <div>
          <label className="text-xs text-slate-400 font-medium block mb-2">Product Focus (optional)</label>
          <select value={product} onChange={e => setProduct(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
            <option value="">General RLAI Brand</option>
            {PRODUCTS.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>

        {/* Industry */}
        <div>
          <label className="text-xs text-slate-400 font-medium block mb-2">Target Industry (optional)</label>
          <select value={industry} onChange={e => setIndustry(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
            <option value="">All Industries</option>
            {INDUSTRIES.map(i => <option key={i} value={i} className="capitalize">{i}</option>)}
          </select>
        </div>

        {/* Topic */}
        <div className="col-span-2">
          <label className="text-xs text-slate-400 font-medium block mb-2">Specific Topic / Angle (optional)</label>
          <input value={topic} onChange={e => setTopic(e.target.value)}
            placeholder="e.g., Why pixel-level CV catches what generic AI misses in quality control"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500" />
        </div>
      </div>

      <button onClick={generate} disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-colors mb-6">
        {loading ? <><Loader2 size={18} className="animate-spin" /> Arjun is writing...</> : <><Wand2 size={18} /> Generate Content</>}
      </button>

      {result && (
        <div className="space-y-4">
          {/* Main content */}
          {(result.post_text || result.caption || result.article_body) && (
            <div className="bg-slate-900 border border-slate-700 rounded-xl p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-white capitalize">{platform} Post</h3>
                <button onClick={() => copy(result.post_text || result.caption || result.article_body)}
                  className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors">
                  {copied ? <CheckCircle size={13} className="text-green-400" /> : <Copy size={13} />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <pre className="text-slate-300 text-sm whitespace-pre-wrap font-sans leading-relaxed">
                {result.post_text || result.caption || result.article_body}
              </pre>
              {result.hashtags?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-slate-800">
                  {result.hashtags.map((h: string) => (
                    <span key={h} className="text-xs text-blue-400/80 bg-blue-500/10 px-2 py-0.5 rounded">{h}</span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-3">
            {result.hook && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                <div className="text-xs text-slate-500 font-medium mb-1">Hook</div>
                <div className="text-sm text-white">{result.hook}</div>
              </div>
            )}
            {result.best_posting_time && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                <div className="text-xs text-slate-500 font-medium mb-1">Best Time to Post</div>
                <div className="text-sm text-white">{result.best_posting_time}</div>
              </div>
            )}
            {result.image_prompt && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 col-span-2">
                <div className="text-xs text-slate-500 font-medium mb-1">Image Prompt (for DALL-E / Midjourney)</div>
                <div className="text-sm text-slate-300 font-mono">{result.image_prompt}</div>
              </div>
            )}
          </div>

          {/* Carousel slides */}
          {result.carousel_slides?.length > 0 && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h3 className="font-semibold text-white mb-3">Carousel Slides</h3>
              <div className="space-y-3">
                {result.carousel_slides.map((s: any) => (
                  <div key={s.slide_number} className="bg-slate-800 rounded-lg p-3">
                    <div className="text-xs text-slate-500 mb-1">Slide {s.slide_number}</div>
                    <div className="font-medium text-white text-sm">{s.headline}</div>
                    <div className="text-slate-400 text-sm mt-1">{s.body}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
