import { useRef, useState } from 'react'
import { uploadDocument } from '../services/api'

export default function UploadButton({ onUploadSuccess }) {
    const inputRef = useRef(null)
    const [uploading, setUploading] = useState(false)
    const [error, setError] = useState(null)

    function handleClick() {
        setError(null)
        inputRef.current?.click()
    }

    async function handleChange(e) {
        const file = e.target.files?.[0]
        if (!file) return

        if (file.type !== 'application/pdf') {
            setError('Only PDF files are accepted.')
            e.target.value = ''
            return
        }

        setUploading(true)
        setError(null)

        try {
            const data = await uploadDocument(file)
            onUploadSuccess({
                filename: data.filename,
                document_id: data.document_id,
                pages: data.pages,
                chunks: data.chunks,
            })
        } catch (err) {
            if (err.message.includes('fetch') || err.message.includes('Failed to fetch')) {
                setError('Unable to connect to DocMind AI. Please make sure the backend is running.')
            } else {
                setError(err.message)
            }
        } finally {
            setUploading(false)
            e.target.value = ''
        }
    }

    return (
        <div className="upload-area">
            <input
                ref={inputRef}
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleChange}
                style={{ display: 'none' }}
                aria-label="Upload PDF"
            />
            <button
                className="upload-btn"
                onClick={handleClick}
                disabled={uploading}
                aria-busy={uploading}
            >
                {uploading ? (
                    <>
                        <span className="spinner" aria-hidden="true" />
                        Uploading…
                    </>
                ) : (
                    <>
                        <svg viewBox="0 0 16 16" fill="none" aria-hidden="true" className="upload-icon">
                            <path d="M8 2v8M5 5l3-3 3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M2 11v1a2 2 0 002 2h8a2 2 0 002-2v-1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                        </svg>
                        Upload PDF
                    </>
                )}
            </button>

            {error && (
                <p className="upload-error" role="alert">{error}</p>
            )}
        </div>
    )
}
