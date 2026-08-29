# ML — Embeddings, Candidate Generation & Ranking

**Owner:** Person 3 · **Stack:** sentence-transformers (all-MiniLM-L6-v2), pgvector, LightGBM, pandas, scikit-learn

## Responsibilities
- Compute item embeddings from restaurant/menu data
- pgvector nearest-neighbor candidate generation (~50 candidates per feed request)
- Real-time user embedding update logic (weighted average of positively-engaged items)
- Train and evaluate the LightGBM ranking model
- Synthetic interaction simulator (to test the loop before real users exist)
- Batch retraining script

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Two speeds of learning

| Speed | What updates | How |
|---|---|---|
| Real-time | User's embedding vector | Weighted average, recomputed on every interaction |
| Batch (daily/weekly) | LightGBM ranking model | Retrained offline on accumulated logs, then swapped in |

## Cold start

Before any ranking model exists, rely on candidate generation + diverse sampling alone (or a rule-based fallback) until enough interaction data accumulates to train the first model version.
