import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from 'react-router-dom'
import { useTheme } from '@/hooks/useTheme'
import { Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'
import EventsPage from '@/pages/EventsPage'
import ClubsPage from '@/pages/ClubsPage'

function Navigation() {
  const location = useLocation()
  const navigate = useNavigate()
  const { theme, toggleTheme } = useTheme()
  
  const isActive = (path: string) => {
    return location.pathname === path || (path === '/events' && location.pathname === '/')
  }

  return (
    <nav className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="text-base font-bold text-gray-900 dark:text-white">Event Hub</div>
            <div className="hidden sm:ml-8 sm:flex sm:space-x-6">
              <button
                onMouseDown={() => navigate('/events')}
                className={`text-sm font-medium ${
                  isActive('/events')
                    ? 'text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Events
              </button>
              <button
                onMouseDown={() => navigate('/clubs')}
                className={`text-sm font-medium ${
                  isActive('/clubs')
                    ? 'text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Clubs
              </button>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <Button
              variant="ghost"
              size="sm"
              onMouseDown={toggleTheme}
              className="p-2"
            >
              {theme === 'dark' ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>
            
            <div className="sm:hidden flex items-center space-x-2">
              <button
                onMouseDown={() => navigate('/events')}
                className={`text-sm font-medium ${
                  isActive('/events')
                    ? 'text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Events
              </button>
              <button
                onMouseDown={() => navigate('/clubs')}
                className={`text-sm font-medium ${
                  isActive('/clubs')
                    ? 'text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Clubs
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-white dark:bg-gray-900">
        <Navigation />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Routes>
            <Route path="/" element={<EventsPage />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/clubs" element={<ClubsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
