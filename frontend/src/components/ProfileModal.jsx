// ProfileModal.jsx
// Shows the currently logged-in user's profile information.
// Reads from the user object passed down from App.jsx (sourced from
// localStorage docmind_user, populated at login time).

function getInitials(name) {
    if (!name) return '?'
    const parts = name.trim().split(/\s+/)
    if (parts.length >= 2) {
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
    }
    return parts[0].slice(0, 2).toUpperCase()
}

export default function ProfileModal({ user, onClose }) {
    const initials = getInitials(user?.name)

    return (
        <div className="profile-overlay" role="dialog" aria-modal="true" aria-labelledby="profile-title">
            {/* Backdrop */}
            <div className="profile-backdrop" onClick={onClose} aria-hidden="true" />

            <div className="profile-card">
                {/* Header */}
                <div className="profile-header">
                    <h2 className="profile-title" id="profile-title">Profile</h2>
                    <button
                        className="profile-close-btn"
                        onClick={onClose}
                        aria-label="Close profile"
                    >
                        <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
                            <path d="M3 3l10 10M13 3L3 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                        </svg>
                    </button>
                </div>

                {/* Avatar + name */}
                <div className="profile-identity">
                    <div className="profile-avatar" aria-hidden="true">
                        {initials}
                    </div>
                    <div className="profile-name-wrap">
                        <span className="profile-name">{user?.name ?? '—'}</span>
                        <span className="profile-email">{user?.email ?? '—'}</span>
                    </div>
                </div>

                {/* Details */}
                <div className="profile-details">
                    <div className="profile-detail-row">
                        <span className="profile-detail-label">Name</span>
                        <span className="profile-detail-value">{user?.name ?? '—'}</span>
                    </div>
                    <div className="profile-detail-row">
                        <span className="profile-detail-label">Email</span>
                        <span className="profile-detail-value">{user?.email ?? '—'}</span>
                    </div>
                    <div className="profile-detail-row">
                        <span className="profile-detail-label">Account status</span>
                        <span className="profile-status-active">
                            <span className="profile-status-dot" aria-hidden="true" />
                            Active
                        </span>
                    </div>
                </div>

                <div className="profile-footer">
                    <p className="profile-note">
                        Profile editing will be available in a future update.
                    </p>
                </div>
            </div>
        </div>
    )
}
