import { useEffect, useRef } from 'react'
import Message from './Message'
import LoadingIndicator from './LoadingIndicator'
import QuestionInput from './QuestionInput'

export default function Chat({ messages, loading, onSubmit, hasDocuments }) {
    const bottomRef = useRef(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, loading])

    const isEmpty = messages.length === 0

    return (
        <main className="chat-main">
            <div className="chat-header">
                <h1 className="chat-title">Ask your documents</h1>
                <p className="chat-subtitle">Search across your uploaded documents</p>
            </div>

            <div className="chat-messages" aria-live="polite" aria-label="Conversation">
                {isEmpty && !loading && (
                    <div className="empty-state">
                        <div className="empty-icon" aria-hidden="true">
                            <svg viewBox="0 0 48 48" fill="none">
                                <rect x="8" y="6" width="24" height="30" rx="2" stroke="currentColor" strokeWidth="2" />
                                <path d="M16 16v3h8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                <circle cx="36" cy="36" r="8" fill="currentColor" opacity="0.08" stroke="currentColor" strokeWidth="2" />
                                <path d="M33 36l2 2 4-4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </div>
                        <h2 className="empty-title">
                            {hasDocuments ? 'Ask a question' : 'Welcome to DocMind AI'}
                        </h2>
                        <p className="empty-body">
                            {hasDocuments
                                ? 'Type a question below to search your uploaded documents.'
                                : 'Upload a PDF in the sidebar, then ask questions about its contents.'}
                        </p>
                    </div>
                )}

                {messages.map((msg) => (
                    <Message key={msg.id} message={msg} />
                ))}

                {loading && <LoadingIndicator />}

                <div ref={bottomRef} />
            </div>

            <div className="chat-input-area">
                <QuestionInput onSubmit={onSubmit} disabled={loading} />
                <p className="chat-input-hint">Press Enter to send · Shift+Enter for new line</p>
            </div>
        </main>
    )
}
