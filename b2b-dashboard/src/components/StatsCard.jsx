// src/components/StatsCard.jsx
import { motion } from 'framer-motion'

export default function StatsCard({ label, value, sub, icon: Icon, accent = false, delay = 0 }) {
  return (
    <motion.div
      initial={{ y: 12, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay, duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
      className={`rounded-lg p-4 border transition-colors duration-150
        ${accent
          ? 'bg-amber-950/30 border-amber-800/60'
          : 'bg-slate-900 border-slate-800 hover:border-slate-700'
        }`}
    >
      <div className="flex items-start justify-between mb-2">
        <p className="text-xs font-mono text-slate-500 uppercase tracking-widest">{label}</p>
        {Icon && (
          <div className={`w-6 h-6 rounded-md flex items-center justify-center
            ${accent ? 'bg-amber-500/20' : 'bg-slate-800'}`}>
            <Icon size={12} className={accent ? 'text-amber-400' : 'text-slate-400'} />
          </div>
        )}
      </div>
      <p className={`text-2xl font-semibold leading-none
        ${accent ? 'text-amber-400' : 'text-white'}`}>
        {value ?? '—'}
      </p>
      {sub && (
        <p className="text-xs text-slate-500 mt-1.5 font-mono">{sub}</p>
      )}
    </motion.div>
  )
}