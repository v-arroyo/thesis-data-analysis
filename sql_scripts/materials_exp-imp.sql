SELECT
    s.region,
    CASE 
        WHEN m.material_local = 1 THEN 'local'
        WHEN m.material_imported = 1 THEN 'imported'
    END as material_type,
    COUNT(*) as count,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY s.region),
        0
    ) as percentage
FROM amulets a
JOIN materials m ON m.material_name = a.material
JOIN sites s ON s.site_id = a.site_id
JOIN burials b ON b.burial_id = a.burial_id
WHERE dating = 'napatan' 
    AND b.site_id IN (4,5,6,7,8,9,10) 
    AND social_group = 'non-elite'
    AND (m.material_local = 1 OR m.material_imported = 1)
GROUP BY s.region, material_type
ORDER BY s.region, material_type;