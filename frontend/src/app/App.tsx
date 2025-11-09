import { Routes, Route } from "react-router-dom";
import { EventsPage } from "@/features/events";
import EventDetailPage from "@/features/events/pages/EventDetailPage";
import { SubmitEventPage } from "@/features/events/pages/SubmitEventPage";
import { MySubmissionsPage } from "@/features/events/pages/MySubmissionsPage";
import { ClubsPage } from "@/features/clubs";
import { AdminPage, PromotionsPage, SubmissionsReviewPage } from "@/features/admin";
import { UnsubscribePage } from "@/features/newsletter";
import { SignInPage, SignUpPage, UserProfilePage } from "@/features/auth/pages";
import {
  ProtectedRoute,
  ProtectedAdminRoute,
  Navbar,
  Footer,
  AboutPage,
  ContactPage,
  NotFoundPage,
  TopBanner,
} from "@/shared";
import { CLERK_ROUTES } from "@/shared/config/clerk";

function App() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 flex flex-col">
      <TopBanner />
      <Navbar />
      <main className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-6 min-w-0">
        <Routes>
          <Route path="/" element={<EventsPage />} />
          <Route path="/events" element={<EventsPage />} />
          <Route path="/events/:eventId" element={<EventDetailPage />} />
          <Route
            path="/submit"
            element={
              <ProtectedRoute>
                <SubmitEventPage />
              </ProtectedRoute>
            }
          />
          <Route path="/clubs" element={<ClubsPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route
            path="/admin"
            element={
              <ProtectedAdminRoute>
                <AdminPage />
              </ProtectedAdminRoute>
            }
          />
          <Route
            path="/admin/promotions"
            element={
              <ProtectedAdminRoute>
                <PromotionsPage />
              </ProtectedAdminRoute>
            }
          />
          <Route
            path="/admin/submissions"
            element={
              <ProtectedAdminRoute>
                <SubmissionsReviewPage />
              </ProtectedAdminRoute>
            }
          />
          <Route path="/unsubscribe/:token" element={<UnsubscribePage />} />

          {/* Clerk Auth Routes */}
          <Route path={CLERK_ROUTES.SIGN_IN} element={<SignInPage />} />
          <Route path={CLERK_ROUTES.SIGN_UP} element={<SignUpPage />} />
          <Route 
            path={`${CLERK_ROUTES.USER_PROFILE}/*`} 
            element={
              <ProtectedRoute allowAdmins={true}>
                <UserProfilePage />
              </ProtectedRoute>
            } 
          />

          <Route
            path={CLERK_ROUTES.DASHBOARD}
            element={
              <ProtectedRoute>
                <MySubmissionsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/submissions"
            element={
              <ProtectedRoute>
                <MySubmissionsPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
