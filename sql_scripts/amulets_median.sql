WITH amulet_counts AS (
    SELECT 
        b.owner,
        COUNT(a.amulet_id) as amulet_count,
        ROW_NUMBER() OVER (PARTITION BY b.owner ORDER BY COUNT(a.amulet_id)) as row_num,
        COUNT(*) OVER (PARTITION BY b.owner) as total_count
    FROM burials b
    LEFT JOIN amulets a ON b.burial_id = a.burial_id
    WHERE b.social_group = 'royal'
      AND b.temp = 'LN'
    GROUP BY b.burial_id, b.owner
),
owner_stats AS (
    SELECT 
        owner,
        AVG(amulet_count) as mean_amulets,
        MIN(amulet_count) as min_amulets,
        MAX(amulet_count) as max_amulets,
        SUM(CASE WHEN amulet_count = 0 THEN 1 ELSE 0 END) as zero_amulet_graves,
        COUNT(*) as total_graves
    FROM amulet_counts
    GROUP BY owner
),
median_calc AS (
    SELECT 
        ac.owner,
        AVG(ac.amulet_count) as median_amulets
    FROM amulet_counts ac
    WHERE ac.row_num IN (
        FLOOR((ac.total_count + 1) / 2),
        CEIL((ac.total_count + 1) / 2)
    )
    GROUP BY ac.owner
)
SELECT 
    os.owner,
    mc.median_amulets,
    os.mean_amulets,
    os.min_amulets,
    os.max_amulets,
    os.zero_amulet_graves,
    os.total_graves,
    ROUND(os.zero_amulet_graves * 100.0 / os.total_graves, 1) as percent_with_zero
FROM owner_stats os
LEFT JOIN median_calc mc ON os.owner = mc.owner
ORDER BY os.owner;