const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function fetchSummary(minutes) {
  const url = minutes ? `${API_URL}/api/metrics/summary?minutes=${minutes}` : `${API_URL}/api/metrics/summary`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Failed to fetch metrics')
  return await res.json()
}

export async function fetchRuns(limit = 20) {
  const res = await fetch(`${API_URL}/api/runs?limit=${limit}`)
  if (!res.ok) throw new Error('Failed to fetch runs')
  return await res.json()
}
