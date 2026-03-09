SELECT
	b.social_group,
    b.temp,
    a.artifact_type
FROM artifacts a
JOIN burials b ON a.burial_id = b.burial_id
WHERE b.dating = 'napatan' AND b.site_id IN (1,2,4,5,6,7,8,9,10) 
GROUP BY 1,2,3
HAVING NOT EXISTS (
    SELECT 1
    FROM artifacts a2
    JOIN burials b2 ON a2.burial_id = b2.burial_id
    WHERE a2.artifact_type = a.artifact_type
        AND b2.temp != b.temp
        AND b2.social_group != b.social_group
        AND b2.dating = 'napatan'
        AND b2.site_id IN (1,2,4,5,6,7,8,9,10) 
        
)
ORDER BY 1,2