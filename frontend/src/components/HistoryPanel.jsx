function formatTime(ts) {
    const d = new Date(ts)
    const now = new Date()
    const diffMs = now - d
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return d.toLocaleDateString()
}

export default function HistoryPanel({ history, onSelect, onDelete, onClear }) {
    if (history.length === 0) {
        return (
            <div className="history-empty">
                <p>No history yet.</p>
                <p className="history-empty-hint">Previous Q&amp;A sessions will appear here.</p>
            </div>
        )
    }

    return (
        <div className="history-list-wrap">
            <div className="history-list-header">
                <span className="history-list-count">{history.length} conversation{history.length !== 1 ? 's' : ''}</span>
                <button className="history-clear-btn" onClick={onClear} aria-label="Clear all history">
                    Clear all
                </button>
            </div>
            <ul className="history-list" aria-label="Conversation history">
                {history.map((item) => (
                    <li key={item.id} className="history-item">
                        <button
                            className="history-item-btn"
                            onClick={() => onSelect(item)}
                            aria-label={`Open: ${item.question}`}
                        >
                            <span className="history-item-q">{item.question}</span>
                            <span className="history-item-time">{formatTime(item.timestamp)}</span>
                        </button>
                        <button
                            className="history-item-del"
                            onClick={(e) => { e.stopPropagation(); onDelete(item.id) }}
                            aria-label="Delete this conversation"
                            title="Delete"
                        >
                            <svg viewBox="0 0 12 12" fill="none" aria-hidden="true">
                                <path d="M2 2l8 8M10 2l-8 8" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
                            </svg>
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    )
}
