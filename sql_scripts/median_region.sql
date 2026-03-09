WITH amulet_counts AS (
    SELECT 
        s.region,
        COUNT(a.amulet_id) as amulet_count,
        ROW_NUMBER() OVER (PARTITION BY s.region ORDER BY COUNT(a.amulet_id)) as row_num,
        COUNT(*) OVER (PARTITION BY s.region) as total_count
    FROM burials b
    LEFT JOIN amulets a ON b.burial_id = a.burial_id
    JOIN sites s ON b.site_id = s.site_id
    WHERE b.social_group = 'non-elite'
    GROUP BY b.burial_id, s.region
)
SELECT 
    region,
    AVG(amulet_count) as median_amulets
FROM amulet_counts
WHERE row_num IN (
    FLOOR((total_count + 1) / 2),
    CEIL((total_count + 1) / 2)
)
GROUP BY region
ORDER BY region;