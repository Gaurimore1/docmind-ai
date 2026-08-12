import { useEffect, useRef, useState } from 'react'
import { checkHealth } from '../services/api'
import Message from './Message'
import LoadingIndicator from './LoadingIndicator'
import QuestionInput from './QuestionInput'
import ThemeToggle from './ThemeToggle'

const SUGGESTIONS = [
    'What technologies were used during the internship?',
    'Summarize the key findings of the document.',
    'What projects were completed?',
    'Who are the main people mentioned?',
]

export default function MainArea({ messages, loading, onSubmit, hasDocuments, onMenuClick, theme, onToggleTheme }) {
    const [connected, setConnected] = useState(null)
    const bottomRef = useRef(null)

    // Health check
    useEffect(() => {
        let active = true
        async function ping() {
            const ok = await checkHealth()
            if (active) setConnected(ok)
        }
        ping()
        const interval = setInterval(ping, 15000)
        return () => { active = false; clearInterval(interval) }
    }, [])

    // Auto-scroll
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, loading])

    const isEmpty = messages.length === 0

    return (
        <div className="main-wrap">
            {/* Top bar */}
            <div className="main-topbar">
                <div className="main-topbar-left">
                    {/* Hamburger — visible only below 900px via CSS */}
                    <button
                        className="menu-btn"
                        onClick={onMenuClick}
                        aria-label="Open documents panel"
                    >
                        <svg viewBox="0 0 20 20" fill="none" width="20" height="20" aria-hidden="true">
                            <path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
                        </svg>
                    </button>
                    <div>
                        <div className="topbar-title">Ask your documents</div>
                        <div className="topbar-sub">Search across your uploaded documents</div>
                    </div>
                </div>

                <div className="topbar-right">
                    <ThemeToggle theme={theme} onToggle={onToggleTheme} />
                    <div className="topbar-status">
                        <span
                            className={`status-dot ${connected === null ? 'status-checking' :
                                    connected ? 'status-connected' : 'status-disconnected'
                                }`}
                            aria-hidden="true"
                        />
                        <span className="status-label">
                            {connected === null ? 'Checking…' : connected ? 'Connected' : 'Disconnected'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Conversation scroll area */}
            <div className="chat-scroll" aria-live="polite" aria-label="Conversation">
                <div className="chat-inner">

                    {/* Empty state */}
                    {isEmpty && !loading && (
                        <div className="empty-wrap">
                            <div className="empty-graphic" aria-hidden="true">
                                <svg viewBox="0 0 32 32" fill="none">
                                    <path d="M6 4h14l6 6v18a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2z"
                                        stroke="currentColor" strokeWidth="1.8" />
                                    <path d="M20 4v6h6" stroke="currentColor" strokeWidth="1.8" />
                                    <path d="M10 14h12M10 18h12M10 22h8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                                </svg>
                            </div>
                            <h2 className="empty-title">Ask anything about your documents</h2>
                            <p className="empty-body">
                                Upload a PDF and ask questions about its contents.
                                DocMind AI will find the relevant sections and generate a grounded answer.
                            </p>

                            {hasDocuments && (
                                <div className="suggestions-grid">
                                    {SUGGESTIONS.map((s) => (
                                        <button
                                            key={s}
                                            className="suggestion-card"
                                            onClick={() => onSubmit(s)}
                                            disabled={loading}
                                        >
                                            {s}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Messages */}
                    {messages.map((msg) => (
                        <Message key={msg.id} message={msg} />
                    ))}

                    {loading && <LoadingIndicator />}

                    <div ref={bottomRef} />
                </div>
            </div>

            {/* Composer */}
            <div className="composer-bar">
                <div className="composer-inner">
                    <QuestionInput onSubmit={onSubmit} disabled={loading} />
                    <p className="composer-hint">Press Enter to send · Shift+Enter for a new line</p>
                </div>
            </div>
        </div>
    )
}
