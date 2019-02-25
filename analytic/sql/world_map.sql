-- World Map
SELECT country, SUM(backers) backers
FROM tx.kickstart
GROUP BY country
;
