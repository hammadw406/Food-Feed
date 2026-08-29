# Frontend — Feed UI

**Owner:** Person 1 · **Stack:** Next.js (React), Tailwind CSS, Zustand/React Context, Framer Motion, TanStack Query

## Responsibilities
- Scrollable/swipeable feed UI
- Client-side interaction capture: dwell time, skip, like, tap
- Wiring the feed to the backend API (`NEXT_PUBLIC_API_URL`)
- Restaurant detail screen (menu, price, reviews)
- Loading/empty states, diverse-feel first-session UX
- Deployment to Vercel

## Setup
```bash
npm install
cp ../.env.example .env.local   # fill in NEXT_PUBLIC_API_URL, etc.
npm run dev
```

## Notes
- Until the backend's real feed endpoint is ready, build against a mocked feed API so frontend and backend can work in parallel (see root README's execution plan, Phase 5).
