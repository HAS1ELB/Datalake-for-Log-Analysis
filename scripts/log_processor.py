#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour traiter les logs stockés dans HDFS et les préparer pour Hive.
"""

import os
import json
import logging
import argparse
import datetime
import pyhdfs

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LogProcessor:
    """Traite les logs bruts stockés dans HDFS et les prépare pour l'analyse avec Hive."""
    
    def __init__(self, hdfs_host="namenode", hdfs_port="9000", hdfs_user="root"):
        """Initialisation avec les paramètres de connexion HDFS."""
        self.hdfs_client = pyhdfs.HdfsClient(hosts=f"{hdfs_host}:{hdfs_port}", user_name=hdfs_user)
    
    def process_logs(self, input_hdfs_file, output_format='csv'):
        """
        Traite les logs bruts et les convertit dans un format adapté pour Hive.
        
        Args:
            input_hdfs_file (str): Chemin HDFS du fichier de logs brut
            output_format (str): Format de sortie ('csv' ou 'parquet')
        
        Returns:
            str: Chemin du fichier traité dans HDFS
        """
        if not self.hdfs_client.exists(input_hdfs_file):
            logger.error(f"Le fichier HDFS {input_hdfs_file} n'existe pas.")
            return None
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        output_hdfs_file = f"/logs/processed/weblogs_{timestamp}.{output_format}"
        
        logger.info(f"Traitement des logs depuis {input_hdfs_file} vers {output_hdfs_file}")
        
        try:
            # Lire le contenu du fichier
            with self.hdfs_client.open(input_hdfs_file) as file:
                content = file.read().decode('utf-8')
                
            # Traiter chaque ligne JSON
            processed_lines = []
            for line in content.splitlines():
                if not line.strip():
                    continue
                
                try:
                    log_entry = json.loads(line)
                    
                    # Pour CSV: extraire les champs nécessaires et les formater
                    if output_format == 'csv':
                        csv_line = (
                            f"{log_entry.get('ip', '-')},"
                            f"{log_entry.get('timestamp', '-')},"
                            f"{log_entry.get('method', '-')},"
                            f"{log_entry.get('url', '-').replace(',', '%2C')},"  # Échapper les virgules
                            f"{log_entry.get('protocol', '-')},"
                            f"{log_entry.get('status', '-')},"
                            f"{log_entry.get('size', '-')},"
                            f"{log_entry.get('referer', '-').replace(',', '%2C')},"  # Échapper les virgules
                            f"{log_entry.get('user_agent', '-').replace(',', '%2C')}"  # Échapper les virgules
                        )
                        processed_lines.append(csv_line)
                    
                    # Pour d'autres formats, ajouter ici le code nécessaire
                    
                except json.JSONDecodeError:
                    logger.warning(f"Impossible de décoder la ligne JSON: {line}")
                    continue
            
            # Écrire le contenu traité dans HDFS
            processed_content = '\n'.join(processed_lines).encode('utf-8')
            self.hdfs_client.create(output_hdfs_file, processed_content)
            
            logger.info(f"Traitement terminé. {len(processed_lines)} lignes traitées.")
            return output_hdfs_file
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement des logs: {str(e)}")
            return None

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description='Traitement des logs HDFS pour Hive')
    parser.add_argument('--input', type=str, required=True, help='Chemin HDFS du fichier de logs brut')
    parser.add_argument('--format', type=str, default='csv', choices=['csv', 'parquet'], 
                        help='Format de sortie (défaut: csv)')
    parser.add_argument('--hdfs-host', type=str, default='namenode', help='Hôte HDFS (défaut: namenode)')
    parser.add_argument('--hdfs-port', type=str, default='9000', help='Port HDFS (défaut: 9000)')
    
    args = parser.parse_args()
    
    processor = LogProcessor(args.hdfs_host, args.hdfs_port)
    processor.process_logs(args.input, args.format)

if __name__ == "__main__":
    main()