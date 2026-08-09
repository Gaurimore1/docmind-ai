const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

/**
 * Check whether the backend is reachable.
 * Returns true if reachable, false otherwise.
 */
export async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE}/`, { signal: AbortSignal.timeout(3000) })
        return res.ok
    } catch {
        return false
    }
}

/**
 * Upload a PDF file to the backend.
 * @param {File} file
 * @returns {Promise<object>} Backend response JSON
 */
export async function uploadDocument(file) {
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(`${API_BASE}/api/v1/upload`, {
        method: 'POST',
        body: formData,
    })

    const data = await res.json()

    if (!res.ok) {
        const detail = data?.detail || `Upload failed (${res.status})`
        throw new Error(detail)
    }

    return data
}

/**
 * Search documents with a natural-language question.
 * @param {string} question
 * @returns {Promise<object>} { answer, sources, results }
 */
export async function searchDocuments(question) {
    const res = await fetch(`${API_BASE}/api/v1/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
    })

    const data = await res.json()

    if (!res.ok) {
        if (res.status === 404) {
            throw new Error('No document is available yet. Upload a PDF first.')
        }
        if (res.status === 422) {
            throw new Error('Please enter a valid question (at least 3 characters).')
        }
        const detail = data?.detail || `Search failed (${res.status})`
        throw new Error(detail)
    }

    return data
}
