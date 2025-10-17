import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Analytics } from '@vercel/analytics/react'
import { EventsPage } from '@/features/events'
import { ClubsPage } from '@/features/clubs'
import { AdminPage } from '@/features/admin'
import { UnsubscribePage } from '@/features/newsletter'
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
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/unsubscribe/:token" element={<UnsubscribePage />} />
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
