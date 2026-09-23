# Sales Data Quality Dashboard

A mini Python data pipeline that ingests sales CSV data, detects and handles common data-quality problems, stores valid records in SQLite, runs SQL analytics, and displays business insights through a Streamlit dashboard.

## Project structure

```text
sales-data-quality-project/
│
├── data/
│   └── sales.csv
│
├── app.py
├── data_pipeline.py
├── queries.sql
├── cleaned_sales.csv
├── validation_report.json
├── sales.db
├── requirements.txt
└── README.md
```

## Features

- CSV ingestion with required-column validation
- Missing-value validation
- Duplicate `order_id` detection
- Invalid date detection
- Invalid quantity and price detection
- Region/category normalization
- Cleaned CSV output
- Automatic JSON validation report
- SQLite database
- SQL business analysis
- Streamlit dashboard
- Recent orders table
- Basic error handling

## Setup

### 1. Create and activate a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Run the data pipeline

From the project root:

```bash
python data_pipeline.py
```

The pipeline:

1. Reads `data/sales.csv`.
2. Checks the required columns.
3. Normalizes text values.
4. Validates dates and numeric fields.
5. Rejects invalid/duplicate rows.
6. Calculates `total_amount`.
7. Creates `cleaned_sales.csv`.
8. Creates `validation_report.json`.
9. Creates `sales.db` with the `sales` table.

The pipeline does not require manual editing of individual rows.

## Launch the dashboard

After running the pipeline:

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal, normally:

```text
http://localhost:8501
```

## SQL analysis

The required SQL queries are stored in `queries.sql`.

The queries calculate:

- Total sales amount
- Total number of orders
- Sales by region
- Sales by category
- Top five products by revenue
- Monthly sales trend
- Average order value
- Recent orders

## Data-quality handling assumptions

### Missing values

Rows with missing required fields are rejected rather than automatically inventing values.

### Duplicate order IDs

The first occurrence is retained. Later records with the same `order_id` are rejected.

### Invalid dates

Dates that cannot be parsed are rejected.

### Quantity and price

Quantity and unit price must be greater than zero. Rows with zero, negative, or non-numeric values are rejected.

### Region and category

Values are normalized case-insensitively and with surrounding whitespace removed.

For example:

```text
north
North
 NORTH
NORTH
```

becomes:

```text
North
```

Unknown region/category values are rejected because they cannot be mapped to the known categories.

### Total amount

```text
total_amount = quantity * unit_price
```

## Example issues intentionally included in the sample dataset

The supplied sample contains more than 100 rows and intentionally includes:

- Missing customer name
- Missing product
- Missing category
- Missing region
- Duplicate order IDs
- Invalid dates
- Negative quantity
- Zero quantity
- Negative price
- Zero price
- Mixed capitalization
- Leading/trailing whitespace
- Mixed capitalization in categories

## Validation report

`validation_report.json` is regenerated every time the pipeline runs.

Example structure:

```json
{
  "total_rows_processed": 120,
  "valid_rows": 108,
  "rejected_rows": 12,
  "duplicate_records": 2,
  "missing_values": 4,
  "invalid_dates": 2,
  "invalid_numeric_values": 4
}
```

The exact counts can change if the input CSV is replaced.

## Technology stack

- Python
- Pandas
- SQLite
- SQL
- Streamlit
- CSV
- JSON

## Notes for submission

Before submitting, run:

```bash
python data_pipeline.py
streamlit run app.py
```

Confirm that the dashboard loads and that these generated files exist:

```text
cleaned_sales.csv
validation_report.json
sales.db
```

Then submit the complete project folder or a ZIP file.
