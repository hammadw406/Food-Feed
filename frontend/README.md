# Frontend — Food Feed (Next.js)

Desktop-first responsive web UI for the Food Feed discovery product.
**Owner:** Person 1 · **Stack:** Next.js 14 (App Router, TS) · Tailwind CSS · TanStack Query

## Setup

```bash
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL to the running FastAPI
npm run dev                        # http://localhost:3000
```

## Backend contract consumed

The frontend talks to **only the four endpoints the backend actually exposes**:

| Endpoint | Used by |
|---|---|
| `GET /feed?user_id&limit&offset` | Discovery feed, For-You status |
| `POST /events` | Interaction tracking (`view` / `skip` / `like` / `tap` + `dwell_time_ms`) |
| `GET /restaurants/{restaurant_id}` | Restaurant detail, Food detail context |
| `GET /health` | (available; optional) |

All network calls go through `src/lib/api/` — one client, no duplicate fetch logic.
`src/lib/api/normalizeFeedItem.ts` tolerates both the declared and the actual
`/feed` item shapes (the two disagree in the backend today).

## Anonymous identity

No login. `src/lib/session/identity.ts` mints a stable `user_id` + rolling
`session_id` in `localStorage`; these are sent with every event.

## What is NOT wired (no backend for it)

Sign In / Sign Up, Community, Create Post, cuisine-affinity percentages, bank
offers, food media, match scores and distance have **no backend**. Those screens
are built and clearly labelled as previews — no mock data, no fake success.
See the in-app notices and the implementation report.

## Routes

`/` landing · `/login` `/signup` (static) · `/onboarding` · `/discover` ·
`/foods/[id]` · `/restaurants/[id]` · `/community` `/community/new` (preview) ·
`/for-you` · `/profile`

## Scripts

`npm run dev` · `npm run build` · `npm run lint` · `npm start`
