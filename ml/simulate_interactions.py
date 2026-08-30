"""
simulate_interactions.py

Generates synthetic users with latent preference profiles, then simulates
realistic scroll-feed behavior against the real candidate items already in
Supabase (items table) -- producing view/skip/like/tap events with dwell
times, written to the `interactions` table.

Why simulate at all: with zero real users so far, this gives the
recommendation logic (preference scoring, cold-start sampling) something
real to run against and validate before actual users exist.

How a synthetic user "prefers" things: each simulated user gets a random
mix of 1-3 preferred categories (e.g. "BBQ & Grill", "Pizza") and a
preferred price sensitivity (low/mid/high). Items matching those get
higher engagement probability (more likes/taps, longer dwell); non-matches
get mostly skips with short dwell. This is a simplification of real
behavior, not a claim about how real users behave -- it exists to exercise
the pipeline end-to-end.

Usage:
  python simulate_interactions.py --num-users 50 --skip-db
  python simulate_interactions.py --num-users 50
"""

import argparse
import os
import random
import sys
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent

EVENT_TYPES = ["view", "skip", "like", "tap"]
PRICE_BANDS = {"low": (0, 400), "mid": (400, 900), "high": (900, 10_000)}


def load_items(database_url: str) -> pd.DataFrame:
    import psycopg2
    conn = psycopg2.connect(database_url)
    try:
        df = pd.read_sql(
            "SELECT candidate_id, restaurant_id, category, price, display_name FROM items",
            conn,
        )
    finally:
        conn.close()
    return df


def generate_users(items_df: pd.DataFrame, num_users: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    categories = items_df["category"].dropna().unique().tolist()

    users = []
    for i in range(num_users):
        num_prefs = rng.randint(1, 3)
        preferred_categories = rng.sample(categories, min(num_prefs, len(categories)))
        price_pref = rng.choice(list(PRICE_BANDS.keys()))
        session_length = rng.randint(15, 40)  # how many items this user scrolls per session
        users.append({
            "user_id": f"sim_user_{i:03d}",
            "preferred_categories": preferred_categories,
            "price_pref": price_pref,
            "session_length": session_length,
        })
    return users


def matches_preference(item: pd.Series, user: dict) -> bool:
    category_match = item["category"] in user["preferred_categories"]
    price_lo, price_hi = PRICE_BANDS[user["price_pref"]]
    price = item["price"] if pd.notna(item["price"]) else 500
    price_match = price_lo <= price <= price_hi
    return category_match and price_match


def simulate_session(user: dict, items_df: pd.DataFrame, rng: random.Random) -> list[dict]:
    """One scroll session: user sees session_length items, reacts to each.

    Sampling is mixed: ~40% of shown items are deliberately drawn from the
    user's preferred category/price combo, ~60% are random exploration.
    Pure random sampling from a large, many-category catalog produces too
    few genuine preference matches per session to generate a learnable
    signal (e.g. ~1-2 matches out of 37 random items) -- this mirrors how
    a real feed algorithm would already be nudging toward relevant content
    rather than showing everything with equal probability.
    """
    session_id = str(uuid.uuid4())
    n = min(user["session_length"], len(items_df))

    price_lo, price_hi = PRICE_BANDS[user["price_pref"]]
    matching_pool = items_df[
        items_df["category"].isin(user["preferred_categories"])
        & items_df["price"].fillna(500).between(price_lo, price_hi)
    ]

    n_biased = min(int(n * 0.4), len(matching_pool))
    n_random = n - n_biased

    parts = []
    if n_biased > 0:
        parts.append(matching_pool.sample(n=n_biased, random_state=rng.randint(0, 1_000_000)))
    if n_random > 0:
        parts.append(items_df.sample(n=min(n_random, len(items_df)), random_state=rng.randint(0, 1_000_000)))
    shown_items = pd.concat(parts).drop_duplicates(subset="candidate_id")

    events = []
    for _, item in shown_items.iterrows():
        is_match = matches_preference(item, user)

        if is_match:
            # Preferred items: longer dwell, more likely to like/tap
            dwell = rng.randint(1800, 6000)
            roll = rng.random()
            if roll < 0.35:
                event_type = "like"
            elif roll < 0.55:
                event_type = "tap"
            elif roll < 0.90:
                event_type = "view"
            else:
                event_type = "skip"
        else:
            # Non-preferred: short dwell, mostly skips
            dwell = rng.randint(200, 1500)
            roll = rng.random()
            if roll < 0.05:
                event_type = "like"
            elif roll < 0.10:
                event_type = "tap"
            elif roll < 0.35:
                event_type = "view"
            else:
                event_type = "skip"

        events.append({
            "user_id": user["user_id"],
            "candidate_id": item["candidate_id"],
            "event_type": event_type,
            "dwell_time_ms": dwell if event_type in ("view", "skip") else None,
            "session_id": session_id,
        })
    return events


def simulate_all(users: list[dict], items_df: pd.DataFrame, sessions_per_user: int, seed: int = 42) -> pd.DataFrame:
    rng = random.Random(seed)
    all_events = []
    for user in users:
        for _ in range(sessions_per_user):
            all_events.extend(simulate_session(user, items_df, rng))
    return pd.DataFrame(all_events)


def load_to_postgres(events_df: pd.DataFrame, database_url: str, batch_size: int = 500):
    import psycopg2
    from psycopg2.extras import execute_values

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            total = len(events_df)
            for start in range(0, total, batch_size):
                chunk = events_df.iloc[start:start + batch_size]
                rows = [
                    (
                        r["user_id"],
                        r["candidate_id"],
                        r["event_type"],
                        None if pd.isna(r["dwell_time_ms"]) else int(r["dwell_time_ms"]),
                        r["session_id"],
                    )
                    for _, r in chunk.iterrows()
                ]
                execute_values(
                    cur,
                    """
                    INSERT INTO interactions (user_id, candidate_id, event_type, dwell_time_ms, session_id)
                    VALUES %s
                    """,
                    rows,
                )
                print(f"  loaded {min(start + batch_size, total)}/{total}")
        conn.commit()
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-users", type=int, default=50)
    parser.add_argument("--sessions-per-user", type=int, default=3)
    parser.add_argument("--skip-db", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found in environment / .env")
        sys.exit(1)

    print("Loading items from Supabase...")
    items_df = load_items(database_url)
    print(f"  {len(items_df)} items loaded")

    print(f"\nGenerating {args.num_users} synthetic users...")
    users = generate_users(items_df, args.num_users, seed=args.seed)
    for u in users[:5]:
        print(f"  {u['user_id']}: prefers {u['preferred_categories']}, price={u['price_pref']}, session_len={u['session_length']}")

    print(f"\nSimulating {args.sessions_per_user} session(s) per user...")
    events_df = simulate_all(users, items_df, args.sessions_per_user, seed=args.seed)
    print(f"  generated {len(events_df)} interaction events")
    print("\nEvent type breakdown:")
    print(events_df["event_type"].value_counts())

    out_path = SCRIPT_DIR / "simulated_interactions.csv"
    events_df.to_csv(out_path, index=False)
    print(f"\n[write] {out_path}")

    if args.skip_db:
        print("\nSkipping DB load (--skip-db passed).")
        return

    print("\nLoading into Supabase...")
    load_to_postgres(events_df, database_url)
    print("Done.")


if __name__ == "__main__":
    main()
