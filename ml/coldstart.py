"""
coldstart.py

Builds a first feed for a brand-new user with zero interaction history.

There's no preference vector to rank against yet, so instead of random
sampling (chaotic, teaches the model nothing) or pure "most popular"
(same feed for everyone, generates no preference signal), this pulls a
spread of items across embedding-based clusters (see
precompute_clusters.py), weighted toward higher-rated items within each
cluster, with a cap on how many items can come from any one restaurant.

Requires precompute_clusters.py to have been run at least once (needs
items.cluster_id populated).

Usage:
    python coldstart.py
    python coldstart.py --feed-size 25 --per-restaurant-cap 3
    python coldstart.py --feed-size 20 --seed 7
"""

import argparse
import os
import random

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


def build_coldstart_feed(df: pd.DataFrame, feed_size: int, per_restaurant_cap: int, rng: random.Random):
    """
    df must have columns: candidate_id, restaurant_id, restaurant_name,
    display_name, category, rating, cluster_id.

    Strategy:
      1. Round-robin across clusters so early clusters don't dominate
         just because they're bigger.
      2. Within a cluster, sample weighted toward higher rating (items
         with no rating get a modest default weight so they can still
         surface -- otherwise unrated new-scrape items never appear).
      3. Skip any candidate that would push a restaurant over its cap.
    """
    clusters = {
        cid: group.reset_index(drop=True)
        for cid, group in df.groupby("cluster_id")
    }
    cluster_ids = list(clusters.keys())
    rng.shuffle(cluster_ids)

    # precompute sample weights per cluster (rating-weighted, default for NaN)
    weights = {}
    for cid, group in clusters.items():
        w = group["rating"].fillna(3.5).clip(lower=1.0).to_numpy()
        weights[cid] = w

    restaurant_counts = {}
    chosen_rows = []
    chosen_candidate_ids = set()

    exhausted = set()
    cluster_pointer = 0

    while len(chosen_rows) < feed_size and len(exhausted) < len(cluster_ids):
        cid = cluster_ids[cluster_pointer % len(cluster_ids)]
        cluster_pointer += 1

        if cid in exhausted:
            continue

        group = clusters[cid]
        w = weights[cid]

        # candidates in this cluster not yet chosen and not over restaurant cap
        available_mask = ~group["candidate_id"].isin(chosen_candidate_ids)
        if not available_mask.any():
            exhausted.add(cid)
            continue

        available_idx = group.index[available_mask].tolist()
        available_weights = w[available_mask.to_numpy()]

        # try a few draws to find one that doesn't blow the restaurant cap
        picked = None
        for _ in range(min(10, len(available_idx))):
            idx = rng.choices(available_idx, weights=available_weights.tolist(), k=1)[0]
            row = group.loc[idx]
            rest_id = row["restaurant_id"]
            if restaurant_counts.get(rest_id, 0) < per_restaurant_cap:
                picked = row
                break
            # remove this idx from consideration for this draw round
            pos = available_idx.index(idx)
            available_idx.pop(pos)
            available_weights = available_weights[[i for i in range(len(available_weights)) if i != pos]]
            if not available_idx:
                break

        if picked is None:
            # everything left in this cluster is capped out for now
            exhausted.add(cid)
            continue

        chosen_rows.append(picked)
        chosen_candidate_ids.add(picked["candidate_id"])
        restaurant_counts[picked["restaurant_id"]] = restaurant_counts.get(picked["restaurant_id"], 0) + 1

    return pd.DataFrame(chosen_rows).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--feed-size", type=int, default=20)
    parser.add_argument("--per-restaurant-cap", type=int, default=2)
    parser.add_argument("--seed", type=int, default=None, help="omit for a fresh random feed each run")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    engine = create_engine(DATABASE_URL)

    print("Loading items with cluster assignments from Supabase...")
    df = pd.read_sql(
        text(
            """
            SELECT candidate_id, restaurant_id, restaurant_name,
                   display_name, category, rating, cluster_id
            FROM items
            WHERE cluster_id IS NOT NULL
            """
        ),
        engine,
    )

    if df.empty:
        raise SystemExit(
            "No items have cluster_id set. Run precompute_clusters.py first."
        )

    print(f"  {len(df)} clustered items across {df['cluster_id'].nunique()} clusters")

    feed = build_coldstart_feed(df, args.feed_size, args.per_restaurant_cap, rng)

    print(f"\nCold-start feed ({len(feed)} items, cap={args.per_restaurant_cap}/restaurant):")
    for _, row in feed.iterrows():
        print(
            f"  cluster {row['cluster_id']:>2}  {row['display_name']:<35} "
            f"[{row['category']}]  ({row['restaurant_name']})"
        )

    restaurant_spread = feed["restaurant_id"].value_counts()
    print(f"\nRestaurant spread: {len(restaurant_spread)} unique restaurants, "
          f"max {restaurant_spread.max()} items from any one")
    print(f"Cluster spread: {feed['cluster_id'].nunique()} of {df['cluster_id'].nunique()} clusters represented")


if __name__ == "__main__":
    main()
