import { useState, useRef, useEffect } from 'react'

export default function QuestionInput({ onSubmit, disabled }) {
    const [value, setValue] = useState('')
    const textareaRef = useRef(null)

    // Auto-resize textarea
    useEffect(() => {
        const ta = textareaRef.current
        if (!ta) return
        ta.style.height = 'auto'
        ta.style.height = Math.min(ta.scrollHeight, 160) + 'px'
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
    }

    return (
        <div className="question-input-wrap">
            <textarea
                ref={textareaRef}
                className="question-textarea"
                placeholder="Ask a question about your documents…"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={disabled}
                rows={1}
                aria-label="Question input"
            />
            <button
                className="question-send"
                onClick={submit}
                disabled={disabled || !value.trim()}
                aria-label="Send question"
            >
                <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
                    <path d="M8 12V4M5 7l3-3 3 3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            </button>
        </div>
    )
}
