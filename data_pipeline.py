"""
Sales Data Quality Pipeline

Reads data/sales.csv, validates and cleans records, writes:
- cleaned_sales.csv
- validation_report.json
- sales.db
"""

from pathlib import Path
import json
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "sales.csv"
CLEANED_FILE = BASE_DIR / "cleaned_sales.csv"
REPORT_FILE = BASE_DIR / "validation_report.json"
DB_FILE = BASE_DIR / "sales.db"

REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "customer_name",
    "product",
    "category",
    "quantity",
    "unit_price",
    "region",
]

NORMALIZED_REGIONS = {
    "north": "North",
    "south": "South",
    "east": "East",
    "west": "West",
}

NORMALIZED_CATEGORIES = {
    "electronics": "Electronics",
    "furniture": "Furniture",
    "stationery": "Stationery",
    "accessories": "Accessories",
}


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise ValueError("The CSV file is empty.")
    except pd.errors.ParserError as exc:
        raise ValueError(f"Malformed CSV file: {exc}") from exc

    missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    return df[REQUIRED_COLUMNS].copy()


def clean_and_validate(df: pd.DataFrame):
    original = df.copy()
    total_rows = len(df)

    # Normalize text before validation.
    text_columns = ["order_id", "customer_name", "product", "category", "region"]
    for col in text_columns:
        df[col] = df[col].astype("string").str.strip()

    df["region"] = (
        df["region"].str.lower().map(NORMALIZED_REGIONS)
    )
    df["category"] = (
        df["category"].str.lower().map(NORMALIZED_CATEGORIES)
    )

    # Convert date/numeric fields safely.
    parsed_dates = pd.to_datetime(df["order_date"], errors="coerce")
    df["order_date"] = parsed_dates.dt.strftime("%Y-%m-%d")

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    # Count validation problems.
    missing_mask = df[REQUIRED_COLUMNS].isna() | (df[REQUIRED_COLUMNS] == "")
    missing_values = int(missing_mask.sum().sum())

    invalid_dates = int(parsed_dates.isna().sum())

    invalid_numeric_mask = (
        df["quantity"].isna()
        | (df["quantity"] <= 0)
        | df["unit_price"].isna()
        | (df["unit_price"] <= 0)
    )
    invalid_numeric_values = int(invalid_numeric_mask.sum())

    duplicate_mask = df["order_id"].duplicated(keep="first")
    duplicate_records = int(duplicate_mask.sum())

    # A record is valid only if every required field is valid.
    valid_mask = (
        ~missing_mask.any(axis=1)
        & ~parsed_dates.isna()
        & ~invalid_numeric_mask
        & ~duplicate_mask
    )

    cleaned = df.loc[valid_mask, REQUIRED_COLUMNS].copy()

    # Quantity should be an integer for the final schema.
    cleaned["quantity"] = cleaned["quantity"].astype(int)
    cleaned["unit_price"] = cleaned["unit_price"].astype(float).round(2)
    cleaned["total_amount"] = (
        cleaned["quantity"] * cleaned["unit_price"]
    ).round(2)

    rejected_rows = int((~valid_mask).sum())

    report = {
        "total_rows_processed": total_rows,
        "valid_rows": int(valid_mask.sum()),
        "rejected_rows": rejected_rows,
        "duplicate_records": duplicate_records,
        "missing_values": missing_values,
        "invalid_dates": invalid_dates,
        "invalid_numeric_values": invalid_numeric_values,
        "input_file": str(INPUT_FILE.relative_to(BASE_DIR)),
        "output_file": str(CLEANED_FILE.relative_to(BASE_DIR)),
    }

    return cleaned, report


def save_outputs(cleaned: pd.DataFrame, report: dict):
    cleaned.to_csv(CLEANED_FILE, index=False)

    with REPORT_FILE.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DROP TABLE IF EXISTS sales")
        conn.execute(
            """
            CREATE TABLE sales (
                order_id TEXT PRIMARY KEY,
                order_date TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                product TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                unit_price REAL NOT NULL CHECK(unit_price > 0),
                region TEXT NOT NULL,
                total_amount REAL NOT NULL
            )
            """
        )

        cleaned.to_sql("sales", conn, if_exists="append", index=False)

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_sales_order_date ON sales(order_date)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_sales_region ON sales(region)"
        )
        conn.commit()


def main():
    print("Loading:", INPUT_FILE)
    df = load_data(INPUT_FILE)
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")

    cleaned, report = clean_and_validate(df)
    save_outputs(cleaned, report)

    print("\nValidation report")
    for key, value in report.items():
        print(f"{key}: {value}")

    print(f"\nCreated: {CLEANED_FILE}")
    print(f"Created: {REPORT_FILE}")
    print(f"Created: {DB_FILE}")


if __name__ == "__main__":
    main()
