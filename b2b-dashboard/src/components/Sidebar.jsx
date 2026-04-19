// src/components/Sidebar.jsx
import { motion } from 'framer-motion'
import { Zap, LayoutDashboard, Users, Settings, Activity, ChevronRight } from 'lucide-react'

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', id: 'dashboard', active: true },
  { icon: Users,           label: 'Leads',     id: 'leads',     active: false },
  { icon: Activity,        label: 'Analytics', id: 'analytics', active: false },
  { icon: Settings,        label: 'Settings',  id: 'settings',  active: false },
]

export default function Sidebar({ healthStatus }) {
  return (
    <aside
      className="w-56 flex-shrink-0 flex flex-col h-screen sticky top-0 border-r border-slate-800"
      style={{ background: '#020617' }}
    >
      {/* Logo */}
      <div className="px-5 py-5 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center flex-shrink-0">
            <Zap size={16} className="text-black" strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-sm font-semibold text-white leading-none">LeadForge</p>
            <p className="text-xs text-slate-500 mt-0.5 font-mono">B2B Intelligence</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {navItems.map((item, i) => (
          <motion.button
            key={item.id}
            initial={{ x: -12, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.05 + i * 0.04, duration: 0.3 }}
            className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-sm
              transition-all duration-150
              ${item.active
                ? 'bg-slate-800 text-white'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
          >
            <item.icon
              size={15}
              className={item.active ? 'text-amber-400' : 'text-slate-500'}
            />
            <span className={`flex-1 text-left text-sm ${item.active ? 'font-medium' : ''}`}>
              {item.label}
            </span>
            {item.active && <ChevronRight size={12} className="text-slate-500" />}
          </motion.button>
        ))}
      </nav>

      {/* Health status */}
      <div className="px-3 py-4 border-t border-slate-800">
        <div className="rounded-md border border-slate-800 bg-slate-900 px-3 py-3 space-y-1.5">
          <p className="text-xs font-mono text-slate-600 uppercase tracking-widest">API Status</p>
          <div className="flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full flex-shrink-0 ${
                healthStatus === 'ok'    ? 'bg-emerald-400' :
                healthStatus === 'error' ? 'bg-red-400' :
                                           'bg-slate-600'
              }`}
            />
            <span className="text-xs text-slate-300">
              {healthStatus === 'ok'    ? 'Connected' :
               healthStatus === 'error' ? 'Disconnected' :
                                          'Checking…'}
            </span>
          </div>
        </div>
      </div>
    </aside>
  )
}