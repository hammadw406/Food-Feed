"""
train_ranking_model.py

Trains a LightGBM LambdaRank model on the features produced by
build_training_features.py.

LambdaRank (not plain classification/regression) because the goal is
relative ordering *within a session* -- given ~50 pgvector candidates
for a feed refresh, which order should they appear in -- not an
absolute probability per item.

Usage:
    python train_ranking_model.py
    python train_ranking_model.py --input training_data.csv --test-size 0.2
"""

import argparse
import os

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

FEATURE_COLS = ["pref_similarity", "rating", "price", "cluster_id", "review_count"]
CATEGORICAL_COLS = ["cluster_id"]


def make_dataset(df: pd.DataFrame):
    """
    LightGBM's ranking API needs data sorted by group (session_id) with
    a parallel 'group' array giving the size of each contiguous group.
    """
    df = df.sort_values("session_id").reset_index(drop=True)
    group_sizes = df.groupby("session_id", sort=False).size().values
    X = df[FEATURE_COLS].copy()
    y = df["label"].values
    return X, y, group_sizes, df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="training_data.csv")
    parser.add_argument("--output", default="models/ranking_model.txt")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    print(f"Loading {args.input}...")
    df = pd.read_csv(args.input)
    print(f"  {len(df)} rows, {df['session_id'].nunique()} sessions")

    # fill remaining gaps (e.g. missing review_count / price for some items)
    for col in ["rating", "price", "review_count"]:
        if df[col].isna().any():
            fill_val = df[col].median()
            n_missing = df[col].isna().sum()
            df[col] = df[col].fillna(fill_val)
            print(f"  filled {n_missing} missing '{col}' values with median ({fill_val:.2f})")

    df["cluster_id"] = df["cluster_id"].fillna(-1).astype(int)

    # split by session_id, not by row, so no session is split across train/test
    print(f"Splitting train/test by session (test_size={args.test_size})...")
    splitter = GroupShuffleSplit(n_splits=1, test_size=args.test_size, random_state=args.random_state)
    train_idx, test_idx = next(splitter.split(df, groups=df["session_id"]))
    train_df = df.iloc[train_idx].reset_index(drop=True)
    test_df = df.iloc[test_idx].reset_index(drop=True)
    print(f"  train: {len(train_df)} rows / {train_df['session_id'].nunique()} sessions")
    print(f"  test:  {len(test_df)} rows / {test_df['session_id'].nunique()} sessions")

    X_train, y_train, group_train, train_df = make_dataset(train_df)
    X_test, y_test, group_test, test_df = make_dataset(test_df)

    train_set = lgb.Dataset(
        X_train, label=y_train, group=group_train,
        categorical_feature=CATEGORICAL_COLS, free_raw_data=False,
    )
    test_set = lgb.Dataset(
        X_test, label=y_test, group=group_test,
        categorical_feature=CATEGORICAL_COLS, reference=train_set, free_raw_data=False,
    )

    params = {
        "objective": "lambdarank",
        "metric": "ndcg",
        "ndcg_eval_at": [5, 10],
        "learning_rate": 0.05,
        "num_leaves": 31,
        "min_data_in_leaf": 20,
        "verbose": -1,
    }

    print("\nTraining LightGBM LambdaRank model...")
    model = lgb.train(
        params,
        train_set,
        num_boost_round=200,
        valid_sets=[train_set, test_set],
        valid_names=["train", "test"],
        callbacks=[lgb.log_evaluation(period=20), lgb.early_stopping(stopping_rounds=20)],
    )

    print("\nFeature importance (gain):")
    importances = model.feature_importance(importance_type="gain")
    for feat, imp in sorted(zip(FEATURE_COLS, importances), key=lambda x: -x[1]):
        print(f"  {feat:<20} {imp:.1f}")

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    model.save_model(args.output)
    print(f"\nModel saved to {args.output}")
    print("(models/ is already gitignored -- do not commit this file)")


if __name__ == "__main__":
    main()
