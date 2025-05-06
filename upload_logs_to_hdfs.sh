#!/bin/bash

# Ce script télécharge les logs générés vers HDFS et exécute le script Hive pour analyser les logs

echo "Génération des logs d'application web..."
python3 generate_logs.py

echo "Création des répertoires HDFS nécessaires..."
docker exec -it namenode hdfs dfs -mkdir -p /data/raw_logs

echo "Upload des logs vers HDFS..."
docker cp web_logs.log namenode:/tmp/web_logs.log
docker exec -it namenode hadoop fs -put /tmp/web_logs.log /data/web_logs.log

echo "Exécution des requêtes Hive pour créer et charger les tables..."
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000 -f prepare_hive_tables.hql

echo "Vérification des données chargées..."
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000 -e "SELECT COUNT(*) FROM logs_analysis.web_logs;"

echo "Processus terminé. Les logs sont maintenant chargés dans Hive et prêts pour l'analyse."