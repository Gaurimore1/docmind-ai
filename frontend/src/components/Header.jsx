import { useEffect, useState } from 'react'
import { checkHealth } from '../services/api'

export default function Header() {
    const [connected, setConnected] = useState(null)

    useEffect(() => {
        let active = true
        async function ping() {
            const ok = await checkHealth()
            if (active) setConnected(ok)
        }
        ping()
        const interval = setInterval(ping, 15000)
        return () => {
            active = false
            clearInterval(interval)
        }
    }, [])

    return (
        <header className="header">
            <div className="header-brand">
                <svg className="header-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path
                        d="M7 3h8l4 4v14a1 1 0 01-1 1H6a1 1 0 01-1-1V4a1 1 0 011-1z"
                        stroke="currentColor" strokeWidth="1.5" fill="none"
                    />
                    <path d="M15 3v4h4" stroke="currentColor" strokeWidth="1.5" />
                    <path d="M9 12h6M9 15h6M9 18h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
                <span className="header-title">DocMind AI</span>
            </div>

            <div className="header-status" aria-live="polite">
                <span
                    className={`status-dot ${connected === null ? 'status-checking' : connected ? 'status-connected' : 'status-disconnected'}`}
                    aria-hidden="true"
                />
                <span className="status-label">
                    {connected === null ? 'Checking…' : connected ? 'Connected' : 'Disconnected'}
                </span>
            </div>
        </header>
    )
}
