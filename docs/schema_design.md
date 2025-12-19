# Star Schema Design

## Overview
The data model is designed to analyze sales performance across multiple channels (Online, Store) and regions.

## Diagram (Conceptual)
Central Fact Table: `fact_sales`
Dimensions:
- `dim_product`
- `dim_store`
- `dim_customer`
- `dim_channel`
- `dim_date`

## Table Definitions

### `fact_sales`
- `transaction_id` (PK)
- `date_key` (FK)
- `product_id` (FK)
- `store_id` (FK) - Nullable for online sales? Or use a "Web Store" placeholder? -> *Decision: Use separate Channel dimension, store_id can be null or map to 'Online' placeholder structure.*
- `customer_id` (FK)
- `channel_id` (FK)
- `quantity`
- `unit_price`
- `discount_amount`
- `net_amount` (quantity * unit_price - discount)
- `cost_amount` (for margin calc)

### `dim_product`
- `product_id` (PK)
- `product_name`
- `category`
- `subcategory`
- `brand`
- `unit_cost`

### `dim_store`
- `store_id` (PK)
- `store_name`
- `city`
- `region`
- `country`
- `size_sqm`
- `opening_date`

### `dim_customer`
- `customer_id` (PK)
- `first_name`
- `last_name`
- `email`
- `join_date`
- `loyalty_tier`

### `dim_channel`
- `channel_id` (PK)
- `channel_name` (e.g., 'Store', 'Online App', 'Online Web')

### `dim_date`
- `date_key` (PK, YYYYMMDD)
- `date`
- `year`
- `quarter`
- `month`
- `month_name`
- `day_of_week`
- `is_weekend`
