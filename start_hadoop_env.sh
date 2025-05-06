#!/bin/bash

# Ce script configure et démarre l'environnement Hadoop+Hive pour l'analyse de logs

echo "Démarrage de l'environnement Hadoop et Hive..."
docker-compose up -d

echo "Attente du démarrage complet des services..."
# Attendre 30 secondes pour que les services démarrent correctement
sleep 30

echo "Vérification des services..."
docker-compose ps

echo "Configuration des volumes pour les scripts et données..."
# Création du répertoire pour les données montées
mkdir -p data

# Copie des scripts et données dans le répertoire monté
cp generate_logs.py data/
cp prepare_hive_tables.hql data/
cp sample_queries.hql data/
cp web_logs.log data/ 2>/dev/null || echo "Aucun fichier de logs existant, va être généré."

echo "L'environnement est prêt. Vous pouvez maintenant exécuter upload_logs_to_hdfs.sh"
echo "Pour générer les logs et les charger dans HDFS."