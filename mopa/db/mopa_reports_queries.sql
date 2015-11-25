SELECT recent.*, recent.tempo_medio_resolucao - old.tempo_medio_resolucao as variacao
FROM
(
SELECT type,
    COUNT(*) as no_occorencias,
    (COUNT(*)/b.total_reports * 100) as `pct_do_total`,
  AVG(a.time_diff) `tempo_medio_resolucao`
FROM mopa_reports
  JOIN (SELECT id, TIMESTAMPDIFF(HOUR, requested_datetime, updated_datetime) time_diff FROM mopa_reports) AS a
    ON mopa_reports.id=a.id
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports WHERE requested_datetime BETWEEN '2015-10-27' AND '2015-11-03') b
WHERE requested_datetime BETWEEN '2015-10-27' AND '2015-11-03'
GROUP BY type
) AS recent JOIN
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
ON recent.type=old.type;
-- --------------------
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
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports WHERE requested_datetime BETWEEN '2015-10-27' AND '2015-11-03') b
WHERE requested_datetime BETWEEN '2015-10-27' AND '2015-11-03'
GROUP BY district, neighbourhood
) AS recent LEFT JOIN
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
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports WHERE requested_datetime BETWEEN '2015-10-20' AND '2015-10-27') b
WHERE requested_datetime BETWEEN '2015-10-20' AND '2015-10-27'
GROUP BY district, neighbourhood
) as old
ON recent.district=old.district AND recent.neighbourhood=old.neighbourhood
;
-- ---
SELECT * FROM
(
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
WHERE requested_datetime BETWEEN '2015-10-27' AND '2015-11-03'
GROUP BY neighbourhood, nature
) as a RIGHT JOIN (
  SELECT 'Tchova não passou' AS problema, 0 as registado, 0 as em_processo, 0 as resolvido, 0 as arquivado, 0 as invalido, 0 as total
  UNION
  SELECT 'Contentor está cheio' AS problema, 0 as registado, 0 as em_processo, 0 as resolvido, 0 as arquivado, 0 as invalido, 0 as total
  UNION
  SELECT 'Lixeira informal' AS problema, 0 as registado, 0 as em_processo, 0 as resolvido, 0 as arquivado, 0 as invalido, 0 as total
  UNION
  SELECT 'Lixo fora do contentor' AS problema, 0 as registado, 0 as em_processo, 0 as resolvido, 0 as arquivado, 0 as invalido, 0 as total
  UNION
  SELECT 'Lixo na vala de drenagem' AS problema, 0 as registado, 0 as em_processo, 0 as resolvido, 0 as arquivado, 0 as invalido, 0 as total
  UNION
  SELECT 'Camião não passou' AS problema, 0 as registado, 0 as em_processo, 0 as resolvido, 0 as arquivado, 0 as invalido, 0 as total
) b ON a.problema = b.problema
;

-----