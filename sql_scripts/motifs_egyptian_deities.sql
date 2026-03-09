SELECT
	temp_early,
    temp_late,
    social_group,
    CASE 
        WHEN a.form IN ("aker", "amun", "amun/isis/horus", "amun/khonsu/monthu", "amun/mut/khonsu",
            "anubis", "bastet", "bes", "duamutef", "hapi", "hapi, nile god", "hathor", "heh", "horus", "horus child", "imsety", "isis", "isis and horus", "khonsu",
            "maat", "min", "mut", "nefertum", "neith", "nephthys", "onuris", "osiris", "pataikos", "ptah", "qebehsenuef", "ra", "ra-horakhty", "sekhmet", "shu",
            "taweret", "thoth") THEN 'egyptian deities'
        ELSE "local adaptations"
    END AS form_source,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY social_group), 0) AS percentage
FROM burials b
JOIN amulets a ON a.burial_id = b.burial_id
JOIN materials m ON m.material_name = a.material
JOIN sites s ON s.site_id = b.site_id
WHERE dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10)
GROUP BY 1,2,3,4