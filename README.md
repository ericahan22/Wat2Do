# Instagram Event Scraper API

This project has been restructured to follow a modern Django-based architecture.

## Project Structure

```
my_project/
│
├── docker-compose.yml
├── requirements.txt
│
├── backend/
│   ├── Dockerfile
│   ├── manage.py
│   ├── requirements.txt
│
│   ├── scraping/              # Placeholder for future scraping logic
│   │   └── __init__.py
│
│   ├── my_django_project/     # Django project folder (settings, etc.)
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│
│   ├── app/                   # API app (no templates/static)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── urls.py
│   │   └── views.py
│
│   └── scripts/               # Scraping scripts and data files
│       ├── __init__.py
│       ├── ai_client.py
│       ├── instagram_feed.py
│       ├── scrape.py
│       ├── club_info.csv
│       └── event_info.csv
│
└── frontend/                  # React app (handled independently)
    └── ...
```

## Migration Summary

### Changes Made:
1. **Restructured folders**: Moved scraping files from `/scraping/` to `/backend/scripts/`
2. **Migrated from Flask to Django**: Converted Flask API to Django REST Framework
3. **Updated requirements.txt**: Replaced Flask dependencies with Django and DRF
4. **Created Docker setup**: Added Dockerfile for backend containerization
5. **Created empty frontend folder**: Ready for React development
6. **Created empty docker-compose.yml**: Ready for multi-container setup

### API Endpoints (Django REST Framework):
- `GET /api/` - Home endpoint with API info
- `GET /api/health/` - Health check
- `GET /api/events/` - Get all events from event_info.csv
- `GET /api/clubs/` - Get all clubs from club_info.csv
- `GET /api/events/search/?club_name=<name>` - Search events by club name

## Setup Instructions

### Frontend (React)
```bash
cd frontend
npm i
npm run dev
```

### Backend (Django)
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Docker
```bash
cd backend
docker build -t instagram-scraper-api .
docker run -p 8000:8000 instagram-scraper-api
```

## Dependencies

### Backend Requirements:
- Django 4.2.7
- Django REST Framework 3.14.0
- Django CORS Headers 4.3.1
- Pandas 2.0.3
- NumPy 1.24.3
- Gunicorn 21.2.0
- Plus scraping utilities (instaloader, requests, beautifulsoup4, openai)

## Notes

- The Django server runs on port 8000
- CSV files are now located in `/backend/scripts/`
- API endpoints are prefixed with `/api/`
- CORS is enabled for frontend integration
- Database is SQLite (can be changed to PostgreSQL for production)

## API Commands

| Goal/Description | cURL Command |
|------------------|--------------|
| Get API info | `curl http://localhost:8000/api/` |
| Health check | `curl http://localhost:8000/api/health/` |
| Get all events | `curl http://localhost:8000/api/events/` |
| Get all clubs | `curl http://localhost:8000/api/clubs/` |
| Create mock event | `curl -X POST http://localhost:8000/api/mock-event/ -H "Content-Type: application/json" -d '{"name": "Test Event", "location": "Test Location", "food": "Pizza"}'` |
| Find similar events | `curl "http://localhost:8000/api/test-similarity/?text=Your%20Search%20Text"` | 