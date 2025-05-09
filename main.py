#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script principal pour orchestrer le processus de collecte et d'analyse des logs.
"""

import os
import sys
import time
import logging
import argparse
import subprocess

# Import des modules du projet
from scripts.log_collector import LogCollector
from scripts.log_processor import LogProcessor
from scripts.create_hive_tables import HiveTableCreator

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_hdfs(host="namenode", port="9000", max_retries=30, retry_interval=10):
    """Attend que HDFS soit disponible."""
    import pyhdfs
    
    logger.info(f"Attente de la disponibilité de HDFS ({host}:{port})...")
    
    retries = 0
    while retries < max_retries:
        try:
            client = pyhdfs.HdfsClient(hosts=f"{host}:{port}", user_name="root")
            client.list_status('/')  # Test simple pour vérifier si HDFS est opérationnel
            logger.info("HDFS disponible.")
            return True
        except Exception as e:
            retries += 1
            logger.info(f"Tentative {retries}/{max_retries} échouée: {str(e)}")
            time.sleep(retry_interval)
    
    logger.error(f"HDFS n'est pas disponible après {max_retries} tentatives.")
    return False

def main():
    """Fonction principale d'orchestration."""
    parser = argparse.ArgumentParser(description='Datalake pour analyse de logs web')
    parser.add_argument('--log-file', type=str, required=True, help='Chemin vers le fichier de logs à traiter')
    parser.add_argument('--hdfs-host', type=str, default='namenode', help='Hôte HDFS (défaut: namenode)')
    parser.add_argument('--hdfs-port', type=str, default='9000', help='Port HDFS (défaut: 9000)')
    parser.add_argument('--hive-host', type=str, default='hive-server', help='Hôte Hive (défaut: hive-server)')
    parser.add_argument('--hive-port', type=int, default=10000, help='Port Hive (défaut: 10000)')
    parser.add_argument('--database', type=str, default='weblogs', help='Nom de la base de données Hive (défaut: weblogs)')
    parser.add_argument('--skip-collect', action='store_true', help='Ignorer la collecte des logs')
    parser.add_argument('--skip-process', action='store_true', help='Ignorer le traitement des logs')
    parser.add_argument('--skip-hive', action='store_true', help='Ignorer la création des tables Hive')
    parser.add_argument('--run-queries', action='store_true', help='Exécuter les requêtes analytiques')
    
    args = parser.parse_args()
    
    # Attendre que les services soient disponibles
    if not wait_for_hdfs(args.hdfs_host, args.hdfs_port):
        logger.error("Impossible de se connecter à HDFS. Arrêt du programme.")
        sys.exit(1)
    
    hdfs_raw_file = None
    hdfs_processed_file = None
    
    # Étape 1: Collecte des logs
    if not args.skip_collect:
        logger.info("=== ÉTAPE 1: COLLECTE DES LOGS ===")
        collector = LogCollector(args.hdfs_host, args.hdfs_port)
        hdfs_raw_file = collector.collect_logs(args.log_file)
        
        if not hdfs_raw_file:
            logger.error("La collecte des logs a échoué. Arrêt du programme.")
            sys.exit(1)
    
    # Étape 2: Traitement des logs
    if not args.skip_process:
        logger.info("=== ÉTAPE 2: TRAITEMENT DES LOGS ===")
        processor = LogProcessor(args.hdfs_host, args.hdfs_port)
        
        # Si nous avons ignoré la collecte, utiliser le dernier fichier disponible
        if not hdfs_raw_file:
            # Trouver le dernier fichier brut dans HDFS
            import pyhdfs
            client = pyhdfs.HdfsClient(hosts=f"{args.hdfs_host}:{args.hdfs_port}", user_name="root")
            if client.exists('/logs/raw'):
                files = client.list_status('/logs/raw')
                if files:
                    # Trier par date de modification (plus récent en premier)
                    files.sort(key=lambda x: x.modificationTime, reverse=True)
                    hdfs_raw_file = f"/logs/raw/{files[0].pathSuffix}"
                    logger.info(f"Utilisation du fichier brut le plus récent: {hdfs_raw_file}")
                else:
                    logger.error("Aucun fichier brut trouvé dans HDFS. Arrêt du programme.")
                    sys.exit(1)
            else:
                logger.error("Le répertoire des logs bruts n'existe pas dans HDFS. Arrêt du programme.")
                sys.exit(1)
        
        hdfs_processed_file = processor.process_logs(hdfs_raw_file)
        
        if not hdfs_processed_file:
            logger.error("Le traitement des logs a échoué. Arrêt du programme.")
            sys.exit(1)
    
    # Étape 3: Création des tables Hive
    if not args.skip_hive:
        logger.info("=== ÉTAPE 3: CRÉATION DES TABLES HIVE ===")
        creator = HiveTableCreator(args.hive_host, args.hive_port)
        creator.create_all_tables(args.database)
        creator.close()
    
    # Étape 4: Exécution des requêtes analytiques (optionnel)
    if args.run_queries:
        logger.info("=== ÉTAPE 4: EXÉCUTION DES REQUÊTES ANALYTIQUES ===")
        run_analytics(args.hive_host, args.hive_port, args.database)
    
    logger.info("Traitement terminé avec succès.")

def run_analytics(hive_host, hive_port, database):
    """Exécute plusieurs requêtes analytiques sur les données de logs."""
    from pyhive import hive
    
    try:
        conn = hive.Connection(host=hive_host, port=hive_port)
        cursor = conn.cursor()
        
        # Utiliser la base de données spécifiée
        cursor.execute(f"USE {database}")
        
        # Requête 1: Nombre de requêtes par statut HTTP
        logger.info("Analyse: Nombre de requêtes par statut HTTP")
        cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM processed_logs
        GROUP BY status
        ORDER BY count DESC
        """)
        results = cursor.fetchall()
        for row in results:
            logger.info(f"  Statut {row[0]}: {row[1]} requêtes")
        
        # Requête 2: Top 10 des URLs les plus demandées
        logger.info("Analyse: Top 10 des URLs les plus demandées")
        cursor.execute("""
        SELECT url, COUNT(*) as count
        FROM processed_logs
        GROUP BY url
        ORDER BY count DESC
        LIMIT 10
        """)
        results = cursor.fetchall()
        for row in results:
            logger.info(f"  URL '{row[0]}': {row[1]} requêtes")
        
        # Requête 3: Répartition des navigateurs utilisés
        logger.info("Analyse: Répartition des navigateurs utilisés")
        cursor.execute("""
        SELECT browser, COUNT(*) as count
        FROM web_analytics
        GROUP BY browser
        ORDER BY count DESC
        """)
        results = cursor.fetchall()
        for row in results:
            logger.info(f"  {row[0]}: {row[1]} requêtes")
        
        # Requête 4: Trafic par heure de la journée
        logger.info("Analyse: Trafic par heure de la journée")
        cursor.execute("""
        SELECT hour, COUNT(*) as count
        FROM web_analytics
        GROUP BY hour
        ORDER BY hour
        """)
        results = cursor.fetchall()
        for row in results:
            logger.info(f"  {row[0]:02d}:00 - {row[0]:02d}:59: {row[1]} requêtes")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution des requêtes analytiques: {str(e)}")

if __name__ == "__main__":
    main()