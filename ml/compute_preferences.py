"""
compute_preferences.py

Turns each user's raw interaction history into a single 384-dim preference
vector, stored in `user_preferences`. This vector lives in the same
embedding space as `items.embedding`, so ranking candidates for a user
becomes a plain cosine similarity query against pgvector -- no separate
ranking model needed yet.

Weighting scheme (implicit signal strength):
    like                        -> +1.0
    tap                         -> +0.7
    view, dwell > 3000ms        -> +0.3
    view, dwell <= 3000ms       -> -0.1
    skip                        -> -0.3

A user's preference vector = weighted average of the embeddings of items
they've interacted with. Negative weights pull the vector away from
disliked/skipped items, not just toward liked ones.

Usage:
  python compute_preferences.py --dry-run
  python compute_preferences.py
  python compute_preferences.py --sample-user sim_user_004   # sanity check one user
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd
from dotenv import load_dotenv

EVENT_WEIGHTS = {
    "like": 1.0,
    "tap": 0.7,
    "skip": -0.3,
}
VIEW_LONG_DWELL_WEIGHT = 0.3
VIEW_SHORT_DWELL_WEIGHT = -0.1
DWELL_THRESHOLD_MS = 3000
EMBEDDING_DIM = 384


def parse_vector(raw) -> np.ndarray:
    """pgvector returns embeddings as '[0.1,0.2,...]' strings via psycopg2."""
    if isinstance(raw, str):
        return np.array([float(x) for x in raw.strip("[]").split(",")], dtype=np.float32)
    return np.array(raw, dtype=np.float32)


def weight_for_event(event_type: str, dwell_time_ms) -> float:
    if event_type == "view":
        dwell = dwell_time_ms if pd.notna(dwell_time_ms) else 0
        return VIEW_LONG_DWELL_WEIGHT if dwell > DWELL_THRESHOLD_MS else VIEW_SHORT_DWELL_WEIGHT
    return EVENT_WEIGHTS.get(event_type, 0.0)


def fetch_interactions_with_embeddings(database_url: str) -> pd.DataFrame:
    import psycopg2
    conn = psycopg2.connect(database_url)
    try:
        df = pd.read_sql(
            """
            SELECT i.user_id, i.candidate_id, i.event_type, i.dwell_time_ms, it.embedding
            FROM interactions i
            JOIN items it ON it.candidate_id = i.candidate_id
            """,
            conn,
        )
    finally:
        conn.close()
    return df


def compute_user_vectors(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["embedding_arr"] = df["embedding"].apply(parse_vector)

    # Bucket each interaction into one of 5 signal groups, so that volume
    # within a group (e.g. having 2580 skips vs 216 likes) doesn't distort
    # the result -- we average WITHIN each group first, then combine
    # group averages using the coefficients below. This prevents whichever
    # event type happens to be most common from dominating the vector.
    def bucket(row):
        if row["event_type"] in ("like", "tap", "skip"):
            return row["event_type"]
        # view: split by dwell time
        dwell = row["dwell_time_ms"] if pd.notna(row["dwell_time_ms"]) else 0
        return "view_long" if dwell > DWELL_THRESHOLD_MS else "view_short"

    df["bucket"] = df.apply(bucket, axis=1)

    bucket_weights = {
        "like": 1.0,
        "tap": 0.7,
        "view_long": 0.3,
        "view_short": -0.1,
        "skip": -0.3,
    }

    user_vectors = {}
    for user_id, user_df in df.groupby("user_id"):
        combined = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        total_abs_weight = 0.0
        for bucket_name, weight in bucket_weights.items():
            bucket_df = user_df[user_df["bucket"] == bucket_name]
            if bucket_df.empty:
                continue
            bucket_mean = np.stack(bucket_df["embedding_arr"].to_numpy()).mean(axis=0)
            combined += weight * bucket_mean
            total_abs_weight += abs(weight)

        if total_abs_weight > 0:
            combined = combined / total_abs_weight

        norm = np.linalg.norm(combined)
        if norm > 0:
            combined = combined / norm

        user_vectors[user_id] = combined
    return user_vectors


def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            preference_vector vector(384),
            num_interactions INTEGER,
            updated_at TIMESTAMPTZ DEFAULT now()
        );
    """)


def load_to_postgres(user_vectors: dict, interaction_counts: dict, database_url: str):
    import psycopg2
    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            create_table(cur)
            for user_id, vec in user_vectors.items():
                vec_literal = "[" + ",".join(f"{x:.6f}" for x in vec) + "]"
                cur.execute(
                    """
                    INSERT INTO user_preferences (user_id, preference_vector, num_interactions, updated_at)
                    VALUES (%s, %s, %s, now())
                    ON CONFLICT (user_id) DO UPDATE SET
                        preference_vector = EXCLUDED.preference_vector,
                        num_interactions = EXCLUDED.num_interactions,
                        updated_at = now()
                    """,
                    (user_id, vec_literal, interaction_counts[user_id]),
                )
        conn.commit()
        print(f"[db] upserted {len(user_vectors)} user preference vectors")
    finally:
        conn.close()


def sanity_check(database_url: str, user_id: str, top_n: int = 8):
    import psycopg2
    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT it.display_name, it.category, it.restaurant_name,
                       1 - (it.embedding <=> up.preference_vector) AS similarity
                FROM items it, user_preferences up
                WHERE up.user_id = %s
                ORDER BY it.embedding <=> up.preference_vector
                LIMIT %s;
            """, (user_id, top_n))
            rows = cur.fetchall()
        print(f"\nTop {top_n} recommended candidates for {user_id}:")
        for display_name, category, restaurant_name, similarity in rows:
            print(f"  {similarity:.3f}  {display_name}  [{category}]  ({restaurant_name})")
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Compute vectors but don't write to DB")
    parser.add_argument("--sample-user", default=None, help="Run a nearest-candidates sanity check for this user_id after loading")
    args = parser.parse_args()

    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found in environment / .env")
        sys.exit(1)

    print("Fetching interactions joined with item embeddings...")
    df = fetch_interactions_with_embeddings(database_url)
    print(f"  {len(df)} interaction rows across {df['user_id'].nunique()} users")

    print("\nComputing weighted preference vectors...")
    user_vectors = compute_user_vectors(df)
    interaction_counts = df.groupby("user_id").size().to_dict()
    print(f"  computed {len(user_vectors)} user preference vectors")

    sample_id = next(iter(user_vectors))
    print(f"\nSample vector shape check ({sample_id}): {user_vectors[sample_id].shape}")

    if args.dry_run:
        print("\nDry run OK -- no DB writes made.")
        return

    load_to_postgres(user_vectors, interaction_counts, database_url)

    if args.sample_user:
        sanity_check(database_url, args.sample_user)


if __name__ == "__main__":
    main()
