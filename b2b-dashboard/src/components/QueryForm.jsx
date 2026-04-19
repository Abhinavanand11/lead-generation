// src/components/QueryForm.jsx
import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { MapPin, Linkedin, Play, Loader2, ChevronDown, Plus, X } from 'lucide-react'

const EXAMPLE_QUERIES = [
  'restaurants in Connaught Place Delhi',
  'gyms in Hauz Khas Delhi',
  'dental clinics in South Delhi',
]

const EXAMPLE_LINKEDIN = [
  { keywords: 'Founder', location: 'Mumbai', max_results: 25 },
  { keywords: 'CTO', location: 'Bangalore', max_results: 25 },
]

export default function QueryForm({ onScrape, isLoading }) {
  const [gmQueries, setGmQueries] = useState(EXAMPLE_QUERIES.join('\n'))
  const [linkedinSearches, setLinkedinSearches] = useState(EXAMPLE_LINKEDIN)
  const [showLinkedin, setShowLinkedin] = useState(false)
  const [includePreview, setIncludePreview] = useState(true)

  function handleAddLinkedin() {
    setLinkedinSearches(prev => [...prev, { keywords: '', location: '', max_results: 25 }])
  }

  function handleRemoveLinkedin(idx) {
    setLinkedinSearches(prev => prev.filter((_, i) => i !== idx))
  }

  function handleLinkedinChange(idx, field, val) {
    setLinkedinSearches(prev =>
      prev.map((s, i) => i === idx ? { ...s, [field]: val } : s)
    )
  }

  function handleSubmit(e) {
    e.preventDefault()
    const queries = gmQueries.split('\n').map(q => q.trim()).filter(Boolean)
    const validLinkedin = linkedinSearches.filter(s => s.keywords || s.location)
    onScrape({ queries, linkedinSearches: validLinkedin, includeLeadsPreview: includePreview })
  }

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 overflow-hidden w-full">
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-800 flex items-center gap-3">
        <div className="w-7 h-7 bg-amber-500 rounded-md flex items-center justify-center flex-shrink-0">
          <Play size={13} className="text-black" strokeWidth={2.5} />
        </div>
        <div>
          <h2 className="text-sm font-semibold text-white">Configure Scrape</h2>
          <p className="text-xs text-slate-400 mt-0.5">Define your lead generation queries</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-5 space-y-5">
        {/* Google Maps */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <MapPin size={13} className="text-amber-400 flex-shrink-0" />
            <label className="text-xs font-mono text-slate-400 uppercase tracking-widest">
              Google Maps Queries
            </label>
          </div>
          <textarea
            value={gmQueries}
            onChange={e => setGmQueries(e.target.value)}
            rows={4}
            placeholder={`gyms in Delhi\nrestaurants in Mumbai\ndental clinics in Bangalore`}
            className="w-full bg-slate-950 border border-slate-700 rounded-md px-3 py-2.5
              text-sm text-slate-200 placeholder-slate-600 font-mono leading-relaxed
              focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500/30
              transition-colors duration-150 resize-y"
          />
          <p className="text-xs text-slate-500 font-mono">One query per line</p>
        </div>

        {/* LinkedIn (collapsible) */}
        <div className="space-y-2">
          <button
            type="button"
            onClick={() => setShowLinkedin(v => !v)}
            className="flex items-center gap-2 w-full text-left py-1 hover:opacity-80 transition-opacity"
          >
            <Linkedin size={13} className="text-blue-400 flex-shrink-0" />
            <span className="text-xs font-mono text-slate-400 uppercase tracking-widest flex-1">
              LinkedIn Searches
            </span>
            <ChevronDown
              size={13}
              className={`text-slate-500 transition-transform duration-200 ${showLinkedin ? 'rotate-180' : ''}`}
            />
          </button>

          <AnimatePresence>
            {showLinkedin && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden space-y-2"
              >
                {linkedinSearches.map((s, idx) => (
                  <div key={idx} className="flex gap-2 items-center">
                    <input
                      type="text"
                      placeholder="Keywords (e.g. CTO)"
                      value={s.keywords}
                      onChange={e => handleLinkedinChange(idx, 'keywords', e.target.value)}
                      className="flex-1 bg-slate-950 border border-slate-700 rounded-md px-3 py-2
                        text-sm text-slate-200 placeholder-slate-600
                        focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20
                        transition-colors duration-150"
                    />
                    <input
                      type="text"
                      placeholder="Location"
                      value={s.location}
                      onChange={e => handleLinkedinChange(idx, 'location', e.target.value)}
                      className="flex-1 bg-slate-950 border border-slate-700 rounded-md px-3 py-2
                        text-sm text-slate-200 placeholder-slate-600
                        focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20
                        transition-colors duration-150"
                    />
                    <input
                      type="number"
                      placeholder="Max"
                      value={s.max_results}
                      onChange={e => handleLinkedinChange(idx, 'max_results', parseInt(e.target.value) || 25)}
                      className="w-16 bg-slate-950 border border-slate-700 rounded-md px-2 py-2
                        text-sm text-slate-200 placeholder-slate-600
                        focus:outline-none focus:border-blue-500 transition-colors duration-150"
                    />
                    <button
                      type="button"
                      onClick={() => handleRemoveLinkedin(idx)}
                      className="w-8 h-8 flex items-center justify-center rounded-md text-slate-500
                        hover:text-red-400 hover:bg-red-950 transition-all border border-slate-700"
                    >
                      <X size={13} />
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={handleAddLinkedin}
                  className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-blue-400
                    transition-colors py-1"
                >
                  <Plus size={12} /> Add search
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Toggle */}
        <label className="flex items-center gap-3 cursor-pointer">
          <button
            type="button"
            onClick={() => setIncludePreview(v => !v)}
            className={`w-9 h-5 rounded-full relative transition-colors duration-200 flex-shrink-0
              ${includePreview ? 'bg-amber-500' : 'bg-slate-700'}`}
          >
            <span className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all duration-200
              ${includePreview ? 'left-4' : 'left-0.5'}`}
            />
          </button>
          <span className="text-sm text-slate-400">Include leads preview in response</span>
        </label>

        {/* Submit */}
        <button
          type="submit"
          disabled={isLoading}
          className={`w-full py-3 rounded-md font-semibold text-sm flex items-center justify-center gap-2
            transition-all duration-150
            ${isLoading
              ? 'bg-amber-500/40 text-black/50 cursor-not-allowed'
              : 'bg-amber-500 hover:bg-amber-400 text-black active:scale-[0.99]'
            }`}
        >
          {isLoading ? (
            <>
              <Loader2 size={15} className="animate-spin" />
              Running pipeline…
            </>
          ) : (
            <>
              <Play size={14} strokeWidth={2.5} />
              Launch Scrape
            </>
          )}
        </button>
      </form>
    </div>
  )
}