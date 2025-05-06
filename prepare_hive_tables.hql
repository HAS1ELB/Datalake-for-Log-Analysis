-- Création de la base de données pour l'analyse des logs
CREATE DATABASE IF NOT EXISTS logs_analysis;
USE logs_analysis;

-- Création d'une table externe pour les logs bruts
-- Cette table sera utilisée pour charger les données brutes depuis HDFS
CREATE EXTERNAL TABLE IF NOT EXISTS raw_logs (
  log_line STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\n'
STORED AS TEXTFILE
LOCATION '/data/raw_logs';

-- Création d'une table pour stocker les logs analysés
CREATE TABLE IF NOT EXISTS web_logs (
  ip STRING,
  client_identd STRING,
  user_id STRING,
  timestamp STRING,
  request STRING,
  status_code INT,
  size BIGINT,
  referer STRING,
  user_agent STRING,
  -- Colonnes dérivées pour faciliter l'analyse
  method STRING,
  endpoint STRING,
  protocol STRING,
  day INT,
  month STRING,
  year INT,
  hour INT,
  minute INT,
  second INT
)
PARTITIONED BY (date_ymd STRING)
STORED AS ORC;

-- Création d'une vue pour extraire les informations des logs bruts
-- Cette requête utilise des expressions régulières pour extraire les différentes parties d'une ligne de log
CREATE VIEW IF NOT EXISTS parsed_logs AS
SELECT
  regexp_extract(log_line, '^([^ ]*)', 1) AS ip,
  regexp_extract(log_line, '^[^ ]* ([^ ]*)', 1) AS client_identd,
  regexp_extract(log_line, '^[^ ]* [^ ]* ([^ ]*)', 1) AS user_id,
  regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1) AS timestamp,
  regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[.*\\] "([^"]*)"', 1) AS request,
  regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[.*\\] "[^"]*" ([0-9]*)', 1) AS status_code,
  regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[.*\\] "[^"]*" [0-9]* ([0-9]*)', 1) AS size,
  regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[.*\\] "[^"]*" [0-9]* [0-9]* "([^"]*)"', 1) AS referer,
  regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[.*\\] "[^"]*" [0-9]* [0-9]* "[^"]*" "([^"]*)"', 1) AS user_agent,
  regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[.*\\] "([^"]*)"', 1), '^([^ ]*)', 1) AS method,
  regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[.*\\] "([^"]*)"', 1), '^[^ ]* ([^ ]*)', 1) AS endpoint,
  regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[.*\\] "([^"]*)"', 1), '^[^ ]* [^ ]* ([^ ]*)', 1) AS protocol,
  regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^([0-9]*)', 1) AS day,
  regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/([^/]*)', 1) AS month,
  regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/[^/]*/([0-9]*)', 1) AS year,
  regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/[^/]*/[0-9]*:([0-9]*)', 1) AS hour,
  regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/[^/]*/[0-9]*:[0-9]*:([0-9]*)', 1) AS minute,
  regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/[^/]*/[0-9]*:[0-9]*:[0-9]*:([0-9]*)', 1) AS second,
  concat(
    regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/[^/]*/([0-9]*)', 1),
    '-',
    CASE 
      WHEN regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/([^/]*)', 1) = 'Jan' THEN '01'
      WHEN regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/([^/]*)', 1) = 'Feb' THEN '02'
      WHEN regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/([^/]*)', 1) = 'Mar' THEN '03'
      WHEN regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/([^/]*)', 1) = 'Apr' THEN '04'
      WHEN regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/([^/]*)', 1) = 'May' THEN '05'
      WHEN regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/([^/]*)', 1) = 'Jun' THEN '06'
      WHEN regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/([^/]*)', 1) = 'Jul' THEN '07'
      WHEN regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/([^/]*)', 1) = 'Aug' THEN '08'
      WHEN regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/([^/]*)', 1) = 'Sep' THEN '09'
      WHEN regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/([^/]*)', 1) = 'Oct' THEN '10'
      WHEN regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/([^/]*)', 1) = 'Nov' THEN '11'
      WHEN regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^[0-9]*/([^/]*)', 1) = 'Dec' THEN '12'
      ELSE '00'
    END,
    '-',
    regexp_extract(regexp_extract(log_line, '^[^ ]* [^ ]* [^ ]* \\[([^\\]]*)\\]', 1), '^([0-9]*)', 1)
  ) AS date_ymd
FROM raw_logs;

-- Insert pour charger les données analysées dans la table partitionnée
-- Activer le partitionnement dynamique
SET hive.exec.dynamic.partition=true;
SET hive.exec.dynamic.partition.mode=nonstrict;

-- Requête d'insertion pour charger les données de la vue dans la table partitionnée
INSERT OVERWRITE TABLE web_logs PARTITION(date_ymd)
SELECT
  ip,
  client_identd,
  user_id,
  timestamp,
  request,
  CAST(status_code AS INT),
  CAST(size AS BIGINT),
  referer,
  user_agent,
  method,
  endpoint,
  protocol,
  CAST(day AS INT),
  month,
  CAST(year AS INT),
  CAST(hour AS INT),
  CAST(minute AS INT),
  CAST(second AS INT),
  date_ymd
FROM parsed_logs;