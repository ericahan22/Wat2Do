import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Analytics } from "@vercel/analytics/react";
import { EventsPage } from "@/features/events";
import { ClubsPage } from "@/features/clubs";
import { AdminPage } from "@/features/admin";
import { UnsubscribePage } from "@/features/newsletter";
import { VerifyEmailPage, Dashboard } from "@/features/auth";
import { AuthPage } from "@/features/auth/pages/AuthPage";
import { ProtectedRoute } from "@/shared/components/ProtectedRoute";
import { Navbar, Footer } from "@/shared";
import AboutPage from "@/shared/components/layout/AboutPage";
import ContactPage from "@/shared/components/layout/ContactPage";
import NotFoundPage from "@/shared/components/layout/NotFoundPage";
import TopBanner from "@/shared/components/layout/TopBanner";
import { SEOHead } from "@/shared/components/SEOHead";

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <SEOHead />
        <div className="min-h-screen bg-white dark:bg-gray-900 flex flex-col">
          <TopBanner />
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
              <Route path="/auth" element={<AuthPage />} />
              <Route path="/auth/verify-email" element={<VerifyEmailPage />} />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </main>
          <Footer />
        </div>
        <Analytics />
      </Router>
    </QueryClientProvider>
  );
}

export default App;
