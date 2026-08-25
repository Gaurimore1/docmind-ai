import { useState } from 'react'
import { useTheme } from '../hooks/useTheme'

// ── Section definitions ────────────────────────────────────────────────────
const SECTIONS = [
    {
        id: 'general',
        label: 'General',
        icon: (
            <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
                <circle cx="9" cy="9" r="2.5" stroke="currentColor" strokeWidth="1.4" />
                <path d="M9 1.5v2M9 14.5v2M1.5 9h2M14.5 9h2M3.4 3.4l1.42 1.42M13.18 13.18l1.42 1.42M3.4 14.6l1.42-1.42M13.18 4.82l1.42-1.42"
                    stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
            </svg>
        ),
    },
    {
        id: 'appearance',
        label: 'Appearance',
        icon: (
            <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
                <circle cx="9" cy="9" r="7" stroke="currentColor" strokeWidth="1.4" />
                <path d="M9 2a7 7 0 000 14V2z" fill="currentColor" opacity=".25" />
            </svg>
        ),
    },
    {
        id: 'account',
        label: 'Account',
        icon: (
            <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
                <circle cx="9" cy="6" r="3" stroke="currentColor" strokeWidth="1.4" />
                <path d="M2.5 15.5c0-3.5 2.9-5.5 6.5-5.5s6.5 2 6.5 5.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
            </svg>
        ),
    },
    {
        id: 'security',
        label: 'Security',
        icon: (
            <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
                <path d="M9 1.5L2.5 4.5v5c0 3.5 2.9 6 6.5 7 3.6-1 6.5-3.5 6.5-7v-5L9 1.5z"
                    stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
                <path d="M6.5 9l1.75 1.75L11.5 7.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
        ),
    },
    {
        id: 'documents',
        label: 'Documents',
        icon: (
            <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
                <path d="M3.5 2.5h8l3 3v10a1 1 0 01-1 1h-10a1 1 0 01-1-1v-12a1 1 0 011-1z"
                    stroke="currentColor" strokeWidth="1.4" />
                <path d="M11.5 2.5v3h3" stroke="currentColor" strokeWidth="1.4" />
                <path d="M5.5 9h7M5.5 11.5h7M5.5 14h4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
            </svg>
        ),
    },
    {
        id: 'about',
        label: 'About',
        icon: (
            <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
                <circle cx="9" cy="9" r="7" stroke="currentColor" strokeWidth="1.4" />
                <path d="M9 8.5v4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
                <circle cx="9" cy="6" r=".75" fill="currentColor" />
            </svg>
        ),
    },
]

// ── Reusable card wrapper ──────────────────────────────────────────────────
function Card({ children }) {
    return <div className="settings-card">{children}</div>
}

function CardHeader({ title, description }) {
    return (
        <div className="settings-card-header">
            <h3 className="settings-card-title">{title}</h3>
            {description && <p className="settings-card-desc">{description}</p>}
        </div>
    )
}

function SettingRow({ label, description, children }) {
    return (
        <div className="settings-row">
            <div className="settings-row-label">
                <span className="settings-row-name">{label}</span>
                {description && <span className="settings-row-desc">{description}</span>}
            </div>
            <div className="settings-row-control">{children}</div>
        </div>
    )
}

function Toggle({ checked, onChange, label }) {
    return (
        <button
            role="switch"
            aria-checked={checked}
            aria-label={label}
            className={`settings-toggle ${checked ? 'settings-toggle-on' : ''}`}
            onClick={() => onChange(!checked)}
        >
            <span className="settings-toggle-thumb" />
        </button>
    )
}

function Badge({ children, variant = 'default' }) {
    return <span className={`settings-badge settings-badge-${variant}`}>{children}</span>
}

// ── Section panels ─────────────────────────────────────────────────────────

function SectionGeneral() {
    const [notifications, setNotifications] = useState(true)
    const [autoScroll, setAutoScroll] = useState(true)
    const [language] = useState('English')

    return (
        <div className="settings-section-content">
            <div className="settings-section-heading">
                <h2>General</h2>
                <p>Manage your general application preferences.</p>
            </div>

            <Card>
                <CardHeader title="Behaviour" description="Control how DocMind AI behaves during your sessions." />
                <SettingRow label="Auto-scroll to new answers" description="Automatically scroll down when a new answer is generated.">
                    <Toggle checked={autoScroll} onChange={setAutoScroll} label="Toggle auto-scroll" />
                </SettingRow>
                <SettingRow label="Desktop notifications" description="Receive notifications when long-running searches complete.">
                    <Toggle checked={notifications} onChange={setNotifications} label="Toggle notifications" />
                </SettingRow>
            </Card>

            <Card>
                <CardHeader title="Language & Region" />
                <SettingRow label="Language" description="Interface display language.">
                    <select className="settings-select" value={language} onChange={() => { }}>
                        <option>English</option>
                    </select>
                </SettingRow>
            </Card>
        </div>
    )
}

function SectionAppearance() {
    const { theme, toggle } = useTheme()
    const [fontSize, setFontSize] = useState('medium')
    const [compactMode, setCompactMode] = useState(false)

    return (
        <div className="settings-section-content">
            <div className="settings-section-heading">
                <h2>Appearance</h2>
                <p>Customize how DocMind AI looks on your screen.</p>
            </div>

            <Card>
                <CardHeader title="Theme" description="Choose between light and dark mode." />
                <div className="settings-theme-picker">
                    <button
                        className={`settings-theme-option ${theme === 'light' ? 'settings-theme-option-active' : ''}`}
                        onClick={() => { if (theme !== 'light') toggle() }}
                        aria-pressed={theme === 'light'}
                    >
                        <div className="settings-theme-preview settings-theme-preview-light">
                            <div className="stp-sidebar" />
                            <div className="stp-main">
                                <div className="stp-bar" />
                                <div className="stp-content" />
                            </div>
                        </div>
                        <span>Light</span>
                    </button>
                    <button
                        className={`settings-theme-option ${theme === 'dark' ? 'settings-theme-option-active' : ''}`}
                        onClick={() => { if (theme !== 'dark') toggle() }}
                        aria-pressed={theme === 'dark'}
                    >
                        <div className="settings-theme-preview settings-theme-preview-dark">
                            <div className="stp-sidebar" />
                            <div className="stp-main">
                                <div className="stp-bar" />
                                <div className="stp-content" />
                            </div>
                        </div>
                        <span>Dark</span>
                    </button>
                </div>
            </Card>

            <Card>
                <CardHeader title="Display" />
                <SettingRow label="Font size" description="Controls the base text size across the application.">
                    <select className="settings-select" value={fontSize} onChange={(e) => setFontSize(e.target.value)}>
                        <option value="small">Small</option>
                        <option value="medium">Medium</option>
                        <option value="large">Large</option>
                    </select>
                </SettingRow>
                <SettingRow label="Compact mode" description="Reduce spacing for a denser layout.">
                    <Toggle checked={compactMode} onChange={setCompactMode} label="Toggle compact mode" />
                </SettingRow>
            </Card>
        </div>
    )
}

function SectionAccount({ user }) {
    return (
        <div className="settings-section-content">
            <div className="settings-section-heading">
                <h2>Account</h2>
                <p>Manage your DocMind AI account details.</p>
            </div>

            <Card>
                <CardHeader title="Profile" description="Your account information." />
                <div className="settings-profile-row">
                    <div className="settings-profile-avatar">
                        {user?.name
                            ? user.name.trim().split(/\s+/).map(p => p[0]).slice(0, 2).join('').toUpperCase()
                            : '?'}
                    </div>
                    <div>
                        <div className="settings-profile-name">{user?.name ?? '—'}</div>
                        <div className="settings-profile-email">{user?.email ?? '—'}</div>
                    </div>
                    <Badge variant="success">Active</Badge>
                </div>
            </Card>

            <Card>
                <CardHeader title="Account Details" />
                <SettingRow label="Display name" description="Your name shown in the interface.">
                    <input className="settings-input" defaultValue={user?.name ?? ''} placeholder="Enter your name" readOnly />
                </SettingRow>
                <SettingRow label="Email address" description="Your login email address.">
                    <input className="settings-input" defaultValue={user?.email ?? ''} type="email" placeholder="you@example.com" readOnly />
                </SettingRow>
                <div className="settings-card-footer">
                    <span className="settings-note">Profile editing will be available in a future update.</span>
                </div>
            </Card>
        </div>
    )
}

function SectionSecurity() {
    const [twoFactor, setTwoFactor] = useState(false)
    const [sessionAlerts, setSessionAlerts] = useState(true)

    return (
        <div className="settings-section-content">
            <div className="settings-section-heading">
                <h2>Security</h2>
                <p>Protect your account with security settings.</p>
            </div>

            <Card>
                <CardHeader title="Password" description="Change your account password." />
                <SettingRow label="Current password">
                    <input className="settings-input" type="password" placeholder="Enter current password" />
                </SettingRow>
                <SettingRow label="New password">
                    <input className="settings-input" type="password" placeholder="Minimum 8 characters" />
                </SettingRow>
                <SettingRow label="Confirm new password">
                    <input className="settings-input" type="password" placeholder="Repeat new password" />
                </SettingRow>
                <div className="settings-card-footer">
                    <button className="settings-btn-primary" disabled>Update password</button>
                    <span className="settings-note">Password update will be available in a future update.</span>
                </div>
            </Card>

            <Card>
                <CardHeader title="Advanced Security" />
                <SettingRow label="Two-factor authentication" description="Add an extra layer of protection to your account.">
                    <Toggle checked={twoFactor} onChange={setTwoFactor} label="Toggle 2FA" />
                </SettingRow>
                <SettingRow label="Session alerts" description="Notify you when a new sign-in occurs.">
                    <Toggle checked={sessionAlerts} onChange={setSessionAlerts} label="Toggle session alerts" />
                </SettingRow>
            </Card>
        </div>
    )
}

function SectionDocuments() {
    const [autoChunk, setAutoChunk] = useState(true)
    const [showPreview, setShowPreview] = useState(true)
    const [chunkSize] = useState('1000')
    const [maxResults] = useState('5')

    return (
        <div className="settings-section-content">
            <div className="settings-section-heading">
                <h2>Documents</h2>
                <p>Control how your documents are processed and searched.</p>
            </div>

            <Card>
                <CardHeader title="Processing" description="Configure how uploaded PDFs are handled." />
                <SettingRow label="Auto-chunk on upload" description="Automatically split documents into searchable segments when uploaded.">
                    <Toggle checked={autoChunk} onChange={setAutoChunk} label="Toggle auto-chunk" />
                </SettingRow>
                <SettingRow label="Show text preview" description="Display a 500-character text preview after upload.">
                    <Toggle checked={showPreview} onChange={setShowPreview} label="Toggle text preview" />
                </SettingRow>
            </Card>

            <Card>
                <CardHeader title="Search Configuration" />
                <SettingRow label="Chunk size" description="Characters per chunk used during PDF processing.">
                    <input className="settings-input settings-input-sm" defaultValue={chunkSize} readOnly />
                </SettingRow>
                <SettingRow label="Max search results" description="Maximum number of chunks returned per query.">
                    <input className="settings-input settings-input-sm" defaultValue={maxResults} readOnly />
                </SettingRow>
                <div className="settings-card-footer">
                    <span className="settings-note">These values reflect the current backend configuration.</span>
                </div>
            </Card>
        </div>
    )
}

function SectionAbout() {
    return (
        <div className="settings-section-content">
            <div className="settings-section-heading">
                <h2>About</h2>
                <p>Information about DocMind AI.</p>
            </div>

            <Card>
                <div className="settings-about-brand">
                    <div className="settings-about-icon" aria-hidden="true">✦</div>
                    <div>
                        <h3>DocMind AI</h3>
                        <p>Intelligent Enterprise Document Agent</p>
                    </div>
                </div>

                <div className="settings-about-grid">
                    <div className="settings-about-item">
                        <span className="settings-about-label">Version</span>
                        <span className="settings-about-value">0.1.0</span>
                    </div>
                    <div className="settings-about-item">
                        <span className="settings-about-label">Model</span>
                        <span className="settings-about-value">phi3:mini via Ollama</span>
                    </div>
                    <div className="settings-about-item">
                        <span className="settings-about-label">Embeddings</span>
                        <span className="settings-about-value">all-MiniLM-L6-v2</span>
                    </div>
                    <div className="settings-about-item">
                        <span className="settings-about-label">Vector store</span>
                        <span className="settings-about-value">PostgreSQL + pgvector</span>
                    </div>
                    <div className="settings-about-item">
                        <span className="settings-about-label">Framework</span>
                        <span className="settings-about-value">FastAPI + React</span>
                    </div>
                    <div className="settings-about-item">
                        <span className="settings-about-label">License</span>
                        <span className="settings-about-value">MIT</span>
                    </div>
                </div>
            </Card>

            <Card>
                <CardHeader title="Technology Stack" />
                {[
                    ['Backend', 'Python 3.10 · FastAPI · SQLAlchemy 2.0'],
                    ['Database', 'PostgreSQL 17 · pgvector'],
                    ['AI / ML', 'Ollama · phi3:mini · SentenceTransformers'],
                    ['Frontend', 'React 18 · Vite · CSS variables'],
                    ['Auth', 'JWT · bcrypt'],
                    ['Deployment', 'Docker · Docker Compose'],
                ].map(([k, v]) => (
                    <div className="settings-stack-row" key={k}>
                        <span className="settings-stack-key">{k}</span>
                        <span className="settings-stack-val">{v}</span>
                    </div>
                ))}
            </Card>
        </div>
    )
}

// ── Main SettingsPage ──────────────────────────────────────────────────────

export default function SettingsPage({ user, onClose }) {
    const [activeSection, setActiveSection] = useState('general')

    const sectionMap = {
        general: <SectionGeneral />,
        appearance: <SectionAppearance />,
        account: <SectionAccount user={user} />,
        security: <SectionSecurity />,
        documents: <SectionDocuments />,
        about: <SectionAbout />,
    }

    return (
        <div className="settings-page">
            {/* Top bar */}
            <div className="settings-topbar">
                <button className="settings-back-btn" onClick={onClose} aria-label="Back to documents">
                    <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
                        <path d="M10 3L5 8l5 5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    Back
                </button>
                <h1 className="settings-topbar-title">Settings</h1>
                <div />
            </div>

            <div className="settings-body">
                {/* Left nav */}
                <nav className="settings-nav" aria-label="Settings sections">
                    <ul>
                        {SECTIONS.map((s) => (
                            <li key={s.id}>
                                <button
                                    className={`settings-nav-item ${activeSection === s.id ? 'settings-nav-item-active' : ''}`}
                                    onClick={() => setActiveSection(s.id)}
                                    aria-current={activeSection === s.id ? 'page' : undefined}
                                >
                                    <span className="settings-nav-icon">{s.icon}</span>
                                    <span>{s.label}</span>
                                </button>
                            </li>
                        ))}
                    </ul>

                    {/* Mobile: pill row */}
                    <div className="settings-nav-mobile">
                        {SECTIONS.map((s) => (
                            <button
                                key={s.id}
                                className={`settings-nav-pill ${activeSection === s.id ? 'settings-nav-pill-active' : ''}`}
                                onClick={() => setActiveSection(s.id)}
                            >
                                {s.label}
                            </button>
                        ))}
                    </div>
                </nav>

                {/* Right panel */}
                <main className="settings-main">
                    {sectionMap[activeSection]}
                </main>
            </div>
        </div>
    )
}
