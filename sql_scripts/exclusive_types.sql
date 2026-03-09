SELECT 
    temp,
    type,
    COUNT(DISTINCT form) as exclusive_types_count
FROM (
    SELECT 
        b.temp,
        a.form,
        a.type
    FROM amulets a
    JOIN burials b ON a.burial_id = b.burial_id
    WHERE b.dating = 'napatan' 
        AND b.social_group = 'non-elite'
    GROUP BY b.temp, a.form, a.type
    HAVING NOT EXISTS (
        SELECT 1
        FROM amulets a2
        JOIN burials b2 ON a2.burial_id = b2.burial_id
        WHERE a2.form = a.form
            AND b2.temp != b.temp
            AND b2.dating = 'napatan' 
            AND b2.social_group = 'non-elite'
    )
) exclusive_types
GROUP BY temp, type
ORDER BY temp, type;