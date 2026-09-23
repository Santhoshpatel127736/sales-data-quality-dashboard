"""
Streamlit dashboard for the Sales Data Quality Project.

Run:
    streamlit run app.py
"""

from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "sales.db"

st.set_page_config(
    page_title="Sales Data Quality Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Sales Data Quality Dashboard")
st.caption("Cleaned sales data stored in SQLite and analyzed with SQL.")

if not DB_FILE.exists():
    st.error(
        "sales.db was not found. Run `python data_pipeline.py` first."
    )
    st.stop()


@st.cache_data
def query_db(query: str) -> pd.DataFrame:
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query(query, conn)


metrics = query_db(
    """
    SELECT
        ROUND(SUM(total_amount), 2) AS revenue,
        COUNT(*) AS orders,
        ROUND(AVG(total_amount), 2) AS average_order_value
    FROM sales
    """
).iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"₹{metrics['revenue']:,.2f}")
col2.metric("Number of Orders", f"{int(metrics['orders']):,}")
col3.metric("Average Order Value", f"₹{metrics['average_order_value']:,.2f}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Revenue by Region")
    region_df = query_db(
        """
        SELECT region, ROUND(SUM(total_amount), 2) AS revenue
        FROM sales
        GROUP BY region
        ORDER BY revenue DESC
        """
    )
    st.bar_chart(region_df.set_index("region"))

with right:
    st.subheader("Revenue by Category")
    category_df = query_db(
        """
        SELECT category, ROUND(SUM(total_amount), 2) AS revenue
        FROM sales
        GROUP BY category
        ORDER BY revenue DESC
        """
    )
    st.bar_chart(category_df.set_index("category"))

st.subheader("Top Five Products by Revenue")
top_products = query_db(
    """
    SELECT product, ROUND(SUM(total_amount), 2) AS revenue
    FROM sales
    GROUP BY product
    ORDER BY revenue DESC
    LIMIT 5
    """
)
st.dataframe(top_products, use_container_width=True, hide_index=True)

st.subheader("Monthly Sales Trend")
monthly = query_db(
    """
    SELECT strftime('%Y-%m', order_date) AS month,
           ROUND(SUM(total_amount), 2) AS revenue
    FROM sales
    GROUP BY month
    ORDER BY month
    """
)
st.line_chart(monthly.set_index("month"))

st.subheader("Recent Orders")
recent = query_db(
    """
    SELECT order_id, order_date, customer_name, product,
           category, quantity, unit_price, region, total_amount
    FROM sales
    ORDER BY order_date DESC
    LIMIT 10
    """
)
st.dataframe(recent, use_container_width=True, hide_index=True)

st.sidebar.header("Data Quality")
report_file = BASE_DIR / "validation_report.json"

if report_file.exists():
    import json
    report = json.loads(report_file.read_text(encoding="utf-8"))

    st.sidebar.metric("Rows Processed", report["total_rows_processed"])
    st.sidebar.metric("Valid Rows", report["valid_rows"])
    st.sidebar.metric("Rejected Rows", report["rejected_rows"])
    st.sidebar.write("Duplicates:", report["duplicate_records"])
    st.sidebar.write("Missing values:", report["missing_values"])
    st.sidebar.write("Invalid dates:", report["invalid_dates"])
    st.sidebar.write(
        "Invalid numeric values:", report["invalid_numeric_values"]
    )
