const API_BASE =
    import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const TOKEN_KEY = 'docmind_access_token'


// ============================================================
// TOKEN MANAGEMENT
// ============================================================

export function getToken() {
    return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
    localStorage.removeItem(TOKEN_KEY)
}


// ============================================================
// AUTHENTICATED FETCH
// ============================================================

async function authenticatedFetch(url, options = {}) {
    const token = getToken()

    const headers = {
        ...(options.headers || {}),
    }

    if (token) {
        headers.Authorization = `Bearer ${token}`
    }

    const response = await fetch(url, {
        ...options,
        headers,
    })

    // JWT expired / invalid
    if (response.status === 401) {
        clearToken()

        window.dispatchEvent(
            new CustomEvent('docmind-auth-expired')
        )
    }

    return response
}


// ============================================================
// HEALTH CHECK
// ============================================================

export async function checkHealth() {
    try {
        const res = await fetch(
            `${API_BASE}/`,
            {
                signal: AbortSignal.timeout(3000),
            }
        )

        return res.ok
    } catch {
        return false
    }
}


// ============================================================
// SIGNUP
// ============================================================

export async function signupUser(name, email, password) {
    const res = await fetch(
        `${API_BASE}/api/v1/auth/signup`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                email,
                password,
            }),
        }
    )

    const data = await res.json()

    if (!res.ok) {
        const detail =
            data?.detail ||
            `Signup failed (${res.status})`

        if (Array.isArray(detail)) {
            throw new Error(
                detail
                    .map((item) => item.msg)
                    .join(', ')
            )
        }

        throw new Error(detail)
    }

    return data
}


// ============================================================
// LOGIN
// ============================================================

export async function loginUser(email, password) {
    const res = await fetch(
        `${API_BASE}/api/v1/auth/login`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                password,
            }),
        }
    )

    const data = await res.json()

    if (!res.ok) {
        const detail =
            data?.detail ||
            `Login failed (${res.status})`

        if (Array.isArray(detail)) {
            throw new Error(
                detail
                    .map((item) => item.msg)
                    .join(', ')
            )
        }

        throw new Error(detail)
    }

    // Backend returns access_token.
    const token =
        data?.access_token ||
        data?.token

    if (!token) {
        throw new Error(
            'Login succeeded but no access token was returned by the server.'
        )
    }

    setToken(token)

    return data
}


// ============================================================
// LOGOUT
// ============================================================

export function logoutUser() {
    clearToken()

    window.dispatchEvent(
        new CustomEvent('docmind-logout')
    )
}


// ============================================================
// UPLOAD DOCUMENT
// ============================================================

export async function uploadDocument(file) {
    const token = getToken()

    if (!token) {
        throw new Error('Please log in before uploading a document.')
    }

    const formData = new FormData()

    formData.append('file', file)

    const res = await authenticatedFetch(
        `${API_BASE}/api/v1/upload`,
        {
            method: 'POST',
            body: formData,
        }
    )

    const data = await res.json()

    if (!res.ok) {
        const detail =
            data?.detail ||
            `Upload failed (${res.status})`

        throw new Error(detail)
    }

    return data
}


// ============================================================
// SEARCH DOCUMENTS
// ============================================================

export async function searchDocuments(
    question,
    documentId = null
) {
    const token = getToken()

    if (!token) {
        throw new Error('Please log in before searching documents.')
    }

    const body = {
        question,
    }

    if (documentId !== null) {
        body.document_id = documentId
    }

    const res = await authenticatedFetch(
        `${API_BASE}/api/v1/search`,
        {
            method: 'POST',

            headers: {
                'Content-Type': 'application/json',
            },

            body: JSON.stringify(body),
        }
    )

    const data = await res.json()

    if (!res.ok) {
        if (res.status === 404) {
            const detail =
                data?.detail ||
                'No document is available yet. Upload a PDF first.'

            throw new Error(detail)
        }

        if (res.status === 422) {
            throw new Error(
                'Please enter a valid question (at least 3 characters).'
            )
        }

        const detail =
            data?.detail ||
            `Search failed (${res.status})`

        throw new Error(detail)
    }

    return data
}