-- Success Rate of Campaigns per Category
SELECT main_category,
       SUM(CASE
               WHEN state = 'successful' THEN 1
               ELSE 0
           END) success_count,
       SUM(CASE
               WHEN state <> 'successful' THEN 1
               ELSE 0
           END) fail_count
FROM tx.kickstart k
WHERE state NOT IN ('live',
                    'undefined')
GROUP BY main_category
;
