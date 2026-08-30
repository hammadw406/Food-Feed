"""
build_training_features.py

Joins interactions -> items -> user_preferences into a single training
table for the LightGBM ranking model (Phase 5).

Label (graded relevance, used by LambdaRank):
    like / tap -> 2
    view       -> 1
    skip       -> 0

Deliberately excludes dwell_time_ms as a *feature* -- it's only known
after the user has already reacted to the item, so using it as an
input would leak the outcome into the prediction. It's a fine label
signal (already used in compute_preferences.py), but not a safe feature.

Features:
    - pref_similarity: cosine similarity between the user's preference
      vector (at time of scoring, i.e. their current stored vector) and
      the item's embedding
    - rating: item rating
    - price: item price
    - cluster_id: from precompute_clusters.py (categorical)
    - review_count: restaurant-level review count, if available

Grouping:
    - session_id, required by LightGBM's LambdaRank objective, which
      ranks items *within* a group against each other rather than
      globally.

Usage:
    python build_training_features.py
    python build_training_features.py --output training_data.csv
"""

import argparse
import ast
import os

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

LABEL_MAP = {"like": 2, "tap": 2, "view": 1, "skip": 0}


def parse_vector(raw):
    if raw is None:
        return None
    if isinstance(raw, str):
        return np.array(ast.literal_eval(raw), dtype=np.float32)
    return np.array(raw, dtype=np.float32)


def cosine_sim(a, b):
    if a is None or b is None:
        return 0.0
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="training_data.csv")
    args = parser.parse_args()

    engine = create_engine(DATABASE_URL)

    print("Loading interactions...")
    interactions = pd.read_sql(
        text(
            """
            SELECT interaction_id, user_id, candidate_id, event_type,
                   session_id
            FROM interactions
            """
        ),
        engine,
    )
    print(f"  {len(interactions)} interaction rows")

    print("Loading items...")
    items = pd.read_sql(
        text(
            """
            SELECT candidate_id, restaurant_id, rating, price,
                   cluster_id, embedding
            FROM items
            """
        ),
        engine,
    )
    print(f"  {len(items)} item rows")

    print("Loading restaurants (for review_count)...")
    restaurants = pd.read_sql(
        text("SELECT restaurant_id, review_count FROM restaurants"),
        engine,
    )
    print(f"  {len(restaurants)} restaurant rows")

    print("Loading user preference vectors...")
    prefs = pd.read_sql(
        text("SELECT user_id, preference_vector FROM user_preferences"),
        engine,
    )
    print(f"  {len(prefs)} user preference rows")

    print("Parsing embeddings and preference vectors...")
    items["embedding_parsed"] = items["embedding"].apply(parse_vector)
    prefs["pref_parsed"] = prefs["preference_vector"].apply(parse_vector)

    print("Joining...")
    df = interactions.merge(items, on="candidate_id", how="left")
    df = df.merge(restaurants, on="restaurant_id", how="left")
    df = df.merge(prefs[["user_id", "pref_parsed"]], on="user_id", how="left")

    before = len(df)
    df = df.dropna(subset=["embedding_parsed", "pref_parsed"])
    dropped = before - len(df)
    if dropped:
        print(f"  dropped {dropped} rows with missing embedding or preference vector "
              f"(e.g. users below the interaction threshold for a preference vector)")

    print("Computing user-item cosine similarity...")
    df["pref_similarity"] = df.apply(
        lambda r: cosine_sim(r["pref_parsed"], r["embedding_parsed"]), axis=1
    )

    print("Assigning graded relevance labels...")
    df["label"] = df["event_type"].map(LABEL_MAP)
    unmapped = df["label"].isna().sum()
    if unmapped:
        print(f"  WARNING: {unmapped} rows had an unrecognized event_type, dropping them")
        df = df.dropna(subset=["label"])
    df["label"] = df["label"].astype(int)

    print("Label distribution:")
    print(df["label"].value_counts().sort_index())

    output_cols = [
        "session_id", "user_id", "candidate_id", "label",
        "pref_similarity", "rating", "price", "cluster_id", "review_count",
    ]
    final = df[output_cols].copy()

    # LightGBM's group format needs rows sorted/contiguous by session_id
    final = final.sort_values("session_id").reset_index(drop=True)

    final.to_csv(args.output, index=False)
    print(f"\nWrote {len(final)} training rows to {args.output}")
    print(f"  sessions: {final['session_id'].nunique()}")
    print(f"  users: {final['user_id'].nunique()}")


if __name__ == "__main__":
    main()
