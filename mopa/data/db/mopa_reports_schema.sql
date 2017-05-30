/*
-- Drupal
SELECT * FROM node WHERE `type`='report';

SELECT * FROM node_revision;
SELECT * FROM taxonomy_term_data;
content_type_* and content_field_*

SELECT * FROM  node_type;
SELECT * FROM field_data_body WHERE bund;
-- Mopa Specific
*/

DROP TABLE IF EXISTS mopa_reports;
CREATE TABLE mopa_reports(
  -- _id INT AUTO_INCREMENT ,
	id VARCHAR(255) PRIMARY KEY,
	district TEXT,
	neighbourhood TEXT,
	location_name TEXT,
	nature TEXT,
	requested_datetime DATETIME,
	updated_datetime DATETIME,
	type TEXT,
	status TEXT,
	status_notes TEXT
);

/*
SELECT * FROM mopa_reports;
DELETE FROM mopa_reports;


-- Louis Report 1
SELECT recent.*, recent.tempo_medio_resolucao-old.tempo_medio_resolucao as variacao
FROM
(
SELECT type,
	COUNT(*) as no_occorencias,
	(COUNT(*)/b.total_reports * 100) as `pct_do_total`,
  AVG(a.time_diff) `tempo_medio_resolucao`
FROM mopa_reports
  JOIN (SELECT id, TIMESTAMPDIFF(HOUR, requested_datetime, updated_datetime) time_diff FROM mopa_reports) AS a
    ON mopa_reports.id=a.id
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports WHERE requested_datetime BETWEEN '2015-09-20' AND '2015-09-26') b
WHERE requested_datetime BETWEEN '2015-09-20' AND '2015-09-26'
GROUP BY type
) AS recent JOIN
(
SELECT type,
  AVG(a.time_diff) `tempo_medio_resolucao`
FROM mopa_reports
  JOIN (SELECT id, TIMESTAMPDIFF(HOUR, requested_datetime, updated_datetime) time_diff FROM mopa_reports) AS a
    ON mopa_reports.id=a.id
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports WHERE requested_datetime BETWEEN '2015-09-13' AND '2015-09-19') b
WHERE requested_datetime BETWEEN '2015-09-13' AND '2015-09-19'
GROUP BY type
) AS old
ON recent.type=old.type;

-- Louis Report 2
SELECT recent.*, recent.tempo_medio_resolucao - old.tempo_medio_resolucao as variacao_do_tempo_medio
FROM
(
SELECT
	district,
	neighbourhood,
	COUNT(*) as no_occorencias,
	ROUND((COUNT(*)/b.total_reports * 100),2) as `pct_do_total`,
	AVG(a.time_diff) `tempo_medio_resolucao`
FROM mopa_reports
  JOIN (SELECT id, TIMESTAMPDIFF(HOUR, requested_datetime, updated_datetime) time_diff FROM mopa_reports) AS a
      ON mopa_reports.id=a.id
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports) b
WHERE TRIM(LOWER(district)) IN ('kamaxaquene', 'kamubukwana', 'katembe', 'inhagoia b')
  AND requested_datetime BETWEEN '2015-09-20' AND '2015-09-26'
GROUP BY district, neighbourhood
) AS recent JOIN
(
SELECT
	district,
	neighbourhood,
	COUNT(*) as no_occorencias,
	ROUND((COUNT(*)/b.total_reports * 100),2) as `pct_do_total`,
	AVG(a.time_diff) `tempo_medio_resolucao`
FROM mopa_reports
  JOIN (SELECT id, TIMESTAMPDIFF(HOUR, requested_datetime, updated_datetime) time_diff FROM mopa_reports) AS a
      ON mopa_reports.id=a.id
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports) b
WHERE TRIM(LOWER(district)) IN ('kamaxaquene', 'kamubukwana', 'katembe', 'inhagoia b')
  AND requested_datetime BETWEEN '2015-09-13' AND '2015-09-19'
GROUP BY district, neighbourhood
) as old
ON recent.district=old.district AND recent.neighbourhood=old.neighbourhood;

-- Tiago Report
SELECT
	neighbourhood as bairro,
  nature as problema,
  SUM(CASE WHEN status='Registado' THEN 1 ELSE 0 END) AS registado,
  SUM(CASE WHEN status='Em processo' THEN 1 ELSE 0 END) AS em_processo,
  SUM(CASE WHEN status='Resolvido' THEN 1 ELSE 0 END) AS resolvido,
  SUM(CASE WHEN status='Arquivado' THEN 1 ELSE 0 END) AS arquivado,
  SUM(CASE WHEN status='Inválido' THEN 1 ELSE 0 END) AS invalido,
  COUNT(*) total
FROM mopa_reports
WHERE requested_datetime BETWEEN '2015-09-13' AND '2015-09-19'
GROUP BY neighbourhood, nature;

SELECT * FROM mopa_reports;

-- ----------
-- Testing
SELECT recent.*, recent.tempo_medio_resolucao-old.tempo_medio_resolucao as variacao
FROM
(
SELECT type,
    COUNT(*) as no_occorencias,
    (COUNT(*)/b.total_reports * 100) as `pct_do_total`,
  AVG(a.time_diff) `tempo_medio_resolucao`
FROM mopa_reports
  JOIN (SELECT _id, TIMESTAMPDIFF(HOUR, requested_datetime, updated_datetime) time_diff FROM mopa_reports) AS a
    ON mopa_reports._id=a._id
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports WHERE requested_datetime BETWEEN '2015-10-24' AND '2015-10-31') b
WHERE requested_datetime BETWEEN '2015-10-24' AND '2015-10-31'
GROUP BY type
) AS recent JOIN
(
SELECT type,
  AVG(a.time_diff) `tempo_medio_resolucao`
FROM mopa_reports
  JOIN (SELECT _id, TIMESTAMPDIFF(HOUR, requested_datetime, updated_datetime) time_diff FROM mopa_reports) AS a
    ON mopa_reports._id=a._id
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports WHERE requested_datetime BETWEEN '2015-10-17' AND '2015-10-24') b
WHERE requested_datetime BETWEEN '2015-10-17' AND '2015-10-24'
GROUP BY type
) AS old
ON recent.type=old.type;

SELECT * FROM mopa_reports WHERE requested_datetime BETWEEN '2015-10-17' AND '2015-10-24';


SELECT * FROM mopa_reports LIMIT 1;

SELECT a.*, @curRank := @curRank + 1 AS rank
FROM
(
SELECT location_name, COUNT(*) as count
FROM mopa_reports
WHERE neighbourhood='Inhagoia B' AND requested_datetime BETWEEN '2015-10-17' AND '2015-10-24'
GROUP BY district, neighbourhood, location_name
ORDER BY 2 DESC
LIMIT 5) a, (SELECT @curRank := 0) r;




SELECT recent.*, recent.tempo_medio_resolucao - old.tempo_medio_resolucao as variacao
FROM
(
SELECT type,
    COUNT(*) as no_occorencias,
    ROUND((COUNT(*)/b.total_reports * 100),2) as `pct_do_total`,
    AVG(a.time_diff) `tempo_medio_resolucao`
FROM mopa_reports
  JOIN (SELECT id, TIMESTAMPDIFF(HOUR, requested_datetime, updated_datetime) time_diff FROM mopa_reports) AS a
    ON mopa_reports.id=a.id
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports WHERE requested_datetime BETWEEN '2015-10-27' AND '2015-11-03') b
WHERE requested_datetime BETWEEN '2015-10-27' AND '2015-11-03'
GROUP BY type
) AS recent LEFT JOIN
(
SELECT type,
  AVG(a.time_diff) `tempo_medio_resolucao`
FROM mopa_reports
  JOIN (SELECT id, TIMESTAMPDIFF(HOUR, requested_datetime, updated_datetime) time_diff FROM mopa_reports) AS a
    ON mopa_reports.id=a.id
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports WHERE requested_datetime BETWEEN '2015-10-20' AND '2015-10-27') b
WHERE requested_datetime BETWEEN '2015-10-20' AND '2015-10-27'
GROUP BY type
) AS old
ON recent.type=old.type
*/
