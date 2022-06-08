FW_QUERY = """SELECT
   fw.id,
   fw.title,
   fw.description,
   fw.rating,
   fw.type,
   fw.created,
   fw.modified,
   COALESCE (
       json_agg(
           DISTINCT jsonb_build_object(
               'person_role', pfw.role,
               'person_id', p.id,
               'person_name', p.full_name
           )
       ) FILTER (WHERE p.id is not null),
       '[]'
   ) as persons,
   COALESCE (
       json_agg(
           DISTINCT jsonb_build_object(
               'g_id', g.id,
               'g_name', g.name
           )
       ) FILTER (WHERE g.id is not null),
       '[]'
   ) as genres
   
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE fw.modified > '%s' or p.id in (SELECT id FROM content.person WHERE modified > '%s' ORDER BY modified)
or g.id in (SELECT id FROM content.genre WHERE modified > '%s' ORDER BY modified)
GROUP BY fw.id
ORDER BY fw.modified"""


PERSON_QUERY = """
SELECT
    p.id,
    p.full_name,
    p.modified,
   COALESCE (
       json_agg(
           DISTINCT jsonb_build_object(
               'fw_id', fw.id,
               'fw_title', fw.title,
               'fw_rating', fw.rating,
               'fw_type', fw.type
           )
       ) FILTER (WHERE fw.id is not null),
       '[]'
   ) as films,
   array_agg(DISTINCT pfw.role) as roles
FROM content.person p
LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
LEFT JOIN content.film_work fw ON fw.id = pfw.film_work_id
WHERE p.modified > '%s'
GROUP BY p.id
ORDER BY p.modified"""


GENRE_QUERY = """
SELECT
    g.id as genre_id,
    g.name as genre_name,
    g.description as genre_description,
    g.modified 
FROM content.genre g
WHERE g.modified > '%s';
"""

counts = {FW_QUERY: 3, PERSON_QUERY: 1, GENRE_QUERY: 1}
