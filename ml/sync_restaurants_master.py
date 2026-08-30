"""
sync_restaurants_master.py

restaurants_master.csv (built locally, e.g. 164 rows including 38 new
restaurants discovered via menu scraping) may NOT match the live
`restaurants` table in Supabase, which only has the original rows loaded
by clean_restaurants.py (e.g. 126).

This script:
  1. Reads restaurants_master.csv and the CURRENT live `restaurants` table.
  2. Fuzzy-matches each master row against live rows by name.
  3. For matches: records the real (live) restaurant_id.
  4. For non-matches (new restaurants): INSERTs them into `restaurants`,
     letting Postgres assign the real SERIAL id.
  5. Writes restaurant_id_map.csv: local_restaurant_id -> real_restaurant_id
     This map MUST be applied to feed_candidates_with_index.csv's
     restaurant_id column before loading into the items/pgvector table,
     since local ids in restaurants_master.csv are not guaranteed to
     match what Postgres actually assigned.

Usage:
  python sync_restaurants_master.py --dry-run
  python sync_restaurants_master.py
"""

import argparse
import difflib
import os
import re
import sys

import pandas as pd
from dotenv import load_dotenv

MATCH_THRESHOLD = 0.90


def norm(s: str) -> str:
    s = str(s).lower()
    s = re.sub(r"\bdha\b|phase\s*\d+|-|\(|\)", " ", s)
    s = re.sub(r"[^a-z0-9 ]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def fetch_live_restaurants(cur) -> pd.DataFrame:
    cur.execute("SELECT restaurant_id, name FROM restaurants;")
    rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["restaurant_id", "name"])


def match_master_to_live(master_df: pd.DataFrame, live_df: pd.DataFrame) -> dict:
    live_df = live_df.copy()
    live_df["norm_name"] = live_df["name"].apply(norm)
    target_list = live_df["norm_name"].tolist()

    local_to_real = {}
    for _, row in master_df.iterrows():
        local_id = row["restaurant_id"]
        normed = norm(row["name"])
        close = difflib.get_close_matches(normed, target_list, n=1, cutoff=0.0)
        if close:
            score = difflib.SequenceMatcher(None, normed, close[0]).ratio()
            if score >= MATCH_THRESHOLD:
                real_id = live_df.loc[live_df["norm_name"] == close[0], "restaurant_id"].iloc[0]
                local_to_real[local_id] = ("existing", int(real_id))
                continue
        local_to_real[local_id] = ("new", None)
    return local_to_real


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", default="restaurants_master.csv")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    master_df = pd.read_csv(args.master)
    print(f"Loaded {len(master_df)} rows from {args.master}")

    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found")
        sys.exit(1)

    import psycopg2

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            live_df = fetch_live_restaurants(cur)
            print(f"Found {len(live_df)} restaurants currently live in Supabase")

            match_result = match_master_to_live(master_df, live_df)
            existing_count = sum(1 for v in match_result.values() if v[0] == "existing")
            new_count = sum(1 for v in match_result.values() if v[0] == "new")
            print(f"\nMatched to existing: {existing_count}")
            print(f"New (not yet in DB): {new_count}")

            if args.dry_run:
                print("\nDry run -- no DB writes. Sample of new restaurants that WOULD be inserted:")
                new_ids = [k for k, v in match_result.items() if v[0] == "new"]
                sample = master_df[master_df["restaurant_id"].isin(new_ids)].head(10)
                print(sample[["restaurant_id", "name", "area"]].to_string())
                return

            # Insert new restaurants, capture real ids
            final_map = {}
            for local_id, (status, real_id) in match_result.items():
                if status == "existing":
                    final_map[local_id] = real_id
                    continue
                row = master_df[master_df["restaurant_id"] == local_id].iloc[0]
                cur.execute(
                    """
                    INSERT INTO restaurants (name, area, cuisine, price_band, rating, review_count, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING restaurant_id
                    """,
                    (
                        row["name"],
                        None if pd.isna(row.get("area")) else row.get("area"),
                        None if pd.isna(row.get("cuisine")) else row.get("cuisine"),
                        None if pd.isna(row.get("price_band")) else row.get("price_band"),
                        None if pd.isna(row.get("rating")) else float(row.get("rating")),
                        None if pd.isna(row.get("review_count")) else int(row.get("review_count")),
                        row.get("source", "restaurants_master_sync"),
                    ),
                )
                new_real_id = cur.fetchone()[0]
                final_map[local_id] = new_real_id
            conn.commit()

            map_df = pd.DataFrame(
                [(k, v) for k, v in final_map.items()],
                columns=["local_restaurant_id", "real_restaurant_id"],
            )
            map_df.to_csv("restaurant_id_map.csv", index=False)
            print(f"\n[write] restaurant_id_map.csv ({len(map_df)} rows)")
            print("Apply this mapping to feed_candidates_with_index.csv's restaurant_id "
                  "column before loading items.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
