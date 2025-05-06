# Rapport : Implémentation d'un Datalake pour l'Analyse des Logs avec HDFS et Hive

## Introduction

Dans le cadre de ce projet, nous avons mis en place un datalake pour stocker et analyser les données de logs d'une application web. L'objectif principal était de collecter les logs, les stocker dans une architecture distribuée (HDFS) et mettre en place une interface d'interrogation SQL (Hive) pour faciliter leur analyse.

Ce rapport détaille l'architecture mise en place, les technologies utilisées, les défis rencontrés et les résultats obtenus.

## Architecture du Projet

Notre solution repose sur une architecture en couches, typique des projets de Big Data :

1. **Couche de collecte** : Simulation de logs d'application web (dans un scénario réel, cette couche pourrait utiliser des outils comme Flume ou Kafka)
2. **Couche de stockage** : HDFS (Hadoop Distributed File System)
3. **Couche de traitement** : Hive pour l'analyse SQL des données
4. **Couche d'application** : Scripts d'analyse et requêtes SQL prédéfinies

### Schéma de l'architecture

```
Génération de logs → Stockage dans HDFS → Traitement avec Hive → Analyse SQL
```

## Technologies Utilisées

### HDFS (Hadoop Distributed File System)

HDFS est le système de fichiers distribué qui sert de fondation à notre datalake. Ses principales caractéristiques qui ont motivé notre choix :

- **Tolérance aux pannes** : Les données sont répliquées sur plusieurs nœuds
- **Scalabilité horizontale** : Possibilité d'ajouter des nœuds pour augmenter la capacité
- **Optimisation pour les gros fichiers** : Parfait pour le stockage de logs volumineux
- **Haute disponibilité** : Architecture avec NameNode et DataNodes

Dans notre implémentation, HDFS stocke les logs bruts dans un format texte.

### Hive

Hive est notre couche d'abstraction SQL au-dessus d'HDFS, permettant :

- **Requêtes SQL sur des données non structurées** : Transformation des logs en format tabulaire
- **Partitionnement des données** : Organisation des logs par date pour optimiser les requêtes
- **Schéma à la lecture** : Flexibilité pour adapter le schéma aux besoins d'analyse
- **Intégration avec l'écosystème Hadoop** : Compatibilité avec d'autres outils comme Spark

Nous utilisons Hive avec un metastore PostgreSQL pour stocker les métadonnées des tables.

## Implémentation

### 1. Collecte des Logs

Pour simuler la collecte de logs d'une application web, nous avons développé un script Python (`generate_logs.py`) qui génère des logs au format Apache Combined Log Format. Ce format est l'un des standards de l'industrie et contient des informations comme :

- Adresse IP du client
- Identifiant de l'utilisateur
- Horodatage
- Méthode HTTP, URL et protocole
- Code de statut HTTP
- Taille de la réponse
- Référent
- User-Agent

Exemple de log généré :
```
192.168.1.42 - - [04/May/2025:15:34:22 +0000] "GET /products HTTP/1.1" 200 8643 "https://www.google.com/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
```

### 2. Stockage dans HDFS

Les logs générés sont ensuite chargés dans HDFS à l'aide du script `upload_logs_to_hdfs.sh`. Ce script :

1. Crée le répertoire `/data/raw_logs` dans HDFS
2. Charge les fichiers de logs dans ce répertoire

Cette approche permet de stocker les données brutes de manière distribuée et résiliente.

### 3. Traitement avec Hive

Une fois les logs stockés dans HDFS, nous utilisons Hive pour les structurer et les analyser. Le script `prepare_hive_tables.hql` :

1. Crée une base de données `logs_analysis`
2. Crée une table externe `raw_logs` qui pointe vers les fichiers bruts dans HDFS
3. Définit une vue `parsed_logs` qui utilise des expressions régulières pour extraire les différents champs des logs
4. Crée une table optimisée `web_logs` qui stocke les données analysées dans un format ORC partitionné par date

L'utilisation d'expressions régulières permet d'extraire efficacement les différentes informations des logs selon le format standard Apache.

### 4. Analyse des Logs

Une fois les données structurées dans Hive, nous pouvons effectuer diverses analyses à l'aide de requêtes SQL. Le script `sample_queries.hql` contient des exemples de requêtes pour :

- Identifier les URLs les plus visitées
- Analyser la distribution des codes de statut HTTP
- Visualiser le trafic par heure/jour
- Analyser la répartition des navigateurs et systèmes d'exploitation
- Examiner les sources de trafic (référents)

## Défis et Solutions

### 1. Parsing des logs

**Défi** : Les logs web ont un format complexe qui nécessite un parsing précis.

**Solution** : Utilisation d'expressions régulières dans Hive pour extraire les différentes composantes des logs. Création d'une vue intermédiaire pour valider le parsing avant de charger les données dans la table finale.

### 2. Optimisation des performances

**Défi** : Les requêtes sur de grandes quantités de logs peuvent être lentes.

**Solution** : 
- Partitionnement des données par date
- Stockage au format ORC (Optimized Row Columnar) qui offre une compression efficace et des performances de lecture améliorées
- Création de colonnes dérivées pour faciliter les requêtes fréquentes

### 3. Environnement de développement

**Défi** : Mise en place d'un environnement Hadoop complet pour le développement.

**Solution** : Utilisation de Docker Compose pour créer un cluster Hadoop virtualisé avec tous les composants nécessaires (HDFS, YARN, Hive, PostgreSQL).

## Résultats et Analyses

Après avoir chargé les logs dans notre datalake, nous avons pu effectuer diverses analyses qui seraient utiles dans un contexte réel :

### Analyse du trafic par URL

Les requêtes SQL nous ont permis d'identifier les pages les plus visitées, ce qui donne des indications précieuses sur les centres d'intérêt des utilisateurs.

### Analyse des erreurs

L'analyse des codes de statut HTTP a permis de détecter les erreurs (codes 4xx et 5xx) et d'identifier les pages problématiques.

### Analyse temporelle

La visualisation du trafic par heure a révélé des patterns d'utilisation avec des pics à certaines heures de la journée, information cruciale pour le dimensionnement des ressources.

### Analyse des utilisateurs

L'extraction d'informations des user-agents a permis de comprendre quels navigateurs et systèmes d'exploitation sont les plus utilisés, ce qui guide les décisions de développement et de compatibilité.

## Extensions Possibles

Ce projet pourrait être étendu de plusieurs façons :

1. **Ingestion en temps réel** : Utilisation de Kafka et Flume pour collecter les logs en temps réel
2. **Analyses avancées avec Spark** : Intégration de Spark pour des analyses plus complexes et du machine learning
3. **Visualisation** : Connexion à des outils comme Superset, Tableau ou Grafana pour créer des tableaux de bord
4. **Alerting** : Mise en place d'alertes basées sur des conditions spécifiques (ex: augmentation soudaine d'erreurs)
5. **Détection d'anomalies** : Implémentation d'algorithmes de détection d'anomalies pour identifier les comportements suspects

## Conclusion

L'implémentation d'un datalake pour l'analyse des logs avec HDFS et Hive fournit une solution robuste et flexible pour stocker et analyser de grandes quantités de données de logs. Cette architecture permet non seulement d'analyser les tendances historiques, mais aussi de poser les bases pour des analyses plus avancées et même prédictives.

La solution développée répond aux objectifs initiaux du projet en permettant :
- La collecte et le stockage efficace des logs
- L'analyse SQL simplifiée de ces données
- L'extraction d'insights précieux pour améliorer les performances et l'expérience utilisateur

Dans un contexte d'entreprise réel, cette infrastructure pourrait être utilisée pour optimiser les performances des applications, détecter les problèmes de sécurité, comprendre le comportement des utilisateurs et guider les décisions stratégiques basées sur les données.