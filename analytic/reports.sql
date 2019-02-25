-- Backers & Pledges per Month
WITH k AS
(
    SELECT DATE_TRUNC('MONTH', launched) launched_month,
        backers, usd_pledged pledged,
        MAX(DATE_TRUNC('MONTH', launched)) OVER (PARTITION BY 1) mx_month
    FROM kickstart k
    WHERE state NOT IN ('live', 'undefined')
)
SELECT launched_month,
   SUM(backers) backers,
   SUM(pledged) pledged
FROM k
WHERE launched_month < mx_month
GROUP BY launched_month

-- Backers Main Categories per Month
WITH k AS
(
    SELECT main_category, DATE_TRUNC('MONTH', launched) launched_month,
        backers, usd_pledged pledged,
        MAX(DATE_TRUNC('MONTH', launched)) OVER (PARTITION BY 1) mx_month
    FROM kickstart k
    WHERE state NOT IN ('live', 'undefined')
)
SELECT main_category, launched_month,
   SUM(backers) backers,
   SUM(pledged) pledged
FROM k
WHERE launched_month < mx_month
GROUP BY main_category, launched_month

-- Sub-categories per Category
SELECT category, main_category,
       SUM(backers) backers,
       SUM(usd_pledged) pledged
FROM kickstart k
GROUP BY category, main_category

-- Revenue per Backer by Main Category
SELECT main_category,
       SUM(backers) backers,
       SUM(usd_pledged) pledged,
       SUM(usd_pledged) / SUM(backers)::FLOAT revenue_per_backer
FROM kickstart k
WHERE state NOT IN ('live', 'undefined')
GROUP BY main_category
ORDER BY revenue_per_backer DESC

-- Success Rates
WITH s AS
(
    SELECT k.*,
        CASE WHEN state = 'successful' THEN 1 ELSE 0 END success
    FROM tx.kickstart k
    WHERE state NOT IN ('live', 'undefined')
), ss AS
(
SELECT
    main_category,
    success,
    COUNT(1) campaign_count,
    SUM(backers) backers,
    SUM(usd_pledged) pledged,
    SUM(COUNT(1)) OVER (PARTITION BY main_category) campaign_ttl,
    ROUND(AVG(deadline::DATE - launched::DATE)) campaign_days_avg
FROM s
GROUP BY
    main_category,
    success
)
SELECT
    main_category,
    success,
    campaign_count,
    ROUND(100.0 * campaign_count / campaign_ttl) campaign_percent,
    backers,
    ROUND(pledged/backers::FLOAT, 2) pledge_per_backer,
    campaign_days_avg
FROM ss
ORDER BY main_category, success

-- World Map
SELECT country,
    SUM(backers) backers
FROM tx.kickstart
GROUP BY country
