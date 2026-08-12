import { useState } from 'react'
import UploadButton from './UploadButton'
import DocumentList from './DocumentList'
import HistoryPanel from './HistoryPanel'

export default function Sidebar({
    documents,
    onUploadSuccess,
    isOpen,
    onClose,
    history,
    onHistorySelect,
    onHistoryDelete,
    onHistoryClear,
}) {
    const [historyOpen, setHistoryOpen] = useState(false)

    return (
        <>
            {isOpen && (
                <div
                    className="sidebar-overlay"
                    onClick={onClose}
                    aria-hidden="true"
                />
            )}

            <aside
                className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}
                aria-label="Documents panel"
            >
                {/* Brand + close button (mobile only) */}
                <div className="sidebar-brand">
                    <div className="sidebar-brand-name">
                        <div className="brand-icon">
                            <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
                                <path
                                    d="M5 3h8l3 3v11a1 1 0 01-1 1H5a1 1 0 01-1-1V4a1 1 0 011-1z"
                                    stroke="currentColor" strokeWidth="1.5" fill="none"
                                />
                                <path d="M13 3v3h3" stroke="currentColor" strokeWidth="1.5" />
                                <path d="M7 10h6M7 13h6M7 16h4" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
                            </svg>
                        </div>
                        <div className="brand-text-wrap">
                            <span className="brand-title">DocMind AI</span>
                            <span className="brand-sub">Document Intelligence</span>
                        </div>
                    </div>
                    <button
                        className="sidebar-close-btn"
                        onClick={onClose}
                        aria-label="Close sidebar"
                    >
                        <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
                            <path d="M3 3l10 10M13 3L3 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                        </svg>
                    </button>
                </div>

                {/* Scrollable content */}
                <div className="sidebar-scroll">
                    {/* Upload section */}
                    <div className="sidebar-section">
                        <div className="sidebar-section-label">Documents</div>
                        <UploadButton onUploadSuccess={onUploadSuccess} />
                    </div>

                    {/* Document library */}
                    <div className="sidebar-docs">
                        <DocumentList documents={documents} />
                    </div>

                    {/* History section */}
                    <div className="sidebar-section sidebar-section-history">
                        <button
                            className="sidebar-section-toggle"
                            onClick={() => setHistoryOpen((o) => !o)}
                            aria-expanded={historyOpen}
                            aria-controls="history-panel"
                        >
                            <span className="sidebar-section-label" style={{ margin: 0, padding: 0 }}>
                                History
                            </span>
                            {history.length > 0 && (
                                <span className="history-count-badge">{history.length}</span>
                            )}
                            <svg
                                className={`toggle-chevron ${historyOpen ? 'toggle-chevron-open' : ''}`}
                                viewBox="0 0 12 12" fill="none" aria-hidden="true"
                            >
                                <path d="M3 4.5l3 3 3-3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </button>

                        {historyOpen && (
                            <div id="history-panel">
                                <HistoryPanel
                                    history={history}
                                    onSelect={onHistorySelect}
                                    onDelete={onHistoryDelete}
                                    onClear={onHistoryClear}
                                />
                            </div>
                        )}
                    </div>
                </div>
            </aside>
        </>
    )
}
