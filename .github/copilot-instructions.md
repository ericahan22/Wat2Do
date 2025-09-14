# Instagram Event Scraper API

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

This is a full-stack web application consisting of a Django REST API backend and a React + TypeScript frontend for scraping and displaying Instagram events from university clubs.

## Working Effectively

### Bootstrap Environment
- Run these commands in sequence to set up the development environment:
  - Backend setup:
    ```bash
    cd backend
    source .venv/bin/activate
    pip install -r requirements.txt   
    python manage.py migrate    
    python manage.py runserver 8000  
    ```
  - Frontend setup:
    ```bash
    cd frontend
    npm install                
    npm run build                 
    npm run dev                   
    ```

### Development Database Configuration
- **CRITICAL**: Always set `export USE_SQLITE=1` before running Django commands for local development
- Without this environment variable, Django will try to connect to PostgreSQL and fail
- The production environment uses PostgreSQL via Supabase, but local development uses SQLite

### Build and Test Commands
- Backend:
  - `python manage.py check` - Django configuration check (<1 second)
  - `python manage.py test` - Run Django tests (currently no tests defined)
  - `python manage.py migrate` - Apply database migrations (<1 second)
- Frontend:
  - `npm run build` - Production build (~9 seconds)
  - `npm run lint` - ESLint check (~3 seconds, may show warnings/errors)
  - `npm run dev` - Development server (starts immediately)
  - `npm run preview` - Preview production build

### Running Applications
- Backend API server:
  ```bash
  cd backend
  export USE_SQLITE=1
  python manage.py runserver 8000
  ```
  Available at http://localhost:8000/ with endpoints:
  - `GET /` - API information
  - `GET /health/` - Health check  
  - `GET /events/` - Get all events
  - `GET /clubs/` - Get all clubs

- Frontend development server:
  ```bash
  cd frontend
  npm run dev
  ```
  Available at http://localhost:5173/

## Validation

### Always Test These Scenarios After Making Changes
1. **Backend API validation**:
   - Start backend server with SQLite
   - Test endpoints: `curl http://localhost:8000/health/` should return `{"status":"healthy","message":"Server is running"}`
   - Test API info: `curl http://localhost:8000/` should return JSON with endpoints info
   - Test events endpoint: `curl http://localhost:8000/events/` should return events list (may be empty)

2. **Frontend validation**:
   - Build frontend successfully with `npm run build`
   - Start development server with `npm run dev`
   - Verify server starts on port 5173 with no errors
   - Check that `curl -I http://localhost:5173/` returns HTTP 200

3. **Full-stack integration**:
   - Run both backend (port 8000) and frontend (port 5173) simultaneously
   - Frontend should connect to backend API for data

### Linting and Code Quality
- **Backend**: Use Django's built-in checks: `python manage.py check --deploy`
- **Frontend**: Always run `npm run lint` before committing (may show existing warnings, focus on new ones)
- Frontend linting currently shows some pre-existing issues - do not spend time fixing unless directly related to your changes

## Common Issues and Workarounds

### Database Connection Issues
- **Problem**: `django.db.utils.OperationalError: could not translate host name "your-project.supabase.co"`
- **Solution**: Always set `export USE_SQLITE=1` environment variable for local development

### Secret Key Issues  
- **Problem**: `ImproperlyConfigured: The SECRET_KEY setting must not be empty`
- **Solution**: Already fixed in settings.py with a default development key

### Static Files Warning
- **Problem**: `The directory '/path/to/backend/static' in the STATICFILES_DIRS setting does not exist`
- **Solution**: Run `mkdir -p backend/static` (already resolved)

### Docker Build Issues
- **Problem**: Docker build fails with SSL certificate errors in restricted environments
- **Solution**: Do not attempt Docker builds in restricted environments. Use local Python environment instead.

### Frontend ESLint Errors
- **Problem**: ESLint shows errors in existing code (currently 6 errors, 1 warning)
- **Solution**: Focus only on new errors introduced by your changes. Existing issues in EventsCalendar.tsx, button.tsx, and dateUtils.ts are pre-existing.

## Project Structure

### Backend (`/backend/`)
```
backend/
├── api/                    # Django project configuration
│   ├── settings.py        # Main settings (database, CORS, etc.)
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI application
├── example/               # Main Django app
│   ├── models.py          # Database models (Clubs, Events)
│   ├── views.py           # API endpoints
│   └── urls.py            # App-specific URLs
├── scraping/              # Instagram scraping scripts
│   ├── instagram_feed.py  # Main scraping script (requires secrets)
│   ├── ai_client.py       # OpenAI integration
│   └── scrape.py          # Scraping utilities
├── requirements.txt       # Python dependencies
├── manage.py              # Django management script
└── Dockerfile            # Docker configuration (may not work in restricted environments)
```

### Frontend (`/frontend/`)
```
frontend/
├── src/
│   ├── components/        # React components
│   ├── hooks/             # Custom React hooks  
│   ├── lib/               # Utility functions
│   └── App.tsx            # Main application component
├── package.json           # Node.js dependencies and scripts
├── vite.config.ts         # Vite build configuration
├── tsconfig.json          # TypeScript configuration
└── eslint.config.js       # ESLint configuration
```

## Dependencies and Versions

### Backend Requirements
- Django 4.2.7
- Django REST Framework 3.14.0
- PostgreSQL support (psycopg2-binary)
- Data processing: pandas, numpy
- Scraping: instaloader (custom build), requests, beautifulsoup4
- AI: openai
- Production: gunicorn, whitenoise

### Frontend Dependencies  
- React 19.1.0 with TypeScript
- Build tool: Vite 7.1.3
- Styling: TailwindCSS 4.1.11
- UI components: Radix UI components
- State management: TanStack Query
- Development: ESLint, TypeScript ESLint

## CI/CD Integration

### GitHub Actions Workflow (`.github/workflows/instagram_feed.yml`)
- Runs daily Instagram scraping job
- Requires external secrets (Instagram credentials, OpenAI API key, database URL)
- Uses Python 3.11 runtime
- Caches pip dependencies for faster builds
- Uploads scraping logs as artifacts

### Important Notes
- The scraping workflow requires external services and credentials not available in local development
- Focus development on the API and frontend components rather than scraping functionality
- The workflow is configured for production environment with real Instagram data

## Timing Expectations and Timeouts

- **pip install**: 22 seconds, set timeout to 60+ seconds, NEVER CANCEL
- **npm install**: 12 seconds, set timeout to 30+ seconds, NEVER CANCEL  
- **npm run build**: 9 seconds, set timeout to 30+ seconds, NEVER CANCEL
- **Database migrations**: <1 second
- **Server startup**: Both backend and frontend start immediately (<5 seconds)
- **ESLint**: 3 seconds

## Quick Command Reference

```bash
# Backend development
cd backend
export USE_SQLITE=1
pip install -r requirements.txt
python manage.py migrate  
python manage.py runserver 8000

# Frontend development  
cd frontend
npm install
npm run dev

# Testing
curl http://localhost:8000/health/     # Backend health check
curl -I http://localhost:5173/         # Frontend health check

# Build and validate
cd frontend && npm run build && npm run lint
cd backend && export USE_SQLITE=1 && python manage.py check

# Full workflow validation
cd backend && export USE_SQLITE=1 && python manage.py check
cd ../frontend && npm run build
echo "All systems operational!"
```

## Manual Validation Scenarios

After making any changes, always complete these validation scenarios:

1. **Complete Development Setup Test**:
   - Start fresh terminal
   - Follow bootstrap instructions exactly
   - Verify both servers start without errors
   - Test all API endpoints respond correctly

2. **Build Pipeline Test**:
   - Clean build: `rm -rf frontend/dist backend/db.sqlite3`
   - Full rebuild following bootstrap instructions
   - Verify no new linting errors beyond existing 7 issues
   - Confirm both development servers start successfully

3. **API Functionality Test**:
   - Start backend with SQLite
   - Test each endpoint: `/`, `/health/`, `/events/`, `/clubs/`
   - Verify JSON responses are well-formed
   - Check database operations work (migrations, etc.)

4. **Cross-Platform Compatibility**:
   - Instructions tested on Linux with Python 3.12 and Node.js 20.19
   - SQLite configuration ensures database portability
   - No external services required for basic development