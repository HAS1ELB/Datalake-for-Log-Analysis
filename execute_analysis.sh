#!/bin/bash

# Ce script exécute des requêtes d'analyse sur les données de logs chargées dans Hive

echo "Exécution des requêtes d'analyse Hive..."
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000 -f /opt/data/sample_queries.hql

echo "Exemple de quelques requêtes spécifiques..."

echo "1. Top 10 des URLs les plus visitées:"
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000 -e "USE logs_analysis; SELECT endpoint, COUNT(*) as visit_count FROM web_logs GROUP BY endpoint ORDER BY visit_count DESC LIMIT 10;"

echo "2. Distribution des codes de statut HTTP:"
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000 -e "USE logs_analysis; SELECT status_code, COUNT(*) as count FROM web_logs GROUP BY status_code ORDER BY count DESC;"

echo "3. Analyse du trafic par heure:"
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000 -e "USE logs_analysis; SELECT hour, COUNT(*) as request_count FROM web_logs GROUP BY hour ORDER BY hour;"

echo "Analyse terminée. Vous pouvez exécuter d'autres requêtes directement via beeline."