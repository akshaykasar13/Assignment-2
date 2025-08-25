import React from 'react'
import StatusPill from './StatusPill'

export default function RunsTable({ runs }) {
  return (
    <div style={{background:'#111827', border:'1px solid #1f2937', borderRadius:12, overflow:'hidden'}}>
      <div style={{padding:12, borderBottom:'1px solid #1f2937', fontWeight:600}}>Recent Runs</div>
      <table style={{width:'100%', borderCollapse:'collapse'}}>
        <thead>
          <tr style={{textAlign:'left', fontSize:12, opacity:0.7}}>
            <th style={{padding:'8px 12px'}}>Pipeline</th>
            <th style={{padding:'8px 12px'}}>Status</th>
            <th style={{padding:'8px 12px'}}>Duration (s)</th>
            <th style={{padding:'8px 12px'}}>Started</th>
            <th style={{padding:'8px 12px'}}>Finished</th>
            <th style={{padding:'8px 12px'}}>Branch</th>
            <th style={{padding:'8px 12px'}}>Commit</th>
            <th style={{padding:'8px 12px'}}>Actor</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((r) => (
            <tr key={r.id} style={{borderTop:'1px solid #1f2937'}}>
              <td style={{padding:'8px 12px'}}>{r.pipeline}</td>
              <td style={{padding:'8px 12px'}}><StatusPill status={r.status} /></td>
              <td style={{padding:'8px 12px'}}>{r.duration_sec ? Math.round(r.duration_sec) : '—'}</td>
              <td style={{padding:'8px 12px'}}>{new Date(r.started_at).toLocaleString()}</td>
              <td style={{padding:'8px 12px'}}>{r.finished_at ? new Date(r.finished_at).toLocaleString() : '—'}</td>
              <td style={{padding:'8px 12px'}}>{r.branch || '—'}</td>
              <td style={{padding:'8px 12px', fontFamily:'monospace'}}>{r.commit || '—'}</td>
              <td style={{padding:'8px 12px'}}>{r.triggered_by || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
