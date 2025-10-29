import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@/shared/lib/theme'
import { ClerkAppProvider } from '@/shared/components/ClerkAppProvider'
import '@/app/index.css'
import App from '@/app/App.tsx'
import { BrowserRouter } from 'react-router-dom'
import { SEOHead } from '@/shared'
import { Analytics } from '@vercel/analytics/react'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
    <ClerkAppProvider>
      <ThemeProvider>
        <QueryClientProvider client={queryClient}>
          <SEOHead />
          <Analytics />
          <App />
        </QueryClientProvider>
      </ThemeProvider>
    </ClerkAppProvider>
    </BrowserRouter>
  </StrictMode>,
)
