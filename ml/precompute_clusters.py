"""
precompute_clusters.py

Clusters all item embeddings into K groups using KMeans, so cold-start
sampling can pull a diverse spread of items without relying on the
(known unreliable) `category` column.

Run this whenever items materially change (new scrape, new candidates
loaded). It's cheap — a few seconds for ~3k items — so there's no harm
re-running it after every load_items_to_pgvector.py run.

Usage:
    python precompute_clusters.py
    python precompute_clusters.py --k 20
    python precompute_clusters.py --k 18 --random-state 42

Requires: DATABASE_URL in ml/.env (session pooler connection string,
same as the rest of the pipeline).
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


def parse_embedding(raw):
    """pgvector comes back over the wire as a string like '[0.1,0.2,...]'."""
    if isinstance(raw, str):
        return np.array(ast.literal_eval(raw), dtype=np.float32)
    return np.array(raw, dtype=np.float32)


def ensure_cluster_column(engine):
    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE items ADD COLUMN IF NOT EXISTS cluster_id INTEGER"
            )
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--k", type=int, default=18, help="number of clusters (default: 18)"
    )
    parser.add_argument(
        "--random-state", type=int, default=42, help="KMeans random seed"
    )
    args = parser.parse_args()

    engine = create_engine(DATABASE_URL)

    print("Loading item embeddings from Supabase...")
    df = pd.read_sql(
        text("SELECT candidate_id, embedding FROM items"),
        engine,
    )
    print(f"  {len(df)} items loaded")

    print("Parsing embeddings...")
    embeddings = np.vstack(df["embedding"].apply(parse_embedding).values)
    print(f"  embedding matrix shape: {embeddings.shape}")

    # Import here so the script fails fast above (with a clear DB error)
    # rather than a slow scikit-learn import first if the DB is unreachable.
    from sklearn.cluster import KMeans

    print(f"Running KMeans with k={args.k}...")
    kmeans = KMeans(n_clusters=args.k, random_state=args.random_state, n_init=10)
    labels = kmeans.fit_predict(embeddings)
    df["cluster_id"] = labels

    print("Cluster size distribution:")
    counts = df["cluster_id"].value_counts().sort_index()
    for cluster_id, count in counts.items():
        print(f"  cluster {cluster_id:>2}: {count} items")

    print("Ensuring cluster_id column exists on items table...")
    ensure_cluster_column(engine)

    print("Writing cluster assignments back to Supabase...")
    with engine.begin() as conn:
        rows = list(zip(df["cluster_id"].tolist(), df["candidate_id"].tolist()))
        for i in range(0, len(rows), 500):
            batch = rows[i : i + 500]
            conn.execute(
                text("UPDATE items SET cluster_id = :cluster_id WHERE candidate_id = :candidate_id"),
                [{"cluster_id": int(c), "candidate_id": cid} for c, cid in batch],
            )
            print(f"  updated {min(i + 500, len(rows))}/{len(rows)}")

    print("Done.")


if __name__ == "__main__":
    main()
