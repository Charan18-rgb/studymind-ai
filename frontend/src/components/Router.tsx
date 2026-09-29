import { Routes, Route } from 'react-router-dom'
import Dashboard from '@/pages/Dashboard'
import Materials from '@/pages/Materials'
import KnowledgeMap from '@/pages/KnowledgeMap'
import AdaptivePractice from '@/pages/AdaptivePractice'
import Quizzes from '@/pages/Quizzes'
import StudyPlan from '@/pages/StudyPlan'
import Progress from '@/pages/Progress'
import Settings from '@/pages/Settings'

export default function Router() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/materials" element={<Materials />} />
      <Route path="/knowledge-map" element={<KnowledgeMap />} />
      <Route path="/adaptive-practice" element={<AdaptivePractice />} />
      <Route path="/quizzes" element={<Quizzes />} />
      <Route path="/study-plan" element={<StudyPlan />} />
      <Route path="/progress" element={<Progress />} />
      <Route path="/settings" element={<Settings />} />
    </Routes>
  )
}
