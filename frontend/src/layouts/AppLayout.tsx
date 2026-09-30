import { Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import Router from '@/components/Router'
import { Brain, BookOpen, Network, Target, FileText, Calendar, BarChart3, Settings, Home, Menu, X, LogOut } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/auth/AuthContext'
import { useNavigate } from 'react-router-dom'

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Knowledge Map', href: '/knowledge-map', icon: Network },
  { name: 'Adaptive Practice', href: '/adaptive-practice', icon: Target },
  { name: 'Materials', href: '/materials', icon: BookOpen },
  { name: 'Progress', href: '/progress', icon: BarChart3 },
  { name: 'Study Plan', href: '/study-plan', icon: Calendar },
  { name: 'Quizzes', href: '/quizzes', icon: FileText },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function AppLayout() {
  const location = useLocation()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const handleLogout = async () => { await logout(); navigate('/login', { replace: true }) }

  return (
    <div className="relative min-h-screen bg-background/40">
      <div className="app-atmosphere" aria-hidden="true" />
      {/* Top Navigation - Mobile */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-card/95 border-b border-white/10 backdrop-blur-xl">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2">
            <Brain className="w-6 h-6 text-primary" />
            <span className="font-semibold text-lg">StudyMind AI</span>
          </div>
          <button aria-label={mobileNavOpen ? 'Close navigation' : 'Open navigation'} aria-expanded={mobileNavOpen} onClick={() => setMobileNavOpen(!mobileNavOpen)} className="p-2 hover:bg-accent rounded-md">
            {mobileNavOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
        {mobileNavOpen && <nav className="max-h-[calc(100vh-4rem)] overflow-y-auto border-t border-white/10 bg-card/95 p-3 space-y-1 backdrop-blur-xl">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return <Link key={item.name} to={item.href} onClick={() => setMobileNavOpen(false)} className={cn('nav-link flex items-center gap-3 rounded-md px-4 py-3 text-sm font-medium', isActive ? 'nav-link-active text-foreground' : 'text-muted-foreground hover:bg-accent hover:text-foreground')}>
              <item.icon className="w-5 h-5" />{item.name}
            </Link>
          })}
          <button onClick={handleLogout} className="nav-link flex w-full items-center gap-3 rounded-md px-4 py-3 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground"><LogOut className="w-5 h-5" />Log out · {user?.email}</button>
        </nav>}
      </div>

      <div className="flex">
        {/* Sidebar - Desktop */}
        <aside className="hidden lg:flex flex-col w-[16rem] shrink-0 min-h-screen bg-card/65 border-r border-white/10 backdrop-blur-xl">
          <div className="p-6 border-b border-white/10">
            <div className="flex items-center gap-3">
              <Brain className="w-8 h-8 text-primary" />
              <div>
                <h1 className="font-bold text-xl">StudyMind AI</h1>
                <p className="max-w-[10rem] text-[11px] leading-relaxed text-muted-foreground">Adaptive learning that understands the learner.</p>
              </div>
            </div>
          </div>

          <nav className="flex-1 p-4 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    "nav-link flex items-center gap-3 px-4 py-3 rounded-md text-sm font-medium",
                    isActive
                      ? "nav-link-active text-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  )}
                >
                  <item.icon className="w-5 h-5" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          <div className="p-4 border-t border-white/10">
            <div className="flex items-center gap-3 px-4 py-3">
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <span className="text-sm font-medium text-primary">{user?.name?.[0]?.toUpperCase() || 'U'}</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user?.name}</p>
                <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
              </div>
              <button aria-label="Log out" onClick={handleLogout} className="rounded-md p-2 text-muted-foreground hover:bg-accent hover:text-foreground"><LogOut className="h-4 w-4" /></button>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 min-h-screen lg:pt-0 pt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <Router />
          </div>
        </main>
      </div>
    </div>
  )
}
