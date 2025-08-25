import React, { useEffect, useState } from 'react'
import { fetchSummary, fetchRuns } from './api'
import { connectMetrics } from './ws'
import Header from './components/Header'
import MetricsCards from './components/MetricsCards'
import RunsTable from './components/RunsTable'
import LastBuild from './components/LastBuild'

export default function App() {
  const [summary, setSummary] = useState(null)
  const [runs, setRuns] = useState([])
  const [error, setError] = useState(null)

  async function load() {
    try {
      const [s, r] = await Promise.all([fetchSummary(), fetchRuns(20)])
      setSummary(s)
      setRuns(r)
    } catch (e) {
      setError(e.message)
    }
  }

  useEffect(() => {
    load()
    const ws = connectMetrics((payload) => {
      setSummary(payload)
      fetchRuns(20).then(setRuns).catch(() => {})
    })
    return () => ws && ws.close()
  }, [])

  return (
    <div style={{maxWidth: 1100, margin: '0 auto', padding: '24px'}}>
      <Header />
      {error && <div style={{background:'#7f1d1d', padding:12, borderRadius:8}}>Error: {error}</div>}
      {summary ? (
        <>
          <MetricsCards summary={summary} />
          <LastBuild summary={summary} />
          <RunsTable runs={runs} />
        </>
      ) : (
        <div>Loading...</div>
      )}
    </div>
  )
}
