-- Backers & Pledges per Month
WITH k AS
(
    SELECT DATE_TRUNC('MONTH', launched) launched_month,
        backers, usd_pledged pledged,
        MAX(DATE_TRUNC('MONTH', launched))
            OVER (PARTITION BY 1) mx_month
    FROM kickstart k
    WHERE state NOT IN ('live', 'undefined')
)
SELECT launched_month,
   SUM(backers) backers,
   SUM(pledged) pledged
FROM k
WHERE launched_month < mx_month
GROUP BY launched_month
;
