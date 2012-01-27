-- top 10 maintainers as carnivore ID
CREATE OR REPLACE FUNCTION active_uploader_ids_of_pkggroup(text,int) RETURNS SETOF RECORD AS $$
  SELECT ce.id
         , COUNT(*)::int
    FROM (SELECT source, changed_by_email, nmu FROM upload_history) uh
    JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
   WHERE source IN (           -- source packages that are maintained by the team
       SELECT DISTINCT source FROM upload_history
        WHERE maintainer_email = $1
          AND nmu = 'f'
      )
    AND changed_by_email IN ( -- email of uploaders who at least once uploaded on behalf of the team
       SELECT DISTINCT ce.email FROM upload_history uh
         JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
        WHERE maintainer_email = $1
          AND nmu = 'f'
   )
     AND nmu = 'f'
   GROUP BY ce.id
   ORDER BY count DESC
   LIMIT $2
$$ LANGUAGE 'SQL';

/*
SELECT * FROM active_uploader_ids_of_pkggroup('debian-med-packaging@lists.alioth.debian.org',50) AS (id int, count int);
SELECT * FROM active_uploader_ids_of_pkggroup('debian-science-maintainers@lists.alioth.debian.org',50) AS (id int, count int);
*/

-- top 10 maintainers with acticity per year
-- Remark: There is no need to transform carnivore IDs into names because the calling functions needs to
--         recreate table header anyway
CREATE OR REPLACE FUNCTION active_uploader_per_year_of_pkggroup(text,int) RETURNS SETOF RECORD AS $$
  SELECT cn.name, uh.year, COUNT(*)::int FROM
    (SELECT source, EXTRACT(year FROM date)::int AS year, changed_by_email
       FROM upload_history
      WHERE nmu = 'f'
    ) uh
    JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
    JOIN (SELECT * FROM carnivore_names
           WHERE id IN (SELECT idupl FROM active_uploader_ids_of_pkggroup($1, $2) AS (idupl int, count int))
    )  cn ON ce.id    = cn.id
    JOIN carnivore_names_prefered cnp ON cn.id = cnp.id
   WHERE source IN (           -- source packages that are maintained by the team
      SELECT DISTINCT source FROM upload_history
      WHERE maintainer_email = $1
        AND nmu = 'f'
     )
     AND changed_by_email IN ( -- email of uploaders who at least once uploaded on behalf of the team
      SELECT DISTINCT ce.email FROM upload_history uh
        JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
       WHERE maintainer_email = $1
     )
     AND cn.name = cnp.name
   GROUP BY cn.name, uh.year
   ORDER BY year, count DESC, cn.name
$$ LANGUAGE 'SQL';

/*
SELECT * FROM active_uploader_per_year_of_pkggroup('debian-med-packaging@lists.alioth.debian.org',50) AS (name text, year int, count int);
SELECT * FROM active_uploader_per_year_of_pkggroup('debian-science-maintainers@lists.alioth.debian.org',50) AS (name text, year int, count int);
*/

-- top 10 maintainers as (hopefully!!!) unique name
CREATE OR REPLACE FUNCTION active_uploader_names_of_pkggroup(text, int) RETURNS SETOF RECORD AS $$
  SELECT cnp.name FROM
    (SELECT id FROM active_uploader_ids_of_pkggroup($1, $2) AS (id int, count int)) au
    JOIN carnivore_names_prefered cnp ON au.id = cnp.id
$$ LANGUAGE 'SQL';

/*
SELECT * FROM active_uploader_names_of_pkggroup('debian-med-packaging@lists.alioth.debian.org',50) AS (name text);
SELECT * FROM active_uploader_names_of_pkggroup('debian-science-maintainers@lists.alioth.debian.org',50) AS (name text);
*/

/*
 Finally you need to

   psql udd -c 'CREATE EXTENSION tablefunc;'

 to be able to run uploader statistics script
 */