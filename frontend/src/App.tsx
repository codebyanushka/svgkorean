import { Route, Routes } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import StudentLayout from './layouts/StudentLayout'
import TeacherLayout from './layouts/TeacherLayout'
import ProtectedRoute from './components/ProtectedRoute'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import AdminPage from './pages/AdminPage'
import NotFoundPage from './pages/NotFoundPage'
import StudentHomePage from './pages/student/StudentHomePage'
import UnitLessonsPage from './pages/student/UnitLessonsPage'
import LearnPage from './pages/student/LearnPage'
import PracticePage from './pages/student/PracticePage'
import ReviewPage from './pages/student/ReviewPage'
import ProgressPage from './pages/student/ProgressPage'
import ProfilePage from './pages/student/ProfilePage'
import TeacherOverviewPage from './pages/teacher/TeacherOverviewPage'
import StudentsPage from './pages/teacher/StudentsPage'
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
        <Route index element={<HomePage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>

      <Route element={<ProtectedRoute allowedRoles={['STUDENT']} />}>
        <Route element={<StudentLayout />}>
          <Route path="student" element={<StudentHomePage />} />
          <Route path="student/units/:unitNumber" element={<UnitLessonsPage />} />
          <Route path="student/learn" element={<LearnPage />} />
          <Route path="student/practice" element={<PracticePage />} />
          <Route path="student/review" element={<ReviewPage />} />
          <Route path="student/progress" element={<ProgressPage />} />
          <Route path="student/profile" element={<ProfilePage />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute allowedRoles={['TEACHER']} />}>
        <Route element={<TeacherLayout />}>
          <Route path="teacher" element={<TeacherOverviewPage />} />
          <Route path="teacher/students" element={<StudentsPage />} />
          <Route path="teacher/lessons" element={<LessonsPage />} />
          <Route path="teacher/activity" element={<ActivityPage />} />
          <Route path="teacher/mistakes" element={<MistakesPage />} />
          <Route path="teacher/analytics" element={<AnalyticsPage />} />
          <Route path="teacher/content" element={<ContentPage />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
        <Route element={<AppLayout />}>
          <Route path="admin" element={<AdminPage />} />
        </Route>
      </Route>
    </Routes>
  )
}

export default App
