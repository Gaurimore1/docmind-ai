export default function SourceCard({ source }) {
    const pct = Math.round((source.similarity_score ?? 0) * 100)

    return (
        <div className="source-card">
            <div className="source-left">
                <div className="source-pdf-icon" aria-hidden="true">
                    <svg viewBox="0 0 16 16" fill="none">
                        <path
                            d="M3 2h7l3 3v9a1 1 0 01-1 1H3a1 1 0 01-1-1V3a1 1 0 011-1z"
                            stroke="currentColor"
                            strokeWidth="1.2"
                        />
                        <path d="M10 2v3h3" stroke="currentColor" strokeWidth="1.2" />
                    </svg>
                </div>
                <div className="source-info">
                    <span className="source-filename" title={source.filename}>
                        {source.filename}
                    </span>
                    <span className="source-location">
                        Page {source.page_number} · Chunk {source.chunk_index}
                    </span>
                </div>
            </div>
            <span className="source-badge" title={`Similarity: ${pct}%`}>
                {pct}%
            </span>
        </div>
    )
}
