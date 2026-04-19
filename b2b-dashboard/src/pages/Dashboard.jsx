// src/pages/Dashboard.jsx
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Users, MapPin, Linkedin, Filter, AlertCircle } from 'lucide-react'

import Sidebar from '../components/Sidebar'
import QueryForm from '../components/QueryForm'
import StatsCard from '../components/StatsCard'
import LeadTable from '../components/LeadTable'
import ExportSection from '../components/ExportSection'
import { scrapeLeads, checkHealth } from '../services/api'

export default function Dashboard() {
  const [healthStatus, setHealthStatus] = useState('checking')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [hasRun, setHasRun] = useState(false)

  useEffect(() => {
    checkHealth()
      .then(() => setHealthStatus('ok'))
      .catch(() => setHealthStatus('error'))
  }, [])

  async function handleScrape(params) {
    setIsLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await scrapeLeads(params)
      setResult(data)
      setHasRun(true)
    } catch (err) {
      setError(err.message || 'Pipeline failed. Check your APIFY_API_TOKEN and server logs.')
    } finally {
      setIsLoading(false)
    }
  }

  const stats = result?.stats

  return (
    <div className="flex min-h-screen" style={{ background: '#020617' }}>
      <Sidebar healthStatus={healthStatus} />

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto px-6 py-8 space-y-6">

          {/* Page header */}
          <div className="border-b border-slate-800 pb-6">
            <p className="text-xs font-mono text-amber-400 uppercase tracking-widest mb-1">
              B2B Intelligence Platform
            </p>
            <h1 className="text-2xl font-semibold text-white">
              Lead Generation Dashboard
            </h1>
            <p className="text-slate-400 mt-1 text-sm">
              Scrape Google Maps &amp; LinkedIn, validate, deduplicate, and export to Excel.
            </p>
          </div>

          {/* Stats row — shown after result */}
          <AnimatePresence>
            {result && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="grid grid-cols-2 lg:grid-cols-4 gap-4"
              >
                <StatsCard label="Total Leads"         value={result.total_leads}          icon={Users}    accent delay={0} />
                <StatsCard label="Google Maps"         value={stats?.google_maps_raw ?? '—'} sub={`${stats?.valid ?? '—'} passed validation`}    icon={MapPin}   delay={0.05} />
                <StatsCard label="LinkedIn"            value={stats?.linkedin_raw ?? '—'}  sub={`${stats?.parsed ?? '—'} parsed total`}           icon={Linkedin} delay={0.1} />
                <StatsCard label="Duplicates Removed"  value={stats?.duplicates_removed ?? '—'} sub={`${stats?.rejected ?? '—'} rejected`}       icon={Filter}   delay={0.15} />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error banner */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex items-start gap-3 p-4 rounded-lg border border-red-800 bg-red-950/60"
              >
                <AlertCircle size={16} className="text-red-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm text-red-300 font-medium">Pipeline failed</p>
                  <p className="text-xs text-red-400/80 mt-0.5 font-mono">{error}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* 1. Configure Scrape — full width */}
          <QueryForm onScrape={handleScrape} isLoading={isLoading} />

          {/* 2. Export Section — shown after run */}
          <AnimatePresence>
            {(hasRun || result) && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                <ExportSection result={result} hasRun={hasRun} />
              </motion.div>
            )}
          </AnimatePresence>

          {/* 3. Leads Table — full width */}
          {isLoading ? (
            <LoadingState />
          ) : (
            <LeadTable leads={result?.leads || []} />
          )}

        </div>
      </main>
    </div>
  )
}

function LoadingState() {
  const steps = [
    'Scraping Google Maps…',
    'Scraping LinkedIn…',
    'Parsing & normalising…',
    'Validating leads…',
    'Deduplicating…',
    'Exporting to Excel…',
  ]

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="rounded-lg border border-slate-800 bg-slate-900 p-10 flex flex-col items-center justify-center min-h-52"
    >
      <div className="w-10 h-10 rounded-lg bg-amber-500 flex items-center justify-center mb-6 animate-pulse">
        <span className="text-black font-bold text-lg">↯</span>
      </div>
      <p className="text-white font-semibold mb-1">Pipeline Running</p>
      <p className="text-xs text-slate-500 font-mono mb-6">This may take several minutes…</p>
      <div className="space-y-2 w-full max-w-xs">
        {steps.map((step, i) => (
          <motion.div
            key={step}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.15 }}
            className="flex items-center gap-3"
          >
            <div className="w-1.5 h-1.5 rounded-full bg-amber-400/50 animate-pulse" style={{ animationDelay: `${i * 0.3}s` }} />
            <p className="text-xs text-slate-400 font-mono">{step}</p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}