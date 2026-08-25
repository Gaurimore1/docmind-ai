export default function LogoutModal({ onCancel, onConfirm }) {
    return (
        <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="logout-title">
            {/* Backdrop click cancels */}
            <div className="modal-backdrop" onClick={onCancel} aria-hidden="true" />

            <div className="modal-card">
                {/* Icon */}
                <div className="modal-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" fill="none">
                        <path
                            d="M16 17l5-5m0 0l-5-5m5 5H9m4 5a9 9 0 110-18"
                            stroke="currentColor" strokeWidth="1.8"
                            strokeLinecap="round" strokeLinejoin="round"
                        />
                    </svg>
                </div>

                <h2 className="modal-title" id="logout-title">Sign out of DocMind AI?</h2>

                <p className="modal-body">
                    You'll need to sign in again to access your documents.
                </p>

                <div className="modal-actions">
                    <button
                        className="modal-btn-cancel"
                        onClick={onCancel}
                        autoFocus
                    >
                        Cancel
                    </button>
                    <button
                        className="modal-btn-confirm"
                        onClick={onConfirm}
                    >
                        Sign out
                    </button>
                </div>
            </div>
        </div>
    )
}
