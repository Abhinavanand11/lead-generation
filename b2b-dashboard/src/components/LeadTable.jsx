// src/components/LeadTable.jsx
import { useState } from 'react'
import { MapPin, Linkedin, Phone, Mail, ChevronUp, ChevronDown } from 'lucide-react'

const SOURCE_CONFIG = {
  google_maps: {
    label: 'Maps',
    icon: MapPin,
    className: 'text-amber-400 bg-amber-950/60 border-amber-800',
  },
  linkedin: {
    label: 'LinkedIn',
    icon: Linkedin,
    className: 'text-blue-400 bg-blue-950/60 border-blue-800',
  },
}

function SourceBadge({ source }) {
  const cfg = SOURCE_CONFIG[source] || SOURCE_CONFIG.google_maps
  const Icon = cfg.icon
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded border text-[10px] font-mono ${cfg.className}`}>
      <Icon size={9} />
      {cfg.label}
    </span>
  )
}

function truncate(str, n = 28) {
  if (!str) return '—'
  return str.length > n ? str.slice(0, n) + '…' : str
}

const COLS = [
  { key: 'name',    label: 'Name',    sortable: true },
  { key: 'company', label: 'Company', sortable: true },
  { key: 'phone',   label: 'Phone',   sortable: false },
  { key: 'email',   label: 'Email',   sortable: true },
  { key: 'city',    label: 'City',    sortable: true },
  { key: 'source',  label: 'Source',  sortable: true },
]

export default function LeadTable({ leads = [] }) {
  const [sortCol, setSortCol] = useState('name')
  const [sortDir, setSortDir] = useState('asc')

  function handleSort(col) {
    if (sortCol === col) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortCol(col)
      setSortDir('asc')
    }
  }

  const sorted = [...leads].sort((a, b) => {
    const va = (a[sortCol] || '').toLowerCase()
    const vb = (b[sortCol] || '').toLowerCase()
    const cmp = va < vb ? -1 : va > vb ? 1 : 0
    return sortDir === 'asc' ? cmp : -cmp
  })

  if (leads.length === 0) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-12 text-center">
        <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center mx-auto mb-3">
          <MapPin size={18} className="text-slate-600" />
        </div>
        <p className="text-slate-500 text-sm">No leads yet — run a scrape to see results</p>
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 overflow-hidden w-full">
      {/* Table header bar */}
      <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-white">Lead Preview</h3>
          <p className="text-xs text-slate-500 mt-0.5 font-mono">{leads.length} records (first 20)</p>
        </div>
        <div className="flex items-center gap-2">
          {Object.entries(
            leads.reduce((acc, l) => {
              acc[l.source] = (acc[l.source] || 0) + 1
              return acc
            }, {})
          ).map(([src, count]) => (
            <span key={src} className="flex items-center gap-1.5">
              <SourceBadge source={src} />
              <span className="text-[10px] text-slate-500 font-mono">{count}</span>
            </span>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/80 sticky top-0 z-10">
              {COLS.map(col => (
                <th
                  key={col.key}
                  onClick={() => col.sortable && handleSort(col.key)}
                  className={`px-4 py-3 text-left text-xs font-mono text-slate-500 uppercase tracking-wider
                    ${col.sortable ? 'cursor-pointer hover:text-slate-300 select-none' : ''}
                    transition-colors duration-100`}
                >
                  <span className="inline-flex items-center gap-1">
                    {col.label}
                    {col.sortable && sortCol === col.key && (
                      sortDir === 'asc'
                        ? <ChevronUp size={11} className="text-amber-400" />
                        : <ChevronDown size={11} className="text-amber-400" />
                    )}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((lead, i) => (
              <tr
                key={i}
                className={`border-b border-slate-800/60 transition-colors duration-100
                  hover:bg-slate-800/50
                  ${i % 2 === 0 ? '' : 'bg-slate-800/20'}`}
              >
                <td className="px-4 py-3">
                  <span className="text-slate-100 font-medium">{truncate(lead.name)}</span>
                </td>
                <td className="px-4 py-3">
                  <span className="text-slate-300">{truncate(lead.company)}</span>
                </td>
                <td className="px-4 py-3">
                  {lead.phone ? (
                    <span className="inline-flex items-center gap-1.5 text-slate-400 font-mono text-xs">
                      <Phone size={10} className="text-slate-600" />
                      {lead.phone}
                    </span>
                  ) : (
                    <span className="text-slate-700">—</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  {lead.email ? (
                    <span className="inline-flex items-center gap-1.5 text-slate-400 text-xs">
                      <Mail size={10} className="text-slate-600" />
                      {truncate(lead.email, 24)}
                    </span>
                  ) : (
                    <span className="text-slate-700">—</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <span className="text-slate-400 text-xs">{lead.city || '—'}</span>
                </td>
                <td className="px-4 py-3">
                  <SourceBadge source={lead.source} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}