"""
compute_embeddings.py

Computes sentence-transformer embeddings for every feed candidate
(menu items + restaurant-level fallbacks) and saves them as a .npy array
alongside the candidate table, ready to load into pgvector.
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    candidates = pd.read_csv("feed_candidates.csv")
    print(f"Loading model: {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME)

    texts = candidates["embed_text"].fillna("").tolist()
    print(f"Computing embeddings for {len(texts)} candidates ...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)

    print(f"Embedding shape: {embeddings.shape}")  # (n_candidates, 384)

    np.save("candidate_embeddings.npy", embeddings)
    candidates["embedding_index"] = range(len(candidates))
    candidates.to_csv("feed_candidates_with_index.csv", index=False)

    print()
    print("Saved candidate_embeddings.npy and feed_candidates_with_index.csv")
    print("embedding_index in the CSV maps each row to its vector's row in the .npy file")

    # quick sanity check: find nearest neighbors for one item using cosine similarity
    from numpy.linalg import norm
    sample_idx = 0
    query = embeddings[sample_idx]
    sims = embeddings @ query / (norm(embeddings, axis=1) * norm(query) + 1e-8)
    top5 = np.argsort(-sims)[:5]
    print()
    print(f"Sanity check -- items most similar to: '{candidates.iloc[sample_idx]['display_name']}'")
    for i in top5:
        print(f"  {sims[i]:.3f}  {candidates.iloc[i]['display_name']} ({candidates.iloc[i]['restaurant_name']})")

if __name__ == "__main__":
    main()
