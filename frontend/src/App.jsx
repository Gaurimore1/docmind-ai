import { useState, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import MainArea from './components/MainArea'
import { searchDocuments } from './services/api'
import { useTheme } from './hooks/useTheme'
import { useHistory } from './hooks/useHistory'

let msgId = 0
const nextId = () => ++msgId

export default function App() {
    const [documents, setDocuments] = useState([])
    const [messages, setMessages] = useState([])
    const [loading, setLoading] = useState(false)
    const [sidebarOpen, setSidebarOpen] = useState(false)

    const { theme, toggle: toggleTheme } = useTheme()
    const { history, addHistoryItem, deleteHistoryItem, clearHistory } = useHistory()

    const handleUploadSuccess = useCallback((docInfo) => {
        setDocuments((prev) => {
            const exists = prev.some((d) => d.document_id === docInfo.document_id)
            if (exists) return prev
            return [docInfo, ...prev]
        })
    }, [])

    const handleQuestion = useCallback(async (question) => {
        setMessages((prev) => [
            ...prev,
            { id: nextId(), role: 'user', content: question },
        ])
        setLoading(true)
        setSidebarOpen(false)

        try {
            const data = await searchDocuments(question)
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
            // Save to history only on success
            addHistoryItem(question, data.answer, data.sources ?? [])
        } catch (err) {
            let msg = err.message
            if (msg.includes('fetch') || msg.includes('Failed to fetch')) {
                msg = 'Unable to connect to DocMind AI. Please make sure the backend is running.'
            }
            setMessages((prev) => [
                ...prev,
                { id: nextId(), role: 'assistant', content: msg, error: true },
            ])
        } finally {
            setLoading(false)
        }
    }, [addHistoryItem])

    // Restore a history item into the chat
    const handleHistorySelect = useCallback((item) => {
        setMessages([
            { id: nextId(), role: 'user', content: item.question },
            {
                id: nextId(),
                role: 'assistant',
                content: item.answer,
                sources: item.sources ?? [],
                error: false,
            },
        ])
        setSidebarOpen(false)
    }, [])

    return (
        <div className="app">
            <div className="app-body">
                <Sidebar
                    documents={documents}
                    onUploadSuccess={handleUploadSuccess}
                    isOpen={sidebarOpen}
                    onClose={() => setSidebarOpen(false)}
                    history={history}
                    onHistorySelect={handleHistorySelect}
                    onHistoryDelete={deleteHistoryItem}
                    onHistoryClear={clearHistory}
                />
                <MainArea
                    messages={messages}
                    loading={loading}
                    onSubmit={handleQuestion}
                    hasDocuments={documents.length > 0}
                    onMenuClick={() => setSidebarOpen((o) => !o)}
                    theme={theme}
                    onToggleTheme={toggleTheme}
                />
            </div>
        </div>
    )
}
