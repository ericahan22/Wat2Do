import { Routes, Route } from "react-router-dom";
import { EventsPage } from "@/features/events";
import EventDetailPage from "@/features/events/pages/EventDetailPage";
import { ClubsPage } from "@/features/clubs";
import { SignInPage } from "@/features/auth/pages";
import {
  Navbar,
  Footer,
  NotFoundPage,
  AboutPage,
  ContactPage,
} from "@/shared";
import { MigrationBanner } from "@/shared/components/layout/MigrationBanner";
import { BackToTopButton } from "@/shared/components/common/BackToTopButton";

function App() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 flex flex-col">
      <MigrationBanner />
      <Navbar />
      <main className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-6 min-w-0">
        <Routes>
          <Route path="/" element={<EventsPage />} />
          <Route path="/events" element={<EventsPage />} />
          <Route path="/events/:eventId" element={<EventDetailPage />} />
          <Route path="/clubs" element={<ClubsPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/login" element={<SignInPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
      <Footer />
      <BackToTopButton />
    </div>
  );
}

export default App;