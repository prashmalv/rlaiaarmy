import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Zap, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'

export function NewProject() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [requirements, setRequirements] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState<'text' | 'file'>('text')

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) setFile(accepted[0])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv'],
      'text/plain': ['.txt'],
    },
    multiple: false,
  })

  const handleSubmit = async () => {
    if (!name.trim()) { toast.error('Project name required'); return }
    if (mode === 'text' && !requirements.trim()) { toast.error('Requirements required'); return }
    if (mode === 'file' && !file) { toast.error('Please upload a file'); return }

    setLoading(true)
    try {
      let response
      if (mode === 'file' && file) {
        const fd = new FormData()
        fd.append('name', name)
        fd.append('file', file)
        response = await axios.post('/api/projects/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      } else {
        response = await axios.post('/api/projects', { name, requirements })
      }
      toast.success('AI Dev Team started!')
      navigate(`/projects/${response.data.project_id}`)
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to start project')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-2">New Project</h1>
      <p className="text-slate-400 mb-8">Provide your requirements and the AI Dev Team will handle everything.</p>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Project Name</label>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="e.g., E-Commerce Platform, HR Management System"
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        <div>
          <div className="flex gap-3 mb-4">
            <button onClick={() => setMode('text')} className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${mode === 'text' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'}`}>
              <FileText size={14} className="inline mr-2" />Type Requirements
            </button>
            <button onClick={() => setMode('file')} className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${mode === 'file' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'}`}>
              <Upload size={14} className="inline mr-2" />Upload File (Excel/CSV)
            </button>
          </div>

          {mode === 'text' ? (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Requirements</label>
              <textarea
                value={requirements}
                onChange={e => setRequirements(e.target.value)}
                placeholder={`Describe what you want to build. Be as detailed as possible.\n\nExample:\nBuild a project management tool where users can:\n- Create projects and invite team members\n- Create tasks with due dates, priorities, and assignees\n- Track time spent on tasks\n- Generate weekly reports\n- Admin can manage users and billing\n- Support dark mode\n- Mobile responsive`}
                rows={14}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors font-mono text-sm resize-none"
              />
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Upload Requirements File</label>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${isDragActive ? 'border-blue-500 bg-blue-500/10' : 'border-slate-700 hover:border-slate-500 bg-slate-900'}`}
              >
                <input {...getInputProps()} />
                <Upload className="mx-auto mb-3 text-slate-500" size={32} />
                {file ? (
                  <div>
                    <p className="text-white font-medium">{file.name}</p>
                    <p className="text-slate-400 text-sm mt-1">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                ) : (
                  <div>
                    <p className="text-slate-400">Drop Excel, CSV, or TXT file here</p>
                    <p className="text-slate-600 text-sm mt-1">or click to browse</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex gap-3">
          <AlertCircle size={16} className="text-blue-400 mt-0.5 shrink-0" />
          <div className="text-sm text-slate-400">
            <strong className="text-slate-300">What happens next:</strong> BA Agent analyses your requirements → Architect designs system → Engineers code in parallel → Security & Performance tests run → Report generated → Email sent for production approval.
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3.5 rounded-lg font-semibold flex items-center justify-center gap-2 transition-colors"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Starting AI Dev Team...
            </>
          ) : (
            <>
              <Zap size={18} />
              Launch AI Dev Team
            </>
          )}
        </button>
      </div>
    </div>
  )
}
