export default function DocumentList({ documents, selectedDocumentId, onSelectDocument }) {
    if (documents.length === 0) {
        return (
            <div className="doc-empty">
                <div className="doc-empty-icon">
                    <svg viewBox="0 0 40 40" fill="none" aria-hidden="true">
                        <path d="M10 8h14l6 6v18a2 2 0 01-2 2H10a2 2 0 01-2-2V10a2 2 0 012-2z"
                            stroke="currentColor" strokeWidth="1.5" />
                        <path d="M24 8v6h6" stroke="currentColor" strokeWidth="1.5" />
                        <path d="M14 20h12M14 24h12M14 28h8" stroke="currentColor" strokeWidth="1.3"
                            strokeLinecap="round" />
                    </svg>
                </div>
                <p>No documents yet.</p>
                <p className="doc-empty-hint">Upload a PDF to get started.</p>
            </div>
        )
    }

    return (
        <ul className="doc-list" role="listbox" aria-label="Uploaded documents">
            {documents.map((doc) => {
                const isSelected = doc.document_id === selectedDocumentId
                return (
                    <li
                        key={doc.document_id}
                        className={`doc-item doc-item-selectable ${isSelected ? 'doc-item-selected' : ''}`}
                        role="option"
                        aria-selected={isSelected}
                        onClick={() => onSelectDocument(doc.document_id)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault()
                                onSelectDocument(doc.document_id)
                            }
                        }}
                        tabIndex={0}
                    >
                        {/* Radio-style selection indicator */}
                        <div className="doc-radio" aria-hidden="true">
                            {isSelected ? (
                                /* Filled circle = selected */
                                <svg viewBox="0 0 16 16" fill="none">
                                    <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
                                    <circle cx="8" cy="8" r="4" fill="currentColor" />
                                </svg>
                            ) : (
                                /* Empty circle = unselected */
                                <svg viewBox="0 0 16 16" fill="none">
                                    <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
                                </svg>
                            )}
                        </div>

                        {/* PDF icon */}
                        <div className="doc-icon-wrap">
                            <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
                                <path d="M3 2h7l3 3v9a1 1 0 01-1 1H3a1 1 0 01-1-1V3a1 1 0 011-1z"
                                    stroke="currentColor" strokeWidth="1.2" />
                                <path d="M10 2v3h3" stroke="currentColor" strokeWidth="1.2" />
                            </svg>
                        </div>

                        {/* Filename + page count */}
                        <div className="doc-info">
                            <span className="doc-name" title={doc.filename}>{doc.filename}</span>
                            {doc.pages != null && (
                                <span className="doc-meta">{doc.pages} page{doc.pages !== 1 ? 's' : ''}</span>
                            )}
                        </div>
                    </li>
                )
            })}
        </ul>
    )
}
