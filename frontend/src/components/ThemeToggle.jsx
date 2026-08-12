export default function ThemeToggle({ theme, onToggle }) {
    const isDark = theme === 'dark'
    return (
        <button
            className="theme-toggle"
            onClick={onToggle}
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            title={isDark ? 'Light mode' : 'Dark mode'}
        >
            {isDark ? (
                /* Sun icon */
                <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
                    <circle cx="10" cy="10" r="4" stroke="currentColor" strokeWidth="1.5" />
                    <path
                        d="M10 2v2M10 16v2M2 10h2M16 10h2M4.22 4.22l1.42 1.42M14.36 14.36l1.42 1.42M4.22 15.78l1.42-1.42M14.36 5.64l1.42-1.42"
                        stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"
                    />
                </svg>
            ) : (
                /* Moon icon */
                <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
                    <path
                        d="M17.5 11.5A7.5 7.5 0 0 1 8.5 2.5a7.5 7.5 0 1 0 9 9z"
                        stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"
                    />
                </svg>
            )}
        </button>
    )
}
