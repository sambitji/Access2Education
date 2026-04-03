import pandas as pd


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return the subset of columns used for clustering.

    This is a simple placeholder implementation; adapt as needed.
    """
    # make sure required columns exist
    required = ["logical", "verbal", "numerical", "memory", "attention"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Input dataframe is missing columns: {missing}")
    return df[required]
