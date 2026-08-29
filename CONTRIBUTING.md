# Contributing

## Branching Model

```
main        ← stable, always deployable
  └── dev   ← integration branch, merge finished features here first
        ├── feature/frontend-feed-ui     (Person 1)
        ├── feature/backend-api          (Person 2)
        ├── feature/ml-embeddings        (Person 3)
        └── feature/infra-etl            (Person 4)
```

## One-time setup

1. Clone the repo:
   ```bash
   git clone https://github.com/<org>/<repo>.git
   cd <repo>
   ```
2. Create the shared `dev` branch (only needs to be done once, by whoever sets up the repo):
   ```bash
   git checkout -b dev
   git push -u origin dev
   ```
3. Each person creates their own feature branch off `dev`:
   ```bash
   git checkout dev
   git pull
   git checkout -b feature/<your-area>
   git push -u origin feature/<your-area>
   ```

## Day-to-day workflow

1. Make sure you're on your branch and up to date:
   ```bash
   git checkout feature/<your-area>
   git pull origin dev --rebase
   ```
2. Commit as you go:
   ```bash
   git add .
   git commit -m "feat: short description of the change"
   ```
3. Push:
   ```bash
   git push
   ```
4. When a chunk of work is ready, open a **Pull Request into `dev`** (not `main`) and tag whoever owns the adjacent layer as reviewer (e.g. Person 1 tags Person 2 on anything touching the API contract).
5. Once `dev` is stable and a phase milestone is hit, open a PR from **`dev` → `main`**.

## Commit message convention

Use a short prefix so history stays scannable:

- `feat:` new functionality
- `fix:` bug fix
- `refactor:` code change with no behavior change
- `docs:` documentation only
- `ci:` build/pipeline changes
- `test:` adding or updating tests

## Branch protection (set once, by repo admin)

In **Settings → Branches**, add a rule for `main`:
- Require a pull request before merging
- Require at least 1 approval
- Require status checks to pass (once CI is set up) before merging

## Code review expectations

- Keep PRs scoped to one feature or fix — small PRs get reviewed faster.
- Cross-cutting changes (event schema, API contract, DB schema) need a review from the adjacent owner, not just anyone.
- Don't merge your own PR without at least one approval, even if CI passes.
