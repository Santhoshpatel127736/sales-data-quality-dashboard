-- Sales Data Quality Dashboard - SQL Analysis
-- Run after executing: python data_pipeline.py

-- 1. Total sales amount
SELECT ROUND(SUM(total_amount), 2) AS total_sales_amount
FROM sales;

-- 2. Total number of orders
SELECT COUNT(*) AS total_orders
FROM sales;

-- 3. Sales by region
SELECT
    region,
    ROUND(SUM(total_amount), 2) AS revenue
FROM sales
GROUP BY region
ORDER BY revenue DESC;

-- 4. Sales by product category
SELECT
    category,
    ROUND(SUM(total_amount), 2) AS revenue
FROM sales
GROUP BY category
ORDER BY revenue DESC;

-- 5. Top five products by revenue
SELECT
    product,
    ROUND(SUM(total_amount), 2) AS revenue
FROM sales
GROUP BY product
ORDER BY revenue DESC
LIMIT 5;

-- 6. Monthly sales trend
SELECT
    strftime('%Y-%m', order_date) AS month,
    ROUND(SUM(total_amount), 2) AS revenue
FROM sales
GROUP BY month
ORDER BY month;

-- 7. Average order value
SELECT
    ROUND(AVG(total_amount), 2) AS average_order_value
FROM sales;

-- 8. Recent orders
SELECT
    order_id,
    order_date,
    customer_name,
    product,
    category,
    quantity,
    unit_price,
    region,
    total_amount
FROM sales
ORDER BY order_date DESC
LIMIT 10;
