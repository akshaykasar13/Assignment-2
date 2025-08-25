import React from 'react'

export default function Header() {
  return (
    <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:16}}>
      <h1 style={{fontSize:24, margin:0}}>CI/CD Pipeline Health Dashboard</h1>
      <span style={{opacity:0.8}}>Realtime via WebSocket</span>
    </div>
  )
}
