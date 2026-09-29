import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Brain,
  Clock,
  Target,
  TrendingUp,
  Zap,
  Network,
  RotateCcw,
  Sparkles,
  ArrowRight,
  AlertTriangle,
  BookOpen,
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { api, DashboardResponse, Recommendation } from '@/lib/api'

export default function Dashboard() {
  const [data, setData] = useState<DashboardResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [demoBusy, setDemoBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.getDashboard()
      setData(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const initDemo = async () => {
    setDemoBusy(true)
    try {
      await api.initializeDemo()
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Demo init failed')
    } finally {
      setDemoBusy(false)
    }
  }

  const resetDemo = async () => {
    setDemoBusy(true)
    try {
      await api.resetDemo()
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Demo reset failed')
    } finally {
      setDemoBusy(false)
    }
  }

  const recommendation: Recommendation | null = data?.next_best_action ?? null
  const stats = data?.stats

  return (
    <div className="dashboard-shell space-y-8 max-w-6xl mx-auto">
      {/* Top Welcome & Demo Controls */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.24em] text-primary">Your learning state</p>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Good morning, {data?.user.name ?? 'Student'} 👋
          </h1>
          <p className="text-muted-foreground text-base sm:text-lg mt-1">
            Most AI tutors answer what you ask. StudyMind AI figures out what you should learn next.
          </p>
          {data?.user.is_demo && (
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-50 border border-amber-200 text-amber-800 dark:bg-amber-950/40 dark:border-amber-800 dark:text-amber-300 text-xs font-semibold mt-2.5">
              <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              Demo Mode Active — Data Structures Benchmark Set
            </div>
          )}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={initDemo} disabled={demoBusy} className="gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-primary" />
            Reload Demo
          </Button>
          <Button variant="secondary" size="sm" onClick={resetDemo} disabled={demoBusy} className="gap-1.5">
            <RotateCcw className="w-3.5 h-3.5" />
            Reset Demo State
          </Button>
        </div>
      </div>

      {error && (
        <Card className="border-destructive/40 bg-destructive/5">
          <CardContent className="p-4 text-sm text-destructive">{error}</CardContent>
        </Card>
      )}

      {stats && !loading && (
        <Card className="ambient-panel overflow-hidden border-white/10">
          <CardContent className="grid grid-cols-1 items-center gap-6 p-5 sm:grid-cols-[auto_1fr_auto] sm:p-7">
            <div className="relative mx-auto grid h-40 w-40 place-items-center rounded-full sm:mx-0" style={{ background: `conic-gradient(from 220deg, #4bd7ef ${Math.max(0, Math.min(100, stats.mastery))}%, rgb(117 143 184 / 14%) 0)` }} aria-label={`Overall mastery ${stats.mastery} percent`}>
              <div className="grid h-[132px] w-[132px] place-items-center rounded-full border border-white/10 bg-[#0a1223] text-center shadow-[inset_0_0_30px_rgba(34,94,138,.18)]">
                <div><div className="text-3xl font-extrabold tracking-tight">{stats.mastery}%</div><div className="mt-1 text-[9px] font-bold uppercase tracking-[0.2em] text-muted-foreground">Overall mastery</div></div>
              </div>
            </div>
            <div className="text-center sm:text-left">
              <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-cyan-300">Learner model · live state</div>
              <h2 className="mt-2 text-xl font-semibold">A knowledge profile in motion</h2>
              <p className="mt-2 max-w-xl text-sm leading-relaxed text-muted-foreground">Mastery reflects the learner model’s current view across your concepts. Focus areas and recommendations update as you practice.</p>
            </div>
            <div className="grid grid-cols-2 gap-3 sm:w-52 sm:grid-cols-1">
              <div className="rounded-lg border border-white/10 bg-black/15 p-3"><p className="text-xl font-bold">{stats.topics_mastered}</p><p className="text-[10px] text-muted-foreground">Topics mastered</p></div>
              <div className="rounded-lg border border-white/10 bg-black/15 p-3"><p className="text-xl font-bold">{stats.quiz_accuracy}%</p><p className="text-[10px] text-muted-foreground">Quiz accuracy</p></div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 1. NEXT BEST ACTION HERO CARD */}
      {loading ? (
        <Card className="ambient-panel border-primary/20">
          <CardContent className="p-10 text-center text-muted-foreground">
            Analyzing your learner model and identifying your Next Best Action...
          </CardContent>
        </Card>
      ) : recommendation ? (
        <Card className="ambient-panel relative overflow-hidden border-primary/30 shadow-[0_24px_70px_rgba(20,100,153,.14)]">
          <div aria-hidden="true" className="pointer-events-none absolute -right-16 -top-24 h-64 w-64 rounded-full bg-cyan-400/10 blur-3xl" />
          <div className="relative space-y-6 p-6 sm:p-8">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-primary/10 rounded-xl text-primary">
                  <Zap className="w-7 h-7" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold tracking-wider text-primary uppercase">
                      ✦ NEXT BEST ACTION
                    </span>
                    <Badge variant="outline" className="text-[10px] font-semibold">
                      Priority {recommendation.priority}/10
                    </Badge>
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground mt-0.5">
                    {recommendation.title}
                  </h2>
                </div>
              </div>

              <div className="flex items-center gap-2 text-xs text-muted-foreground font-semibold">
                <Clock className="w-4 h-4 text-primary" />
                <span>{recommendation.duration_minutes ?? recommendation.recommended_duration ?? 15} min session</span>
              </div>
            </div>

            <p className="text-muted-foreground text-sm sm:text-base leading-relaxed max-w-3xl">
              {recommendation.description}
            </p>

            <div className="pt-2 flex flex-wrap items-center gap-4">
              {recommendation.action === 'adaptive_practice' ? (
                <Button size="lg" asChild className="gap-2 shadow-md">
                  <Link to="/adaptive-practice">
                    <Zap className="w-4 h-4" />
                    Start Adaptive Session
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </Button>
              ) : (
                <Button size="lg" asChild className="gap-2 shadow-md">
                  <Link to="/materials">
                    <BookOpen className="w-4 h-4" />
                    {recommendation.action === 'upload' ? 'Upload Study Material' : 'Continue Learning'}
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </Button>
              )}

              <Button variant="outline" size="lg" asChild className="gap-2">
                <Link to="/knowledge-map">
                  <Network className="w-4 h-4 text-primary" />
                  Inspect in Knowledge Map
                </Link>
              </Button>
            </div>
          </div>
        </Card>
      ) : null}

      {/* 2. KEY LEARNER STATS */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'Overall Mastery', value: `${stats.mastery}%`, icon: Brain, color: 'text-primary' },
            { label: 'Quiz Accuracy', value: `${stats.quiz_accuracy}%`, icon: Target, color: 'text-emerald-600' },
            { label: 'Active Streak', value: `${stats.streak_days} ${stats.streak_days === 1 ? 'day' : 'days'}`, icon: TrendingUp, color: 'text-blue-600' },
            { label: 'Topics Mastered', value: `${stats.topics_mastered}`, icon: Sparkles, color: 'text-purple-600' },
          ].map((stat) => (
            <Card key={stat.label} className="border-2 shadow-sm">
              <CardContent className="p-5">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-muted/60">
                    <stat.icon className={`w-5 h-5 ${stat.color}`} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-foreground">{stat.value}</p>
                    <p className="text-xs text-muted-foreground font-medium">{stat.label}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* 3. TWO-COLUMN: WEAK TOPICS + RECENT ACTIVITY */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Weak Topics Needing Attention */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-rose-500" />
              Focus Areas & Weak Topics
            </h2>
            <Link to="/knowledge-map" className="text-xs font-semibold text-primary hover:underline">
              View Map →
            </Link>
          </div>

          {data?.weak_topics && data.weak_topics.length > 0 ? (
            <div className="space-y-3">
              {data.weak_topics.map((topic) => (
                <Card key={topic.concept_id} className="border transition-all hover:border-primary/50">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm">{topic.name}</span>
                        <Badge
                          variant={
                            topic.learning_status === 'needs_foundation'
                              ? 'destructive'
                              : topic.learning_status === 'developing'
                              ? 'secondary'
                              : 'default'
                          }
                          className="text-[10px] capitalize"
                        >
                          {topic.learning_status.replace('_', ' ')}
                        </Badge>
                      </div>
                      <span className="text-xs font-bold text-foreground">{Math.round(topic.mastery)}%</span>
                    </div>
                    <Progress value={topic.mastery} className="h-2 mb-3" />
                    <div className="flex justify-end gap-2">
                      <Button size="sm" variant="outline" asChild className="h-7 text-xs gap-1">
                        <Link to={`/knowledge-map?concept=${topic.concept_id}`}>Inspect Details</Link>
                      </Button>
                      <Button size="sm" asChild className="h-7 text-xs gap-1">
                        <Link to={`/adaptive-practice?concept=${topic.concept_id}`}>Practice Now</Link>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-6 text-center text-sm text-muted-foreground">
                All concepts are currently in proficient or mastered status! Great job.
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right: Recent Learning Feed */}
        <div className="lg:col-span-5 space-y-4">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Clock className="w-5 h-5 text-primary" />
            Learning Activity Log
          </h2>

          <Card className="border-2 shadow-sm">
            <CardContent className="p-4 space-y-3">
              {data?.recent_activity && data.recent_activity.length > 0 ? (
                data.recent_activity.map((activity, index) => (
                  <div
                    key={index}
                    className="flex items-start justify-between py-2.5 border-b last:border-0 text-xs"
                  >
                    <div className="space-y-0.5">
                      <span className="font-semibold text-foreground block">{activity.action}</span>
                      <span className="text-[10px] uppercase font-mono text-muted-foreground">
                        {activity.activity_type?.replace('_', ' ') || 'activity'}
                      </span>
                    </div>
                    {activity.created_at && (
                      <span className="text-[10px] text-muted-foreground shrink-0 mt-0.5">
                        {new Date(activity.created_at).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-6 text-xs text-muted-foreground">
                  No learning activities logged yet.
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
