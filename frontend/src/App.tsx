import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Analytics } from '@vercel/analytics/react'
import EventsPage from '@/pages/EventsPage'
import ClubsPage from '@/pages/ClubsPage'
import AboutPage from '@/pages/AboutPage'
import ContactPage from '@/pages/ContactPage'
import UnsubscribePage from '@/pages/UnsubscribePage'
import NotFoundPage from '@/pages/NotFoundPage'
import Footer from '@/components/Footer'
import Navbar from '@/components/Navbar'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-white dark:bg-gray-900 flex flex-col">
        <Navbar />
        <main className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Routes>
            <Route path="/" element={<EventsPage />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/clubs" element={<ClubsPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactPage />} />
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
