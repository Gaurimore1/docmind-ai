import { useState, useRef, useEffect } from 'react'

export default function QuestionInput({ onSubmit, disabled }) {
    const [value, setValue] = useState('')
    const textareaRef = useRef(null)

    // Auto-resize textarea — grows with content, scrolls only when capped
    useEffect(() => {
        const ta = textareaRef.current
        if (!ta) return
        // Reset height so scrollHeight reflects actual content size
        ta.style.height = 'auto'
        const MAX = 160
        if (ta.scrollHeight <= MAX) {
            // Content fits — expand to content height, no scrollbar
            ta.style.height = ta.scrollHeight + 'px'
            ta.style.overflowY = 'hidden'
        } else {
            // Content exceeds cap — lock at max and allow scroll
            ta.style.height = MAX + 'px'
            ta.style.overflowY = 'auto'
        }
    }, [value])

    function handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            submit()
        }
    }

    function submit() {
        const q = value.trim()
        if (!q || disabled) return
        onSubmit(q)
        setValue('')
        // Reset height after clear
        if (textareaRef.current) textareaRef.current.style.height = 'auto'
    }

    return (
        <div className="composer-box">
            <textarea
                ref={textareaRef}
                className="composer-textarea"
                placeholder="Ask a question about your documents..."
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={disabled}
                rows={1}
                aria-label="Question input"
            />
            <button
                className="composer-send"
                onClick={submit}
                disabled={disabled || !value.trim()}
                aria-label="Send question"
            >
                <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
                    <path
                        d="M8 12V4M5 7l3-3 3 3"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                </svg>
            </button>
        </div>
    )
}
