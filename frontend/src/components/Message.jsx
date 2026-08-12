import SourceCard from './SourceCard'

export default function Message({ message }) {
    const { role, content, sources, error } = message

    if (role === 'user') {
        return (
            <div className="msg-user-wrap">
                <div className="msg-user-bubble">{content}</div>
            </div>
        )
    }

    // assistant
    if (error) {
        return (
            <div className="msg-ai-wrap">
                <div className="msg-error-card" role="alert">{content}</div>
            </div>
        )
    }

    return (
        <div className="msg-ai-wrap">
            <div className="msg-ai-header">
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
                <span className="ai-label">DocMind AI</span>
            </div>

            <div className="msg-ai-card">
                <p className="msg-answer-text">{content}</p>

                {sources && sources.length > 0 && (
                    <div className="sources-section">
                        <div className="sources-label">Sources</div>
                        <div className="sources-list">
                            {sources.map((src, i) => (
                                <SourceCard
                                    key={`${src.filename}-${src.page_number}-${src.chunk_index}-${i}`}
                                    source={src}
                                />
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
