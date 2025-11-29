SELECT * 
FROM public."stg_Online_Retail"
WHERE "InvoiceNo" NOT LIKE 'C%' AND "Quantity" < 0;

SELECT * 
FROM public."stg_Online_Retail"
WHERE "InvoiceNo"  LIKE 'C%' AND "Quantity" < 0;

-- Null customerID 135080 rows
SELECT DISTINCT "InvoiceNo"
FROM public."stg_Online_Retail"
WHERE "CustomerID" IS NULL;

-- No Nulls for UnitPrice
SELECT DISTINCT "InvoiceNo"
FROM public."stg_Online_Retail"
WHERE "UnitPrice" IS NULL;

-- Duplicate CustomerIDs
-- 1200 customerIDs has products = InvoiceNO
WITH duplicate_customerIDs AS 
(SELECT  "CustomerID", 
		 COUNT(*) AS "duplication_no"
FROM public."stg_Online_Retail"
GROUP BY "CustomerID"
HAVING COUNT(*) > 1
),
distinct_procuts AS (SELECT  "CustomerID",
		COUNT(DISTINCT "Description") AS "distinct_product_no"
FROM public."stg_Online_Retail"
GROUP BY "CustomerID"
)
SELECT  dc."CustomerID",
		dc."duplication_no",
		dp."distinct_product_no"
FROM duplicate_customerIDs dc
JOIN distinct_procuts dp
ON dc."CustomerID" = dp."CustomerID"
-- AND dc."duplication_no" != dp."distinct_product_no"


SELECT COUNT(DISTINCT "Description")
FROM public."stg_Online_Retail"
WHERE "CustomerID" = '17896'

SELECT * 
FROM public."stg_Online_Retail"
limit 10

-- unspecified
SELECT DISTINCT "Country"
FROM public."stg_Online_Retail" 

WITH unspecifed_country AS(
	SELECT * 
	FROM public."stg_Online_Retail" 
	WHERE "Country" = 'Unspecified'
)
SELECT *
FROM public."stg_Online_Retail"
WHERE "CustomerID" IN (	SELECT DISTINCT "CustomerID"
	FROM unspecifed_country)


SELECT *, COUNT(*) 
FROM public."stg_Online_Retail"
GROUP BY "InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"
HAVING COUNT(*) > 1;

SELECT *
FROM public."stg_Online_Retail"
WHERE "InvoiceNo" = '536412'


