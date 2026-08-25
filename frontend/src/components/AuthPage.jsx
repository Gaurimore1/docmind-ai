import { useState } from 'react'
import { loginUser, signupUser } from '../services/api'

export default function AuthPage({ onLogin }) {
    const [mode, setMode] = useState('login')

    const [name, setName] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')

    const handleSubmit = async (e) => {
        e.preventDefault()

        setError('')
        setSuccess('')
        setLoading(true)

        try {
            if (mode === 'signup') {
                if (!name.trim()) {
                    throw new Error('Please enter your name.')
                }

                if (password.length < 8) {
                    throw new Error('Password must be at least 8 characters.')
                }

                await signupUser(name.trim(), email.trim(), password)

                setSuccess('Account created successfully. Logging you in...')

                // Signup API creates the account.
                // Login immediately afterwards so the user does not
                // have to enter their credentials twice.
                const data = await loginUser(email.trim(), password)

                onLogin(data)
            } else {
                const data = await loginUser(email.trim(), password)

                onLogin(data)
            }
        } catch (err) {
            setError(err.message || 'Authentication failed.')
        } finally {
            setLoading(false)
        }
    }

    const switchMode = () => {
        setMode((current) => current === 'login' ? 'signup' : 'login')
        setError('')
        setSuccess('')
    }

    return (
        <div className="auth-page">
            <div className="auth-card">

                <div className="auth-logo">
                    <div className="auth-logo-icon">✦</div>
                    <div>
                        <h1>DocMind AI</h1>
                        <p>Intelligent Enterprise Document Agent</p>
                    </div>
                </div>

                <div className="auth-heading">
                    <h2>
                        {mode === 'login'
                            ? 'Welcome back'
                            : 'Create your account'}
                    </h2>

                    <p>
                        {mode === 'login'
                            ? 'Sign in to continue to your documents.'
                            : 'Create an account to securely manage your documents.'}
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">

                    {mode === 'signup' && (
                        <div className="auth-field">
                            <label htmlFor="name">Name</label>

                            <input
                                id="name"
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Enter your name"
                                autoComplete="name"
                                required
                            />
                        </div>
                    )}

                    <div className="auth-field">
                        <label htmlFor="email">Email</label>

                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="you@example.com"
                            autoComplete="email"
                            required
                        />
                    </div>

                    <div className="auth-field">
                        <label htmlFor="password">Password</label>

                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Minimum 8 characters"
                            autoComplete={
                                mode === 'login'
                                    ? 'current-password'
                                    : 'new-password'
                            }
                            required
                        />
                    </div>

                    {error && (
                        <div className="auth-error">
                            {error}
                        </div>
                    )}

                    {success && (
                        <div className="auth-success">
                            {success}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="auth-submit"
                        disabled={loading}
                    >
                        {loading
                            ? 'Please wait...'
                            : mode === 'login'
                                ? 'Sign In'
                                : 'Create Account'}
                    </button>
                </form>

                <div className="auth-switch">
                    {mode === 'login'
                        ? "Don't have an account?"
                        : 'Already have an account?'}

                    <button
                        type="button"
                        onClick={switchMode}
                    >
                        {mode === 'login'
                            ? 'Create account'
                            : 'Sign in'}
                    </button>
                </div>

            </div>
        </div>
    )
}