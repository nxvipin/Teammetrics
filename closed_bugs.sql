-- top 10 maintainers as carnivore ID
CREATE OR REPLACE FUNCTION bug_closer_ids_of_pkggroup(text,int) RETURNS SETOF RECORD AS $$
  SELECT ce.id
         , COUNT(*)::int
    FROM (SELECT id, source, done_email FROM archived_bugs
     UNION
     SELECT id, source, done_email FROM bugs WHERE status = 'done'
    ) db
    JOIN carnivore_emails ce ON ce.email = db.done_email
   WHERE source IN (           -- source packages that are maintained by the team
       SELECT DISTINCT source FROM upload_history
        WHERE maintainer_email = $1
          AND nmu = 'f'
      )
    AND done_email IN ( -- email of uploaders who at least once uploaded on behalf of the team
       SELECT DISTINCT ce.email FROM upload_history uh
         JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
        WHERE maintainer_email = $1
          AND nmu = 'f'
   )
   GROUP BY ce.id
   ORDER BY count DESC
   LIMIT $2
$$ LANGUAGE 'SQL';

/*
SELECT * FROM bug_closer_ids_of_pkggroup('debian-med-packaging@lists.alioth.debian.org',50) AS (id int, count int);
SELECT * FROM bug_closer_ids_of_pkggroup('debian-science-maintainers@lists.alioth.debian.org',50) AS (id int, count int);
*/

-- top 10 maintainers closing bugs in team packages
CREATE OR REPLACE FUNCTION bug_closer_per_year_of_pkggroup(text,int) RETURNS SETOF RECORD AS $$
  SELECT cn.name, db.year, COUNT(*)::int FROM
--    (SELECT source, EXTRACT(year FROM done_date)::int AS year, done_email   -- done_date is always 1970-01-01
    (SELECT id, source, EXTRACT(year FROM last_modified)::int AS year, done_email FROM archived_bugs
     UNION
     SELECT id, source, EXTRACT(year FROM last_modified)::int AS year, done_email FROM bugs WHERE status = 'done'
    ) db
    JOIN carnivore_emails ce ON ce.email = db.done_email
    JOIN (SELECT * FROM carnivore_names
           WHERE id IN (SELECT idupl FROM bug_closer_ids_of_pkggroup($1, $2) AS (idupl int, count int))
    )  cn ON ce.id    = cn.id
    JOIN carnivore_names_prefered cnp ON cn.id = cnp.id
   WHERE source IN (    -- source packages that are maintained by the team
       SELECT DISTINCT source FROM upload_history
        WHERE maintainer_email = $1
          AND nmu = 'f'
     )
     AND done_email IN ( -- email of uploaders who at least once uploaded on behalf of the team
      SELECT DISTINCT ce.email FROM upload_history uh
        JOIN carnivore_emails ce ON ce.email = uh.changed_by_email
       WHERE maintainer_email = $1
     )
     AND cn.name = cnp.name
   GROUP BY cn.name, db.year
   ORDER BY year, count DESC, cn.name
$$ LANGUAGE 'SQL';

/*
SELECT * FROM bug_closer_per_year_of_pkggroup('debian-med-packaging@lists.alioth.debian.org',50) AS (name text, year int, count int);
SELECT * FROM bug_closer_per_year_of_pkggroup('debian-science-maintainers@lists.alioth.debian.org',50) AS (name text, year int, count int);
*/

-- top 10 maintainers as (hopefully!!!) unique name
CREATE OR REPLACE FUNCTION bug_closer_names_of_pkggroup(text, int) RETURNS SETOF RECORD AS $$
  SELECT cnp.name FROM
    (SELECT id FROM bug_closer_ids_of_pkggroup($1, $2) AS (id int, count int)) au
    JOIN carnivore_names_prefered cnp ON au.id = cnp.id
$$ LANGUAGE 'SQL';

/*
SELECT * FROM bug_closer_names_of_pkggroup('debian-med-packaging@lists.alioth.debian.org',50) AS (name text);
SELECT * FROM bug_closer_names_of_pkggroup('debian-science-maintainers@lists.alioth.debian.org',50) AS (name text);
*/
