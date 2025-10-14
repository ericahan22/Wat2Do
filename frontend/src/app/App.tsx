import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Analytics } from '@vercel/analytics/react'
import { EventsPage, PromoteEventPage } from '@/features/events'
import { ClubsPage } from '@/features/clubs'
import { AdminPage } from '@/features/admin'
import { UnsubscribePage } from '@/features/newsletter'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { EmailVerificationPage } from '@/features/auth/pages/EmailVerificationPage'
import { SubmitPage } from '@/features/events/pages/SubmitPage'
import { MySubmissionsPage } from '@/features/events/pages/MySubmissionsPage'
import { ModerationPage } from '@/features/admin/pages/ModerationPage'
import { AuthGuard } from '@/features/auth/components/AuthGuard'
import { Navbar, Footer } from '@/shared'
import AboutPage from '@/shared/components/layout/AboutPage'
import ContactPage from '@/shared/components/layout/ContactPage'
import NotFoundPage from '@/shared/components/layout/NotFoundPage'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-white dark:bg-gray-900 flex flex-col">
        <Navbar />
        <main className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-6 min-w-0">
          <Routes>
            <Route path="/" element={<EventsPage />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/clubs" element={<ClubsPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/verify-email/:token" element={<EmailVerificationPage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/unsubscribe/:token" element={<UnsubscribePage />} />
            
            {/* Protected Routes */}
            <Route path="/submit" element={
              <AuthGuard>
                <SubmitPage />
              </AuthGuard>
            } />
            <Route path="/my-submissions" element={
              <AuthGuard>
                <MySubmissionsPage />
              </AuthGuard>
            } />
            <Route path="/promote-event" element={
              <AuthGuard>
                <PromoteEventPage />
              </AuthGuard>
            } />
            <Route path="/admin/moderation" element={
              <AuthGuard requireAdmin={true}>
                <ModerationPage />
              </AuthGuard>
            } />
            
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>

        <Footer />
      </div>
      <Analytics />
    </Router>
  )
}

export default App
