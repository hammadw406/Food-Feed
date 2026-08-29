# Food Feed 🍔

**A personalized food discovery feed that learns what you're craving from how you interact with it — and connects that to real restaurants in DHA, Lahore you can actually order from or visit.**

[![CI](https://github.com/hammadw406/Food-Feed-/actions/workflows/ci.yml/badge.svg)](https://github.com/hammadw406/Food-Feed-/actions)
![Status](https://img.shields.io/badge/status-MVP%20in%20development-orange)
![Scope](https://img.shields.io/badge/scope-DHA%2C%20Lahore-blue)
![Version](https://img.shields.io/badge/version-1.0-lightgrey)

---

## Table of Contents

- [The Problem](#the-problem)
- [The Product](#the-product)
- [Goals (MVP)](#goals-mvp)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Data Sources](#data-sources)
- [Repository Structure](#repository-structure)
- [Team & Ownership](#team--ownership)
- [Execution Plan](#execution-plan)
- [Success Metric](#success-metric)
- [Getting Started](#getting-started)
- [Contributing](#contributing)

---

## The Problem

Most food apps assume the user already knows what they want and just need help finding it. In reality, a lot of users open a food app hungry but with no clear intention — and existing platforms have nothing to offer someone who can't yet declare a search term, cuisine, or price filter.

> **Core question:** how do we help a person discover food they're likely to enjoy — even when they don't know what they want — by learning from their behavior and context instead of asking them to declare intent?

## The Product

Not a search engine. Not a directory. Not an ordering platform.

Users scroll a feed of real food and restaurant content. The system watches how they react — dwell time, skips, likes, taps — and uses that signal to learn what they're craving, then reshapes what it shows next.

The core loop — **every interaction reshapes the very next feed the user sees** — *is* the product.

## Goals (MVP)

| Goal | Success looks like |
|---|---|
| **Solve cold start** | A brand-new user gets a reasonably relevant feed within their first 10–15 interactions, without filling any form |
| **Prove the learning loop** | User preference signal visibly shifts feed content within a single session |
| **Ground in real data** | All recommended restaurants and food are real, from real datasets — not fabricated |
| **Keep scope small** | MVP works for one city/area (DHA, Lahore) and one data slice (fast food) before expanding |

**Out of scope for MVP:** ordering/checkout/payments, multi-city coverage, social features, conversational LLM interface, restaurant owner dashboard.

## How It Works

1. **Client app** captures every interaction — view, dwell time, skip, like, tap
2. **Event collector** logs each interaction with a timestamp and context
3. **User embedding** updates in real time — a weighted average of embeddings of items the user engaged with positively
4. **Candidate generation** runs a nearest-neighbor search (pgvector) to find ~50 plausible items for the next feed
5. **Ranking model** (LightGBM) scores and orders those candidates using embedding similarity, rating, price, and context
6. **Real restaurant data** grounds every candidate shown — nothing is fabricated
7. **Feedback loop** — engagement flows back in, shaping the next feed

```
Client → Event Collector → User Embedding → Candidate Generation → Ranking → Feed
                                     ▲                                        │
                                     └────────────── Feedback Loop ───────────┘
```

**Two speeds of learning:**

| Speed | What updates | How |
|---|---|---|
| **Real-time** | User's embedding vector | Weighted average, recomputed instantly on every interaction |
| **Batch** (daily/weekly) | The LightGBM ranking model itself | Retrained offline on accumulated interaction logs, then swapped in |

**Cold start:** before any ranking model exists (day zero), the system relies on candidate generation and diverse sampling alone — no ranking model, or a simple rule-based fallback — until enough interaction data accumulates to train the first version.

## Tech Stack

| Layer | Choice |
|---|---|
| **Frontend** | Next.js (React) · Tailwind CSS · Zustand / React Context · Framer Motion · TanStack Query |
| **Backend, Data & ML** | Python + FastAPI · PostgreSQL · pgvector · Redis · sentence-transformers (`all-MiniLM-L6-v2`) · LightGBM · pandas + scikit-learn |
| **Infrastructure** | Vercel (frontend hosting) · Railway/Render (backend hosting) · Supabase Auth / Clerk (auth) · GitHub Actions (CI/CD) · Sentry (monitoring) · Mapbox (maps) · PostHog (analytics) |

```
Next.js → FastAPI → PostgreSQL + pgvector + Redis → sentence-transformers + LightGBM → real restaurant data
```

## Data Sources

| Source | Rows / scope | Use |
|---|---|---|
| Lahore Fast Food Restaurants (DHA-tagged) | ~247 rows | Primary MVP dataset — area, cuisine, rating, dine-in/delivery flags |
| Pakistan Cities Foodpanda Reviews | ~3,000 Lahore rows | Scale-up dataset once the loop is validated |
| Pakistan Restaurants Data (broad) | Nationwide, 9 columns | Coverage benchmark, not core to MVP |
| Sentiment Analysis Model | Pretrained model | Enriches review text into a sentiment signal for ranking |

## Repository Structure

```
.
├── frontend/     # Next.js feed UI, interaction capture, restaurant detail
├── backend/      # FastAPI service, event pipeline, DB schema, Redis cache, auth
├── ml/           # Embeddings, pgvector candidate generation, LightGBM ranking model
├── infra/        # ETL, dataset cleaning, hosting config, CI/CD, monitoring
└── .github/
    └── workflows/  # GitHub Actions CI
```

## Team & Ownership

| Person | Role | Owns | Branch |
|---|---|---|---|
| Person 1 | Frontend / Product | Client app, feed UI, interaction capture, deployment | `feature/frontend-feed-ui` |
| Person 2 | Backend / API | FastAPI service, event pipeline, database schema | `feature/backend-api` |
| Person 3 | ML / Recommendation | Embeddings, candidate generation, ranking model | `feature/ml-embeddings` |
| Person 4 | Data / Infra | Dataset cleaning, hosting, auth, CI/CD, testing | `feature/infra-etl` |

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full branching workflow.

## Execution Plan

| Phase | What happens | Lead | Support |
|---|---|---|---|
| 1. Data foundation | Clean and unify the DHA fast-food dataset into a single schema | Person 4 | Person 3 |
| 2. Interaction schema + simulator | Define event schema, build synthetic user simulator | Person 3 | Person 2 |
| 3. Preference + cold-start logic | Per-user scoring, epsilon-greedy exploration, diverse cold-start rule | Person 3 | — |
| 4. Embeddings + candidate generation | Compute item embeddings, wire up pgvector | Person 3 | Person 2 |
| 5. Ranking model | Train initial LightGBM model on simulated/early data | Person 3 | — |
| 6. Minimal feed UI | Build scrollable feed wired to real data | Person 1 | Person 2 |
| 7. Internal test loop | Real test users in DHA; confirm feed adapts within a session | Person 4 | Everyone |
| 8. Iterate | Batch retraining cadence, context-awareness, expand dataset | Everyone | — |

## Success Metric

Not revenue, not retention — just proving the loop works:

> A new user, after 10–15 interactions with no explicit input, receives a feed measurably more aligned to their revealed preference than the initial diverse feed — grounded entirely in real restaurant data.

## Getting Started

```bash
git clone https://github.com/hammadw406/Food-Feed-.git
cd Food-Feed-

# frontend
cd frontend && npm install && npm run dev

# backend (in a new terminal)
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Copy `.env.example` to `.env` and fill in real values (database URL, Redis URL, auth keys) before running the backend.

See each module's own README for setup specific to that layer:
- [`frontend/README.md`](./frontend/README.md)
- [`backend/README.md`](./backend/README.md)
- [`ml/README.md`](./ml/README.md)
- [`infra/README.md`](./infra/README.md)

## Contributing

Branch off `dev`, not `main`. See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full workflow, commit conventions, and PR expectations.
