import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Target,
  Zap,
  BookOpen,
  ArrowRight,
  Sparkles,
  RotateCcw,
  Home,
  Network,
} from 'lucide-react'
import {
  api,
  AdaptiveSessionResponse,
  AdaptiveQuestion,
  AdaptiveAnswer,
  AdaptiveSubmitResult,
} from '@/lib/api'

export default function AdaptivePractice() {
  const navigate = useNavigate()
  const [sessionData, setSessionData] = useState<AdaptiveSessionResponse['session'] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Practice state
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [showFeedback, setShowFeedback] = useState(false)
  const [recordedAnswers, setRecordedAnswers] = useState<AdaptiveAnswer[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [submitResult, setSubmitResult] = useState<AdaptiveSubmitResult | null>(null)
  const [startTime, setStartTime] = useState<number>(Date.now())

  useEffect(() => {
    startSession()
  }, [])

  const startSession = async () => {
    setLoading(true)
    setError(null)
    setSubmitResult(null)
    setCurrentQuestionIdx(0)
    setSelectedAnswer(null)
    setShowFeedback(false)
    setRecordedAnswers([])
    setStartTime(Date.now())

    try {
      const res = await api.createAdaptiveSession()
      if (res.session) {
        setSessionData(res.session)
      } else {
        setError(res.message || 'No weak topic found. Try loading demo data or uploading a document.')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initialize adaptive session')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectOption = (option: string) => {
    if (showFeedback) return
    setSelectedAnswer(option)
  }

  const handleCheckAnswer = () => {
    if (!selectedAnswer || !sessionData) return
    const currentQ = sessionData.questions[currentQuestionIdx]
    const elapsedSeconds = Math.max(1, Math.round((Date.now() - startTime) / 1000))

    const newAnswer: AdaptiveAnswer = {
      question_id: currentQ.id,
      selected_answer: selectedAnswer,
      time_spent_seconds: elapsedSeconds,
    }

    const updatedAnswers = [...recordedAnswers, newAnswer]
    setRecordedAnswers(updatedAnswers)
    setShowFeedback(true)
  }

  const handleNextQuestion = async () => {
    if (!sessionData) return

    if (currentQuestionIdx < sessionData.questions.length - 1) {
      setCurrentQuestionIdx(currentQuestionIdx + 1)
      setSelectedAnswer(null)
      setShowFeedback(false)
      setStartTime(Date.now())
    } else {
      // Last question completed - Submit session!
      await submitCompletedSession()
    }
  }

  const submitCompletedSession = async () => {
    if (!sessionData) return
    setSubmitting(true)
    try {
      const res = await api.submitAdaptiveSession(
        sessionData.session_id,
        recordedAnswers
      )
      setSubmitResult(res)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit adaptive session')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Adaptive Learning Engine</h1>
          <p className="text-muted-foreground">Diagnosing knowledge gaps and generating targeted practice...</p>
        </div>
        <Card className="border-2 shadow-sm">
          <CardContent className="p-12 text-center space-y-4">
            <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin mx-auto" />
            <p className="font-semibold text-lg">Synthesizing personalized question sequence...</p>
            <p className="text-xs text-muted-foreground">Adjusting difficulty to match your mastery trajectory</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error || !sessionData) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Adaptive Practice</h1>
        <Card className="border-2 shadow-sm">
          <CardContent className="p-10 text-center space-y-4">
            <Target className="w-14 h-14 text-muted-foreground mx-auto opacity-50" />
            <h3 className="text-xl font-semibold">No Adaptive Session Ready</h3>
            <p className="text-sm text-muted-foreground max-w-md mx-auto">
              {error || 'Load demo data from the dashboard to practice with predefined learner mastery.'}
            </p>
            <div className="flex justify-center gap-3 pt-2">
              <Button onClick={() => navigate('/')} variant="outline" className="gap-2">
                <Home className="w-4 h-4" /> Return to Dashboard
              </Button>
              <Button onClick={startSession} className="gap-2">
                <RotateCcw className="w-4 h-4" /> Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // BEFORE / AFTER IMPROVEMENT SCREEN (The Hero Hackathon Moment)
  if (submitResult) {
    const isImprovement = submitResult.improvement > 0
    return (
      <div className="max-w-3xl mx-auto space-y-8 animate-fadeIn">
        {/* Celebration Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 text-xs font-semibold mb-2">
            <Sparkles className="w-4 h-4" /> Session complete · learner model updated
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight">Your next step is clearer.</h1>
          <p className="text-muted-foreground text-sm max-w-md mx-auto">
            Your real-time learner model has been updated based on your question-by-question performance.
          </p>
        </div>

        {/* Before / After Mastery Card */}
        <Card className="ambient-panel border-primary/30 shadow-xl overflow-hidden">
          <div className="bg-gradient-to-r from-primary/10 via-primary/5 to-transparent p-6 border-b border-white/10">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs uppercase tracking-wider font-semibold text-muted-foreground">
                  Target Concept
                </span>
                <h2 className="text-2xl font-bold text-foreground">{submitResult.concept}</h2>
              </div>
              <Badge className="text-xs font-bold px-3 py-1 bg-primary text-primary-foreground">
                Session Score: {submitResult.score}%
              </Badge>
            </div>
          </div>

          <CardContent className="p-6 sm:p-8 space-y-8">
            {/* Comparison Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center items-center">
              {/* BEFORE */}
              <div className="p-5 rounded-xl bg-muted/40 border border-white/10 space-y-1.5">
                <span className="text-xs font-bold text-muted-foreground uppercase">Before Session</span>
                <div className="text-3xl font-extrabold text-rose-500">
                  {submitResult.before_mastery.toFixed(1)}%
                </div>
                <span className="text-[11px] text-muted-foreground">Starting mastery</span>
              </div>

              {/* ARROW & DELTA */}
              <div className="flex flex-col items-center justify-center p-2">
                <div className="flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 text-primary mb-1">
                  <ArrowRight className="w-6 h-6" />
                </div>
                <span
                  className={`text-lg font-black ${
                    isImprovement ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-600'
                  }`}
                >
                  {isImprovement ? `+${submitResult.improvement.toFixed(1)} pts` : 'Calibrated'}
                </span>
                <span className="text-[10px] text-muted-foreground uppercase font-semibold">Mastery Gain</span>
              </div>

              {/* AFTER */}
              <div className="p-5 rounded-xl bg-emerald-500/10 border border-emerald-400/25 space-y-1.5">
                <span className="text-xs font-bold text-emerald-300 uppercase">
                  After Session
                </span>
                <div className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">
                  {submitResult.after_mastery.toFixed(1)}%
                </div>
                <span className="text-[11px] text-emerald-300 font-semibold">Updated learner mastery</span>
              </div>
            </div>

            {/* Summary Message */}
            <div className="p-4 rounded-lg bg-muted/30 border border-white/10 text-sm text-foreground/90 leading-relaxed">
              <span className="font-semibold block mb-1">What changed</span>
              {submitResult.summary}
            </div>

            <div className="rounded-xl border border-primary/20 bg-card/60 p-4 shadow-[inset_0_0_26px_rgba(40,151,197,.06)]">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">Adaptive loop</p>
              <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-medium">
                <span className="rounded-full bg-muted px-3 py-2">Practice</span><ArrowRight className="h-4 w-4 text-primary" />
                <span className="rounded-full bg-muted px-3 py-2">Measure</span><ArrowRight className="h-4 w-4 text-primary" />
                <span className="rounded-full bg-primary/10 px-3 py-2 text-primary">Update learner model</span><ArrowRight className="h-4 w-4 text-primary" />
                <span className="rounded-full bg-muted px-3 py-2">Adapt next action</span>
              </div>
            </div>

            {/* Updated Next Action Card */}
            {submitResult.next_action && (
              <div className="ambient-panel rounded-xl border border-primary/25 p-5 space-y-3">
                <div className="flex items-center gap-2 text-primary font-semibold text-sm">
                  <Zap className="w-4 h-4" />
                  <span>Next best action</span>
                </div>
                <h4 className="font-bold text-lg text-foreground">{submitResult.next_action.title}</h4>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {submitResult.next_action.description}
                </p>
              </div>
            )}

            {/* Navigation Actions */}
            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <Button asChild size="lg" className="flex-1 gap-2 shadow">
                <Link to="/">
                  <Home className="w-4 h-4" /> Back to Dashboard
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="flex-1 gap-2">
                <Link to="/knowledge-map">
                  <Network className="w-4 h-4" /> View in Knowledge Map
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // ACTIVE QUESTION SOLVING VIEW
  const currentQ: AdaptiveQuestion = sessionData.questions[currentQuestionIdx]
  return (
    <div className="relative max-w-3xl mx-auto space-y-6">
      <div aria-hidden="true" className="practice-orbit pointer-events-none absolute inset-x-0 -top-24 -z-10 h-[32rem]" />
      {/* Session Top Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="capitalize text-xs font-semibold">
              Focused Learning Mode
            </Badge>
            <span className="text-xs text-muted-foreground">
              Target Concept: <strong className="text-foreground">{sessionData.target_concept.name}</strong>
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight mt-1">{sessionData.target_concept.name} Targeted Drills</h1>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <span className="text-xs font-bold text-muted-foreground">
              Question {currentQuestionIdx + 1} of {sessionData.questions.length}
            </span>
            <div className="mt-2 flex items-center gap-1" role="progressbar" aria-label="Session progress" aria-valuemin={0} aria-valuemax={sessionData.questions.length} aria-valuenow={currentQuestionIdx + 1}>
              {sessionData.questions.map((_, index) => <span key={index} className={`h-1.5 flex-1 rounded-full transition-colors ${index <= currentQuestionIdx ? 'bg-primary shadow-[0_0_8px_rgba(70,205,239,.45)]' : 'bg-muted'}`} />)}
            </div>
          </div>
        </div>
      </div>

      {/* Target Concept & Prerequisites Card */}
      <Card className="ambient-panel border-primary/20">
        <CardContent className="p-4">
          <p className="text-xs font-bold uppercase tracking-wide text-primary mb-1">Why these questions?</p>
          <p className="text-sm text-muted-foreground">
            {sessionData.prerequisites?.length
              ? `Your learner model shows ${sessionData.target_concept.name} at ${Math.round(sessionData.target_concept.current_mastery)}% mastery. This session targets it while accounting for its prerequisite${sessionData.prerequisites.length > 1 ? 's' : ''}: ${sessionData.prerequisites.map((p) => `${p.name} (${Math.round(p.mastery)}%)`).join(', ')}.`
              : `Your learner model shows ${sessionData.target_concept.name} at ${Math.round(sessionData.target_concept.current_mastery)}% mastery. This session targets that concept.`}
          </p>
        </CardContent>
      </Card>

      <Card className="bg-muted/20 border border-white/10 shadow-none">
        <CardContent className="p-4 flex flex-wrap items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-primary" />
            <span>
              Baseline Mastery: <strong>{Math.round(sessionData.target_concept.current_mastery)}%</strong>
            </span>
          </div>
          {sessionData.prerequisites && sessionData.prerequisites.length > 0 && (
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <span>Prerequisites considered:</span>
              {sessionData.prerequisites.map((p) => (
                <Badge key={p.id} variant="secondary" className="text-[10px]">
                  {p.name} ({Math.round(p.mastery)}%)
                </Badge>
              ))}
            </div>
          )}
          <Badge variant="outline" className="uppercase font-mono text-[10px]">
            Difficulty: {currentQ.difficulty || sessionData.difficulty}
          </Badge>
        </CardContent>
      </Card>

      {/* Question Card */}
      <Card className="ambient-panel border-white/10 shadow-xl">
        <CardHeader className="py-4 px-6 border-b border-white/10 bg-white/[0.025]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-primary">
              Targeted Question #{currentQuestionIdx + 1}
            </span>
            {currentQ.focus_area && (
              <Badge variant="outline" className="text-xs">
                Focus: {currentQ.focus_area}
              </Badge>
            )}
          </div>
        </CardHeader>

        <CardContent className="p-6 sm:p-8 space-y-6">
          <p className="text-lg sm:text-xl font-medium text-foreground leading-relaxed">
            {currentQ.question_text}
          </p>

          {/* Multiple Choice Options */}
          <div className="space-y-3">
            {currentQ.options &&
              currentQ.options.map((option, idx) => {
                const isSelected = selectedAnswer === option
                const letter = String.fromCharCode(65 + idx)

                return (
                  <button
                    key={idx}
                    disabled={showFeedback}
                    onClick={() => handleSelectOption(option)}
                    className={`w-full flex items-center p-4 rounded-xl border-2 text-left text-sm font-medium transition-all ${
                      isSelected
                        ? 'border-primary bg-primary/10 text-primary shadow-sm'
                        : 'border-border hover:border-muted-foreground/50 hover:bg-muted/30 text-foreground'
                    } ${showFeedback ? 'cursor-default' : 'cursor-pointer'}`}
                  >
                    <span
                      className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs mr-3.5 border ${
                        isSelected
                          ? 'bg-primary text-primary-foreground border-primary'
                          : 'bg-muted text-muted-foreground border-border'
                      }`}
                    >
                      {letter}
                    </span>
                    <span className="flex-1">{option}</span>
                  </button>
                )
              })}
          </div>

          {/* Action Footer: Check Answer vs Next Question */}
          <div className="pt-4 border-t flex items-center justify-between gap-4">
            <span className="text-xs text-muted-foreground">
              {showFeedback ? 'Review answer and continue' : 'Select the best option above'}
            </span>

            {!showFeedback ? (
              <Button
                disabled={!selectedAnswer}
                onClick={handleCheckAnswer}
                size="lg"
                className="gap-2 px-6"
              >
                Check Answer <ArrowRight className="w-4 h-4" />
              </Button>
            ) : (
              <Button
                onClick={handleNextQuestion}
                disabled={submitting}
                size="lg"
                className="gap-2 px-6"
              >
                {submitting ? (
                  'Updating Learner Model...'
                ) : currentQuestionIdx < sessionData.questions.length - 1 ? (
                  <>
                    Next Question <ArrowRight className="w-4 h-4" />
                  </>
                ) : (
                  <>
                    Complete & Compute Mastery <Sparkles className="w-4 h-4" />
                  </>
                )}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
