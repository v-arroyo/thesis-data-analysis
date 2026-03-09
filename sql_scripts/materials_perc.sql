select
	region,
    social_group,
    CASE 
        WHEN m.material_local = 1 THEN 'local'
        WHEN m.material_imported = 1 THEN 'imported'
    END as material_type,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY social_group), 0) as percentage
from burials b
join amulets a ON a.burial_id = b.burial_id
JOIN materials m ON m.material_name = a.material
JOIN sites s ON s.site_id = b.site_id
where dating = 'napatan' and b.site_id in (1,2,4,5,6,7,8,9,10)
group by 1,2,3