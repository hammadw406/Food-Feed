"""
load_items_to_pgvector.py

Creates (if missing) an `items` table with a pgvector `embedding vector(384)`
column in Supabase, and loads every row from feed_candidates_with_index.csv
paired with its corresponding vector from candidate_embeddings.npy (matched
via the `embedding_index` column).

Inputs (defaults assume running from ml/):
  --candidates   ml/feed_candidates_with_index.csv
  --embeddings   ml/candidate_embeddings.npy

Usage:
  python load_items_to_pgvector.py --dry-run     # sanity-check only, no DB writes
  python load_items_to_pgvector.py                # create table + load rows
"""

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv

EXPECTED_DIM = 384


def apply_id_map(df: pd.DataFrame, id_map_path: str) -> pd.DataFrame:
    """Remap restaurant_id using restaurant_id_map.csv from sync_restaurants_master.py,
    since local ids in feed_candidates were assigned locally and may not match
    the real ids Postgres assigned when restaurants were inserted."""
    id_map = pd.read_csv(id_map_path)
    mapping = dict(zip(id_map["local_restaurant_id"], id_map["real_restaurant_id"]))
    df = df.copy()
    unmapped = ~df["restaurant_id"].isin(mapping.keys())
    if unmapped.any():
        raise ValueError(
            f"{unmapped.sum()} rows have a restaurant_id not found in {id_map_path}. "
            "Run sync_restaurants_master.py first and make sure it covers all restaurants."
        )
    df["restaurant_id"] = df["restaurant_id"].map(mapping)
    return df


def load_inputs(candidates_path: str, embeddings_path: str, id_map_path: str = None):
    df = pd.read_csv(candidates_path)
    embeddings = np.load(embeddings_path)

    if id_map_path:
        df = apply_id_map(df, id_map_path)

    if len(df) != embeddings.shape[0]:
        raise ValueError(
            f"Row count mismatch: {len(df)} candidates vs {embeddings.shape[0]} embedding rows. "
            "These files must come from the same compute_embeddings.py run."
        )
    if embeddings.shape[1] != EXPECTED_DIM:
        raise ValueError(f"Expected {EXPECTED_DIM}-dim embeddings, got {embeddings.shape[1]}.")

    # embedding_index should be a clean 0..N-1 mapping into the .npy rows
    if not (df["embedding_index"].sort_values().reset_index(drop=True) == pd.RangeIndex(len(df))).all():
        raise ValueError("embedding_index column is not a clean 0..N-1 range — check the source files.")

    return df, embeddings


def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            candidate_id TEXT PRIMARY KEY,
            restaurant_id INTEGER REFERENCES restaurants(restaurant_id),
            restaurant_name TEXT,
            candidate_type TEXT,
            display_name TEXT,
            category TEXT,
            price NUMERIC(10,2),
            rating NUMERIC(3,2),
            area TEXT,
            embed_text TEXT,
            embedding vector(384),
            created_at TIMESTAMPTZ DEFAULT now()
        );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_items_restaurant ON items(restaurant_id);")
    # ivfflat index for fast approximate nearest-neighbor search.
    # Requires at least a handful of rows to build well; fine at 3k+ rows.
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_items_embedding
        ON items USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 50);
    """)


def load_rows(cur, df: pd.DataFrame, embeddings: np.ndarray, batch_size: int = 200):
    from psycopg2.extras import execute_values

    total = len(df)
    for start in range(0, total, batch_size):
        chunk = df.iloc[start:start + batch_size]
        rows = []
        for _, r in chunk.iterrows():
            vec = embeddings[int(r["embedding_index"])]
            vec_literal = "[" + ",".join(f"{x:.6f}" for x in vec) + "]"
            rows.append((
                r["candidate_id"],
                None if pd.isna(r["restaurant_id"]) else int(r["restaurant_id"]),
                r["restaurant_name"],
                r["candidate_type"],
                r["display_name"],
                None if pd.isna(r["category"]) else r["category"],
                None if pd.isna(r["price"]) else float(r["price"]),
                None if pd.isna(r["rating"]) else float(r["rating"]),
                None if pd.isna(r["area"]) else r["area"],
                r["embed_text"],
                vec_literal,
            ))
        execute_values(
            cur,
            """
            INSERT INTO items (candidate_id, restaurant_id, restaurant_name, candidate_type,
                                display_name, category, price, rating, area, embed_text, embedding)
            VALUES %s
            ON CONFLICT (candidate_id) DO UPDATE SET
                restaurant_id = EXCLUDED.restaurant_id,
                restaurant_name = EXCLUDED.restaurant_name,
                candidate_type = EXCLUDED.candidate_type,
                display_name = EXCLUDED.display_name,
                category = EXCLUDED.category,
                price = EXCLUDED.price,
                rating = EXCLUDED.rating,
                area = EXCLUDED.area,
                embed_text = EXCLUDED.embed_text,
                embedding = EXCLUDED.embedding
            """,
            rows,
        )
        print(f"  loaded {min(start + batch_size, total)}/{total}")


def sanity_check(cur, df: pd.DataFrame):
    sample_id = df.iloc[0]["candidate_id"]
    cur.execute("""
        SELECT display_name, restaurant_name,
               1 - (embedding <=> (SELECT embedding FROM items WHERE candidate_id = %s)) AS similarity
        FROM items
        WHERE candidate_id != %s
        ORDER BY embedding <=> (SELECT embedding FROM items WHERE candidate_id = %s)
        LIMIT 5;
    """, (sample_id, sample_id, sample_id))
    print(f"\nSanity check -- nearest neighbors of '{df.iloc[0]['display_name']}':")
    for display_name, restaurant_name, similarity in cur.fetchall():
        print(f"  {similarity:.3f}  {display_name}  ({restaurant_name})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default="feed_candidates_with_index.csv")
    parser.add_argument("--embeddings", default="candidate_embeddings.npy")
    parser.add_argument("--id-map", default="restaurant_id_map.csv",
                         help="Path to restaurant_id_map.csv from sync_restaurants_master.py")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs only, skip DB entirely")
    parser.add_argument("--batch-size", type=int, default=200)
    args = parser.parse_args()

    df, embeddings = load_inputs(args.candidates, args.embeddings, id_map_path=args.id_map)
    print(f"Loaded {len(df)} candidates, embeddings shape {embeddings.shape}")

    if args.dry_run:
        print("Dry run OK -- inputs are valid and aligned. No DB changes made.")
        return

    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found in environment / .env")
        sys.exit(1)

    import psycopg2
    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            print("Ensuring vector extension + items table exist...")
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            create_table(cur)
            conn.commit()

            print(f"Loading {len(df)} rows...")
            load_rows(cur, df, embeddings, batch_size=args.batch_size)
            conn.commit()

            sanity_check(cur, df)
    finally:
        conn.close()

    print("\nDone.")


if __name__ == "__main__":
    main()
