"""
build_candidates.py

Builds a unified "feed candidates" table combining:
  - menu items (for restaurants with real menu data)
  - restaurant-level fallback rows (for restaurants without menu data yet)

This is the table item embeddings get computed on, and the table
candidate generation (pgvector) will search over.
"""

import pandas as pd

restaurants = pd.read_csv("restaurants_master.csv")
menu_items = pd.read_csv("menu_items_clean.csv")

candidates = []

# --- 1. Menu-item-level candidates (restaurants WITH real menu data) -------
for _, row in menu_items.iterrows():
    rest = restaurants[restaurants["restaurant_id"] == row["restaurant_id"]]
    if rest.empty:
        continue
    rest = rest.iloc[0]
    text_parts = [
        str(row["item_name"]),
        str(row["category"]),
        str(row["description"]) if pd.notna(row["description"]) else "",
        f"at {rest['name']}",
        f"in {rest['area']}",
    ]
    embed_text = " . ".join(p for p in text_parts if p and p != "nan")
    candidates.append({
        "candidate_id": f"item_{row['item_id']}",
        "restaurant_id": row["restaurant_id"],
        "restaurant_name": rest["name"],
        "candidate_type": "menu_item",
        "display_name": row["item_name"],
        "category": row["category"],
        "price": row["price"],
        "rating": rest["rating"],
        "area": rest["area"],
        "embed_text": embed_text,
    })

# --- 2. Restaurant-level fallback candidates (NO menu data) ----------------
no_menu = restaurants[restaurants["has_menu_data"] == False]
for _, rest in no_menu.iterrows():
    text_parts = [str(rest["name"]), str(rest["cuisine"]), f"in {rest['area']}"]
    embed_text = " . ".join(p for p in text_parts if p and p != "nan")
    candidates.append({
        "candidate_id": f"restaurant_{rest['restaurant_id']}",
        "restaurant_id": rest["restaurant_id"],
        "restaurant_name": rest["name"],
        "candidate_type": "restaurant",
        "display_name": rest["name"],
        "category": rest["cuisine"],
        "price": None,
        "rating": rest["rating"],
        "area": rest["area"],
        "embed_text": embed_text,
    })

candidates_df = pd.DataFrame(candidates)
candidates_df.to_csv("feed_candidates.csv", index=False)

print(f"Built {len(candidates_df)} feed candidates:")
print(f"  -> {(candidates_df['candidate_type'] == 'menu_item').sum()} real menu items")
print(f"  -> {(candidates_df['candidate_type'] == 'restaurant').sum()} restaurant-level fallbacks")
print()
print("Sample embed_text values:")
print(candidates_df[["candidate_type", "embed_text"]].sample(5, random_state=1).to_string())
