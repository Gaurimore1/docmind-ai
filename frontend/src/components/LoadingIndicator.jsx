export default function LoadingIndicator() {
    return (
        <div className="loading-row" role="status" aria-label="Thinking">
            <div className="loading-bubble">
                <span className="loading-dot" />
                <span className="loading-dot" />
                <span className="loading-dot" />
                <span className="loading-label">Thinking</span>
            </div>
        </div>
    )
}
