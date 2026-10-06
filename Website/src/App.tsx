import { useEffect } from 'react'

export default function App() {
  useEffect(() => {
    document.title = 'Marine AI: Vessel Monitoring System'
  }, [])

  return (
    <iframe
      src="/marine.html"
      title="Marine AI Vessel Monitoring System"
      style={{ width: '100%', height: '100vh', border: 0, display: 'block' }}
    />
  )
}
