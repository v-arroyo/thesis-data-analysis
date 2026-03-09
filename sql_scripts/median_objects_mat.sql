WITH combined_data AS (
    SELECT b.super, b.sub, b.burial_id, a.artifact_id AS item_id, a.artifact_material AS material
    FROM artifacts a
    JOIN burials b ON b.burial_id = a.burial_id
    WHERE b.dating = 'napatan' 
        AND b.sub != 'deposit'
        AND a.artifact_type IN ('bead nets', 'burial containers', 'canopics', 'heart scarabs', 'mummy trappings', 'offering tables', 'offering vessels', 'stelae')
        AND b.site_id IN (1,2,4,5,6,7,8,9,10)
),
burial_totals AS (
    SELECT 
        super, 
        sub, 
        burial_id, 
        COUNT(item_id) as total_items
    FROM combined_data
    GROUP BY sub, super, burial_id
)
SELECT 
    super, 
    sub, 
    AVG(total_items) as median_total_items
FROM (
    SELECT
        super,
        sub,
        burial_id,
        total_items,
        ROW_NUMBER() OVER (PARTITION BY sub, super ORDER BY total_items) as row_num,
        COUNT(*) OVER (PARTITION BY sub, super) as total_count
    FROM burial_totals
) AS ranked
WHERE row_num IN (FLOOR((total_count + 1) / 2), CEIL((total_count + 1) / 2))
GROUP BY super, sub