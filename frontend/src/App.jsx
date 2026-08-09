import { useState, useCallback } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import Chat from './components/Chat'
import { searchDocuments } from './services/api'

let messageIdCounter = 0
function nextId() {
    return ++messageIdCounter
}

export default function App() {
    const [documents, setDocuments] = useState([])
    const [messages, setMessages] = useState([])
    const [loading, setLoading] = useState(false)
    const [sidebarOpen, setSidebarOpen] = useState(false)

    const handleUploadSuccess = useCallback((docInfo) => {
        setDocuments((prev) => {
            // Avoid exact duplicates (same document_id)
            const exists = prev.some((d) => d.document_id === docInfo.document_id)
            if (exists) return prev
            return [docInfo, ...prev]
        })
    }, [])

    const handleQuestion = useCallback(async (question) => {
        // Append user message
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
    }, [])

    return (
        <div className="app">
            <Header onMenuClick={() => setSidebarOpen((o) => !o)} />

            <div className="app-body">
                <Sidebar
                    documents={documents}
                    onUploadSuccess={handleUploadSuccess}
                    isOpen={sidebarOpen}
                    onClose={() => setSidebarOpen(false)}
                />

                <Chat
                    messages={messages}
                    loading={loading}
                    onSubmit={handleQuestion}
                    hasDocuments={documents.length > 0}
                />
            </div>
        </div>
    )
}
