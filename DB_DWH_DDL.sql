USE master;
GO
IF EXISTS (SELECT name FROM sys.databases WHERE name = 'Ecommerce_Analytics')
BEGIN
    ALTER DATABASE Ecommerce_Analytics SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE Ecommerce_Analytics;
END
GO
CREATE DATABASE Ecommerce_Analytics;
GO


USE Ecommerce_Analytics;
GO

CREATE TABLE raw_sales (
    invoice_no VARCHAR(20),
    stock_code VARCHAR(20),
    description VARCHAR(255),
    quantity INT,
    invoice_date DATETIME,
    unit_price DECIMAL(10, 2),
    customer_id VARCHAR(20),
    country VARCHAR(100),
    load_date DATETIME DEFAULT GETDATE()
);

CREATE TABLE cleaned_sales (
    sales_id INT IDENTITY(1,1) PRIMARY KEY,
    invoice_no VARCHAR(20),
    stock_code VARCHAR(20),
    description VARCHAR(255),
    quantity INT,
    invoice_date DATETIME,
    unit_price DECIMAL(10, 2),
    customer_id VARCHAR(20),
    country VARCHAR(100),
    total_amount AS (quantity * unit_price) PERSISTED,
    load_date DATETIME DEFAULT GETDATE()
);


CREATE TABLE dim_customer (
    customer_key INT IDENTITY(1,1) PRIMARY KEY,
    customer_id VARCHAR(20) UNIQUE,
    first_purchase_date DATETIME,
    total_orders INT DEFAULT 0,
    total_spent DECIMAL(18, 2) DEFAULT 0
);

CREATE TABLE dim_product (
    product_key INT IDENTITY(1,1) PRIMARY KEY,
    stock_code VARCHAR(20) UNIQUE,
    description VARCHAR(255),
    category VARCHAR(100)
);

CREATE TABLE dim_time (
    time_key INT PRIMARY KEY,
    full_date DATETIME,
    day INT,
    month INT,
    year INT,
    quarter INT,
    day_of_week INT,
    day_name VARCHAR(10),
    month_name VARCHAR(10),
    is_weekend BIT
);


CREATE TABLE fact_sales (
    sales_key INT IDENTITY(1,1) PRIMARY KEY,
    time_key INT REFERENCES dim_time(time_key),
    customer_key INT REFERENCES dim_customer(customer_key),
    product_key INT REFERENCES dim_product(product_key),
    quantity INT,
    unit_price DECIMAL(10, 2),
    total_amount DECIMAL(18, 2),
    country VARCHAR(100)
);

use Ecommerce_Analytics;
Go

CREATE OR ALTER PROCEDURE sp_clean_and_transform_data
AS
BEGIN
    INSERT INTO cleaned_sales(
        invoice_no, stock_code, description, 
        quantity, invoice_date, unit_price, 
        customer_id, country
    )
    SELECT 
        invoice_no, 
        UPPER(TRIM(stock_code)) AS stock_code,
        LEFT(description, 255) AS description,
        quantity, 
        invoice_date, 
        unit_price,
        customer_id,
        country
    FROM raw_sales
    WHERE quantity > 0 AND unit_price > 0 AND customer_id IS NOT NULL;

    SELECT @@ROWCOUNT AS 'rows_affected';
END;






