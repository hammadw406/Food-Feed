# Backend — API & Event Pipeline

**Owner:** Person 2 · **Stack:** Python, FastAPI, PostgreSQL, pgvector, Redis

## Responsibilities
- FastAPI endpoints: feed request, event logging, restaurant detail
- PostgreSQL schema: restaurants, menu items, users, events
- Event pipeline: `user_id, item_id, event_type, dwell_time, timestamp, context`
- Redis caching layer for fast feed responses
- Auth integration (Supabase Auth / Clerk)

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env         # fill in DATABASE_URL, REDIS_URL, auth keys
uvicorn main:app --reload
```

## Event schema

| field | type | notes |
|---|---|---|
| user_id | uuid | |
| item_id | uuid | restaurant or menu item |
| event_type | enum | view / dwell / skip / like / tap |
| dwell_time | float (seconds) | nullable for non-dwell events |
| timestamp | datetime | UTC |
| context | jsonb | time of day, session id, etc. |

This schema is shared with the ML side (Person 3) — align on any change before merging.
