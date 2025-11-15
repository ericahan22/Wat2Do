# Instagram Event Scraper API

This is a full-stack web application with a Django REST API backend and a React + TypeScript frontend for scraping and displaying Instagram events from clubs at the University of Waterloo.

DO NOT EVER MANUALLY EDIT MIGRATION FILES EVER OR YOU WILL BE TERMINATED.

---

## Environment Setup

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export USE_SQLITE=1
python manage.py migrate
python manage.py runserver 8000
```

### Frontend
```bash
cd frontend
npm install
npm run build
npm run dev
```

### AI Client Test
```bash
cd backend
python test_ai_client.py
```

---

## Local Development

- **Always set** `export USE_SQLITE=1` before running Django commands locally.
- Production uses PostgreSQL (Supabase); local uses SQLite.

---

## Build & Test Commands

### Backend
- `python manage.py check` — Django config check
- `python manage.py test` — Run Django tests
- `python manage.py migrate` — Apply migrations

### Frontend
- `npm run build` — Production build
- `npm run lint` — ESLint check
- `npm run dev` — Dev server
- `npm run preview` — Preview production build

---

## Running Applications

- **Backend:**  
  http://localhost:8000/
  - `/` — API info
  - `/health/` — Health check
  - `/events/` — All events
  - `/clubs/` — All clubs

- **Frontend:**  
  http://localhost:5173/

---

## Validation Checklist

1. **Backend API**
   - Start backend with SQLite
   - `curl http://localhost:8000/health/` → `{"status":"healthy","message":"Server is running"}`
   - `curl http://localhost:8000/` → endpoints info
   - `curl http://localhost:8000/events/` → events list

2. **Frontend**
   - `npm run build` succeeds
   - `npm run dev` starts on port 5173
   - `curl -I http://localhost:5173/` → HTTP 200

3. **Full-stack**
   - Run both servers
   - Frontend connects to backend API

4. **Linting**
   - Backend: `python manage.py check --deploy`
   - Frontend: `npm run lint` (focus on new errors only)

---

## Common Issues

- **Database:**  
  Set `export USE_SQLITE=1` for local dev to avoid PostgreSQL errors.

- **Static Files:**  
  If you see a static files warning, run:  
  `mkdir -p backend/static`

- **Docker:**  
  Use local Python, not Docker, in restricted environments.

- **ESLint:**  
  Ignore pre-existing frontend lint errors unless you change those files.

---

## Project Structure

### Backend (`/backend/`)
```
backend/
├── api/                # Django config
├── example/            # Main app (models, views, urls)
├── scraping/           # Instagram scraping scripts
├── requirements.txt
├── manage.py
```

### Frontend (`/frontend/`)
```
frontend/
├── src/
│   ├── app/
│   │   └── App.tsx
│   └── shared/
│       ├── components/
│       ├── hooks/
│       └── lib/
├── package.json
├── vite.config.ts
├── tsconfig.json
```

---

## Dependencies

### Backend
- Django 4.2.7
- Django REST Framework 3.14.0
- psycopg2-binary (Postgres)
- django-filter
- django-cors-headers
- whitenoise
- pgvector
- apify_client
- requests, beautifulsoup4
- openai
- python-dotenv
- python-dateutil
- Pillow
- boto3
- gunicorn

### Frontend
- React 19.1.0 + TypeScript
- Vite 7.1.3
- TailwindCSS 4.1.11
- Radix UI
- TanStack Query
- ESLint

---

## CI/CD

- GitHub Actions workflow runs daily scraping job.
- Requires secrets: APIFY_API_TOKEN, OpenAI API key, database URL.
- Uses Python 3.11, caches pip dependencies, uploads logs as artifacts.

---

## Quick Reference

```bash
# Backend
cd backend
export USE_SQLITE=1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000

# Frontend
cd frontend
npm install
npm run dev

# Build & Lint
cd frontend && npm run build && npm run lint
cd backend && export USE_SQLITE=1 && python manage.py check
```

---

## Manual Validation

1. **Setup Test:**  
   - Fresh terminal, follow setup steps, verify both servers start, test endpoints.

2. **Build Pipeline Test:**  
   - Clean build: `rm -rf frontend/dist backend/db.sqlite3`
   - Full rebuild, verify no new lint errors, both servers start.

3. **API Test:**  
   - Backend with SQLite, test `/`, `/health/`, `/events/`, `/clubs/`.

4. **Cross-Platform:**  
   - Works on Linux (Python 3.12, Node.js 20.19), SQLite for portability.

---

**Always reference these instructions first. Use search or bash commands only if you encounter unexpected issues not covered here.**