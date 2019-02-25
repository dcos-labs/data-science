-- Revenue per Backer by Main Category
SELECT main_category,
       SUM(backers) backers,
       SUM(usd_pledged) pledged,
       SUM(usd_pledged) / SUM(backers)::FLOAT revenue_per_backer
FROM kickstart k
WHERE state NOT IN ('live', 'undefined')
GROUP BY main_category
ORDER BY revenue_per_backer DESC
;
