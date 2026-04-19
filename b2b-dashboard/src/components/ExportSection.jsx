// src/components/ExportSection.jsx
import { useState } from 'react'
import { CheckCircle2, Download, Loader2, FileSpreadsheet, AlertCircle } from 'lucide-react'
import { downloadFile } from '../services/api'

export default function ExportSection({ result, hasRun }) {
  const [status, setStatus] = useState('idle') // idle | loading | success | error
  const [errorMsg, setErrorMsg] = useState('')

  async function handleDownload() {
    if (status === 'loading') return
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
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
      <div className="flex items-center gap-2 mb-4">
        <FileSpreadsheet size={15} className="text-slate-400" />
        <h2 className="text-sm font-semibold text-white">Export</h2>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        {/* Pipeline status */}
        {result ? (
          <div className="flex items-start gap-3 p-3 rounded-md border border-emerald-800/60 bg-emerald-950/40 flex-1">
            <CheckCircle2 size={15} className="text-emerald-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm text-emerald-300 font-medium">Pipeline completed</p>
              <p className="text-xs text-emerald-600 mt-0.5 font-mono">{result.output_file}</p>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-slate-500 text-sm">
            <span className="w-2 h-2 rounded-full bg-slate-700 inline-block" />
            No pipeline run yet
          </div>
        )}

        {/* Download button */}
        <div className="flex flex-col items-end gap-1 flex-shrink-0">
          <button
            onClick={handleDownload}
            disabled={!hasRun || status === 'loading'}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-md text-sm font-medium
              transition-all duration-150 border
              ${!hasRun
                ? 'border-slate-700 text-slate-600 cursor-not-allowed bg-transparent'
                : status === 'success'
                ? 'border-emerald-700 text-emerald-400 bg-emerald-950/40'
                : status === 'error'
                ? 'border-red-700 text-red-400 bg-red-950/40'
                : 'border-amber-600 bg-amber-500 hover:bg-amber-400 text-black active:scale-[0.98]'
              }`}
          >
            {status === 'loading' && <Loader2 size={14} className="animate-spin" />}
            {status === 'success' && <CheckCircle2 size={14} />}
            {(status === 'idle' || status === 'error') && <Download size={14} />}
            <span>
              {status === 'loading' ? 'Downloading…'
                : status === 'success' ? 'Downloaded!'
                : status === 'error' ? 'Failed — retry'
                : 'Download Excel'}
            </span>
          </button>
          {!hasRun && (
            <p className="text-xs text-slate-600 font-mono">Run a scrape first</p>
          )}
          {status === 'error' && errorMsg && (
            <p className="text-xs text-red-500 font-mono mt-1">{errorMsg}</p>
          )}
        </div>
      </div>
    </div>
  )
}