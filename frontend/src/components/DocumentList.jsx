export default function DocumentList({ documents }) {
    if (documents.length === 0) {
        return (
            <div className="doc-empty">
                <p>No documents yet.</p>
                <p className="doc-empty-hint">Upload a PDF to get started.</p>
            </div>
        )
    }

    return (
        <ul className="doc-list" aria-label="Uploaded documents">
            {documents.map((doc) => (
                <li key={doc.document_id ?? doc.filename} className="doc-item">
                    <svg viewBox="0 0 16 16" fill="none" aria-hidden="true" className="doc-icon">
                        <path
                            d="M3 2h7l3 3v9a1 1 0 01-1 1H3a1 1 0 01-1-1V3a1 1 0 011-1z"
                            stroke="currentColor" strokeWidth="1.2"
                        />
                        <path d="M10 2v3h3" stroke="currentColor" strokeWidth="1.2" />
                    </svg>
                    <div className="doc-info">
                        <span className="doc-name" title={doc.filename}>{doc.filename}</span>
                        {doc.pages != null && (
                            <span className="doc-meta">{doc.pages} page{doc.pages !== 1 ? 's' : ''}</span>
                        )}
                    </div>
                    <span className="doc-ready" aria-label="Ready">✓</span>
                </li>
            ))}
        </ul>
    )
}
