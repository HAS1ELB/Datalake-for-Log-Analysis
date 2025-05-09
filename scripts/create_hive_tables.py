#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour créer les tables Hive et charger les données.
"""

import os
import logging
import argparse
from pyhive import hive
import time

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HiveTableCreator:
    """Crée et gère les tables Hive pour l'analyse des logs."""
    
    def __init__(self, hive_host="hive-server", hive_port=10000):
        """Initialisation avec les paramètres de connexion Hive."""
        self.hive_host = hive_host
        self.hive_port = hive_port
        self.conn = None
        
        # Attendre que Hive soit prêt
        self._wait_for_hive()
        
        # Créer la connexion Hive
        self._connect_to_hive()
    
    def _wait_for_hive(self, max_retries=30, retry_interval=10):
        """Attend que le serveur Hive soit disponible."""
        logger.info(f"Attente de la disponibilité du serveur Hive ({self.hive_host}:{self.hive_port})...")
        
        retries = 0
        while retries < max_retries:
            try:
                # Tentative de connexion
                conn = hive.Connection(host=self.hive_host, port=self.hive_port)
                cursor = conn.cursor()
                cursor.execute("SHOW DATABASES")
                cursor.fetchall()  # Récupérer les résultats pour s'assurer que la connexion fonctionne
                conn.close()
                logger.info("Serveur Hive disponible.")
                return True
            except Exception as e:
                retries += 1
                logger.info(f"Tentative {retries}/{max_retries} échouée: {str(e)}")
                time.sleep(retry_interval)
        
        logger.error(f"Le serveur Hive n'est pas disponible après {max_retries} tentatives.")
        return False
    
    def _connect_to_hive(self):
        """Établit une connexion avec le serveur Hive."""
        try:
            logger.info(f"Connexion au serveur Hive ({self.hive_host}:{self.hive_port})...")
            self.conn = hive.Connection(host=self.hive_host, port=self.hive_port)
            logger.info("Connecté au serveur Hive.")
        except Exception as e:
            logger.error(f"Erreur de connexion au serveur Hive: {str(e)}")
            raise
    
    def _execute_query(self, query):
        """Exécute une requête Hive."""
        if not self.conn:
            self._connect_to_hive()
        
        try:
            cursor = self.conn.cursor()
            logger.info(f"Exécution de la requête: {query}")
            cursor.execute(query)
            return cursor
        except Exception as e:
            logger.error(f"Erreur d'exécution de la requête: {str(e)}")
            raise
    
    def create_database(self, database_name="weblogs"):
        """Crée une base de données Hive si elle n'existe pas."""
        try:
            self._execute_query(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            logger.info(f"Base de données '{database_name}' créée avec succès.")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la création de la base de données: {str(e)}")
            return False
    
    def create_raw_logs_table(self, database_name="weblogs"):
        """Crée une table Hive pour les logs bruts au format JSON."""
        create_table_query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {database_name}.raw_logs (
            ip STRING,
            timestamp STRING,
            request STRING,
            status INT,
            size BIGINT,
            referer STRING,
            user_agent STRING,
            method STRING,
            url STRING,
            protocol STRING
        )
        ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
        STORED AS TEXTFILE
        LOCATION '/logs/raw/'
        TBLPROPERTIES ('skip.header.line.count'='0');
        """
        
        try:
            self._execute_query(create_table_query)
            logger.info(f"Table '{database_name}.raw_logs' créée avec succès.")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la création de la table raw_logs: {str(e)}")
            return False
    
    def create_processed_logs_table(self, database_name="weblogs"):
        """Crée une table Hive pour les logs traités au format CSV."""
        create_table_query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {database_name}.processed_logs (
            ip STRING,
            timestamp STRING,
            method STRING,
            url STRING,
            protocol STRING,
            status INT,
            size BIGINT,
            referer STRING,
            user_agent STRING
        )
        ROW FORMAT DELIMITED
        FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
        LOCATION '/logs/processed/'
        TBLPROPERTIES ('skip.header.line.count'='0');
        """
        
        try:
            self._execute_query(create_table_query)
            logger.info(f"Table '{database_name}.processed_logs' créée avec succès.")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la création de la table processed_logs: {str(e)}")
            return False
    
    def create_analytics_table(self, database_name="weblogs"):
        """Crée une table analytique pour des requêtes optimisées."""
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {database_name}.web_analytics (
            day STRING,
            hour INT,
            ip STRING,
            url STRING,
            status INT,
            size BIGINT,
            browser STRING,
            os STRING
        )
        PARTITIONED BY (day_of_week INT)
        STORED AS ORC;
        """
        
        try:
            self._execute_query(create_table_query)
            logger.info(f"Table '{database_name}.web_analytics' créée avec succès.")
            
            # Activer les partitions dynamiques
            self._execute_query("SET hive.exec.dynamic.partition.mode=nonstrict")
            
            # Insérer les données depuis processed_logs avec extraction des informations
            insert_query = f"""
            INSERT OVERWRITE TABLE {database_name}.web_analytics PARTITION (day_of_week)
            SELECT
                substr(timestamp, 1, 10) as day,
                cast(substr(timestamp, 12, 2) as INT) as hour,
                ip,
                url,
                status,
                size,
                case
                    when lower(user_agent) like '%chrome%' then 'Chrome'
                    when lower(user_agent) like '%firefox%' then 'Firefox'
                    when lower(user_agent) like '%safari%' then 'Safari'
                    when lower(user_agent) like '%edge%' then 'Edge'
                    when lower(user_agent) like '%msie%' then 'Internet Explorer'
                    else 'Other'
                end as browser,
                case
                    when lower(user_agent) like '%windows%' then 'Windows'
                    when lower(user_agent) like '%mac%' then 'MacOS'
                    when lower(user_agent) like '%linux%' then 'Linux'
                    when lower(user_agent) like '%android%' then 'Android'
                    when lower(user_agent) like '%iphone%' or lower(user_agent) like '%ipad%' then 'iOS'
                    else 'Other'
                end as os,
                pmod(datediff(timestamp, '1900-01-01'), 7) as day_of_week
            FROM {database_name}.processed_logs;
            """
            
            try:
                self._execute_query(insert_query)
                logger.info("Données insérées dans la table web_analytics.")
                return True
            except Exception as e:
                logger.error(f"Erreur lors de l'insertion des données: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la création de la table web_analytics: {str(e)}")
            return False
    
    def create_all_tables(self, database_name="weblogs"):
        """Crée toutes les tables nécessaires."""
        success = self.create_database(database_name)
        
        if success:
            self._execute_query(f"USE {database_name}")
            self.create_raw_logs_table(database_name)
            self.create_processed_logs_table(database_name)
            self.create_analytics_table(database_name)
    
    def close(self):
        """Ferme la connexion Hive."""
        if self.conn:
            self.conn.close()
            logger.info("Connexion Hive fermée.")

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description='Création des tables Hive pour l'analyse des logs')
    parser.add_argument('--hive-host', type=str, default='hive-server', help='Hôte Hive (défaut: hive-server)')
    parser.add_argument('--hive-port', type=int, default=10000, help='Port Hive (défaut: 10000)')
    parser.add_argument('--database', type=str, default='weblogs', help='Nom de la base de données (défaut: weblogs)')
    
    args = parser.parse_args()
    
    creator = HiveTableCreator(args.hive_host, args.hive_port)
    creator.create_all_tables(args.database)
    creator.close()

if __name__ == "__main__":
    main()