export default function SourceCard({ source }) {
    const pct = Math.round((source.similarity_score ?? 0) * 100)

    return (
        <div className="source-card">
            <div className="source-card-left">
                <svg viewBox="0 0 16 16" fill="none" aria-hidden="true" className="source-icon">
                    <path
                        d="M3 2h7l3 3v9a1 1 0 01-1 1H3a1 1 0 01-1-1V3a1 1 0 011-1z"
                        stroke="currentColor" strokeWidth="1.2"
                    />
                    <path d="M10 2v3h3" stroke="currentColor" strokeWidth="1.2" />
                </svg>
                <div className="source-info">
                    <span className="source-filename">{source.filename}</span>
                    <span className="source-location">
                        Page {source.page_number} · Chunk {source.chunk_index}
                    </span>
                </div>
            </div>
            <span className="source-score" title={`Similarity: ${pct}%`}>{pct}%</span>
        </div>
    )
}
