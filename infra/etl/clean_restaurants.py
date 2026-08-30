"""
clean_restaurants.py

Cleans and unifies two raw restaurant datasets into the Food Feed project's
target schema, then loads the result into the `restaurants` table in
Postgres (Supabase).

Inputs (place these in infra/data/raw/ before running):
  1. lahore_fast_food_dha.csv
     Source: https://www.kaggle.com/datasets/qa33ar/lahore-fast-food-restaurants-raw
     Columns: name, area, address, cuisine_type, rating, total_reviews,
              chain_or_independent, chain_or_independent, phone, dine_in,
              takeout, delivery

  2. pk_lahore_restos.csv
     Source: https://www.kaggle.com/datasets/bwandowando/pakistan-cities-food-panda-resto-reviews
     Columns: StoreId, CompleteStoreName, FoodType, AverageRating,
              Reviewers, City

Output:
  - infra/data/clean/restaurants_clean.csv  (local copy for inspection)
  - rows inserted/upserted into the `restaurants` table in Postgres

Usage:
  python clean_restaurants.py
  python clean_restaurants.py --skip-db      # only produce the clean CSV, don't touch Postgres
  python clean_restaurants.py --dha-only     # keep only DHA-tagged rows from dataset 1,
                                              # and only name-matched DHA rows from dataset 2
"""

import argparse
import os
import re
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
RAW_DIR = SCRIPT_DIR / "data" / "raw"
CLEAN_DIR = SCRIPT_DIR / "data" / "clean"

DHA_FASTFOOD_FILE = RAW_DIR / "lahore_fast_food_dha.csv"
FOODPANDA_FILE = RAW_DIR / "pk_lahore_restos.csv"

TARGET_COLUMNS = [
    "name", "area", "cuisine", "price_band",
    "rating", "review_count", "source",
]

# Rough keyword match for isolating DHA-area rows out of the Foodpanda
# dataset, which has no dedicated area column (only restaurant name/city).
DHA_NAME_PATTERN = re.compile(r"\bDHA\b|Defence", re.IGNORECASE)

# Foodpanda's Reviewers column looks like "(100+)", "(1000+)", "(85)" —
# parentheses wrap the count, with a trailing "+" for rounded/bucketed
# values at scale. This extracts the integer inside.
REVIEWERS_PATTERN = re.compile(r"\((\d+)\+?\)")


def parse_reviewers(value) -> "pd.Int64Dtype":
    if pd.isna(value):
        return pd.NA
    match = REVIEWERS_PATTERN.search(str(value))
    return int(match.group(1)) if match else pd.NA


# ---------------------------------------------------------------------------
# Cleaning: Dataset 1 — Lahore Fast Food Restaurants (DHA-tagged)
# ---------------------------------------------------------------------------

def clean_dha_fastfood(path: Path, dha_only: bool) -> pd.DataFrame:
    df = pd.read_csv(path)

    # The raw file reportedly has a duplicated `chain_or_independent` column.
    # Drop exact duplicate columns (keep first occurrence) defensively.
    df = df.loc[:, ~df.columns.duplicated()]

    df = df.rename(columns={
        "name": "name",
        "area": "area",
        "cuisine_type": "cuisine",
        "rating": "rating",
        "total_reviews": "review_count",
    })

    if dha_only and "area" in df.columns:
        before = len(df)
        df = df[df["area"].astype(str).str.contains("DHA", case=False, na=False)]
        print(f"  [dha_fastfood] filtered to DHA area: {before} -> {len(df)} rows")

    # No explicit price_band in this dataset — leave null for now.
    df["price_band"] = pd.NA
    df["source"] = "lahore_fast_food_dha"

    # Coerce types
    df["rating"] = pd.to_numeric(df.get("rating"), errors="coerce")
    df["review_count"] = pd.to_numeric(df.get("review_count"), errors="coerce").astype("Int64")

    return df[TARGET_COLUMNS].drop_duplicates()


# ---------------------------------------------------------------------------
# Cleaning: Dataset 2 — Foodpanda Lahore Reviews
# NOTE: "Reviewers" arrives as "(100+)", "(1000+)", "(85)" — parsed via
# parse_reviewers() above, not plain numeric coercion.
# ---------------------------------------------------------------------------

def clean_foodpanda_lahore(path: Path, dha_only: bool) -> pd.DataFrame:
    df = pd.read_csv(path)

    df = df.rename(columns={
        "CompleteStoreName": "name",
        "FoodType": "cuisine",
        "AverageRating": "rating",
        "Reviewers": "review_count",
    })

    # No dedicated area column in this dataset — best-effort DHA filter
    # by matching "DHA" / "Defence" inside the restaurant name string.
    # NOTE: this will under-count real DHA branches that don't mention DHA
    # in their listed name. Treat as a rough filter, not ground truth.
    if dha_only:
        before = len(df)
        df = df[df["name"].astype(str).str.contains(DHA_NAME_PATTERN, na=False)]
        print(f"  [foodpanda] filtered to name-matched DHA rows: {before} -> {len(df)} rows")

    df["area"] = "DHA" if dha_only else pd.NA
    df["price_band"] = pd.NA
    df["source"] = "foodpanda_lahore"

    df["rating"] = pd.to_numeric(df.get("rating"), errors="coerce")
    df["review_count"] = df["review_count"].apply(parse_reviewers).astype("Int64")

    return df[TARGET_COLUMNS].drop_duplicates()


# ---------------------------------------------------------------------------
# Merge + dedupe
# ---------------------------------------------------------------------------

def merge_and_dedupe(frames: list[pd.DataFrame]) -> pd.DataFrame:
    combined = pd.concat(frames, ignore_index=True)

    for col in TARGET_COLUMNS:
        if col not in combined.columns:
            combined[col] = pd.NA

    combined = combined[TARGET_COLUMNS]

    combined["name"] = combined["name"].astype(str).str.strip()
    combined = combined[combined["name"].str.len() > 0]

    # Dedupe on normalized name + area — same restaurant appearing in both
    # source datasets (e.g. listed on both Foodpanda and the DHA-scraped
    # dataset) collapses to a single row, keeping the first (DHA dataset
    # rows are concatenated first, so they win — richer area/cuisine data).
    combined["_dedupe_key"] = (
        combined["name"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
        + "|"
        + combined["area"].astype(str).str.lower()
    )
    before = len(combined)
    combined = combined.drop_duplicates(subset="_dedupe_key", keep="first")
    combined = combined.drop(columns="_dedupe_key")
    print(f"[merge] deduped: {before} -> {len(combined)} rows")

    return combined.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Load into Postgres
# ---------------------------------------------------------------------------

def load_to_postgres(df: pd.DataFrame, database_url: str) -> None:
    import psycopg2
    from psycopg2.extras import execute_values

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            rows = [
                (
                    r["name"],
                    None if pd.isna(r["area"]) else r["area"],
                    None if pd.isna(r["cuisine"]) else r["cuisine"],
                    None if pd.isna(r["price_band"]) else r["price_band"],
                    None if pd.isna(r["rating"]) else float(r["rating"]),
                    None if pd.isna(r["review_count"]) else int(r["review_count"]),
                    r["source"],
                )
                for _, r in df.iterrows()
            ]

            execute_values(
                cur,
                """
                INSERT INTO restaurants (name, area, cuisine, price_band, rating, review_count, source)
                VALUES %s
                """,
                rows,
            )
        conn.commit()
        print(f"[db] inserted {len(rows)} rows into restaurants")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-db", action="store_true", help="Only write the clean CSV, skip loading into Postgres")
    parser.add_argument("--dha-only", action="store_true", default=True, help="Restrict to DHA-area rows (default: on, matches MVP scope)")
    args = parser.parse_args()

    missing = [p for p in (DHA_FASTFOOD_FILE, FOODPANDA_FILE) if not p.exists()]
    if missing:
        print("Missing raw file(s):")
        for p in missing:
            print(f"  - {p}")
        print(f"\nPlace the raw CSVs in {RAW_DIR} and re-run.")
        sys.exit(1)

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    print("Cleaning lahore_fast_food_dha.csv ...")
    df1 = clean_dha_fastfood(DHA_FASTFOOD_FILE, args.dha_only)
    print(f"  -> {len(df1)} rows")

    print("Cleaning pk_lahore_restos.csv ...")
    df2 = clean_foodpanda_lahore(FOODPANDA_FILE, args.dha_only)
    print(f"  -> {len(df2)} rows")

    merged = merge_and_dedupe([df1, df2])

    out_path = CLEAN_DIR / "restaurants_clean.csv"
    merged.to_csv(out_path, index=False)
    print(f"[write] saved clean dataset -> {out_path} ({len(merged)} rows)")

    if args.skip_db:
        print("Skipping DB load (--skip-db passed).")
        return

    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found in environment / .env — skipping DB load.")
        print("Set DATABASE_URL in infra/.env, or re-run with --skip-db to suppress this message.")
        sys.exit(1)

    load_to_postgres(merged, database_url)


if __name__ == "__main__":
    main()
