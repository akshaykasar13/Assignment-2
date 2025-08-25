import React from 'react'
import StatusPill from './StatusPill'

export default function LastBuild({ summary }) {
  const last = summary.last_status
  return (
    <div style={{display:'flex', alignItems:'center', gap:12, marginBottom:16}}>
      <div style={{background:'#111827', border:'1px solid #1f2937', borderRadius:12, padding:12}}>
        <div style={{fontSize:12, opacity:0.8, marginBottom:6}}>Last Build Status</div>
        {last ? <StatusPill status={last} /> : <span>—</span>}
      </div>
    </div>
  )
}
