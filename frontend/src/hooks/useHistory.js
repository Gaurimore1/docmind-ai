import { useCallback, useEffect, useRef, useState } from 'react'

const MAX_ITEMS = 20

/**
 * Get the localStorage key for a specific user's history.
 * Returns null if no user ID is provided (no history should be loaded/saved when logged out).
 */
function getStorageKey(userId) {
    if (!userId) {
        return null
    }
    return `docmind_history_${userId}`
}

function loadHistory(userId) {
    try {
        const key = getStorageKey(userId)
        if (!key) return []
        const raw = localStorage.getItem(key)
        if (!raw) return []
        const parsed = JSON.parse(raw)
        if (!Array.isArray(parsed)) return []
        // Validate required shape — discard malformed entries.
        // Optional fields (document_id, document_name, search_scope) are
        // allowed to be absent so old history entries remain usable.
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

function saveHistory(items, userId) {
    try {
        const key = getStorageKey(userId)
        if (!key) return
        localStorage.setItem(key, JSON.stringify(items))
    } catch { }
}

export function useHistory(userId) {
    const [history, setHistory] = useState(() => loadHistory(userId))
    const userIdRef = useRef(userId)

    // Reload history when userId changes (e.g., user logs in or out)
    useEffect(() => {
        setHistory(loadHistory(userId))
        userIdRef.current = userId
    }, [userId])

    // Keep localStorage in sync whenever history changes
    // Only save if userId hasn't changed (avoid race condition where old history is saved to new user's key)
    useEffect(() => {
        if (userIdRef.current === userId) {
            saveHistory(history, userId)
        }
    }, [history, userId])

    /**
     * Save a completed conversation to history.
     *
     * @param {string} question
     * @param {string} answer
     * @param {Array}  sources
     * @param {number|null} documentId   - null means "all documents"
     * @param {string|null} documentName - filename of selected doc, or null
     * @param {'selected'|'all'} searchScope
     */
    const addHistoryItem = useCallback((
        question,
        answer,
        sources,
        documentId = null,
        documentName = null,
        searchScope = 'all',
    ) => {
        const item = {
            id: `h-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
            question,
            answer,
            sources: sources ?? [],
            timestamp: Date.now(),
            // Document-scope metadata (absent in old entries — handled gracefully)
            document_id: documentId,
            document_name: documentName,
            search_scope: searchScope,
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
