# Wat2Do

<p align="center">
  <img src="frontend/public/wat2do-logo.svg" alt="Wat2Do Logo" width="180"/>
</p>

<p align="center">
  <a href="https://wat2do.ca" target="_blank">
    <img src="https://img.shields.io/badge/Live%20Site-wat2do.ca-blue?style=flat-square" alt="Live Site"/>
  </a>
  <a href="https://github.com/ericahan22/bug-free-octo-spork/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/ericahan22/bug-free-octo-spork/update-events-data.yml?branch=main&style=flat-square" alt="GitHub Actions Status"/>
  </a>
  <a href="https://vercel.com/ericas-projects-4f2175b1/bug-free-octo-spork-frontend">
    <img src="https://deploy-badge.vercel.app/vercel/bug-free-octo-spork-frontend?logo=&name=vercel+frontend&style=flat-square" alt="Frontend Deployment Status"/>
  </a>
</p>

<a href="https://wat2do.ca" target="_blank">Wat2Do.ca</a> is a web app to help you discover club events at the University of
Waterloo, scraped directly from Instagram.

## ✨ Features

- **Browse, search, and filter events:** See upcoming and past events from campus clubs
- **Club directory:** Explore all clubs with links to their website/Instagram
- **Email newsletter:** Subscribe to get the latest events in your inbox, once daily

**How It Works:**  
Events are automatically collected from club Instagram posts, using the OpenAI API to extract details from captions and images. Data is refreshed daily.

## 🛠️ Project Structure

```
.
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── apps/               # Django apps (events, clubs, newsletter, etc.)
│   ├── scraping/           # Instagram scraping scripts
│   └── config/             # Settings and URLs
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── App.tsx
│   │   ├── features/
│   │   └── shared/
│   │       ├── components/
│   │       └── hooks/
│   ├── package.json
│   └── public/
```

### Environment Setup

#### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🏗️ Build & Test

### Backend
- `python manage.py check` — Django config check
- `python manage.py test` — Run Django tests
- `python manage.py migrate` — Apply migrations

### Frontend
- `npm run build` — Production build
- `npm run lint` — ESLint check
- `npm run dev` — Dev server
- `npm run preview` — Preview production build

## 🌐 API Endpoints

| Description         | URL/Command                                               |
|---------------------|----------------------------------------------------------|
| API info            | `curl http://localhost:8000/`                            |
| Health check        | `curl http://localhost:8000/health/`                     |
| Get all events      | `curl http://localhost:8000/events/`                     |
| Get all clubs       | `curl http://localhost:8000/clubs/`                      |
| Find similar events | `curl "http://localhost:8000/test-similarity/?text=..."` |

---

## 🤝 Support

If you have questions or feedback, please reach out at <a href="https://wat2do.ca/contact" target="_blank">wat2do.ca/contact</a> or add a <a href="https://github.com/ericahan22/bug-free-octo-spork/issues" target="_blank">GitHub issue</a>.

Enjoy discovering events!