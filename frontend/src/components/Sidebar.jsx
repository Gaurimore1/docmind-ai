import UploadButton from './UploadButton'
import DocumentList from './DocumentList'

export default function Sidebar({ documents, onUploadSuccess, isOpen, onClose }) {
    return (
        <>
            {/* Mobile overlay */}
            {isOpen && (
                <div className="sidebar-overlay" onClick={onClose} aria-hidden="true" />
            )}

            <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`} aria-label="Documents panel">
                <div className="sidebar-header">
                    <h2 className="sidebar-title">Documents</h2>
                </div>

                <div className="sidebar-upload">
                    <UploadButton onUploadSuccess={onUploadSuccess} />
                </div>

                <div className="sidebar-docs">
                    <DocumentList documents={documents} />
                </div>
            </aside>
        </>
    )
}
