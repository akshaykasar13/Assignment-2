import React from 'react'

export default function StatusPill({ status }) {
  const color = status === 'success' ? '#14532d' : status === 'failure' ? '#7f1d1d' : '#1e3a8a'
  const bg = status === 'success' ? '#14532d22' : status === 'failure' ? '#7f1d1d22' : '#1e3a8a22'
  return (
    <span style={{background:bg, color, padding:'4px 8px', borderRadius:999, fontSize:12, textTransform:'capitalize'}}>
      {status}
    </span>
  )
}
