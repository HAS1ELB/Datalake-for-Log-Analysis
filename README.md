# Datalake pour l'Analyse des Données de Logs

Ce projet crée un datalake pour stocker et analyser les logs d'une application web en utilisant HDFS (Hadoop Distributed File System) et Hive.

## Architecture du Projet

- **Collecte de logs**: Simulation de logs d'une application web avec un script Python
- **Stockage**: HDFS pour le stockage distribué des données brutes
- **Traitement**: Hive pour l'analyse SQL des logs
- **Infrastructure**: Environnement Hadoop complet déployé via Docker

## Prérequis

- Docker et Docker Compose
- Python 3.x (pour la génération de logs)
- Au moins 8GB de RAM disponible pour exécuter l'environnement Hadoop

## Installation et démarrage

1. Clonez ce dépôt:
   ```bash
   git clone <URL du dépôt>
   cd datalake-logs-project
   ```

2. Démarrez l'environnement Hadoop avec Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Vérifiez que tous les services sont en cours d'exécution:
   ```bash
   docker-compose ps
   ```

## Génération et chargement des logs

1. Exécutez le script pour générer des logs d'application web:
   ```bash
   chmod +x upload_logs_to_hdfs.sh
   ./upload_logs_to_hdfs.sh
   ```

Ce script va:
- Générer des logs d'application web synthétiques
- Créer les répertoires nécessaires dans HDFS
- Charger les logs dans HDFS
- Créer les tables Hive et les remplir avec les données analysées

## Structure des données

Le script Hive crée deux structures principales:

1. **raw_logs**: Table externe Hive qui pointe vers les fichiers de logs bruts dans HDFS
2. **web_logs**: Table Hive optimisée et partitionnée qui stocke les données analysées

## Analyse des logs

Utilisez les requêtes d'exemple pour analyser les données de logs:

```bash
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000 -f /opt/data/sample_queries.hql
```

Ou connectez-vous à Hive pour exécuter vos propres requêtes:

```bash
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000
```

Puis exécutez des requêtes SQL:

```sql
USE logs_analysis;
SELECT * FROM web_logs LIMIT 10;
```

## Exemples d'analyses disponibles

Les requêtes d'exemple incluses permettent de:

1. Identifier les URL les plus visitées
2. Analyser la distribution des codes de statut HTTP
3. Visualiser le trafic par heure
4. Analyser les requêtes par jour
5. Identifier les adresses IP générant le plus de trafic
6. Analyser les navigateurs et systèmes d'exploitation utilisés
7. Examiner les méthodes HTTP et tailles de réponses
8. Analyser les sources de trafic (référents)

## Arrêt de l'environnement

Pour arrêter tous les services:

```bash
docker-compose down
```

Pour supprimer complètement l'environnement (y compris les volumes):

```bash
docker-compose down -v
```

## Personnalisation

- Modifiez `generate_logs.py` pour ajuster le format et le volume des logs générés
- Personnalisez `prepare_hive_tables.hql` pour modifier la structure des tables Hive
- Créez vos propres requêtes d'analyse en vous inspirant de `sample_queries.hql`

## Étendre le projet

Voici quelques idées pour étendre ce projet:

1. Ajoutez un pipeline d'ingestion continue des logs avec Flume ou Kafka
2. Intégrez Spark pour des analyses plus complexes
3. Ajoutez une visualisation avec Superset ou Tableau
4. Implémentez une détection d'anomalies sur les logs
5. Créez un tableau de bord pour surveiller le trafic en temps réel