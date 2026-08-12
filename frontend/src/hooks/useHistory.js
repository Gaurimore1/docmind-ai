import { useCallback, useEffect, useState } from 'react'

const STORAGE_KEY = 'docmind-history'
const MAX_ITEMS = 20

function loadHistory() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY)
        if (!raw) return []
        const parsed = JSON.parse(raw)
        if (!Array.isArray(parsed)) return []
        // Validate shape — discard malformed entries
        return parsed.filter(
            (h) =>
                h &&
                typeof h.id === 'string' &&
                typeof h.question === 'string' &&
                typeof h.answer === 'string' &&
                typeof h.timestamp === 'number'
        )
    } catch {
        return []
    }
}

function saveHistory(items) {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
    } catch { }
}

export function useHistory() {
    const [history, setHistory] = useState(loadHistory)

    // Keep localStorage in sync whenever history changes
    useEffect(() => {
        saveHistory(history)
    }, [history])

    const addHistoryItem = useCallback((question, answer, sources) => {
        const item = {
            id: `h-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
            question,
            answer,
            sources: sources ?? [],
            timestamp: Date.now(),
        }
        setHistory((prev) => [item, ...prev].slice(0, MAX_ITEMS))
    }, [])

    const deleteHistoryItem = useCallback((id) => {
        setHistory((prev) => prev.filter((h) => h.id !== id))
    }, [])

    const clearHistory = useCallback(() => {
        setHistory([])
    }, [])

    return { history, addHistoryItem, deleteHistoryItem, clearHistory }
}
