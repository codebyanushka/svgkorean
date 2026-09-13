import { Route, Routes } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import StudentLayout from './layouts/StudentLayout'
import TeacherLayout from './layouts/TeacherLayout'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import NotFoundPage from './pages/NotFoundPage'
import StudentHomePage from './pages/student/StudentHomePage'
import SearchPage from './pages/student/SearchPage'
import VocabHomePage from './pages/student/vocab/VocabHomePage'
import VocabUnitPage from './pages/student/vocab/VocabUnitPage'
import WordListPage from './pages/student/vocab/WordListPage'
import LearnFlashcardsPage from './pages/student/vocab/LearnFlashcardsPage'
import { RecallPage, ApplyPage, MultipleChoicePage, KoToEnPage, EnToKoPage } from './pages/student/vocab/RecallPage'
import MatchingPage from './pages/student/vocab/MatchingPage'
import FillBlankPage from './pages/student/vocab/FillBlankPage'
import QuickRecallPage from './pages/student/vocab/QuickRecallPage'
import SmartRevisionPage from './pages/student/vocab/SmartRevisionPage'
import TestPage from './pages/student/vocab/TestPage'
import ReviewPage from './pages/student/ReviewPage'
import ProgressPage from './pages/student/ProgressPage'
import ProfilePage from './pages/student/ProfilePage'
import TeacherOverviewPage from './pages/teacher/TeacherOverviewPage'
import StudentsPage from './pages/teacher/StudentsPage'
import StudentDetailPage from './pages/teacher/StudentDetailPage'
import LessonsPage from './pages/teacher/LessonsPage'
import ActivityPage from './pages/teacher/ActivityPage'
import MistakesPage from './pages/teacher/MistakesPage'
import AnalyticsPage from './pages/teacher/AnalyticsPage'
import ContentPage from './pages/teacher/ContentPage'

function App() {
  return (
    <Routes>
      <Route path="login" element={<LoginPage />} />

      <Route element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>

      <Route element={<ProtectedRoute allowedRoles={['STUDENT']} />}>
        <Route element={<StudentLayout />}>
          <Route path="student" element={<StudentHomePage />} />
          <Route path="student/search" element={<SearchPage />} />
          <Route path="student/vocab" element={<VocabHomePage />} />
          <Route path="student/vocab/units/:unitNumber" element={<VocabUnitPage />} />
          <Route path="student/vocab/units/:unitNumber/words" element={<WordListPage />} />
          <Route path="student/vocab/units/:unitNumber/learn" element={<LearnFlashcardsPage />} />
          <Route path="student/vocab/units/:unitNumber/recall" element={<RecallPage />} />
          <Route path="student/vocab/units/:unitNumber/apply" element={<ApplyPage />} />
          <Route path="student/vocab/units/:unitNumber/practice/multiple-choice" element={<MultipleChoicePage />} />
          <Route path="student/vocab/units/:unitNumber/practice/ko-to-en" element={<KoToEnPage />} />
          <Route path="student/vocab/units/:unitNumber/practice/en-to-ko" element={<EnToKoPage />} />
          <Route path="student/vocab/units/:unitNumber/matching" element={<MatchingPage />} />
          <Route path="student/vocab/units/:unitNumber/fill-blank" element={<FillBlankPage />} />
          <Route path="student/vocab/units/:unitNumber/quick" element={<QuickRecallPage />} />
          <Route path="student/vocab/units/:unitNumber/smart-revision" element={<SmartRevisionPage />} />
          <Route path="student/vocab/units/:unitNumber/test" element={<TestPage />} />
          <Route path="student/review" element={<ReviewPage />} />
          <Route path="student/progress" element={<ProgressPage />} />
          <Route path="student/profile" element={<ProfilePage />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute allowedRoles={['TEACHER']} />}>
        <Route element={<TeacherLayout />}>
          <Route path="teacher" element={<TeacherOverviewPage />} />
          <Route path="teacher/students" element={<StudentsPage />} />
          <Route path="teacher/students/:studentId" element={<StudentDetailPage />} />
          <Route path="teacher/lessons" element={<LessonsPage />} />
          <Route path="teacher/activity" element={<ActivityPage />} />
          <Route path="teacher/mistakes" element={<MistakesPage />} />
          <Route path="teacher/analytics" element={<AnalyticsPage />} />
          <Route path="teacher/content" element={<ContentPage />} />
        </Route>
      </Route>
    </Routes>
  )
}

export default App
