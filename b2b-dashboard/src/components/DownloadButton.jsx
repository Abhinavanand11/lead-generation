// src/components/DownloadButton.jsx
import { useState } from 'react'
import { motion } from 'framer-motion'
import { Download, Loader2, FileSpreadsheet, CheckCircle } from 'lucide-react'
import { downloadFile } from '../services/api'

export default function DownloadButton({ disabled }) {
  const [status, setStatus] = useState('idle') // idle | loading | success | error
  const [errorMsg, setErrorMsg] = useState('')

  async function handleDownload() {
    if (disabled || status === 'loading') return
    setStatus('loading')
    setErrorMsg('')
    try {
      await downloadFile()
      setStatus('success')
      setTimeout(() => setStatus('idle'), 3000)
    } catch (err) {
      setStatus('error')
      setErrorMsg(err.message)
      setTimeout(() => setStatus('idle'), 4000)
    }
  }

  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.35, duration: 0.5 }}
      className="glass-card border border-white/5 rounded-2xl p-5"
    >
      <div className="flex items-center gap-3 mb-4">
        <FileSpreadsheet size={15} className="text-emerald-400" />
        <p className="text-xs font-mono text-emerald-400/80 uppercase tracking-widest">
          Export
        </p>
      </div>

      <button
        onClick={handleDownload}
        disabled={disabled || status === 'loading'}
        className={`w-full py-3 rounded-xl text-sm font-medium flex items-center justify-center gap-2.5
          border transition-all duration-300
          ${disabled
            ? 'border-white/5 text-slate-600 cursor-not-allowed bg-transparent'
            : status === 'success'
            ? 'border-emerald-400/40 text-emerald-400 bg-emerald-400/10'
            : status === 'error'
            ? 'border-red-400/40 text-red-400 bg-red-400/10'
            : 'border-white/10 text-slate-300 hover:border-emerald-400/40 hover:text-emerald-400 hover:bg-emerald-400/5'
          }`}
      >
        {status === 'loading' && <Loader2 size={15} className="animate-spin" />}
        {status === 'success' && <CheckCircle size={15} />}
        {status === 'idle' && <Download size={15} />}
        {status === 'error' && <Download size={15} />}
        <span>
          {status === 'loading' ? 'Downloading…'
            : status === 'success' ? 'Downloaded!'
            : status === 'error' ? 'Download failed'
            : 'Download Excel'}
        </span>
      </button>

      {status === 'error' && errorMsg && (
        <p className="text-xs text-red-400/70 mt-2 font-mono leading-relaxed">{errorMsg}</p>
      )}

      {disabled && (
        <p className="text-xs text-slate-600 mt-2 text-center font-mono">
          Run a scrape first
        </p>
      )}
    </motion.div>
  )
}
