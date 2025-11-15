# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack Instagram event scraper application built with Django REST API backend and React + TypeScript frontend. The application scrapes university club events from Instagram and provides a web interface for browsing events and clubs.

## Development Setup Commands

### Backend (Django)
```bash
cd backend
export USE_SQLITE=1  # CRITICAL: Required for local development
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

### Frontend (React + TypeScript)
```bash
cd frontend
npm install
npm run dev  # Development server on port 5173
```

## Build and Test Commands

### Backend
- `python manage.py check` - Django configuration check
- `python manage.py test` - Run Django tests
- `python manage.py migrate` - Apply database migrations
- `python manage.py runserver 8000` - Start development server

### Frontend
- `npm run build` - Production build
- `npm run lint` - ESLint check (shows existing warnings, focus on new ones)
- `npm run lint:fix` - Auto-fix ESLint issues
- `npm run dev` - Development server
- `npm run preview` - Preview production build

### Code Quality
- Backend: Use `ruff` for linting (configured in pyproject.toml)
- Frontend: ESLint with TypeScript support

## Architecture

### Backend Structure (`/backend/`)
- **Django REST Framework** with modular app structure
- **Apps**: `events`, `clubs`, `newsletter`, `promotions`, `core`
- **Database**: PostgreSQL (production) / SQLite (local with USE_SQLITE=1)
- **Services**: OpenAI integration, email service, S3 storage
- **Scraping**: Instagram data extraction with Apify

### Frontend Structure (`/frontend/`)
- **Feature-based architecture** under `/src/features/`
- **Shared components** in `/src/shared/`
- **State management**: TanStack Query for server state, Zustand for client state
- **UI**: TailwindCSS with Radix UI components
- **Routing**: React Router with lazy loading

### Key Frontend Features
- Events calendar and grid views with filtering
- Club directory with search
- Admin panel for event promotion
- Newsletter unsubscribe functionality
- Responsive design with dark mode support

## Database Configuration

**CRITICAL**: Always set `export USE_SQLITE=1` for local development. Without this, Django attempts to connect to PostgreSQL and will fail locally.

## API Endpoints

Base URL: `http://localhost:8000/`
- `GET /` - API information
- `GET /health/` - Health check
- `GET /api/events/` - List events with filtering
- `GET /api/clubs/` - List clubs
- `POST /api/promotions/` - Promote events (admin)

## Common Development Workflows

### Adding New Features
1. Backend: Create new app or extend existing views in `/backend/apps/`
2. Frontend: Add feature under `/src/features/` following existing patterns
3. Use existing UI components from `/src/shared/components/ui/`
4. Follow TypeScript strict mode and existing naming conventions

### Database Changes
```bash
python manage.py makemigrations [app_name]
python manage.py migrate --dry-run  # Review before applying
python manage.py migrate
```

### Testing API Changes
```bash
# Health check
curl http://localhost:8000/health/

# Test events endpoint
curl http://localhost:8000/api/events/

# Test with parameters
curl "http://localhost:8000/api/events/?category=academic"
```

## Important Notes

- The scraping functionality requires external credentials and runs in GitHub Actions
- Frontend has path mapping: `@/*` maps to `./src/*`
- Backend uses environment-based settings (development.py, production.py)
- CORS is configured for frontend-backend communication
- ESLint may show pre-existing warnings - focus only on new issues you introduce

## Production Deployment

- Backend: Configured for Vercel with PostgreSQL
- Frontend: Built with Vite, deployed to Vercel
- Database migrations handled automatically in production
- Environment variables required for Instagram API and OpenAI integration