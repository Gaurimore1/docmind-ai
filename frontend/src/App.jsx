import {
    useState,
    useCallback,
    useEffect,
} from 'react'

import Sidebar from './components/Sidebar'
import MainArea from './components/MainArea'
import AuthPage from './components/AuthPage'
import SettingsPage from './components/SettingsPage'

import {
    searchDocuments,
    getToken,
    logoutUser,
} from './services/api'

import { useTheme } from './hooks/useTheme'
import { useHistory } from './hooks/useHistory'


let msgId = 0

const nextId = () => ++msgId


export default function App() {

    // ============================================================
    // AUTH
    // ============================================================

    const [isAuthenticated, setIsAuthenticated] = useState(
        () => Boolean(getToken())
    )

    // Store the logged-in user's profile (name, email, id).
    // Populated from the login API response and cleared on logout.
    const [user, setUser] = useState(() => {
        try {
            const stored = localStorage.getItem('docmind_user')
            return stored ? JSON.parse(stored) : null
        } catch {
            return null
        }
    })

    const handleLogin = useCallback((data) => {
        // data = { access_token, token_type, user: { id, name, email, is_active } }
        if (data?.user) {
            setUser(data.user)
            try {
                localStorage.setItem('docmind_user', JSON.stringify(data.user))
            } catch { }
        }
        setIsAuthenticated(true)
    }, [])


    const handleLogout = useCallback(() => {
        logoutUser()
        try { localStorage.removeItem('docmind_user') } catch { }

        setUser(null)
        setDocuments([])
        setSelectedDocumentId(null)
        setMessages([])

        setIsAuthenticated(false)
    }, [])


    // Listen for expired JWT
    useEffect(() => {

        const handleAuthExpired = () => {
            setIsAuthenticated(false)
            setUser(null)
            try { localStorage.removeItem('docmind_user') } catch { }
            setDocuments([])
            setSelectedDocumentId(null)
            setMessages([])
        }

        window.addEventListener(
            'docmind-auth-expired',
            handleAuthExpired
        )

        return () => {
            window.removeEventListener(
                'docmind-auth-expired',
                handleAuthExpired
            )
        }

    }, [])


    // ============================================================
    // DOCUMENT STATE
    // ============================================================

    const [documents, setDocuments] = useState([])

    const [selectedDocumentId, setSelectedDocumentId] =
        useState(null)

    const [searchScope, setSearchScope] =
        useState('selected')

    const [messages, setMessages] =
        useState([])

    const [loading, setLoading] =
        useState(false)

    const [sidebarOpen, setSidebarOpen] =
        useState(false)

    // 'chat' | 'settings'
    const [view, setView] = useState('chat')


    // ============================================================
    // THEME / HISTORY
    // ============================================================

    const {
        theme,
        toggle: toggleTheme,
    } = useTheme()

    const {
        history,
        addHistoryItem,
        deleteHistoryItem,
        clearHistory,
    } = useHistory(user?.id)


    // ============================================================
    // UPLOAD SUCCESS
    // ============================================================

    const handleUploadSuccess = useCallback(
        (docInfo) => {

            setDocuments((prev) => {

                const exists = prev.some(
                    (d) =>
                        d.document_id === docInfo.document_id
                )

                if (exists) {
                    return prev
                }

                return [
                    docInfo,
                    ...prev,
                ]
            })

            setSelectedDocumentId(
                docInfo.document_id
            )

            setSearchScope('selected')
        },
        []
    )


    // ============================================================
    // QUESTION
    // ============================================================

    const handleQuestion = useCallback(
        async (question) => {

            if (
                searchScope === 'selected' &&
                selectedDocumentId === null
            ) {

                setMessages((prev) => [
                    ...prev,

                    {
                        id: nextId(),
                        role: 'user',
                        content: question,
                    },

                    {
                        id: nextId(),
                        role: 'assistant',
                        content:
                            'Please select a document first. You can pick one from the sidebar, or switch to "All documents" to search across everything.',
                        error: true,
                    },
                ])

                return
            }


            const documentIdToSend =
                searchScope === 'selected'
                    ? selectedDocumentId
                    : null


            setMessages((prev) => [
                ...prev,

                {
                    id: nextId(),
                    role: 'user',
                    content: question,
                },
            ])


            setLoading(true)
            setSidebarOpen(false)


            try {

                const data =
                    await searchDocuments(
                        question,
                        documentIdToSend
                    )


                setMessages((prev) => [
                    ...prev,

                    {
                        id: nextId(),
                        role: 'assistant',
                        content: data.answer,
                        sources: data.sources ?? [],
                        error: false,
                    },
                ])


                const selectedDoc =
                    documents.find(
                        (d) =>
                            d.document_id ===
                            selectedDocumentId
                    ) ?? null


                addHistoryItem(
                    question,
                    data.answer,
                    data.sources ?? [],
                    documentIdToSend,
                    selectedDoc?.filename ?? null,
                    searchScope
                )

            } catch (err) {

                let msg = err.message

                if (
                    msg.includes('fetch') ||
                    msg.includes('Failed to fetch')
                ) {
                    msg =
                        'Unable to connect to DocMind AI. Please make sure the backend is running.'
                }


                setMessages((prev) => [
                    ...prev,

                    {
                        id: nextId(),
                        role: 'assistant',
                        content: msg,
                        error: true,
                    },
                ])

            } finally {

                setLoading(false)

            }
        },
        [
            searchScope,
            selectedDocumentId,
            documents,
            addHistoryItem,
        ]
    )


    // ============================================================
    // HISTORY
    // ============================================================

    const handleHistorySelect = useCallback(
        (item) => {

            setMessages([
                {
                    id: nextId(),
                    role: 'user',
                    content: item.question,
                },

                {
                    id: nextId(),
                    role: 'assistant',
                    content: item.answer,
                    sources: item.sources ?? [],
                    error: false,
                },
            ])


            const restoredScope =
                item.search_scope ?? 'all'

            setSearchScope(restoredScope)


            if (
                item.document_id != null &&
                restoredScope === 'selected'
            ) {

                const exists =
                    documents.some(
                        (d) =>
                            d.document_id ===
                            item.document_id
                    )

                if (exists) {
                    setSelectedDocumentId(
                        item.document_id
                    )
                }
            }


            setSidebarOpen(false)
        },
        [documents]
    )


    // ============================================================
    // SELECTED DOCUMENT
    // ============================================================

    const selectedDocument =
        documents.find(
            (d) =>
                d.document_id ===
                selectedDocumentId
        ) ?? null


    // ============================================================
    // AUTH GATE
    // ============================================================

    if (!isAuthenticated) {
        return (
            <AuthPage
                onLogin={handleLogin}
            />
        )
    }


    // ============================================================
    // MAIN APPLICATION
    // ============================================================

    // Settings view takes over the full content area
    if (view === 'settings') {
        return (
            <div className="app">
                <div className="app-body">
                    <SettingsPage
                        user={user}
                        onClose={() => setView('chat')}
                    />
                </div>
            </div>
        )
    }

    return (
        <div className="app">

            <div className="app-body">

                <Sidebar
                    documents={documents}
                    selectedDocumentId={
                        selectedDocumentId
                    }
                    onSelectDocument={
                        setSelectedDocumentId
                    }
                    onUploadSuccess={
                        handleUploadSuccess
                    }
                    isOpen={sidebarOpen}
                    onClose={() =>
                        setSidebarOpen(false)
                    }
                    history={history}
                    onHistorySelect={
                        handleHistorySelect
                    }
                    onHistoryDelete={
                        deleteHistoryItem
                    }
                    onHistoryClear={
                        clearHistory
                    }
                    user={user}
                    onLogout={handleLogout}
                    onOpenSettings={() => setView('settings')}
                />


                <MainArea
                    messages={messages}
                    loading={loading}
                    onSubmit={handleQuestion}
                    hasDocuments={
                        documents.length > 0
                    }
                    selectedDocument={
                        selectedDocument
                    }
                    searchScope={searchScope}
                    onScopeChange={
                        setSearchScope
                    }
                    onMenuClick={() =>
                        setSidebarOpen(
                            (o) => !o
                        )
                    }
                    theme={theme}
                    onToggleTheme={
                        toggleTheme
                    }
                />

            </div>

        </div>
    )
}