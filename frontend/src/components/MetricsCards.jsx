import React from 'react'

function StatCard({ title, value, subtitle }) {
  return (
    <div style={{flex:1, background:'#111827', padding:16, borderRadius:12, border:'1px solid #1f2937'}}>
      <div style={{opacity:0.8, fontSize:12, marginBottom:6}}>{title}</div>
      <div style={{fontSize:24, fontWeight:600}}>{value}</div>
      {subtitle && <div style={{opacity:0.6, fontSize:12, marginTop:6}}>{subtitle}</div>}
    </div>
  )
}

export default function MetricsCards({ summary }) {
  const successRatePct = Math.round((summary.success_rate || 0) * 1000)/10
  const avgSecs = summary.avg_duration_sec ? Math.round(summary.avg_duration_sec) : '—'
  return (
    <div style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:12, marginBottom:16}}>
      <StatCard title="Total Runs" value={summary.total} subtitle={`Window: ${summary.window_minutes} min`} />
      <StatCard title="Success / Failure" value={`${summary.success} / ${summary.failure}`} subtitle={`${successRatePct}% success`} />
      <StatCard title="Average Duration" value={`${avgSecs} s`} subtitle="Across window" />
      <StatCard title="Pipelines" value={summary.per_pipeline?.length || 0} subtitle="Distinct" />
    </div>
  )
}
