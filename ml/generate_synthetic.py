"""
Generate synthetic alternative data for financial inclusion risk assessment.

Creates data/raw/synthetic_alt_data.csv with:
- SK_ID_CURR: copied from application_train.csv (same rows, same order)
- mobile_bill_consistency: float between 0 and 1 from numpy Beta(a=5, b=2, seed=42)
  with approximately 2% values set to NaN randomly.
Independent of the TARGET column.
"""

from pathlib import Path
import numpy as np
import pandas as pd


def resolve_paths():
    """Locate input application_train.csv and output synthetic_alt_data.csv."""
    base_dir = Path(__file__).resolve().parent.parent

    # Candidate paths for application_train.csv
    candidates = [
        base_dir / "data" / "raw" / "application_train.csv",
        base_dir / "Data" / "raw" / "application_train.csv",
        Path("data/raw/application_train.csv"),
        Path("Data/raw/application_train.csv"),
    ]

    input_path = None
    for p in candidates:
        if p.exists():
            input_path = p.resolve()
            break

    if input_path is None:
        raise FileNotFoundError(
            "Could not find application_train.csv in data/raw or Data/raw. "
            "Please ensure the file exists."
        )

    # Output directory alongside raw data
    output_dir = input_path.parent
    output_path = output_dir / "synthetic_alt_data.csv"

    return input_path, output_path


def generate_synthetic_alt_data(
    input_path: Path | str | None = None,
    output_path: Path | str | None = None,
    a: float = 5.0,
    b: float = 2.0,
    nan_prob: float = 0.02,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate synthetic alternative data CSV with SK_ID_CURR and mobile_bill_consistency.

    Parameters
    ----------
    input_path : Path | str | None
        Path to application_train.csv. If None, auto-resolved.
    output_path : Path | str | None
        Path to write synthetic_alt_data.csv. If None, auto-resolved.
    a : float
        Alpha parameter for Beta distribution (default 5.0).
    b : float
        Beta parameter for Beta distribution (default 2.0).
    nan_prob : float
        Approximate proportion of values to set to NaN (default 0.02).
    seed : int
        Random seed for reproducibility (default 42).

    Returns
    -------
    pd.DataFrame
        DataFrame containing SK_ID_CURR and mobile_bill_consistency.
    """
    if input_path is None or output_path is None:
        default_in, default_out = resolve_paths()
        input_path = Path(input_path) if input_path else default_in
        output_path = Path(output_path) if output_path else default_out
    else:
        input_path = Path(input_path)
        output_path = Path(output_path)

    print(f"Reading SK_ID_CURR from: {input_path}")
    # Load only SK_ID_CURR, completely independent of TARGET
    df_app = pd.read_csv(input_path, usecols=["SK_ID_CURR"])
    n_samples = len(df_app)
    print(f"Loaded {n_samples:,} rows of SK_ID_CURR.")

    # Set random seed
    np.random.seed(seed)

    # Generate values using numpy Beta distribution
    print(f"Generating Beta(a={a}, b={b}) distribution (seed={seed})...")
    mobile_bill_consistency = np.random.beta(a=a, b=b, size=n_samples)

    # Set approximately 2% of values to NaN randomly
    nan_mask = np.random.random(size=n_samples) < nan_prob
    mobile_bill_consistency[nan_mask] = np.nan
    nan_count = int(nan_mask.sum())
    nan_pct = (nan_count / n_samples) * 100

    print(
        f"Set {nan_count:,} / {n_samples:,} values ({nan_pct:.2f}%) to NaN randomly."
    )

    synthetic_df = pd.DataFrame(
        {
            "SK_ID_CURR": df_app["SK_ID_CURR"],
            "mobile_bill_consistency": mobile_bill_consistency,
        }
    )

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Saving to CSV: {output_path}")
    synthetic_df.to_csv(output_path, index=False)
    print("Successfully saved synthetic alternative data.")

    return synthetic_df


def main():
    df = generate_synthetic_alt_data()
    print("\nSummary Statistics:")
    print(df.describe())
    print(f"\nMissing values:\n{df.isna().sum()}")
    print(f"\nFirst 5 rows:\n{df.head()}")


if __name__ == "__main__":
    main()
