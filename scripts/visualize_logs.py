#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour générer des visualisations à partir des données de logs.
"""

import os
import sys
import logging
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pyhive import hive
from matplotlib.ticker import MaxNLocator

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LogVisualizer:
    """Génère des visualisations à partir des données de logs stockées dans Hive."""
    
    def __init__(self, hive_host="hive-server", hive_port=10000, database="weblogs", output_dir="./visualizations"):
        """Initialisation avec les paramètres de connexion Hive et le répertoire de sortie."""
        self.hive_host = hive_host
        self.hive_port = hive_port
        self.database = database
        self.output_dir = output_dir
        self.conn = None
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Se connecter à Hive
        self._connect_to_hive()
        
        # Configuration des styles de visualisation
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set(font_scale=1.2)
    
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
        """Exécute une requête Hive et renvoie les résultats sous forme de DataFrame."""
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
    
    def _save_figure(self, title, dpi=300):
        """Enregistre la figure courante avec le titre spécifié."""
        filename = title.lower().replace(' ', '_').replace(':', '').replace('(', '').replace(')', '') + '.png'
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close()
        logger.info(f"Figure enregistrée: {filepath}")
    
    def visualize_http_status(self):
        """Visualise la distribution des codes d'état HTTP."""
        query = """
        SELECT status, COUNT(*) as count
        FROM processed_logs
        GROUP BY status
        ORDER BY status
        """
        
        df = self._execute_query(query)
        
        if not df.empty:
            # Ajouter les catégories pour les codes HTTP
            df['category'] = df['status'].apply(lambda x: 
                                              'Succès (2xx)' if 200 <= x < 300 else
                                              'Redirection (3xx)' if 300 <= x < 400 else
                                              'Erreur Client (4xx)' if 400 <= x < 500 else
                                              'Erreur Serveur (5xx)' if 500 <= x < 600 else
                                              'Autre')
            
            # Créer un graphique à barres pour les codes spécifiques
            plt.figure(figsize=(12, 8))
            ax = sns.barplot(x='status', y='count', data=df, palette='viridis')
            
            # Rotation des étiquettes pour une meilleure lisibilité
            plt.xticks(rotation=45)
            
            # Ajout des annotations sur chaque barre
            for p in ax.patches:
                ax.annotate(f"{int(p.get_height())}",
                           (p.get_x() + p.get_width() / 2., p.get_height()),
                           ha='center', va='bottom', fontsize=10)
            
            plt.title('Distribution des codes d\'état HTTP', fontsize=16)
            plt.xlabel('Code d\'état HTTP', fontsize=14)
            plt.ylabel('Nombre de requêtes', fontsize=14)
            self._save_figure('Distribution des codes HTTP')
            
            # Créer un graphique en camembert pour les catégories
            category_df = df.groupby('category')['count'].sum().reset_index()
            plt.figure(figsize=(10, 10))
            plt.pie(category_df['count'], labels=category_df['category'], autopct='%1.1f%%',
                   startangle=90, shadow=True, explode=[0.05] * len(category_df),
                   colors=sns.color_palette('viridis', len(category_df)))
            plt.axis('equal')
            plt.title('Répartition par catégorie de code HTTP', fontsize=16)
            self._save_figure('Repartition par categorie HTTP')
            
            logger.info("Visualisations des codes HTTP créées avec succès.")
        else:
            logger.warning("Aucune donnée disponible pour visualiser les codes HTTP.")
    
    def visualize_top_urls(self, limit=10):
        """Visualise les URLs les plus demandées."""
        query = f"""
        SELECT url, COUNT(*) as count
        FROM processed_logs
        GROUP BY url
        ORDER BY count DESC
        LIMIT {limit}
        """
        
        df = self._execute_query(query)
        
        if not df.empty:
            # Raccourcir les URLs pour une meilleure visualisation
            df['short_url'] = df['url'].apply(lambda x: x if len(x) < 30 else x[:27] + '...')
            
            plt.figure(figsize=(14, 8))
            ax = sns.barplot(y='short_url', x='count', data=df, palette='plasma')
            
            # Ajout des annotations sur chaque barre
            for p in ax.patches:
                ax.annotate(f"{int(p.get_width())}",
                           (p.get_width(), p.get_y() + p.get_height() / 2),
                           ha='left', va='center', fontsize=10)
            
            plt.title(f'Top {limit} des URLs les plus demandées', fontsize=16)
            plt.xlabel('Nombre de requêtes', fontsize=14)
            plt.ylabel('URL', fontsize=14)
            plt.tight_layout()
            self._save_figure(f'Top {limit} URLs')
            
            logger.info(f"Visualisation des Top {limit} URLs créée avec succès.")
        else:
            logger.warning("Aucune donnée disponible pour visualiser les URLs.")
    
    def visualize_browser_os(self):
        """Visualise la répartition des navigateurs et systèmes d'exploitation."""
        # Requête pour les navigateurs
        query_browser = """
        SELECT browser, COUNT(*) as count
        FROM web_analytics
        GROUP BY browser
        ORDER BY count DESC
        """
        
        # Requête pour les systèmes d'exploitation
        query_os = """
        SELECT os, COUNT(*) as count
        FROM web_analytics
        GROUP BY os
        ORDER BY count DESC
        """
        
        df_browser = self._execute_query(query_browser)
        df_os = self._execute_query(query_os)
        
        if not df_browser.empty and not df_os.empty:
            # Créer une figure avec 2 sous-graphiques
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # Graphique des navigateurs
            ax1.pie(df_browser['count'], labels=df_browser['browser'], autopct='%1.1f%%',
                   startangle=90, shadow=True, explode=[0.05] * len(df_browser),
                   colors=sns.color_palette('viridis', len(df_browser)))
            ax1.axis('equal')
            ax1.set_title('Répartition des navigateurs', fontsize=16)
            
            # Graphique des systèmes d'exploitation
            ax2.pie(df_os['count'], labels=df_os['os'], autopct='%1.1f%%',
                   startangle=90, shadow=True, explode=[0.05] * len(df_os),
                   colors=sns.color_palette('plasma', len(df_os)))
            ax2.axis('equal')
            ax2.set_title('Répartition des systèmes d\'exploitation', fontsize=16)
            
            plt.tight_layout()
            self._save_figure('Repartition navigateurs et OS')
            
            logger.info("Visualisation des navigateurs et OS créée avec succès.")
        else:
            logger.warning("Aucune donnée disponible pour visualiser les navigateurs et OS.")
    
    def visualize_hourly_traffic(self):
        """Visualise le trafic par heure de la journée."""
        query = """
        SELECT hour, COUNT(*) as count
        FROM web_analytics
        GROUP BY hour
        ORDER BY hour
        """
        
        df = self._execute_query(query)
        
        if not df.empty:
            plt.figure(figsize=(14, 8))
            ax = sns.lineplot(x='hour', y='count', data=df, marker='o', linewidth=2, markersize=10)
            
            # Formatage de l'axe des x pour afficher toutes les heures
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            plt.xticks(range(0, 24))
            
            # Ajout d'une ligne de tendance avec une moyenne mobile
            if len(df) > 2:
                df['rolling_mean'] = df['count'].rolling(window=3, center=True).mean()
                sns.lineplot(x='hour', y='rolling_mean', data=df, color='red', linestyle='--', label='Tendance (moyenne mobile)')
            
            # Ajout des annotations sur chaque point
            for i, row in df.iterrows():
                plt.annotate(f"{int(row['count'])}",
                            (row['hour'], row['count']),
                            textcoords="offset points",
                            xytext=(0, 10),
                            ha='center')
            
            plt.title('Trafic par heure de la journée', fontsize=16)
            plt.xlabel('Heure', fontsize=14)
            plt.ylabel('Nombre de requêtes', fontsize=14)
            plt.grid(True)
            if len(df) > 2:
                plt.legend()
            
            self._save_figure('Trafic par heure')
            
            logger.info("Visualisation du trafic horaire créée avec succès.")
        else:
            logger.warning("Aucune donnée disponible pour visualiser le trafic horaire.")
    
    def visualize_daily_traffic(self):
        """Visualise le trafic par jour de la semaine."""
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
            plt.figure(figsize=(12, 8))
            ax = sns.barplot(x='jour', y='count', data=df, palette='viridis')
            
            # Ajout des annotations sur chaque barre
            for p in ax.patches:
                ax.annotate(f"{int(p.get_height())}",
                           (p.get_x() + p.get_width() / 2., p.get_height()),
                           ha='center', va='bottom', fontsize=10)
            
            plt.title('Trafic par jour de la semaine', fontsize=16)
            plt.xlabel('Jour', fontsize=14)
            plt.ylabel('Nombre de requêtes', fontsize=14)
            
            self._save_figure('Trafic par jour')
            
            logger.info("Visualisation du trafic journalier créée avec succès.")
        else:
            logger.warning("Aucune donnée disponible pour visualiser le trafic journalier.")
    
    def visualize_all(self):
        """Génère toutes les visualisations disponibles."""
        logger.info("=== GÉNÉRATION DE TOUTES LES VISUALISATIONS ===")
        
        self.visualize_http_status()
        self.visualize_top_urls()
        self.visualize_browser_os()
        self.visualize_hourly_traffic()
        self.visualize_daily_traffic()
        
        logger.info(f"Toutes les visualisations ont été enregistrées dans: {self.output_dir}")
    
    def close(self):
        """Ferme la connexion Hive."""
        if self.conn:
            self.conn.close()
            logger.info("Connexion Hive fermée.")

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description='Visualisation des logs web stockés dans Hive')
    parser.add_argument('--hive-host', type=str, default='hive-server', help='Hôte Hive (défaut: hive-server)')
    parser.add_argument('--hive-port', type=int, default=10000, help='Port Hive (défaut: 10000)')
    parser.add_argument('--database', type=str, default='weblogs', help='Base de données Hive (défaut: weblogs)')
    parser.add_argument('--output-dir', type=str, default='./visualizations', help='Répertoire de sortie (défaut: ./visualizations)')
    parser.add_argument('--viz', type=str, choices=[
        'all', 'status', 'urls', 'browser_os', 'hourly', 'daily'
    ], default='all', help='Type de visualisation à générer (défaut: all)')
    
    args = parser.parse_args()
    
    visualizer = LogVisualizer(args.hive_host, args.hive_port, args.database, args.output_dir)
    
    try:
        if args.viz == 'all':
            visualizer.visualize_all()
        elif args.viz == 'status':
            visualizer.visualize_http_status()
        elif args.viz == 'urls':
            visualizer.visualize_top_urls()
        elif args.viz == 'browser_os':
            visualizer.visualize_browser_os()
        elif args.viz == 'hourly':
            visualizer.visualize_hourly_traffic()
        elif args.viz == 'daily':
            visualizer.visualize_daily_traffic()
    finally:
        visualizer.close()

if __name__ == "__main__":
    main()
