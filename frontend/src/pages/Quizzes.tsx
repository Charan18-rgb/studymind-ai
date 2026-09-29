import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Target,
  Sparkles,
  ArrowRight,
  Network,
  Zap,
} from 'lucide-react'
import { api, GraphNode, QuizSession, QuizSubmitResult } from '@/lib/api'

export default function Quizzes() {
  const [concepts, setConcepts] = useState<GraphNode[]>([])
  const [selectedConceptId, setSelectedConceptId] = useState<number | null>(null)
  const [difficulty, setDifficulty] = useState<string>('medium')
  const [numQuestions, setNumQuestions] = useState<number>(5)

  // Quiz execution state
  const [generating, setGenerating] = useState(false)
  const [activeQuiz, setActiveQuiz] = useState<QuizSession | null>(null)
  const [currentIdx, setCurrentIdx] = useState(0)
  const [selectedOption, setSelectedOption] = useState<string | null>(null)
  const [recordedAnswers, setRecordedAnswers] = useState<
    Array<{ question_id: number; selected_answer: string; time_spent_seconds: number }>
  >([])
  const [submitting, setSubmitting] = useState(false)
  const [quizResult, setQuizResult] = useState<QuizSubmitResult | null>(null)
  const [startTime, setStartTime] = useState<number>(Date.now())

  useEffect(() => {
    loadConcepts()
  }, [])

  const loadConcepts = async () => {
    try {
      const graph = await api.getKnowledgeGraph()
      setConcepts(graph.nodes || [])
      if (graph.nodes && graph.nodes.length > 0) {
        setSelectedConceptId(graph.nodes[0].id)
      }
    } catch (err) {
      console.error('Failed to load concepts for quizzes:', err)
    }
  }

  const handleStartQuiz = async () => {
    if (!selectedConceptId) return
    setGenerating(true)
    setQuizResult(null)
    setCurrentIdx(0)
    setSelectedOption(null)
    setRecordedAnswers([])
    setStartTime(Date.now())

    try {
      const quiz = await api.generateQuiz(selectedConceptId, difficulty, numQuestions)
      setActiveQuiz(quiz)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to generate quiz')
    } finally {
      setGenerating(false)
    }
  }

  const handleAnswerQuestion = () => {
    if (!selectedOption || !activeQuiz) return
    const currentQ = activeQuiz.questions[currentIdx]
    const elapsed = Math.max(1, Math.round((Date.now() - startTime) / 1000))

    const newAnswer = {
      question_id: currentQ.id,
      selected_answer: selectedOption,
      time_spent_seconds: elapsed,
    }
    const updated = [...recordedAnswers, newAnswer]
    setRecordedAnswers(updated)

    if (currentIdx < activeQuiz.questions.length - 1) {
      setCurrentIdx(currentIdx + 1)
      setSelectedOption(null)
      setStartTime(Date.now())
    } else {
      // Finished all questions - Submit
      submitQuizSession(updated)
    }
  }

  const submitQuizSession = async (
    answersToSubmit: Array<{ question_id: number; selected_answer: string; time_spent_seconds: number }>
  ) => {
    if (!activeQuiz) return
    setSubmitting(true)
    const quizId = activeQuiz.quiz_id || activeQuiz.id
    if (!quizId) return

    try {
      const res = await api.submitQuiz(quizId, answersToSubmit)
      setQuizResult(res)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to submit quiz results')
    } finally {
      setSubmitting(false)
    }
  }

  // QUIZ RESULTS VIEW
  if (quizResult) {
    const isGain = quizResult.improvement && quizResult.improvement > 0
    return (
      <div className="max-w-2xl mx-auto space-y-6 animate-fadeIn">
        <Card className="border-2 shadow-lg">
          <CardHeader className="bg-primary/5 text-center pb-4 border-b">
            <Badge className="w-fit mx-auto mb-2">Concept Assessment Complete</Badge>
            <CardTitle className="text-3xl font-bold">Quiz Results</CardTitle>
            <p className="text-sm text-muted-foreground">
              Topic: <strong>{quizResult.concept || 'Data Structures'}</strong>
            </p>
          </CardHeader>
          <CardContent className="p-6 sm:p-8 space-y-6">
            <div className="grid grid-cols-2 gap-4 text-center">
              <div className="p-4 rounded-xl bg-muted/40 border">
                <span className="text-xs text-muted-foreground uppercase font-semibold">Quiz Score</span>
                <div className="text-3xl font-extrabold text-primary mt-1">{quizResult.score}%</div>
                <span className="text-xs text-muted-foreground">
                  {quizResult.correct_answers} / {quizResult.total_questions} Correct
                </span>
              </div>

              <div className="p-4 rounded-xl bg-muted/40 border">
                <span className="text-xs text-muted-foreground uppercase font-semibold">Mastery Update</span>
                <div className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1">
                  {quizResult.after_mastery !== undefined
                    ? `${Math.round(quizResult.after_mastery)}%`
                    : 'Updated'}
                </div>
                {quizResult.improvement !== undefined && (
                  <span className="text-xs font-semibold text-emerald-600">
                    {isGain ? `+${quizResult.improvement} points` : 'Calibrated'}
                  </span>
                )}
              </div>
            </div>

            {quizResult.next_action && (
              <div className="p-4 rounded-lg bg-primary/5 border border-primary/20 space-y-1.5">
                <div className="flex items-center gap-1.5 text-primary text-xs font-semibold">
                  <Zap className="w-3.5 h-3.5" /> Next Best Action
                </div>
                <h4 className="font-bold text-sm">{quizResult.next_action.title}</h4>
                <p className="text-xs text-muted-foreground">{quizResult.next_action.description}</p>
              </div>
            )}

            <div className="flex gap-3 pt-2">
              <Button onClick={() => setActiveQuiz(null)} variant="outline" className="flex-1">
                Take Another Quiz
              </Button>
              <Button asChild className="flex-1 gap-2">
                <Link to="/knowledge-map">
                  <Network className="w-4 h-4" /> View Knowledge Map
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // ACTIVE QUIZ QUESTIONS VIEW
  if (activeQuiz && activeQuiz.questions && activeQuiz.questions.length > 0) {
    const currentQ = activeQuiz.questions[currentIdx]
    const progress = ((currentIdx + 1) / activeQuiz.questions.length) * 100

    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">{activeQuiz.title || 'Concept Quiz'}</h2>
            <span className="text-xs text-muted-foreground">
              Question {currentIdx + 1} of {activeQuiz.questions.length}
            </span>
          </div>
          <Progress value={progress} className="w-28 h-2" />
        </div>

        <Card className="border-2 shadow-md">
          <CardContent className="p-6 sm:p-8 space-y-6">
            <p className="text-lg font-medium leading-relaxed">{currentQ.question_text}</p>

            <div className="space-y-3">
              {currentQ.options.map((opt, i) => {
                const isSelected = selectedOption === opt
                return (
                  <button
                    key={i}
                    onClick={() => setSelectedOption(opt)}
                    className={`w-full flex items-center p-3.5 rounded-xl border text-left text-sm transition-all ${
                      isSelected
                        ? 'border-primary bg-primary/10 text-primary font-semibold shadow-sm'
                        : 'border-border hover:bg-muted/40 text-foreground'
                    }`}
                  >
                    <span
                      className={`w-6 h-6 rounded flex items-center justify-center text-xs font-bold mr-3 border ${
                        isSelected
                          ? 'bg-primary text-primary-foreground border-primary'
                          : 'bg-muted text-muted-foreground'
                      }`}
                    >
                      {String.fromCharCode(65 + i)}
                    </span>
                    {opt}
                  </button>
                )
              })}
            </div>

            <div className="pt-4 border-t flex justify-end">
              <Button
                disabled={!selectedOption || submitting}
                onClick={handleAnswerQuestion}
                size="lg"
                className="gap-2"
              >
                {submitting
                  ? 'Grading Quiz...'
                  : currentIdx < activeQuiz.questions.length - 1
                  ? 'Next Question'
                  : 'Submit Quiz'}
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // QUIZ SELECTION / GENERATOR VIEW
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Concept-Level Quizzes</h1>
        <p className="text-muted-foreground text-sm">
          Target specific concepts in your knowledge graph to validate understanding and advance mastery.
        </p>
      </div>

      <Card className="border-2 shadow-sm">
        <CardHeader className="border-b bg-muted/20">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <Target className="w-5 h-5 text-primary" /> Create Concept Assessment
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          {/* Concept selector */}
          <div className="space-y-2">
            <label className="text-sm font-semibold">Select Topic to Test</label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
              {concepts.map((concept) => {
                const isSelected = selectedConceptId === concept.id
                return (
                  <button
                    key={concept.id}
                    onClick={() => setSelectedConceptId(concept.id)}
                    className={`p-3 rounded-lg border text-left text-xs transition-all ${
                      isSelected
                        ? 'border-primary bg-primary/10 text-primary font-bold ring-2 ring-primary/20'
                        : 'border-border hover:bg-muted/40'
                    }`}
                  >
                    <div className="font-semibold text-sm text-foreground">{concept.name}</div>
                    <div className="text-muted-foreground mt-0.5">
                      Mastery: {Math.round(concept.mastery)}%
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Difficulty & Question count */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-semibold block mb-2">Target Difficulty</label>
              <div className="flex gap-2">
                {['easy', 'medium', 'hard'].map((d) => (
                  <Button
                    key={d}
                    type="button"
                    variant={difficulty === d ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setDifficulty(d)}
                    className="capitalize flex-1 text-xs"
                  >
                    {d}
                  </Button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-sm font-semibold block mb-2">Questions Count</label>
              <div className="flex gap-2">
                {[3, 5, 10].map((n) => (
                  <Button
                    key={n}
                    type="button"
                    variant={numQuestions === n ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setNumQuestions(n)}
                    className="flex-1 text-xs"
                  >
                    {n} Questions
                  </Button>
                ))}
              </div>
            </div>
          </div>

          <div className="pt-2">
            <Button
              onClick={handleStartQuiz}
              disabled={generating || !selectedConceptId}
              size="lg"
              className="w-full gap-2 shadow"
            >
              {generating ? (
                'Generating Targeted Quiz...'
              ) : (
                <>
                  <Sparkles className="w-4 h-4" /> Start Concept Assessment
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
