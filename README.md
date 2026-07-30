# Wat2Do Legacy Frontend

<p align="center">
  <img src="frontend/public/wat2do-logo.svg" alt="Wat2Do Logo" width="180"/>
</p>

This repository contains the legacy Wat2Do frontend served at [wat2do.ca](https://wat2do.ca).
It has no backend or database of its own.
Event and organization data, OTP authentication, and V1-specific saved events all come from the Wat2Do V2 API.

## Supported behavior

- Browse, search, and filter University of Waterloo events.
- Browse the organization directory.
- Sign in with an email OTP issued by Wat2Do V2.
- Save events to the V1-specific saved-events table in Wat2Do V2.

The legacy admin, submission, newsletter, waitlist, promotion, scraping, and server code have been removed.

## Local development

```bash
cd frontend
npm install
npm run dev
```

Copy `frontend/.env.example` to `frontend/.env` when local values are needed.
Production requests under `/api` are proxied to the Wat2Do V2 API by Vercel.

## Verification

```bash
cd frontend
npm run lint
npm run build
```

## Support

Use the [contact page](https://wat2do.ca/contact) or open a [GitHub issue](https://github.com/ericahan22/bug-free-octo-spork/issues).
