import SourceCard from './SourceCard'

export default function Message({ message }) {
    const { role, content, sources, error } = message

    if (role === 'user') {
        return (
            <div className="msg msg-user">
                <p className="msg-text">{content}</p>
            </div>
        )
    }

    // assistant message
    return (
        <div className="msg msg-assistant">
            {error ? (
                <p className="msg-error" role="alert">{content}</p>
            ) : (
                <>
                    <div className="msg-answer-label">AI Answer</div>
                    <div className="msg-answer">{content}</div>

                    {sources && sources.length > 0 && (
                        <div className="msg-sources">
                            <div className="msg-sources-label">Sources</div>
                            <div className="msg-sources-list">
                                {sources.map((src, i) => (
                                    <SourceCard key={`${src.filename}-${src.page_number}-${src.chunk_index}-${i}`} source={src} />
                                ))}
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    )
}
