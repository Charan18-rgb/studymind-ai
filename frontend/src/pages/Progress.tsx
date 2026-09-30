import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress as ProgressBar } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import {
  TrendingUp,
  Target,
  BookOpen,
  Award,
  BarChart3,
  CheckCircle2,
  PieChart,
  Calendar,
} from 'lucide-react'
import { api, AnalyticsResponse } from '@/lib/api'

export default function ProgressPage() {
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    setLoading(true)
    try {
      const data = await api.getAnalytics()
      setAnalytics(data)
    } catch (err) {
      console.error('Failed to load analytics:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading || !analytics) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Progress & Analytics</h1>
        <Card>
          <CardContent className="p-12 text-center text-muted-foreground animate-pulse">
            Analyzing your learner model and historical trajectory...
          </CardContent>
        </Card>
      </div>
    )
  }

  const { metrics, topic_mastery, accuracy_trend, weekly_activity, difficulty_distribution } = analytics

  if (metrics.questions_answered === 0) return <div className="space-y-6"><h1 className="text-3xl font-bold tracking-tight">Progress & Analytics</h1><Card className="ambient-panel"><CardContent className="space-y-3 p-10 text-center"><BarChart3 className="mx-auto h-10 w-10 text-primary" /><h2 className="text-lg font-semibold">Complete your first assessment to see learning analytics</h2><p className="text-sm text-muted-foreground">Your progress view will reflect answers and practice recorded for your account.</p></CardContent></Card></div>

  const topMetrics = [
    { label: 'Overall Mastery', value: `${metrics.overall_mastery}%`, icon: Target, color: 'text-primary' },
    { label: 'Quiz Accuracy', value: `${metrics.overall_accuracy}%`, icon: CheckCircle2, color: 'text-emerald-600' },
    { label: 'Questions Answered', value: `${metrics.questions_answered}`, icon: BookOpen, color: 'text-blue-600' },
    { label: 'Topics Mastered', value: `${metrics.topics_mastered} / ${metrics.total_topics}`, icon: Award, color: 'text-purple-600' },
  ]

  const maxWeeklySessions = Math.max(...weekly_activity.map((d) => d.sessions), 1)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Progress & Learner Analytics</h1>
        <p className="text-muted-foreground text-sm">
          Track concept mastery, assessment results, and study activity recorded by your learner model.
        </p>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {topMetrics.map((metric) => (
          <Card key={metric.label} className="border-2 shadow-sm">
            <CardContent className="p-5">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-muted/60">
                  <metric.icon className={`w-5 h-5 ${metric.color}`} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-foreground">{metric.value}</p>
                  <p className="text-xs text-muted-foreground font-medium">{metric.label}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Two Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Topic-Level Mastery */}
        <div className="lg:col-span-7 space-y-6">
          <Card className="border-2 shadow-sm">
            <CardHeader className="py-4 border-b bg-muted/20">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-primary" />
                Concept Mastery Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent className="p-5 space-y-4">
              {topic_mastery.map((topic) => (
                <div key={topic.name} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-foreground text-sm">{topic.name}</span>
                      <Badge
                        variant={
                          topic.mastery >= 80
                            ? 'default'
                            : topic.mastery < 40
                            ? 'destructive'
                            : 'secondary'
                        }
                        className="text-[10px] capitalize px-1.5 py-0"
                      >
                        {topic.status.replace('_', ' ')}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-muted-foreground">{topic.accuracy}% accuracy</span>
                      <span className="font-bold text-primary">{Math.round(topic.mastery)}%</span>
                    </div>
                  </div>
                  <ProgressBar value={topic.mastery} className="h-2" />
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Quiz Accuracy Over Time */}
          <Card className="border-2 shadow-sm">
            <CardHeader className="py-4 border-b bg-muted/20">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-600" />
                Assessment Performance History
              </CardTitle>
            </CardHeader>
            <CardContent className="p-5">
              <div className="space-y-3">
                {accuracy_trend.length === 0 ? <p className="py-8 text-center text-sm text-muted-foreground">Assessment results will appear here after a quiz or practice session.</p> : accuracy_trend.map((trend, i) => (
                  <div key={i} className="flex items-center justify-between text-xs p-2.5 rounded-lg bg-muted/30 border">
                    <div className="flex items-center gap-2.5">
                      <span className="font-bold text-foreground">{trend.attempt}</span>
                      <span className="text-muted-foreground">({trend.date})</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-32 hidden sm:block">
                        <ProgressBar value={trend.score} className="h-1.5" />
                      </div>
                      <span className="font-bold text-foreground">{trend.score}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Weekly Cadence & Difficulty Distribution */}
        <div className="lg:col-span-5 space-y-6">
          {/* Weekly Study Activity */}
          <Card className="border-2 shadow-sm">
            <CardHeader className="py-4 border-b bg-muted/20">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Calendar className="w-4 h-4 text-blue-600" />
                Practice Activity
              </CardTitle>
            </CardHeader>
            <CardContent className="p-5">
              {!weekly_activity.some((day) => day.sessions > 0) ? <p className="py-8 text-center text-sm text-muted-foreground">No study activity has been recorded yet.</p> : <div className="flex items-end justify-between h-44 gap-2 pt-4">
                {weekly_activity.map((day) => (
                  <div key={day.day} className="flex-1 flex flex-col items-center gap-1.5">
                    <div className="w-full bg-muted/70 rounded-t-md h-32 flex items-end">
                      <div
                        className="w-full bg-gradient-to-t from-primary/70 to-cyan-300 rounded-t-md transition-all hover:brightness-110"
                        style={{ height: `${day.sessions ? Math.max((day.sessions / maxWeeklySessions) * 100, 6) : 0}%` }}
                      />
                    </div>
                    <span className="text-[11px] font-semibold text-muted-foreground">{day.day}</span>
                    <span className="text-[10px] font-bold text-foreground">{day.sessions} {day.sessions === 1 ? 'session' : 'sessions'}</span>
                  </div>
                ))}
              </div>}
            </CardContent>
          </Card>

          {/* Question Difficulty Distribution */}
          <Card className="border-2 shadow-sm">
            <CardHeader className="py-4 border-b bg-muted/20">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <PieChart className="w-4 h-4 text-purple-600" />
                Difficulty Calibration
              </CardTitle>
            </CardHeader>
            <CardContent className="p-5 space-y-3">
              {[
                { label: 'Easy (Foundational)', count: difficulty_distribution.easy, color: 'bg-emerald-500' },
                { label: 'Medium (Core Traversal/Logic)', count: difficulty_distribution.medium, color: 'bg-blue-500' },
                { label: 'Hard (Complex Networks/Graph)', count: difficulty_distribution.hard, color: 'bg-purple-500' },
              ].map((diff) => (
                <div key={diff.label} className="flex items-center justify-between text-xs p-2 rounded bg-muted/30">
                  <div className="flex items-center gap-2">
                    <span className={`w-2.5 h-2.5 rounded-full ${diff.color}`} />
                    <span className="font-medium text-foreground">{diff.label}</span>
                  </div>
                  <span className="font-bold">{diff.count} questions</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
