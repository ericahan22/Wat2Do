# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Wat2Do** ([wat2do.ca](https://wat2do.ca)) is a web app to help you discover club events at the University of Waterloo, scraped directly from Instagram. The application captures all student club events within 10 minutes and provides a web interface for browsing, submitting, and managing events and clubs.

Built with Django REST API backend and React + TypeScript frontend, Wat2Do uses AI to extract event details from Instagram posts.

**Tech Stack:**
- **Backend**: Django 5.1 + Django REST Framework, PostgreSQL
- **Frontend**: React 19 + TypeScript, Vite, TanStack Query, Zustand
- **Authentication**: Clerk (JWT-based)
- **AI**: OpenAI GPT-4o-mini for event extraction
- **Email**: Resend API
- **Storage**: AWS S3
- **Scraping**: Apify Instagram API

**Key Features:**
- **Browse, search, and filter events** - See upcoming and past events from University of Waterloo campus clubs
- **Club directory** - Explore all clubs with links to their websites and Instagram
- **Event submissions** - Users can submit events with AI-powered extraction from screenshots
- **Interest tracking** - Mark events as interested and filter to see only interested events
- **Calendar export** - Export events to iCalendar or Google Calendar
- **Email newsletter** - Subscribe to get the latest events in your inbox daily
- **Admin panel** - Manage event promotions and review user submissions

## Development Setup Commands

### Database Setup

**Option 1: Docker Compose (Recommended)**
```bash
docker compose up --build
```

**Option 3: Local PostgreSQL**
- Install PostgreSQL locally and configure in `backend/config/settings/development.py`

### Backend (Django)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Optional: Populate local DB with production data
python scripts/populate-local-db-with-prod-data.py
python manage.py fix_sequences

# Start development server
python manage.py runserver 8000
```

### Frontend (React + TypeScript)
```bash
cd frontend
npm install
npm run dev  # Development server on port 5173
```

**Important**: The backend must be running for the frontend to work properly. Always start both servers during development.

## Build and Test Commands

### Backend
- `python manage.py check` - Django configuration check
- `python manage.py test` - Run Django tests
- `python manage.py migrate` - Apply database migrations
- `python manage.py makemigrations [app_name]` - Create new migrations
- `python manage.py runserver 8000` - Start development server
- `python scripts/populate-local-db-with-prod-data.py` - Populate local DB with production data
- `python manage.py fix_sequences` - Fix database sequence issues (after populating data)

### Frontend
- `npm run build` - Production build
- `npm run lint` - ESLint check (shows existing warnings, focus on new ones)
- `npm run lint:fix` - Auto-fix ESLint issues
- `npm run dev` - Development server (port 5173)
- `npm run preview` - Preview production build

### Code Quality
- Backend: Use `ruff` for linting (configured in pyproject.toml)
- Frontend: ESLint with TypeScript support

---

## Feature Documentation

### 1. EVENTS FEATURE (Primary feature - most complex)

**Purpose**: Browse, search, filter, and interact with university club events scraped from Instagram

#### Frontend (`/frontend/src/features/events/`)

**Key Pages:**
- `/events` - Main events listing page (frontend/src/features/events/pages/EventsPage.tsx)
- `/events/:eventId` - Single event detail page (frontend/src/features/events/pages/EventDetailPage.tsx)

**Components:**
- `EventsGrid.tsx` - Grid view with infinite scroll
- `EventsCalendar.tsx` - Calendar view using react-big-calendar
- `EventsContent.tsx` - View switcher (grid/calendar modes)
- `EventPreview.tsx` - Event card component with image, title, dates, location
- `EventLegend.tsx` - Category legend
- `QuickFilters.tsx` - Quick filter chips (Newly Added, All, Interested, Export)
- `EventEditForm.tsx` - Edit event form for users

**Hooks:**
- `useEvents.ts` - Main events query with infinite scroll, URL-based filtering, cursor pagination
- `useEventSelection.ts` - Multi-select events for export
- `useEventInterest.ts` - Mark/unmark events as interested with optimistic UI updates
- `useQuickFilters.ts` - Category filter logic

**Key Features:**
- **Infinite scroll**: Cursor-based pagination loading 12 events per page
- **Dual view modes**: Grid view and calendar view
- **Advanced filtering**:
  - Search by title/description (semicolon-separated OR queries)
  - Category filters (multiple categories with OR logic)
  - Date range filters (start date, end date)
  - Price range filters
  - Club type filters
  - "Interested only" filter
- **Event interest system**: Users can mark events interested, shows count on cards
- **Multi-select export**: Export events to iCalendar (.ics) or Google Calendar
- **URL state management**: All filters persisted in URL for shareable links
- **Real-time event count**: Animated number display using NumberFlow
- **Loading skeletons**: Smooth loading states with 12 skeleton cards

**File References:**
- Main page: `frontend/src/features/events/pages/EventsPage.tsx:1`
- Main hook: `frontend/src/features/events/hooks/useEvents.ts:1`
- Interest hook: `frontend/src/features/events/hooks/useEventInterest.ts:1`

#### Backend (`/backend/apps/events/`)

**Models:**

1. **Events** - Core event model
   - Fields: title, description, location, categories (JSONField), status, source_url, source_image_url
   - Metadata: reactions (JSONField), food, registration, price, school, club_type
   - Social handles: ig_handle, discord_handle, x_handle, tiktok_handle, fb_handle, other_handle
   - Timestamps: added_at

2. **EventDates** - Individual event occurrences (one-to-many with Events)
   - Fields: dtstart_utc, dtend_utc, duration, tz (timezone)
   - Supports recurring/multi-date events
   - Indexed on dtstart_utc, dtend_utc for performance

3. **EventInterest** - User interest tracking (many-to-many)
   - Fields: event (FK), user_id (Clerk ID), created_at
   - Unique constraint: (event, user_id)

**API Endpoints:**
```
GET  /api/events/                        - List events with filters, cursor pagination
GET  /api/events/latest-update/          - Get latest event update timestamp
GET  /api/events/<id>/                   - Get single event with all occurrences
PUT  /api/events/<id>/update/            - Update event (submitter/admin only)
DELETE /api/events/<id>/delete/          - Delete event (admin only)
GET  /api/events/export.ics              - Export events as ICS calendar file
GET  /api/events/google-calendar-urls/   - Generate Google Calendar URLs for events
GET  /api/events/my-interests/           - Get user's interested event IDs (JWT required)
POST /api/events/<id>/interest/mark/     - Mark interest in event (JWT required)
DELETE /api/events/<id>/interest/unmark/ - Remove interest (JWT required)
```

**Query Parameters for `/api/events/`:**
- `search` - Search title/description (semicolon-separated OR)
- `categories` - Filter by categories (semicolon-separated OR)
- `dtstart_utc` - Filter by start date (ISO 8601)
- `dtend_utc` - Filter by end date (ISO 8601)
- `added_at` - Filter by date added (ISO 8601)
- `min_price`, `max_price` - Price range filters
- `club_type` - Filter by club type (WUSA, Athletics, Student Society)
- `school` - Filter by school
- `interested` - Show only user's interested events (JWT required)
- `cursor` - Pagination cursor
- `limit` - Results per page (default: 12)

**Rate Limiting:**
- List/detail endpoints: 100-600/hour
- Interest endpoints: 60/hour

**File References:**
- Models: `backend/apps/events/models.py:1`
- Views: `backend/apps/events/views.py:1`
- Filters: `backend/utils/filters.py:1`

---

### 2. EVENT SUBMISSIONS FEATURE

**Purpose**: Allow users to submit events for review using AI-powered extraction from screenshots

#### Frontend (`/frontend/src/features/events/`)

**Key Pages:**
- `/submit` - Submit new event page (frontend/src/features/events/pages/SubmitEventPage.tsx)
- `/dashboard/submissions` - User's submitted events (frontend/src/features/events/pages/MySubmissionsPage.tsx)

**Components:**
- `EventFormFields.tsx` - Reusable form fields for event submission/editing
- `EventEditForm.tsx` - Form for editing submitted events

**Hooks:**
- `useEventSubmission.ts` - Submit event mutation with AI extraction
- `useUserSubmissions.ts` - Fetch user's submitted events

**Workflow:**
1. User uploads screenshot of Instagram event post
2. AI extracts event details (title, date, location, etc.)
3. User reviews and edits extracted data
4. User submits for admin review
5. Admin approves/rejects at `/admin/submissions`
6. Approved events appear in main events list

**Schema:**
- Zod validation in `frontend/src/features/events/schemas/submissionSchema.ts`
- Required fields: title (≥3 chars), location (≥3 chars), at least one occurrence

**File References:**
- Submit page: `frontend/src/features/events/pages/SubmitEventPage.tsx:1`
- Submission hook: `frontend/src/features/events/hooks/useEventSubmission.ts:1`

#### Backend (`/backend/apps/events/`)

**Models:**

**EventSubmission** - User-submitted events pending review
- Fields: submitted_by (Clerk user ID), submitted_at, reviewed_at, reviewed_by
- Status choices: 'pending', 'approved', 'rejected'
- Foreign key: created_event (links to approved Event)

**API Endpoints:**
```
POST /api/events/extract/              - Extract event from screenshot using AI (JWT required)
POST /api/events/submit/               - Submit new event for review (JWT required)
GET  /api/events/my-submissions/       - Get user's submissions (JWT required)
GET  /api/events/submissions/          - Get all submissions for review (admin only)
POST /api/events/submissions/<id>/review/ - Approve/reject submission (admin only)
DELETE /api/events/submissions/<id>/   - Delete submission (JWT required)
```

**AI Extraction (OpenAI Service):**
- Service: `backend/services/openai_service.py`
- Model: GPT-4o-mini with vision
- Extracts: title, description, location, dates, categories, social handles, price, etc.
- Content policy: Rejects memes, inappropriate content, spam
- Requirement: Must have both date AND time specified
- Context-aware: Uses current date and semester end date

**Rate Limiting:**
- Extract endpoint: 5/hour (AI-intensive)
- Submit endpoint: 10/hour
- Review endpoints: 100/hour (admin)

**File References:**
- Submission model: `backend/apps/events/models.py:1`
- Submission views: `backend/apps/events/views.py:1`
- OpenAI service: `backend/services/openai_service.py:1`

---

### 3. CLUBS FEATURE

**Purpose**: Browse university club directory with search functionality

#### Frontend (`/frontend/src/features/clubs/`)

**Key Pages:**
- `/clubs` - Main clubs directory page (frontend/src/features/clubs/pages/ClubsPage.tsx)

**Components:**
- `ClubsGrid.tsx` - Grid of club cards with images, names, categories

**Hooks:**
- `useClubs.ts` - Fetch clubs with search and filters

**Features:**
- Search by club name
- Filter by category
- Responsive grid layout
- Loading skeletons

**File References:**
- Clubs page: `frontend/src/features/clubs/pages/ClubsPage.tsx:1`

#### Backend (`/backend/apps/clubs/`)

**Models:**

**Clubs**
- Fields: club_name (unique), categories (JSONField), club_page, ig, discord
- Club type choices: 'WUSA', 'Athletics', 'Student Society'
- Indexed on club_name

**API Endpoints:**
```
GET /api/clubs/  - List clubs with cursor pagination, search, category filter
```

**Query Parameters:**
- `search` - Search by club name
- `categories` - Filter by category
- `cursor` - Pagination cursor
- `limit` - Results per page (default: 50)

**File References:**
- Models: `backend/apps/clubs/models.py:1`
- Views: `backend/apps/clubs/views.py:1`

---

### 4. ADMIN & PROMOTIONS FEATURE

**Purpose**: Admin panel for managing event promotions and reviewing submissions

#### Frontend (`/frontend/src/features/admin/`)

**Key Pages:**
- `/admin` - Admin dashboard (frontend/src/features/admin/pages/AdminPage.tsx)
- `/admin/promotions` - Manage promoted events (frontend/src/features/admin/pages/PromotionsPage.tsx)
- `/admin/submissions` - Review user submissions (frontend/src/features/admin/pages/SubmissionsReviewPage.tsx)

**Components:**
- `AdminLogin.tsx` - Admin authentication UI
- `PromotionsManager.tsx` - Manage promoted events list
- `PromoteEventForm.tsx` - Form to promote events with priority/expiration

**Hooks:**
- `useEventPromotion.ts` - Promotion mutations (promote, unpromote)
- `useSubmissionsReview.ts` - Review submissions (approve, reject)

**Protected Routes:**
- Uses `ProtectedAdminRoute` component
- Checks `user.publicMetadata.role === 'admin'` via Clerk
- Redirects non-admins to `/events`

**File References:**
- Submissions review: `frontend/src/features/admin/pages/SubmissionsReviewPage.tsx:1`
- Admin routes: `frontend/src/shared/components/ProtectedAdminRoute.tsx:1`

#### Backend (`/backend/apps/promotions/`)

**Models:**

**EventPromotion** (OneToOne with Events)
- Fields: is_active, promoted_at, promoted_by, expires_at
- Priority: 1-10 (higher = more prominent)
- Promotion types: 'standard', 'featured', 'urgent', 'sponsored'
- Properties: is_expired, is_effective

**API Endpoints:**
```
GET  /api/promotions/events/                      - Get promoted events
POST /api/promotions/events/<id>/promote/         - Promote event (admin only)
POST /api/promotions/events/<id>/unpromote/       - Unpromote event (admin only)
GET  /api/promotions/events/<id>/promotion-status/ - Get promotion status (admin only)
```

**File References:**
- Promotion model: `backend/apps/promotions/models.py:1`
- Promotion views: `backend/apps/promotions/views.py:1`

---

### 5. AUTHENTICATION FEATURE

**Purpose**: User authentication and authorization using Clerk

#### Frontend (`/frontend/src/features/auth/`)

**Key Pages:**
- `/auth/sign-in` - Sign in page (frontend/src/features/auth/pages/SignInPage.tsx)
- `/auth/sign-up` - Sign up page (frontend/src/features/auth/pages/SignUpPage.tsx)
- `/auth/verify-email` - Email verification (frontend/src/features/auth/pages/VerifyEmailPage.tsx)
- `/user-profile/*` - User profile management (frontend/src/features/auth/pages/UserProfilePage.tsx)
- `/dashboard` - User dashboard (frontend/src/features/auth/pages/DashboardPage.tsx)

**Components:**
- `UserProfile.tsx` - User profile component
- `EmailVerification.tsx` - Email verification UI
- `ForgotPassword.tsx`, `ResetPassword.tsx` - Password reset flow
- `SuccessMessage.tsx` - Success notification component

**Protected Routes:**
- `ProtectedRoute` - Requires authentication, redirects admins to `/admin`
- `ProtectedAdminRoute` - Requires admin role in `user.publicMetadata.role`

**State Management:**
- Zustand store: `frontend/src/shared/stores/clerkAuthStore.ts`
- Persists: user, session, isAuthenticated, isLoading
- Storage: localStorage with 'clerk-auth-storage' key

**Clerk Configuration:**
- Config file: `frontend/src/shared/config/clerk.ts`
- Provider: `frontend/src/shared/components/ClerkAppProvider.tsx`
- Theme support: Dark/light mode integration

**File References:**
- Clerk store: `frontend/src/shared/stores/clerkAuthStore.ts:1`
- Protected route: `frontend/src/shared/components/ProtectedRoute.tsx:1`
- Clerk provider: `frontend/src/shared/components/ClerkAppProvider.tsx:1`

#### Backend (`/backend/apps/core/`)

**Authentication System:**

**Custom JWT Backend:**
- Class: `JwtAuthBackend` in `backend/apps/core/authentication.py`
- Validates Clerk JWT tokens
- Extracts user_id from 'sub' or 'id' claim
- Checks admin role via 'role' field in JWT
- Validates authorized parties via CLERK_AUTHORIZED_PARTIES

**Decorators:**
- `@jwt_required` - Requires valid JWT token
- `@optional_jwt` - JWT optional, populates user info if present
- `@admin_required` - Requires admin role in JWT payload

**API Endpoints:**
```
GET /api/auth/me/      - Get current user info (JWT required)
GET /api/protected/    - Protected test endpoint (JWT required)
```

**Authentication Flow:**
1. Frontend gets token via Clerk's `getToken()`
2. Token sent in `Authorization: Bearer <token>` header
3. Backend validates JWT signature and claims
4. User object created with `user_id` and `is_admin` attributes

**File References:**
- Auth backend: `backend/apps/core/authentication.py:1`
- Auth decorators: `backend/apps/core/decorators.py:1`

---

### 6. NEWSLETTER FEATURE

**Purpose**: Newsletter subscription management with email notifications

#### Frontend (`/frontend/src/features/newsletter/`)

**Key Pages:**
- `/unsubscribe/:token` - Unsubscribe page (frontend/src/features/newsletter/pages/UnsubscribePage.tsx)

**Components:**
- `UnsubscribeForm.tsx` - Unsubscribe form with reason selection

**Hooks:**
- `useNewsletterSubscribe.ts` - Subscribe mutation
- `useUnsubscribe.ts` - Unsubscribe mutation

**File References:**
- Unsubscribe page: `frontend/src/features/newsletter/pages/UnsubscribePage.tsx:1`

#### Backend (`/backend/apps/newsletter/`)

**Models:**

**NewsletterSubscriber**
- Fields: email, subscribed_at, is_active, unsubscribe_token (UUID)
- Additional: unsubscribe_reason, unsubscribed_at
- Methods: `get_by_email()`, `create_subscriber()`, `get_email_display()` (masked)

**API Endpoints:**
```
POST /api/newsletter/subscribe/            - Subscribe to newsletter
GET  /api/newsletter/unsubscribe/<token>/  - Get unsubscribe info
POST /api/newsletter/unsubscribe/<token>/  - Unsubscribe with reason
POST /api/newsletter/test-email/           - Send test email (internal)
```

**Email Service:**
- Service: `backend/services/email_service.py`
- Provider: Resend API
- Welcome email sent on subscription
- Newsletter emails include events added in last 24 hours
- Unsubscribe link in all emails

**Email Features:**
- HTML email templates with event images
- Event formatting with dates, times, locations
- Masked email addresses for privacy (e.g., "t***@example.com")

**File References:**
- Newsletter model: `backend/apps/newsletter/models.py:1`
- Email service: `backend/services/email_service.py:1`

---

### 7. SEARCH FEATURE

**Purpose**: Global search functionality with localStorage persistence

#### Frontend (`/frontend/src/features/search/`)

**Components:**
- `SearchInput.tsx` - Search input with clear button and debouncing

**Hooks:**
- `useSearchState.ts` - Search state with localStorage persistence and URL sync

**Features:**
- Debounced search input (300ms delay)
- Persists last search to localStorage
- Syncs with URL search params
- Clear button to reset search

**File References:**
- Search hook: `frontend/src/features/search/hooks/useSearchState.ts:1`
- Search input: `frontend/src/features/search/components/SearchInput.tsx:1`

---

## Architecture & Infrastructure

### Backend Architecture

#### Django Apps Structure (`/backend/apps/`)

```
backend/apps/
├── events/          # Events, submissions, interests, calendar export
├── clubs/           # Club directory
├── newsletter/      # Newsletter subscriptions
├── promotions/      # Event promotions
├── core/            # Authentication, health checks, base functionality
└── payments/        # Placeholder (not implemented yet)
```

#### Services Layer (`/backend/services/`)

1. **OpenAI Service** (`openai_service.py`)
   - AI-powered event extraction from Instagram screenshots
   - Model: GPT-4o-mini with vision capabilities
   - Text embeddings: text-embedding-3-small (1536-dim vectors)
   - Content filtering and validation

2. **Email Service** (`email_service.py`)
   - Email sending via Resend API
   - Newsletter generation with recent events
   - Welcome email templates
   - HTML email formatting

3. **Storage Service** (`storage_service.py`)
   - AWS S3 file upload and management
   - Image validation (JPEG, PNG, WEBP)
   - 10MB size limit
   - Public-read ACL with cache headers

#### Database Models & Relationships

```
Events (1) ←→ (1) EventPromotion
Events (1) → (many) EventDates
Events (1) → (many) EventInterest
Events (1) ← (1) EventSubmission

Clubs (standalone)
NewsletterSubscriber (standalone)
```

**Key Indexes:**
- EventDates: dtstart_utc, dtend_utc, (event, dtstart_utc)
- EventInterest: event, user_id, unique(event, user_id)
- Clubs: club_name

#### Middleware Stack

1. HealthCheckMiddleware - Fast /health responses
2. CorsMiddleware - CORS handling
3. SecurityMiddleware
4. SessionMiddleware
5. CommonMiddleware
6. CsrfViewMiddleware
7. AuthenticationMiddleware
8. MessagesMiddleware
9. ClickjackingMiddleware
10. RatelimitMiddleware

#### Authentication Backends

1. **JwtAuthBackend** (Clerk) - Primary authentication
2. **ModelBackend** (Django) - Fallback for admin panel

### Frontend Architecture

#### Feature Structure

```
frontend/src/features/
├── events/          # 65+ files - Primary feature
│   ├── components/  # EventsGrid, EventsCalendar, EventPreview, etc.
│   ├── hooks/       # useEvents, useEventInterest, useEventSelection, etc.
│   ├── pages/       # EventsPage, EventDetailPage, SubmitEventPage, etc.
│   ├── schemas/     # Zod validation schemas
│   └── types/       # TypeScript type definitions
├── clubs/           # Club directory
├── admin/           # Admin panel, promotions, submissions review
├── auth/            # Clerk authentication pages
├── newsletter/      # Newsletter unsubscribe
└── search/          # Global search
```

#### Shared Components (`/frontend/src/shared/`)

**UI Components** (`/shared/components/ui/`)
- 20+ Radix UI primitives with custom styling
- Badge, Button variants, Card, Checkbox, Dropdown, Form, Input, Select, Tabs, Tooltip, etc.
- Custom components: DragDropFileUpload, JSONEditor (CodeMirror), Loading, Skeleton

**Layout Components** (`/shared/components/layout/`)
- `Navbar.tsx` - Main navigation with user menu
- `Footer.tsx` - Footer with links
- `TopBanner.tsx` - Dismissible banner ("Events added in real time!")
- `AboutPage.tsx`, `ContactPage.tsx`, `NotFoundPage.tsx`

**Common Components** (`/shared/components/common/`)
- `FloatingEventExportBar.tsx` - Export bar for selected events

**Badge Components** (`/shared/components/badges/`)
- `EventBadges.tsx` - Category badge display

#### State Management

**Server State (TanStack Query)**
- Configuration: `frontend/src/app/main.tsx`
- Query cache with global error handling
- 5-minute stale time
- Retry: 1 attempt

**Patterns:**
1. **Infinite Queries** - Events use cursor-based pagination
2. **Optimistic Updates** - Event interest updates cache immediately
3. **Query Invalidation** - Mutations invalidate related queries
4. **Cache Updates** - Direct cache manipulation for performance

**Client State (Zustand)**
- `clerkAuthStore.ts` - Clerk authentication state (persisted to localStorage)
- `authStore.ts` - Legacy auth store (minimal usage)

**URL State**
- Heavily used for filters and navigation
- Events: search, categories, dates, interested, view mode
- All managed via React Router's `useSearchParams()`

#### API Client Pattern

**Architecture**: Constructor pattern with dependency injection

```typescript
// Base client with token injection
const baseClient = new BaseAPIClient(() => getToken());

// Feature-specific clients
const eventsClient = new EventsAPIClient(baseClient);
const adminClient = new AdminAPIClient(baseClient);
```

**API Clients** (`/shared/api/`):
- `BaseAPIClient.ts` - Axios wrapper with auth token injection
- `EventsAPIClient.ts` - Events CRUD + submissions + interests
- `AdminAPIClient.ts` - Admin operations (promotions, reviews)
- `NewsletterAPIClient.ts` - Newsletter subscribe/unsubscribe
- `ClubsAPIClient.ts` - Clubs API
- `SimpleAPIClient.ts` - Lightweight client

**File References:**
- API index: `frontend/src/shared/api/index.ts:1`
- Base client: `frontend/src/shared/api/BaseAPIClient.ts:1`

#### Routing Structure (`/frontend/src/app/App.tsx`)

```typescript
// Public routes
/ → EventsPage
/events → EventsPage
/events/:eventId → EventDetailPage
/clubs → ClubsPage
/about → AboutPage
/contact → ContactPage

// Protected routes (authentication required)
/submit → ProtectedRoute(SubmitEventPage)
/user-profile/* → ProtectedRoute(UserProfilePage)
/dashboard → ProtectedRoute(MySubmissionsPage)
/dashboard/submissions → ProtectedRoute(MySubmissionsPage)

// Admin routes (admin role required)
/admin → ProtectedAdminRoute(AdminPage)
/admin/promotions → ProtectedAdminRoute(PromotionsPage)
/admin/submissions → ProtectedAdminRoute(SubmissionsReviewPage)

// Auth routes
/auth/sign-in → SignInPage
/auth/sign-up → SignUpPage

// Newsletter
/unsubscribe/:token → UnsubscribePage

// Fallback
* → NotFoundPage
```

#### Tech Stack Dependencies

**Core:**
- React 19.1.0, TypeScript 5.8.3, Vite 7.0.4, React Router 7.7.1

**State Management:**
- TanStack Query 5.90.5 (server state)
- Zustand 5.0.8 (client state)

**Authentication:**
- Clerk React 5.53.3

**UI:**
- Radix UI (various packages)
- TailwindCSS 4.1.11
- Framer Motion 12.23.24 (animations)
- Lucide React 0.536.0 (icons)
- Sonner 2.0.7 (toasts)
- Number Flow 0.5.10 (animated numbers)

**Forms:**
- React Hook Form 7.65.0
- Zod 4.1.12

**Date/Time:**
- date-fns 4.1.0
- date-fns-tz 3.2.0
- react-big-calendar 1.19.4

**Utilities:**
- Axios 1.7.7
- clsx 2.1.1
- tailwind-merge 3.3.1

### Scraping Infrastructure (`/backend/scraping/`)

**Key Files:**
- `main.py` - Orchestrates all Instagram scraping and post-processing (entrypoint for daily and single-user scrapes)
- `instagram_scraper.py` - Apify Instagram API client logic
- `event_processor.py` - Post-processing logic for scraped events (image upload, AI extraction, DB insert)

**Features:**
- **Fast scraping**: Captures all student club events within 10 minutes
- Apify-based Instagram scraping
- AI-powered event extraction from posts using GPT-4o-mini
- Automated scraping via GitHub Actions on schedule

---

## Complete API Reference

**Base URL**: `http://localhost:8000/`

### Core Endpoints
```
GET  /                 - API information and endpoint listing
GET  /health/          - Health check
GET  /api/auth/me/     - Get current user info (JWT required)
GET  /api/protected/   - Protected test endpoint (JWT required)
```

### Events Endpoints
```
GET  /api/events/                        - List events (pagination, filters)
GET  /api/events/latest-update/          - Latest event update timestamp
GET  /api/events/<id>/                   - Event detail with all occurrences
PUT  /api/events/<id>/update/            - Update event (JWT required)
DELETE /api/events/<id>/delete/          - Delete event (admin only)
GET  /api/events/export.ics              - Export to iCalendar format
GET  /api/events/google-calendar-urls/   - Generate Google Calendar URLs
POST /api/events/extract/                - AI event extraction (JWT required)
POST /api/events/submit/                 - Submit event (JWT required)
GET  /api/events/my-submissions/         - User's submissions (JWT required)
GET  /api/events/submissions/            - All submissions (admin only)
POST /api/events/submissions/<id>/review/ - Approve/reject (admin only)
DELETE /api/events/submissions/<id>/     - Delete submission (JWT required)
GET  /api/events/my-interests/           - User's interested events (JWT required)
POST /api/events/<id>/interest/mark/     - Mark interest (JWT required)
DELETE /api/events/<id>/interest/unmark/ - Unmark interest (JWT required)
```

### Clubs Endpoints
```
GET  /api/clubs/  - List clubs with cursor pagination, search, filters
```

### Newsletter Endpoints
```
POST /api/newsletter/subscribe/            - Subscribe to newsletter
GET  /api/newsletter/unsubscribe/<token>/  - Get unsubscribe info
POST /api/newsletter/unsubscribe/<token>/  - Unsubscribe with reason
POST /api/newsletter/test-email/           - Send test email (internal)
```

### Promotions Endpoints
```
GET  /api/promotions/events/                      - Get promoted events
POST /api/promotions/events/<id>/promote/         - Promote event (admin)
POST /api/promotions/events/<id>/unpromote/       - Unpromote event (admin)
GET  /api/promotions/events/<id>/promotion-status/ - Get promotion status (admin)
```

---

## Common Development Workflows

### Adding New Features

1. **Backend**:
   - Create new app: `python manage.py startapp app_name`
   - Add models in `backend/apps/app_name/models.py`
   - Create serializers in `backend/apps/app_name/serializers.py`
   - Add views in `backend/apps/app_name/views.py`
   - Register URLs in `backend/apps/app_name/urls.py`
   - Include in `backend/config/urls.py`
   - Create migrations: `python manage.py makemigrations app_name`
   - Apply migrations: `python manage.py migrate`

2. **Frontend**:
   - Add feature under `/frontend/src/features/feature_name/`
   - Follow structure: components/, hooks/, pages/, types/, schemas/
   - Create API client in `/frontend/src/shared/api/`
   - Add routes in `/frontend/src/app/App.tsx`
   - Use existing UI components from `/frontend/src/shared/components/ui/`
   - Follow TypeScript strict mode and existing naming conventions

### Database Changes

```bash
# Create migrations
python manage.py makemigrations [app_name]

# Review migrations (dry-run)
python manage.py migrate --dry-run

# Apply migrations
python manage.py migrate

# Rollback migration (if needed)
python manage.py migrate app_name <migration_number>
```

### Testing API Changes

```bash
# Health check
curl http://localhost:8000/health/

# Test events endpoint
curl http://localhost:8000/api/events/

# Test with filters
curl "http://localhost:8000/api/events/?search=tech&categories=academic"

# Test authenticated endpoint (replace TOKEN)
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/events/my-interests/
```

### Working with Protected Routes

**Frontend Pattern:**
```typescript
// Wrap page with ProtectedRoute for authentication
<Route path="/submit" element={<ProtectedRoute><SubmitEventPage /></ProtectedRoute>} />

// Wrap page with ProtectedAdminRoute for admin-only access
<Route path="/admin" element={<ProtectedAdminRoute><AdminPage /></ProtectedAdminRoute>} />
```

**Backend Pattern:**
```python
from apps.core.decorators import jwt_required, admin_required

@jwt_required
def my_view(request):
    user_id = request.user.user_id
    # ... user-specific logic

@admin_required
def admin_view(request):
    # ... admin-only logic
```

---

## Important Notes

### Critical Development Requirements

- **Database setup**: Use Docker Compose (recommended),  or local PostgreSQL
- Backend must be running for frontend to work (ports 8000 and 5173)
- Frontend path mapping: `@/*` maps to `./src/*`
- Backend uses environment-based settings (development.py, production.py)
- CORS is configured for frontend-backend communication
- Optional: Use `python scripts/populate-local-db-with-prod-data.py` to get production data locally

### Authentication

- All protected endpoints require JWT token in `Authorization: Bearer <token>` header
- Frontend gets token via Clerk's `getToken()` method
- Admin endpoints check `role` field in JWT payload
- User ID extracted from JWT `sub` claim

### Data Patterns

- **Cursor-based pagination**: All list endpoints use cursor pagination
- **Semicolon-separated OR queries**: Search and category filters support `value1;value2;value3`
- **UTC timestamps**: All dates stored in UTC, timezone info in `tz` field
- **JSONField usage**: For flexible data (categories, reactions, metadata)

### Rate Limiting

Events endpoints vary by operation type:
- List/detail: 100-600/hour
- Submissions: 5-10/hour (AI-intensive)
- Interests: 60/hour
- Admin: 100/hour

### Code Quality

- **Backend**: Use `ruff` for linting (configured in pyproject.toml)
- **Frontend**: ESLint with TypeScript support
- ESLint may show pre-existing warnings - focus only on new issues you introduce
- Follow existing patterns for consistency

### Scraping & AI

- Scraping runs in GitHub Actions (requires credentials)
- AI extraction requires OPENAI_API_KEY environment variable
- Content filtering: Rejects memes, inappropriate content, spam
- AI extraction requires both date AND time for events

---

## Recent Changes & Updates

### New Features (Last 2 Weeks)

1. **Event Interest System** - Users can mark events as "interested", filter by interested events
2. **Event Submissions with AI** - User-submitted events with AI extraction from screenshots
3. **Submissions Review Page** - Admin interface at `/admin/submissions` for reviewing submissions
4. **Loading Skeletons** - Added throughout events and clubs for better UX
5. **Real-time Events Banner** - TopBanner shows "Events added in real time!" message
6. **Multi-select Event Export** - Export multiple events to iCalendar or Google Calendar
7. **Search with localStorage** - Persists last search across sessions

### Infrastructure Changes

1. **Apify Migration** - Scraping migrated from Instaloader to Apify Instagram API
2. **Single User Scraping** - New workflow for scraping individual Instagram users
3. **Improved Price Parsing** - Better handling for free events and price extraction
4. **Enhanced Logging** - Clearer logging in scraping workflows
5. **Static Data Generation** - Updated to support RSS feeds

### Upcoming Features (Payments App)

- `/backend/apps/payments/` exists as placeholder
- Not yet implemented

---

## Production Deployment

### Backend (Vercel + PostgreSQL)
- Configured for Vercel serverless deployment
- PostgreSQL database (production)
- Database migrations handled automatically in production
- Environment variables required:
  - `CLERK_SECRET_KEY` - Clerk authentication
  - `OPENAI_API_KEY` - AI extraction
  - `RESEND_API_KEY` - Email sending
  - `AWS_S3_BUCKET_NAME`, `AWS_DEFAULT_REGION` - S3 storage
  - `SECRET_KEY` - Django secret key
  - `ALLOWED_PARTIES` - Authorized domains

### Frontend (Vercel)
- Built with Vite
- Deployed to Vercel
- Environment variables required:
  - `VITE_CLERK_PUBLISHABLE_KEY` - Clerk public key
  - `VITE_API_BASE_URL` - Backend API URL

### GitHub Actions
- Automated scraping runs on schedule
- Requires Instagram API credentials
- Generates static data files (events.json, rss.xml)

---

## File Reference Guide

### Key Frontend Files
- Main app: `frontend/src/app/App.tsx:1`
- App setup: `frontend/src/app/main.tsx:1`
- Events page: `frontend/src/features/events/pages/EventsPage.tsx:1`
- Events hook: `frontend/src/features/events/hooks/useEvents.ts:1`
- Interest hook: `frontend/src/features/events/hooks/useEventInterest.ts:1`
- API clients: `frontend/src/shared/api/index.ts:1`
- Protected routes: `frontend/src/shared/components/ProtectedRoute.tsx:1`
- Clerk store: `frontend/src/shared/stores/clerkAuthStore.ts:1`

### Key Backend Files
- Events models: `backend/apps/events/models.py:1`
- Events views: `backend/apps/events/views.py:1`
- Event filters: `backend/utils/filters.py:1`
- Auth backend: `backend/apps/core/authentication.py:1`
- Auth decorators: `backend/apps/core/decorators.py:1`
- OpenAI service: `backend/services/openai_service.py:1`
- Email service: `backend/services/email_service.py:1`
- Storage service: `backend/services/storage_service.py:1`
- Main URLs: `backend/config/urls.py:1`
- Settings: `backend/config/settings/base.py:1`

---

## Getting Help

### Support & Contact
- **Live Site**: [wat2do.ca](https://wat2do.ca)
- **Contact Form**: [wat2do.ca/contact](https://wat2do.ca/contact)
- **GitHub Issues**: [github.com/ericahan22/bug-free-octo-spork/issues](https://github.com/ericahan22/bug-free-octo-spork/issues)

### Troubleshooting
- Check GitHub issues for known problems
- Review error logs in browser console (frontend) or terminal (backend)
- Use `/health/` endpoint to verify backend is running
- Verify database setup (Docker,  , or PostgreSQL)
- Check that both frontend and backend servers are running
- Ensure Clerk environment variables are set correctly
