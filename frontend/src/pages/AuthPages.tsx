import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Brain } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { api } from '@/lib/api'
import { useAuth } from '@/auth/AuthContext'

export default function AuthPage({ mode }: { mode: 'login' | 'register' }) {
  const isRegister = mode === 'register'
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { refresh } = useAuth()

  const submit = async (event: FormEvent) => {
    event.preventDefault(); setError('')
    if (isRegister && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) { setError('Enter a valid email address.'); return }
    if (password.length < 8) { setError('Password must be at least 8 characters.'); return }
    if (isRegister && password !== confirm) { setError('Passwords do not match.'); return }
    setBusy(true)
    try {
      if (isRegister) await api.register({ name: name.trim(), email: email.trim().toLowerCase(), password })
      else await api.login({ email: email.trim().toLowerCase(), password })
      await refresh(); navigate('/', { replace: true })
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to authenticate. Try again.') }
    finally { setBusy(false) }
  }

  return <main className="relative min-h-screen overflow-hidden grid place-items-center px-4 py-10">
    <div className="app-atmosphere" aria-hidden="true" />
    <div className="relative w-full max-w-md space-y-6">
      <div className="text-center"><div className="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-2xl border border-primary/30 bg-primary/10 text-primary shadow-lg shadow-primary/10"><Brain className="h-7 w-7" /></div><h1 className="text-2xl font-bold">StudyMind AI</h1><p className="mt-2 text-sm text-muted-foreground">Adaptive learning that understands the learner.</p></div>
      <section className="ambient-panel rounded-2xl border border-white/10 p-6 shadow-2xl sm:p-8"><h2 className="text-xl font-semibold">{isRegister ? 'Create your account' : 'Welcome back'}</h2><p className="mt-1 text-sm text-muted-foreground">{isRegister ? 'Start building your personal learning model.' : 'Sign in to continue your learning.'}</p>
        <form onSubmit={submit} className="mt-6 space-y-4" noValidate>
          {isRegister && <label className="block space-y-1.5 text-sm">Name<Input autoComplete="name" value={name} onChange={e => setName(e.target.value)} required maxLength={120} /></label>}
          <label className="block space-y-1.5 text-sm">Email<Input type="email" autoComplete="email" value={email} onChange={e => setEmail(e.target.value)} required /></label>
          <label className="block space-y-1.5 text-sm">Password<Input type="password" autoComplete={isRegister ? 'new-password' : 'current-password'} value={password} onChange={e => setPassword(e.target.value)} required minLength={8} /></label>
          {isRegister && <label className="block space-y-1.5 text-sm">Confirm password<Input type="password" autoComplete="new-password" value={confirm} onChange={e => setConfirm(e.target.value)} required minLength={8} /></label>}
          {error && <p role="alert" className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">{error}</p>}
          <Button type="submit" disabled={busy || !email.trim() || !password || (isRegister && (!name.trim() || !confirm))} className="w-full">{busy ? (isRegister ? 'Creating account…' : 'Signing in…') : (isRegister ? 'Create account' : 'Log in')}</Button>
        </form>
        <p className="mt-5 text-center text-sm text-muted-foreground">{isRegister ? 'Already have an account?' : 'New to StudyMind AI?'}{' '}<Link className="font-semibold text-primary hover:underline" to={isRegister ? '/login' : '/register'}>{isRegister ? 'Log in' : 'Create an account'}</Link></p>
      </section>
    </div>
  </main>
}
