WITH amulet_counts AS (
    SELECT 
        b.site_id,
        b.temp,
        COUNT(a.amulet_id) as amulet_count,
        ROW_NUMBER() OVER (PARTITION BY b.site_id, b.temp ORDER BY COUNT(a.amulet_id)) as row_num,
        COUNT(*) OVER (PARTITION BY b.site_id, b.temp) as total_count
    FROM burials b
    LEFT JOIN amulets a ON b.burial_id = a.burial_id
    WHERE b.social_group = 'non-elite'
    GROUP BY b.burial_id, b.site_id, b.temp
)
SELECT 
    site_id,
    temp,
    AVG(amulet_count) as median_amulets
FROM amulet_counts
WHERE row_num IN (
    FLOOR((total_count + 1) / 2),
    CEIL((total_count + 1) / 2)
)
GROUP BY site_id, temp
ORDER BY site_id, temp;