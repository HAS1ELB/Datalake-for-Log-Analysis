-- Utilisation de la base de données
USE logs_analysis;

-- Requête 1: Top 10 des URLs les plus visitées
SELECT endpoint, COUNT(*) as visit_count
FROM web_logs
GROUP BY endpoint
ORDER BY visit_count DESC
LIMIT 10;

-- Requête 2: Distribution des codes de statut HTTP
SELECT status_code, COUNT(*) as count
FROM web_logs
GROUP BY status_code
ORDER BY count DESC;

-- Requête 3: Analyse du trafic par heure
SELECT hour, COUNT(*) as request_count
FROM web_logs
GROUP BY hour
ORDER BY hour;

-- Requête 4: Requêtes par jour
SELECT date_ymd, COUNT(*) as daily_requests
FROM web_logs
GROUP BY date_ymd
ORDER BY date_ymd;

-- Requête 5: Top 10 des adresses IP ayant généré le plus de trafic
SELECT ip, COUNT(*) as request_count
FROM web_logs
GROUP BY ip
ORDER BY request_count DESC
LIMIT 10;

-- Requête 6: Les navigateurs les plus utilisés (extraction à partir du user-agent)
SELECT 
  CASE
    WHEN LOWER(user_agent) LIKE '%chrome%' THEN 'Chrome'
    WHEN LOWER(user_agent) LIKE '%firefox%' THEN 'Firefox'
    WHEN LOWER(user_agent) LIKE '%safari%' AND NOT LOWER(user_agent) LIKE '%chrome%' THEN 'Safari'
    WHEN LOWER(user_agent) LIKE '%edge%' THEN 'Edge'
    WHEN LOWER(user_agent) LIKE '%opera%' OR LOWER(user_agent) LIKE '%opr%' THEN 'Opera'
    WHEN LOWER(user_agent) LIKE '%msie%' OR LOWER(user_agent) LIKE '%trident%' THEN 'Internet Explorer'
    ELSE 'Other'
  END AS browser,
  COUNT(*) as count
FROM web_logs
GROUP BY
  CASE
    WHEN LOWER(user_agent) LIKE '%chrome%' THEN 'Chrome'
    WHEN LOWER(user_agent) LIKE '%firefox%' THEN 'Firefox'
    WHEN LOWER(user_agent) LIKE '%safari%' AND NOT LOWER(user_agent) LIKE '%chrome%' THEN 'Safari'
    WHEN LOWER(user_agent) LIKE '%edge%' THEN 'Edge'
    WHEN LOWER(user_agent) LIKE '%opera%' OR LOWER(user_agent) LIKE '%opr%' THEN 'Opera'
    WHEN LOWER(user_agent) LIKE '%msie%' OR LOWER(user_agent) LIKE '%trident%' THEN 'Internet Explorer'
    ELSE 'Other'
  END
ORDER BY count DESC;

-- Requête 7: Les systèmes d'exploitation utilisés
SELECT 
  CASE
    WHEN LOWER(user_agent) LIKE '%windows%' THEN 'Windows'
    WHEN LOWER(user_agent) LIKE '%macintosh%' OR LOWER(user_agent) LIKE '%mac os%' THEN 'MacOS'
    WHEN LOWER(user_agent) LIKE '%linux%' THEN 'Linux'
    WHEN LOWER(user_agent) LIKE '%android%' THEN 'Android'
    WHEN LOWER(user_agent) LIKE '%iphone%' OR LOWER(user_agent) LIKE '%ipad%' THEN 'iOS'
    ELSE 'Other'
  END AS os,
  COUNT(*) as count
FROM web_logs
GROUP BY
  CASE
    WHEN LOWER(user_agent) LIKE '%windows%' THEN 'Windows'
    WHEN LOWER(user_agent) LIKE '%macintosh%' OR LOWER(user_agent) LIKE '%mac os%' THEN 'MacOS'
    WHEN LOWER(user_agent) LIKE '%linux%' THEN 'Linux'
    WHEN LOWER(user_agent) LIKE '%android%' THEN 'Android'
    WHEN LOWER(user_agent) LIKE '%iphone%' OR LOWER(user_agent) LIKE '%ipad%' THEN 'iOS'
    ELSE 'Other'
  END
ORDER BY count DESC;

-- Requête 8: Analyse des méthodes HTTP utilisées
SELECT method, COUNT(*) as count
FROM web_logs
GROUP BY method
ORDER BY count DESC;

-- Requête 9: Taille moyenne des réponses par endpoint (en octets)
SELECT endpoint, AVG(size) as avg_size
FROM web_logs
GROUP BY endpoint
ORDER BY avg_size DESC
LIMIT 15;

-- Requête 10: Répartition des sites référents
SELECT 
  CASE
    WHEN referer = '-' THEN 'Direct Traffic'
    WHEN referer LIKE '%google%' THEN 'Google'
    WHEN referer LIKE '%bing%' THEN 'Bing'
    WHEN referer LIKE '%facebook%' THEN 'Facebook'
    WHEN referer LIKE '%twitter%' THEN 'Twitter'
    WHEN referer LIKE '%instagram%' THEN 'Instagram'
    WHEN referer LIKE '%linkedin%' THEN 'LinkedIn'
    ELSE 'Other'
  END AS referer_source,
  COUNT(*) as count
FROM web_logs
GROUP BY
  CASE
    WHEN referer = '-' THEN 'Direct Traffic'
    WHEN referer LIKE '%google%' THEN 'Google'
    WHEN referer LIKE '%bing%' THEN 'Bing'
    WHEN referer LIKE '%facebook%' THEN 'Facebook'
    WHEN referer LIKE '%twitter%' THEN 'Twitter'
    WHEN referer LIKE '%instagram%' THEN 'Instagram'
    WHEN referer LIKE '%linkedin%' THEN 'LinkedIn'
    ELSE 'Other'
  END
ORDER BY count DESC;