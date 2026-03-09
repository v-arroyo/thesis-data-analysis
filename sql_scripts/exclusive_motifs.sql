SELECT 
    b.temp,
    a.form
FROM amulets a
JOIN burials b ON a.burial_id = b.burial_id
JOIN sites s ON a.site_id = s.site_id
WHERE b.dating = 'napatan' 
    AND b.social_group = 'non-elite'
    AND a.form2 IS NULL
GROUP BY b.temp, a.form
HAVING NOT EXISTS (
    SELECT 1
    FROM amulets a2
    JOIN burials b2 ON a2.burial_id = b2.burial_id
    JOIN sites s2 ON a2.site_id = s2.site_id
    WHERE a2.form = a.form
        AND b2.temp != b.temp
        AND b2.dating = 'napatan' 
        AND b2.social_group = 'non-elite'
        AND a2.form2 IS NULL
)
ORDER BY 1,2