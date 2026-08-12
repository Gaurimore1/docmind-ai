export default function LoadingIndicator() {
    return (
        <div className="loading-wrap" role="status" aria-label="Thinking">
            <div className="ai-avatar" aria-hidden="true">
                <svg viewBox="0 0 20 20" fill="none">
                    <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5" />
                    <path
                        d="M7 10l2 2 4-4"
                        stroke="currentColor"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                </svg>
            </div>
            <div className="loading-dots" aria-hidden="true">
                <span className="loading-dot" />
                <span className="loading-dot" />
                <span className="loading-dot" />
            </div>
            <span className="loading-text">Thinking…</span>
        </div>
    )
}
