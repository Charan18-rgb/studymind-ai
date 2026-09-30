import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  CheckCircle2,
  Sparkles,
} from 'lucide-react'
import { api, StudyPlanResponse } from '@/lib/api'

export default function StudyPlan() {
  const [plan, setPlan] = useState<StudyPlanResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [hoursPerDay, setHoursPerDay] = useState(2)
  const [preferredTime, setPreferredTime] = useState('morning')
  const [examDate, setExamDate] = useState('')
  const [generating, setGenerating] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    loadStudyPlan()
  }, [])

  const loadStudyPlan = async () => {
    setLoading(true)
    try {
      const data = await api.getCurrentStudyPlan()
      setPlan(data)
    } catch (err) {
      console.error('Failed to load study plan:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleGeneratePlan = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError(null)
    setGenerating(true)
    try {
      const newPlan = await api.generateStudyPlan({
        hours_per_day: Number(hoursPerDay) || 2,
        preferred_study_time: preferredTime,
        exam_date: examDate || undefined,
      })
      setPlan(newPlan)
      setShowCreate(false)
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Failed to generate plan')
    } finally {
      setGenerating(false)
    }
  }

  if (!loading && plan?.items.length === 0) return <div className="space-y-6"><h1 className="text-3xl font-bold tracking-tight">Study Plan</h1><Card className="ambient-panel"><CardContent className="space-y-3 p-10 text-center"><Sparkles className="mx-auto h-10 w-10 text-primary" /><h2 className="text-lg font-semibold">Build your learner model first</h2><p className="text-sm text-muted-foreground">Your personalized study plan will appear after StudyMind understands your learning material and current mastery.</p></CardContent></Card></div>

  const handleToggleItem = async (itemId: number) => {
    if (!plan) return
    // Optimistic update
    const updatedItems = plan.items.map((it) =>
      it.id === itemId ? { ...it, completed: !it.completed } : it
    )
    const completedCount = updatedItems.filter((it) => it.completed).length
    const rate = round((completedCount / updatedItems.length) * 100, 1)

    setPlan({
      ...plan,
      items: updatedItems,
      completed_items: completedCount,
      completion_rate: rate,
    })

    try {
      await api.toggleStudyPlanItem(itemId)
    } catch (err) {
      console.error('Toggle error:', err)
      // Revert if error
      loadStudyPlan()
    }
  }

  const round = (val: number, decimals = 1) => Number(Math.round(Number(val + 'e' + decimals)) + 'e-' + decimals)

  if (loading || !plan) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Adaptive Study Planner</h1>
        <Card>
          <CardContent className="p-12 text-center text-muted-foreground animate-pulse">
            Synthesizing weak topics and knowledge graph into daily schedule...
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Adaptive Study Planner</h1>
          <p className="text-muted-foreground text-sm">
            AI-generated study schedule prioritized by your weak topics and prerequisite dependencies.
          </p>
        </div>
        <Button onClick={() => setShowCreate(!showCreate)} className="gap-2 shadow-sm">
          <Sparkles className="w-4 h-4" />
          {showCreate ? 'Close Form' : 'Regenerate Adaptive Plan'}
        </Button>
      </div>

      {/* Plan Generation Form Drawer */}
      {showCreate && (
        <Card className="border-2 border-primary/30 shadow-md">
          <CardHeader className="py-4 bg-muted/20 border-b">
            <CardTitle className="text-base font-semibold">Customize Study Constraints</CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <form onSubmit={handleGeneratePlan} className="space-y-4">
              {formError && <p role="alert" className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">{formError}</p>}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="text-xs font-semibold block mb-1.5">Target Exam Date</label>
                  <Input
                    type="date"
                    value={examDate}
                    onChange={(e) => setExamDate(e.target.value)}
                    className="text-xs"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold block mb-1.5">Daily Study Hours</label>
                  <Input
                    type="number"
                    min="1"
                    max="8"
                    value={hoursPerDay}
                    onChange={(e) => setHoursPerDay(Number(e.target.value))}
                    className="text-xs"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold block mb-1.5">Preferred Time Window</label>
                  <select
                    value={preferredTime}
                    onChange={(e) => setPreferredTime(e.target.value)}
                    className="w-full h-9 px-3 py-1 border rounded-md bg-background text-xs"
                  >
                    <option value="morning">Morning (09:00 - 12:00)</option>
                    <option value="afternoon">Afternoon (14:00 - 17:00)</option>
                    <option value="evening">Evening (18:00 - 21:00)</option>
                  </select>
                </div>
              </div>

              <div className="pt-2 flex justify-end">
                <Button type="submit" disabled={generating} className="gap-2">
                  <Sparkles className="w-4 h-4" />
                  {generating ? 'Re-optimizing Plan...' : 'Generate New Schedule'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Weekly Progress Card */}
      <Card className="border-2 shadow-sm bg-gradient-to-br from-card to-primary/[0.03]">
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-3">
            <div>
              <span className="text-xs font-bold text-primary uppercase tracking-wider">Active Strategy</span>
              <h3 className="text-xl font-bold text-foreground mt-0.5">{plan.title}</h3>
            </div>
            <div className="text-right">
              <span className="text-2xl font-black text-primary">{Math.round(plan.completion_rate)}%</span>
              <p className="text-xs text-muted-foreground">
                {plan.completed_items} of {plan.total_items} items completed
              </p>
            </div>
          </div>
          <Progress value={plan.completion_rate} className="h-2.5" />
        </CardContent>
      </Card>

      {/* Schedule Items List */}
      <div className="space-y-3">
        <h2 className="text-lg font-bold">Planned Learning Sessions</h2>
        {plan.items.map((item, index) => (
          <Card
            key={item.id}
            onClick={() => handleToggleItem(item.id)}
            className={`cursor-pointer transition-all border hover:border-primary/50 ${
              item.completed ? 'opacity-65 bg-muted/30 border-muted' : 'border-border shadow-sm'
            }`}
          >
            <CardContent className="p-4 sm:p-5">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3.5">
                  <span aria-hidden="true" className="hidden sm:grid h-9 w-9 shrink-0 place-items-center rounded-xl border border-primary/20 bg-primary/10 text-xs font-bold text-primary">{String(index + 1).padStart(2, '0')}</span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleToggleItem(item.id)
                    }}
                    className={`p-1.5 rounded-lg border transition-colors ${
                      item.completed
                        ? 'bg-emerald-500 text-white border-emerald-500'
                        : 'bg-muted/50 text-muted-foreground hover:bg-primary/20'
                    }`}
                  >
                    <CheckCircle2 className="w-5 h-5" />
                  </button>
                  <div>
                    <h4
                      className={`font-semibold text-sm ${
                        item.completed ? 'line-through text-muted-foreground' : 'text-foreground'
                      }`}
                    >
                      {item.topic}
                    </h4>
                    <p className="text-xs text-muted-foreground">
                      {item.day} • {item.time} ({item.duration})
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Badge
                    variant={
                      item.activity === 'Practice'
                        ? 'default'
                        : item.activity === 'Quiz'
                        ? 'secondary'
                        : 'outline'
                    }
                    className="capitalize text-[11px]"
                  >
                    {item.activity}
                  </Badge>
                  <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                    {item.difficulty}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
