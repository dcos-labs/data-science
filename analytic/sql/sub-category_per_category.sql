-- Sub-categories per Category
SELECT category, main_category,
       SUM(backers) backers,
       SUM(usd_pledged) pledged
FROM kickstart k
GROUP BY category, main_category
;
