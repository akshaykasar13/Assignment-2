const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function connectMetrics(onMessage) {
  const wsUrl = API_URL.replace('http', 'ws') + '/ws/metrics'
  const socket = new WebSocket(wsUrl)

  socket.onopen = () => {
    setInterval(() => {
      try { socket.send('ping') } catch {}
    }, 30000)
  }

  socket.onmessage = (ev) => {
    try {
      const data = JSON.parse(ev.data)
      if (data?.type === 'metrics_update') onMessage(data.payload)
    } catch {}
  }

  return socket
}
