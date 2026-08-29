# Infra — Data, Deployment & CI/CD

**Owner:** Person 4 · **Stack:** GitHub Actions, Railway/Render, Sentry

## Responsibilities
- Clean and unify the DHA fast-food + Foodpanda Lahore datasets into the shared schema
- Own the ETL pipeline (raw CSVs → Postgres)
- Backend hosting setup (Railway or Render)
- CI/CD via GitHub Actions
- Error monitoring (Sentry)
- Coordinate the internal test loop with real DHA users, collect feedback, track the success metric

## Data sources

| Source | Rows / scope | Use |
|---|---|---|
| Lahore Fast Food Restaurants (DHA-tagged) | ~247 rows | Primary MVP dataset |
| Pakistan Cities Foodpanda Reviews | ~3,000 Lahore rows | Scale-up dataset |
| Pakistan Restaurants Data (broad) | Nationwide, 9 columns | Coverage benchmark |
| Sentiment Analysis Model | Pretrained model | Review sentiment signal |

## ETL target schema

`restaurant_id, name, area, cuisine, price_band, rating, review_count`

## Folders
```
infra/
├── etl/           # cleaning + ingestion scripts
├── data/samples/  # small sample CSVs safe to commit
└── ci/            # shared CI config helpers, if any
```

Raw and processed data files are gitignored — only small samples belong in version control.
