#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour exécuter des requêtes analytiques avancées sur les données de logs.
"""

import os
import sys
import time
import logging
import argparse
import pandas as pd
from pyhive import hive
import matplotlib.pyplot as plt
from tabulate import tabulate

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LogAnalytics:
    """Exécute des requêtes analytiques sur les données de logs stockées dans Hive."""
    
    def __init__(self, hive_host="hive-server", hive_port=10000, database="weblogs"):
        """Initialisation avec les paramètres de connexion Hive."""
        self.hive_host = hive_host
        self.hive_port = hive_port
        self.database = database
        self.conn = None
        
        # Se connecter à Hive
        self._connect_to_hive()
    
    def _connect_to_hive(self):
        """Établit une connexion avec le serveur Hive."""
        try:
            logger.info(f"Connexion au serveur Hive ({self.hive_host}:{self.hive_port})...")
            self.conn = hive.Connection(host=self.hive_host, port=self.hive_port)
            cursor = self.conn.cursor()
            cursor.execute(f"USE {self.database}")
            logger.info(f"Connecté à la base de données '{self.database}'.")
        except Exception as e:
            logger.error(f"Erreur de connexion au serveur Hive: {str(e)}")
            raise
    
    def _execute_query(self, query):
        """Exécute une requête Hive et renvoie les résultats."""
        if not self.conn:
            self._connect_to_hive()
        
        try:
            logger.info(f"Exécution de la requête: {query}")
            cursor = self.conn.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            logger.error(f"Erreur d'exécution de la requête: {str(e)}")
            return pd.DataFrame()
    
    def http_status_distribution(self):
        """Analyse la distribution des codes d'état HTTP."""
        query = """
        SELECT status, COUNT(*) as count
        FROM processed_logs
        GROUP BY status
        ORDER BY count DESC
        """
        
        df = self._execute_query(query)
        
        if not df.empty:
            logger.info("\n=== Distribution des codes d'état HTTP ===")
            logger.info(tabulate(df, headers=df.columns, tablefmt='psql', showindex=False))
            
            # Catégories pour les codes HTTP
            df['category'] = df['status'].apply(lambda x: 
                                              'Succès (2xx)' if 200 <= x < 300 else
                                              'Redirection (3xx)' if 300 <= x < 400 else
                                              'Erreur Client (4xx)' if 400 <= x < 500 else
                                              'Erreur Serveur (5xx)' if 500 <= x < 600 else
                                              'Autre')
            
            # Agréger par catégorie
            category_df = df.groupby('category').sum().reset_index()
            
            logger.info("\n=== Distribution par catégorie de code HTTP ===")
            logger.info(tabulate(category_df, headers=category_df.columns, tablefmt='psql', showindex=False))
        else:
            logger.warning("Aucune donnée disponible pour l'analyse des codes d'état HTTP.")
    
    def top_urls(self, limit=10):
        """Identifie les URLs les plus demandées."""
        query = f"""
        SELECT url, COUNT(*) as count
        FROM processed_logs
        GROUP BY url
        ORDER BY count DESC
        LIMIT {limit}
        """
        
        df = self._execute_query(query)
        
        if not df.empty:
            logger.info(f"\n=== Top {limit} des URLs les plus demandées ===")
            logger.info(tabulate(df, headers=df.columns, tablefmt='psql', showindex=False))
        else:
            logger.warning("Aucune donnée disponible pour l'analyse des URLs.")
    
    def browser_distribution(self):
        """Analyse la répartition des navigateurs utilisés."""
        query = """
        SELECT browser, COUNT(*) as count
        FROM web_analytics
        GROUP BY browser
        ORDER BY count DESC
        """
        
        df = self._execute_query(query)
        
        if not df.empty:
            logger.info("\n=== Répartition des navigateurs utilisés ===")
            logger.info(tabulate(df, headers=df.columns, tablefmt='psql', showindex=False))
        else:
            logger.warning("Aucune donnée disponible pour l'analyse des navigateurs.")
    
    def os_distribution(self):
        """Analyse la répartition des systèmes d'exploitation utilisés."""
        query = """
        SELECT os, COUNT(*) as count
        FROM web_analytics
        GROUP BY os
        ORDER BY count DESC
        """
        
        df = self._execute_query(query)
        
        if not df.empty:
            logger.info("\n=== Répartition des systèmes d'exploitation utilisés ===")
            logger.info(tabulate(df, headers=df.columns, tablefmt='psql', showindex=False))
        else:
            logger.warning("Aucune donnée disponible pour l'analyse des systèmes d'exploitation.")
    
    def hourly_traffic(self):
        """Analyse le trafic par heure de la journée."""
        query = """
        SELECT hour, COUNT(*) as count
        FROM web_analytics
        GROUP BY hour
        ORDER BY hour
        """
        
        df = self._execute_query(query)
        
        if not df.empty:
            logger.info("\n=== Trafic par heure de la journée ===")
            logger.info(tabulate(df, headers=df.columns, tablefmt='psql', showindex=False))
        else:
            logger.warning("Aucune donnée disponible pour l'analyse du trafic par heure.")
    
    def daily_traffic(self):
        """Analyse le trafic par jour de la semaine."""
        query = """
        SELECT 
            day_of_week,
            CASE day_of_week
                WHEN 0 THEN 'Dimanche'
                WHEN 1 THEN 'Lundi'
                WHEN 2 THEN 'Mardi'
                WHEN 3 THEN 'Mercredi'
                WHEN 4 THEN 'Jeudi'
                WHEN 5 THEN 'Vendredi'
                WHEN 6 THEN 'Samedi'
            END as jour,
            COUNT(*) as count
        FROM web_analytics
        GROUP BY day_of_week
        ORDER BY day_of_week
        """
        
        df = self._execute_query(query)
        
        if not df.empty:
            logger.info("\n=== Trafic par jour de la semaine ===")
            logger.info(tabulate(df, headers=df.columns, tablefmt='psql', showindex=False))
        else:
            logger.warning("Aucune donnée disponible pour l'analyse du trafic par jour.")
    
    def error_analysis(self):
        """Analyse détaillée des erreurs (codes 4xx et 5xx)."""
        query = """
        SELECT 
            status,
            url,
            COUNT(*) as count
        FROM processed_logs
        WHERE status >= 400
        GROUP BY status, url
        ORDER BY count DESC
        LIMIT 20
        """
        
        df = self._execute_query(query)
        
        if not df.empty:
            logger.info("\n=== Analyse détaillée des erreurs ===")
            logger.info(tabulate(df, headers=df.columns, tablefmt='psql', showindex=False))
        else:
            logger.warning("Aucune donnée disponible pour l'analyse des erreurs.")
    
    def ip_analysis(self, limit=10):
        """Identifie les adresses IP les plus actives."""
        query = f"""
        SELECT ip, COUNT(*) as count
        FROM processed_logs
        GROUP BY ip
        ORDER BY count DESC
        LIMIT {limit}
        """
        
        df = self._execute_query(query)
        
        if not df.empty:
            logger.info(f"\n=== Top {limit} des adresses IP les plus actives ===")
            logger.info(tabulate(df, headers=df.columns, tablefmt='psql', showindex=False))
        else:
            logger.warning("Aucune donnée disponible pour l'analyse des adresses IP.")
    
    def run_all_analytics(self):
        """Exécute toutes les analyses disponibles."""
        logger.info("=== DÉMARRAGE DE L'ANALYSE COMPLÈTE DES LOGS ===")
        
        self.http_status_distribution()
        self.top_urls()
        self.browser_distribution()
        self.os_distribution()
        self.hourly_traffic()
        self.daily_traffic()
        self.error_analysis()
        self.ip_analysis()
        
        logger.info("=== ANALYSE COMPLÈTE TERMINÉE ===")
    
    def close(self):
        """Ferme la connexion Hive."""
        if self.conn:
            self.conn.close()
            logger.info("Connexion Hive fermée.")

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description='Analyse des logs web stockés dans Hive')
    parser.add_argument('--hive-host', type=str, default='hive-server', help='Hôte Hive (défaut: hive-server)')
    parser.add_argument('--hive-port', type=int, default=10000, help='Port Hive (défaut: 10000)')
    parser.add_argument('--database', type=str, default='weblogs', help='Base de données Hive (défaut: weblogs)')
    parser.add_argument('--analysis', type=str, choices=[
        'all', 'status', 'urls', 'browsers', 'os', 'hourly', 'daily', 'errors', 'ips'
    ], default='all', help='Type d\'analyse à exécuter (défaut: all)')
    
    args = parser.parse_args()
    
    analytics = LogAnalytics(args.hive_host, args.hive_port, args.database)
    
    try:
        if args.analysis == 'all':
            analytics.run_all_analytics()
        elif args.analysis == 'status':
            analytics.http_status_distribution()
        elif args.analysis == 'urls':
            analytics.top_urls()
        elif args.analysis == 'browsers':
            analytics.browser_distribution()
        elif args.analysis == 'os':
            analytics.os_distribution()
        elif args.analysis == 'hourly':
            analytics.hourly_traffic()
        elif args.analysis == 'daily':
            analytics.daily_traffic()
        elif args.analysis == 'errors':
            analytics.error_analysis()
        elif args.analysis == 'ips':
            analytics.ip_analysis()
    finally:
        analytics.close()

if __name__ == "__main__":
    main()
