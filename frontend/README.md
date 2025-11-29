# Plantio Frontend

This is a Vite + React starter frontend for the Plantio project.

## Setup

1. Install dependencies:
   ```
   npm install
   ```

2. Create `.env` file in project root (optional) and set API base:
   ```
   VITE_API_BASE=http://localhost:8000
   ```

3. Start dev server:
   ```
   npm run dev
   ```

The app expects backend endpoints:
- `GET /api/v1/plants`
- `GET /api/v1/diseases`
- `POST /api/v1/diagnose` (multipart form with key `file`)
