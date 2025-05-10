# Sujet 5 : Migration de Données Relationnelles vers Hadoop avec Sqoop

## Description du Projet

Ce projet vise à développer un pipeline pour migrer des données d'une base de données relationnelle (MySQL) vers un environnement Big Data (HDFS) en utilisant Apache Sqoop. Il démontre l'interopérabilité entre les bases de données traditionnelles et les systèmes de fichiers distribués, avec une structuration ultérieure des données dans Hive pour faciliter les requêtes SQL.

## Objectifs

* Configurer une base de données MySQL avec des données transactionnelles.
* Utiliser Sqoop pour importer ces données dans HDFS.
* Créer des tables externes Hive par-dessus les données HDFS pour permettre leur interrogation via SQL.
* Effectuer une analyse simple pour valider la migration et l'accessibilité des données dans Hive.

## Technologies Utilisées

* **Base de Données Relationnelle**: MySQL
* **Outil de Migration de Données**: Apache Sqoop 1.4.7
* **Système de Fichiers Distribué**: Hadoop HDFS (Hadoop 3.3.4)
* **Data Warehouse & Requêtage**: Apache Hive 3.1.3 (utilisant Hive-on-MR)
* **Orchestration de Conteneurs**: Docker & Docker Compose

## Structure du Projet

```
projet-migration-mysql-hadoop/
├── docker-compose.yml        # Fichier Docker Compose pour orchestrer les services
├── hadoop/                   # Configurations et Dockerfile pour Hadoop (Namenode, Datanode)
│   ├── configs/
│   └── Dockerfile
├── hadoop.env                # Variables d'environnement pour Hadoop
├── hive/                     # Dockerfile et configurations pour Hive (HiveServer2, Metastore)
│   ├── Dockerfile
│   └── hive-site.xml
├── mysql/                    # Dockerfile et script d'initialisation pour MySQL
│   ├── Dockerfile
│   └── init.sql
├── README.md                 # Ce fichier
├── scripts/                  # Scripts pour l'importation, la création de tables Hive et l'analyse
│   ├── analyse_data.hql
│   ├── create_hive_tables.hql
│   ├── import_data.sh
│   └── run_beeline_with_retry.sh # (Utilisé potentiellement pour l'automatisation de la création des tables Hive)
└── sqoop/                    # Dockerfile et script d'entrée pour Sqoop
    ├── Dockerfile
    └── entrypoint.sh
```

## Prérequis

* Docker installé et en cours d'exécution.
* Docker Compose installé.

## Instructions de Configuration et d'Exécution

### 1. Démarrer l'Environnement Docker

Placez-vous à la racine du projet (`datalake-logs-project`) et exécutez :

```bash
docker-compose up -d
```

Cette commande va construire les images Docker pour chaque service (si elles ne sont pas déjà construites) et démarrer tous les conteneurs nécessaires (Namenode, Datanode, MySQL, Hive Server, Sqoop).

Attendez quelques instants que tous les services s'initialisent, en particulier HDFS et HiveServer2. Le script `run_beeline_with_retry.sh` (s'il est utilisé par un service au démarrage) ou le `entrypoint.sh` de Sqoop contient des logiques d'attente pour la disponibilité des services.

### 2. Exécuter le Script d'Importation Sqoop

Une fois les conteneurs démarrés, exécutez le script d'importation Sqoop pour migrer les données de MySQL vers HDFS. Ce script importe les tables `clients`, `produits`, `ventes`, et `details_ventes` en tant que fichiers texte délimités par des virgules.

```bash
docker exec -it sqoop bash -c "bash /scripts/import_data.sh"
```

Ce script est configuré pour supprimer les répertoires cibles existants dans HDFS avant chaque importation pour garantir un import frais. Il utilise des options robustes pour la gestion des colonnes, des types Java et des délimiteurs.

### 3. Créer les Tables Externes Hive

Après l'importation des données dans HDFS, créez les tables externes Hive qui pointent vers ces données.

```bash
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000 -f /scripts/create_hive_tables.hql
```

Ce script crée la base de données `retail_analytics` (si elle n'existe pas) et définit les tables `clients`, `produits`, `ventes`, et `details_ventes` comme des tables externes stockées en tant que `TEXTFILE`, avec des propriétés pour gérer correctement les délimiteurs et les valeurs nulles (`\N`).

### 4. Effectuer une Analyse Simple pour Valider la Migration

Pour valider que les données sont accessibles via Hive, exécutez le script `analyse_data.hql` qui contient des requêtes `SELECT` simples.

```bash
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000 -f /scripts/analyse_data.hql
```

Ce script est actuellement configuré pour exécuter `SELECT * FROM <tablename> LIMIT 5;` pour chaque table, affichant les premières lignes pour confirmer leur contenu.

## Résultats Attendus et Validation

* **Importation Sqoop**: Le script `import_data.sh` doit se terminer avec un message "Importation des données terminée avec succès!" et les logs Sqoop pour chaque table doivent indiquer un import réussi (par exemple, "Retrieved X records").
* **Création des Tables Hive**: Le script `create_hive_tables.hql` doit s'exécuter sans erreurs, avec des messages "OK" pour chaque instruction `CREATE TABLE`.
* **Analyse Simple Hive**: Le script `analyse_data.hql` (avec les `SELECT * ... LIMIT 5`) doit afficher les 5 premières lignes de chaque table, confirmant que les données sont correctement structurées et accessibles via Hive.

## Problèmes Connus et Limitations

* **Analyse Complexe Hive via MapReduce**: Lors des tentatives d'exécution de requêtes Hive plus complexes (impliquant des jointures et des agrégations sur l'ensemble des données, comme dans la version originale du fichier `analyse_data.hql`), l'environnement Hive-on-MapReduce (tel que configuré dans cette configuration Docker locale) échoue systématiquement avec une erreur générique `FAILED: Execution Error, return code 2 from org.apache.hadoop.hive.ql.exec.mr.MapRedTask`.
  * Ce problème persiste malgré de nombreuses tentatives de configuration des propriétés Sqoop (gestion des délimiteurs, NULLs, types de colonnes) et des propriétés des tables Hive (SerDe, format de null, `textinputformat.ignore.errors`).
  * Les données brutes dans HDFS semblent correctes, et les simples `SELECT * LIMIT n` fonctionnent, suggérant que le problème réside dans l'exécution des tâches MapReduce par Hive dans cet environnement spécifique.
  * La dépréciation de Hive-on-MR est un facteur à considérer ; des moteurs d'exécution plus modernes comme Tez ou Spark pourraient ne pas présenter ces problèmes.
* **Support ORC par Sqoop**: Les tentatives d'utilisation de Sqoop pour importer directement des fichiers au format ORC (`--as-orcfile`) ont échoué en raison d'arguments non reconnus ou de dépendances manquantes (potentiellement liées à HCatalog) dans la version/configuration de Sqoop 1.4.7 utilisée dans ce projet.

## Améliorations Possibles

* **Résoudre le Problème Hive-on-MR**: Un débogage plus approfondi de l'environnement d'exécution Hadoop/Hive local, ou la migration vers un moteur d'exécution plus récent (Tez, Spark) pour Hive, pourrait résoudre les échecs des requêtes analytiques complexes.
* **Activer le Support ORC dans Sqoop**: Configurer correctement HCatalog et les dépendances nécessaires dans le conteneur Sqoop pour permettre des imports directs au format ORC, ce qui est généralement plus performant et robuste pour l'analytique.
* **Automatisation Complète**: Intégrer le script `run_beeline_with_retry.sh` dans le `docker-compose.yml` (par exemple via le `entrypoint` du service Sqoop ou d'un service dédié à l'initialisation de Hive) pour automatiser la création des tables Hive après le démarrage des services.
* **Sécurité**: Supprimer les mots de passe en clair des scripts et utiliser des mécanismes plus sécurisés pour la gestion des identifiants (par exemple, des fichiers de mots de passe Sqoop, des coffres-forts de secrets).
