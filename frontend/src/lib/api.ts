const API = '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, init)
  if (!res.ok) {
    const text = await res.text()
    try {
      const errJson = JSON.parse(text)
      throw new Error(errJson.detail || errJson.message || `Request failed: ${res.status}`)
    } catch {
      throw new Error(text || `Request failed: ${res.status}`)
    }
  }
  return res.json()
}

export const api = {
  // Demo
  initializeDemo: () => request<{ message: string }>('/demo/initialize', { method: 'POST' }),
  resetDemo: () => request<{ message: string }>('/demo/reset', { method: 'POST' }),

  // Dashboard & Recommendations
  getDashboard: () => request<DashboardResponse>('/dashboard'),
  getNextAction: () => request<Recommendation>('/recommendations/next-action'),

  // Knowledge Graph & Concepts
  getKnowledgeGraph: (documentId?: number) =>
    request<KnowledgeGraph>(
      documentId ? `/concepts/graph?document_id=${documentId}` : '/concepts/graph'
    ),
  getConcept: (conceptId: number) => request<ConceptDetail>(`/concepts/${conceptId}`),
  getAdaptiveExplanation: (conceptId: number) =>
    request<AdaptiveExplanation>(`/concepts/${conceptId}/explanation`),
  getLearnerMastery: () => request<LearnerMastery[]>('/concepts/learner/mastery'),
  getWeakTopics: () => request<WeakTopic[]>('/concepts/learner/weak-topics'),
  getDiagnosis: () => request<DiagnosisResponse>('/concepts/learner/diagnosis'),

  // Adaptive Practice
  createAdaptiveSession: (documentId?: number) =>
    request<AdaptiveSessionResponse>(
      documentId ? `/adaptive/session?document_id=${documentId}` : '/adaptive/session',
      { method: 'POST' }
    ),
  submitAdaptiveSession: (sessionId: number, answers: AdaptiveAnswer[]) =>
    request<AdaptiveSubmitResult>(`/adaptive/session/${sessionId}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers }),
    }),

  // Quizzes
  generateQuiz: (conceptId: number, difficulty = 'medium', numQuestions = 5) =>
    request<QuizSession>(`/quizzes/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ concept_id: conceptId, difficulty, num_questions: numQuestions }),
    }),
  getQuiz: (quizId: number) => request<QuizSession>(`/quizzes/${quizId}`),
  submitQuiz: (quizId: number, answers: { question_id: number; selected_answer: string; time_spent_seconds?: number }[]) =>
    request<QuizSubmitResult>(`/quizzes/${quizId}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers }),
    }),

  // Documents & Notes RAG
  getDocuments: () => request<DocumentItem[]>('/documents/'),
  getDocument: (documentId: number) => request<DocumentItem>(`/documents/${documentId}`),
  uploadDocument: (file: File, title?: string) => {
    const form = new FormData()
    form.append('file', file)
    if (title) form.append('title', title)
    return request<DocumentItem>('/documents/upload', { method: 'POST', body: form })
  },
  askDocument: (documentId: number, question: string) =>
    request<AskResponse>(`/documents/${documentId}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    }),

  // Study Plans
  getCurrentStudyPlan: () => request<StudyPlanResponse>('/study-plans/current'),
  generateStudyPlan: (data: { hours_per_day: number; preferred_study_time: string; exam_date?: string }) =>
    request<StudyPlanResponse>('/study-plans/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),
  toggleStudyPlanItem: (itemId: number) =>
    request<{ id: number; is_completed: boolean }>(`/study-plans/items/${itemId}/toggle`, {
      method: 'POST',
    }),

  // Analytics
  getAnalytics: () => request<AnalyticsResponse>('/analytics'),
}

// -------------------------------------------------------------
// Type Definitions
// -------------------------------------------------------------

export interface Recommendation {
  type?: string
  target_concept: string | null
  target_concept_id?: number
  related_concept?: string | null
  related_concept_id?: number
  action: string
  title: string
  description: string
  duration_minutes?: number
  recommended_duration?: number
  reason: string
  priority: number
}

export interface DashboardResponse {
  user: { name: string; email: string; is_demo: boolean }
  stats: {
    mastery: number
    quiz_accuracy: number
    streak_days: number
    study_hours: number
    topics_mastered: number
  }
  weak_topics: WeakTopic[]
  recent_activity: {
    action: string
    activity_type?: string
    created_at?: string
    metadata?: Record<string, any>
  }[]
  next_best_action: Recommendation
}

export interface WeakTopic {
  concept_id: number
  name: string
  mastery: number
  accuracy?: number
  learning_status: string
  recent_accuracy?: number
}

export interface DiagnosisResponse {
  primary_weakness: {
    concept_id: number
    concept: string
    mastery: number
    accuracy: number
  } | null
  prerequisites: Array<{
    concept_id: number
    concept: string
    mastery: number
    accuracy: number
  }>
}

export interface KnowledgeGraph {
  document_id: number | null
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface GraphNode {
  id: number
  name: string
  description?: string
  difficulty?: string
  mastery: number
  accuracy: number
  total_attempts: number
  correct_attempts: number
  status: string
}

export interface GraphEdge {
  source: number
  target: number
  relationship: string
  confidence?: number
}

export interface ConceptDetail {
  id: number
  document_id: number
  name: string
  description?: string
  difficulty: string
  estimated_importance: number
  learner_mastery?: LearnerMastery
}

export interface AdaptiveExplanation {
  concept_id: number
  concept_name: string
  learner_mastery: number
  learning_status: string
  level_label: string
  prerequisites: string[]
  simple_explanation: string
  real_world_analogy?: string
  example?: string
  common_mistakes: string[]
  quick_check?: string
  why_this_matters?: string
}

export interface AdaptiveSessionResponse {
  session: {
    session_id: number
    target_concept: {
      id: number
      name: string
      description: string
      current_mastery: number
    }
    prerequisites: Array<{ id: number; name: string; mastery: number }>
    questions: AdaptiveQuestion[]
    difficulty: string
    focus_areas: string[]
  } | null
  message?: string
}

export interface AdaptiveQuestion {
  id: number
  question_text: string
  question_type?: string
  options: string[]
  difficulty: string
  focus_area?: string
}

export interface AdaptiveAnswer {
  question_id: number
  selected_answer: string
  time_spent_seconds?: number
}

export interface AdaptiveSubmitResult {
  before_mastery: number
  after_mastery: number
  improvement: number
  concept: string
  questions_completed: number
  score: number
  summary: string
  next_action: Recommendation
}

export interface QuizSession {
  quiz_id?: number
  id?: number
  title?: string
  concept?: string
  questions: Array<{
    id: number
    question_text: string
    options: string[]
    difficulty: string
    concept_id?: number
  }>
}

export interface QuizSubmitResult {
  quiz_id: number
  attempt_id: number
  score: number
  correct_answers: number
  total_questions: number
  concept?: string
  concept_id?: number
  before_mastery?: number
  after_mastery?: number
  improvement?: number
  next_action?: Recommendation
}

export interface DocumentItem {
  id: number
  title: string
  filename: string
  page_count: number
  status: string
  created_at?: string
}

export interface AskResponse {
  answer: string
  sources: { chunk_index: number; page_number?: number; excerpt: string }[]
  grounded: boolean
  disclaimer?: string
}

export interface LearnerMastery {
  id?: number
  concept_id: number
  mastery_score: number
  accuracy: number
  recent_accuracy?: number
  total_attempts?: number
  correct_attempts?: number
  learning_status: string
  consecutive_correct?: number
  consecutive_incorrect?: number
  confidence?: number
}

export interface StudyPlanResponse {
  id: number
  title: string
  hours_per_day: number
  preferred_study_time: string
  completion_rate: number
  total_items: number
  completed_items: number
  items: StudyPlanItemData[]
}

export interface StudyPlanItemData {
  id: number
  day: string
  day_index: number
  time: string
  topic: string
  concept_id?: number
  duration: string
  duration_minutes: number
  activity: string
  difficulty: string
  completed: boolean
}

export interface AnalyticsResponse {
  metrics: {
    overall_mastery: number
    overall_accuracy: number
    questions_answered: number
    topics_mastered: number
    total_topics: number
    study_hours: number
    streak_days: number
  }
  topic_mastery: Array<{
    name: string
    mastery: number
    accuracy: number
    status: string
    attempts: number
    difficulty: string
  }>
  accuracy_trend: Array<{
    attempt: string
    score: number
    date: string
  }>
  difficulty_distribution: {
    easy: number
    medium: number
    hard: number
  }
  status_distribution: {
    needs_foundation: number
    developing: number
    proficient: number
    mastered: number
  }
  weekly_activity: Array<{
    day: string
    date: string
    hours: number
    sessions: number
  }>
}
