// src/services/api.js
// Central API service for B2B Lead Generation backend

const BASE_URL = import.meta.env.VITE_API_URL || ''

/**
 * Check API health and token status.
 * @returns {Promise<{status: string, apify_token_set: boolean}>}
 */
export async function checkHealth() {
  const res = await fetch(`${BASE_URL}/health`)
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`)
  return res.json()
}

/**
 * Trigger the full lead generation pipeline.
 *
 * @param {Object} params
 * @param {string[]} params.queries            - Google Maps search strings
 * @param {Object[]} params.linkedinSearches   - LinkedIn search configs
 * @param {boolean}  params.includeLeadsPreview - Include first 20 leads in response
 * @returns {Promise<ScrapeResponse>}
 */
export async function scrapeLeads({
  queries = [],
  linkedinSearches = [],
  includeLeadsPreview = true,
} = {}) {
  const body = {
    queries,
    linkedin_searches: linkedinSearches,
    include_leads_preview: includeLeadsPreview,
  }

  const res = await fetch(`${BASE_URL}/scrape`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!res.ok) {
    let detail = res.statusText
    try {
      const err = await res.json()
      detail = err.detail || detail
    } catch {}
    throw new Error(detail)
  }

  return res.json()
}

/**
 * Download the latest Excel export. Triggers a browser file download.
 */
export async function downloadFile() {
  const res = await fetch(`${BASE_URL}/download`)

  if (!res.ok) {
    let detail = res.statusText
    try {
      const err = await res.json()
      detail = err.detail || detail
    } catch {}
    throw new Error(detail)
  }

  const blob = await res.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'leads.xlsx'
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(url)
}
