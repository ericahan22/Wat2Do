# Wat2Do Legacy Frontend

This repository is frontend-only.
Do not add a backend, database, admin surface, Clerk integration, or a second API implementation.

## Architecture

- `frontend/src/app` owns routes and application setup.
- `frontend/src/features` owns event, organization, search, and OTP authentication behavior.
- `frontend/src/shared/api` is the only API client layer.
- `frontend/src/shared/components` owns reusable presentation.
- Wat2Do V2 is the source of truth for events, organizations, authentication, and V1-specific saved events.
- Production `/api` requests are proxied to `https://wat2do.io/api` by `frontend/vercel.json`.

## Supported authenticated behavior

- Request and verify an email OTP through `/api/auth`.
- Refresh and end a V2 session through `/api/auth`.
- Read and update V1-specific saved events through `/api/v1/saved-events`.

Do not add registration, passwords, administration, event submission, or any legacy server behavior.
New users are created by the V2 OTP flow.

## Commands

Run commands from `frontend/`.

```bash
npm install
npm run lint
npm run build
```

Do not commit build output or local environment files.
