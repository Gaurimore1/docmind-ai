import { useState, useRef, useEffect } from 'react'
import UploadButton from './UploadButton'
import DocumentList from './DocumentList'
import HistoryPanel from './HistoryPanel'
import LogoutModal from './LogoutModal'
import ProfileModal from './ProfileModal'

// Derive two-letter initials from a display name.
// "Gauri More" → "GM", "gauri" → "G"
function getInitials(name) {
    if (!name) return '?'
    const parts = name.trim().split(/\s+/)
    if (parts.length >= 2) {
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
    }
    return parts[0].slice(0, 2).toUpperCase()
}

export default function Sidebar({
    documents,
    selectedDocumentId,
    onSelectDocument,
    onUploadSuccess,
    isOpen,
    onClose,
    history,
    onHistorySelect,
    onHistoryDelete,
    onHistoryClear,
    user,
    onLogout,
    onOpenSettings,
}) {
    const [historyOpen, setHistoryOpen] = useState(false)
    const [menuOpen, setMenuOpen] = useState(false)
    const [showLogoutModal, setShowLogoutModal] = useState(false)
    const [showProfileModal, setShowProfileModal] = useState(false)
    const menuRef = useRef(null)

    // Close the dropdown when the user clicks outside it
    useEffect(() => {
        if (!menuOpen) return
        function handleOutside(e) {
            if (menuRef.current && !menuRef.current.contains(e.target)) {
                setMenuOpen(false)
            }
        }
        document.addEventListener('mousedown', handleOutside)
        return () => document.removeEventListener('mousedown', handleOutside)
    }, [menuOpen])

    // Close dropdown on Escape key
    useEffect(() => {
        if (!menuOpen) return
        function handleKey(e) {
            if (e.key === 'Escape') setMenuOpen(false)
        }
        document.addEventListener('keydown', handleKey)
        return () => document.removeEventListener('keydown', handleKey)
    }, [menuOpen])

    function handleLogoutClick() {
        setMenuOpen(false)
        setShowLogoutModal(true)
    }

    function handleLogoutConfirm() {
        setShowLogoutModal(false)
        onLogout()
    }

    const initials = user ? getInitials(user.name) : '?'
    const displayName = user?.name ?? 'Account'
    const displayEmail = user?.email ?? ''

    return (
        <>
            {/* Mobile overlay */}
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
                {/* Brand + mobile close */}
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

                {/* Scrollable body */}
                <div className="sidebar-scroll">
                    {/* Upload */}
                    <div className="sidebar-section">
                        <div className="sidebar-section-label">Documents</div>
                        <UploadButton onUploadSuccess={onUploadSuccess} />
                    </div>

                    {/* Document list */}
                    <div className="sidebar-docs">
                        <DocumentList
                            documents={documents}
                            selectedDocumentId={selectedDocumentId}
                            onSelectDocument={onSelectDocument}
                        />
                    </div>

                    {/* History */}
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

                {/* ── User profile footer ── */}
                <div className="sidebar-user" ref={menuRef}>
                    <button
                        className="user-menu-trigger"
                        onClick={() => setMenuOpen((o) => !o)}
                        aria-haspopup="menu"
                        aria-expanded={menuOpen}
                        aria-label={`Account menu for ${displayName}`}
                    >
                        <div className="user-avatar" aria-hidden="true">
                            {initials}
                        </div>
                        <div className="user-info">
                            <span className="user-name">{displayName}</span>
                            <span className="user-email">{displayEmail}</span>
                        </div>
                        <svg
                            className="user-chevron"
                            viewBox="0 0 12 12" fill="none" aria-hidden="true"
                        >
                            <path d="M3 4.5l3 3 3-3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </button>

                    {/* Dropdown menu */}
                    {menuOpen && (
                        <div className="user-dropdown" role="menu" aria-label="Account options">
                            <button className="user-dropdown-item" role="menuitem" onClick={() => { setMenuOpen(false); setShowProfileModal(true) }}>
                                <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
                                    <circle cx="8" cy="5.5" r="2.5" stroke="currentColor" strokeWidth="1.3" />
                                    <path d="M2.5 13.5c0-3 2.5-4.5 5.5-4.5s5.5 1.5 5.5 4.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
                                </svg>
                                Profile
                            </button>

                            <button className="user-dropdown-item" role="menuitem" onClick={() => { setMenuOpen(false); onOpenSettings?.() }}>
                                <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
                                    <circle cx="8" cy="8" r="2" stroke="currentColor" strokeWidth="1.3" />
                                    <path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.22 3.22l1.42 1.42M11.36 11.36l1.42 1.42M3.22 12.78l1.42-1.42M11.36 4.64l1.42-1.42" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
                                </svg>
                                Settings
                            </button>

                            <div className="user-dropdown-divider" />

                            <button
                                className="user-dropdown-item user-dropdown-item-danger"
                                role="menuitem"
                                onClick={handleLogoutClick}
                            >
                                <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
                                    <path d="M10.5 5.5l3 2.5-3 2.5M6 8h7.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
                                    <path d="M6 3H3a1 1 0 00-1 1v8a1 1 0 001 1h3" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
                                </svg>
                                Logout
                            </button>
                        </div>
                    )}
                </div>
            </aside>

            {/* Logout confirmation modal */}
            {showLogoutModal && (
                <LogoutModal
                    onCancel={() => setShowLogoutModal(false)}
                    onConfirm={handleLogoutConfirm}
                />
            )}

            {/* Profile modal */}
            {showProfileModal && (
                <ProfileModal
                    user={user}
                    onClose={() => setShowProfileModal(false)}
                />
            )}
        </>
    )
}
