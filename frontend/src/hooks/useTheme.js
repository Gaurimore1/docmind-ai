import { useEffect, useState } from 'react'

function getInitialTheme() {
    try {
        const saved = localStorage.getItem('docmind-theme')
        if (saved === 'dark' || saved === 'light') return saved
    } catch { }
    // Respect OS preference as fallback
    if (typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark'
    }
    return 'light'
}

export function useTheme() {
    const [theme, setTheme] = useState(getInitialTheme)

    useEffect(() => {
        const root = document.documentElement
        if (theme === 'dark') {
            root.setAttribute('data-theme', 'dark')
        } else {
            root.removeAttribute('data-theme')
        }
        try {
            localStorage.setItem('docmind-theme', theme)
        } catch { }
    }, [theme])

    function toggle() {
        setTheme((t) => (t === 'dark' ? 'light' : 'dark'))
    }

    return { theme, toggle }
}
