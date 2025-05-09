#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour collecter et transférer des logs vers HDFS.
"""

import os
import time
import logging
import datetime
import argparse
import pyhdfs
from apachelogs import LogParser
from pathlib import Path
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LogCollector:
    """Collecte les logs d'une application web et les transfère vers HDFS."""
    
    def __init__(self, hdfs_host="namenode", hdfs_port="9000", hdfs_user="root"):
        """Initialisation avec les paramètres de connexion HDFS."""
        self.hdfs_client = pyhdfs.HdfsClient(hosts=f"{hdfs_host}:{hdfs_port}", user_name=hdfs_user)
        self.log_parser = LogParser("%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"")
        
        # Vérifier et créer les répertoires HDFS
        self._initialize_hdfs_directories()
    
    def _initialize_hdfs_directories(self):
        """Création des répertoires nécessaires dans HDFS."""
        base_dir = '/logs'
        raw_dir = f'{base_dir}/raw'
        processed_dir = f'{base_dir}/processed'
        
        for directory in [base_dir, raw_dir, processed_dir]:
            if not self.hdfs_client.exists(directory):
                logger.info(f"Création du répertoire HDFS: {directory}")
                self.hdfs_client.mkdirs(directory)
    
    def _process_log_line(self, line):
        """Traite une ligne de log et la convertit en format JSON."""
        try:
            entry = self.log_parser.parse(line)
            
            # Conversion en dictionnaire pour JSON
            log_dict = {
                'ip': entry.remote_host,
                'timestamp': entry.request_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'request': entry.request_line,
                'status': entry.final_status,
                'size': entry.bytes_sent,
                'referer': entry.headers_in.get('Referer', '-'),
                'user_agent': entry.headers_in.get('User-Agent', '-'),
                'method': entry.request_line.split(' ')[0] if ' ' in entry.request_line else '-',
                'url': entry.request_line.split(' ')[1] if ' ' in entry.request_line and len(entry.request_line.split(' ')) > 1 else '-',
                'protocol': entry.request_line.split(' ')[2] if ' ' in entry.request_line and len(entry.request_line.split(' ')) > 2 else '-'
            }
            
            return json.dumps(log_dict)
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la ligne: {line}, erreur: {str(e)}")
            return None

    def collect_logs(self, log_file_path, batch_size=1000):
        """
        Collecte les logs à partir d'un fichier et les transfère vers HDFS.
        
        Args:
            log_file_path (str): Chemin vers le fichier de logs
            batch_size (int): Nombre de lignes à traiter par lot
        """
        log_file = Path(log_file_path)
        
        if not log_file.exists():
            logger.error(f"Le fichier de log {log_file_path} n'existe pas.")
            return
        
        # Générer un nom de fichier HDFS basé sur la date et l'heure
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        hdfs_raw_file = f"/logs/raw/weblogs_{timestamp}.json"
        
        logger.info(f"Début de la collecte des logs depuis {log_file_path}")
        
        # Traitement par lots pour économiser la mémoire
        batch = []
        count = 0
        total_count = 0
        
        try:
            with open(log_file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    
                    json_line = self._process_log_line(line)
                    if json_line:
                        batch.append(json_line)
                        count += 1
                        
                    # Traiter le lot quand il atteint la taille spécifiée
                    if count >= batch_size:
                        self._upload_batch_to_hdfs(batch, hdfs_raw_file)
                        total_count += count
                        logger.info(f"Transféré {total_count} lignes vers HDFS")
                        batch = []
                        count = 0
            
            # Traiter le lot restant s'il y en a
            if batch:
                self._upload_batch_to_hdfs(batch, hdfs_raw_file)
                total_count += len(batch)
                logger.info(f"Transféré {total_count} lignes vers HDFS")
            
            logger.info(f"Collecte terminée. Total de {total_count} lignes traitées.")
            
            return hdfs_raw_file
                
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des logs: {str(e)}")
            return None
    
    def _upload_batch_to_hdfs(self, batch, hdfs_file):
        """Télécharge un lot de lignes de logs vers HDFS."""
        if not batch:
            return
        
        data = '\n'.join(batch).encode('utf-8')
        
        # Si le fichier existe déjà, on écrit à la suite
        if self.hdfs_client.exists(hdfs_file):
            self.hdfs_client.append(hdfs_file, data)
        else:
            self.hdfs_client.create(hdfs_file, data)

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description='Collecte de logs web vers HDFS')
    parser.add_argument('--file', type=str, required=True, help='Chemin vers le fichier de logs')
    parser.add_argument('--hdfs-host', type=str, default='namenode', help='Hôte HDFS (défaut: namenode)')
    parser.add_argument('--hdfs-port', type=str, default='9000', help='Port HDFS (défaut: 9000)')
    parser.add_argument('--batch-size', type=int, default=1000, help='Taille des lots (défaut: 1000)')
    
    args = parser.parse_args()
    
    collector = LogCollector(args.hdfs_host, args.hdfs_port)
    collector.collect_logs(args.file, args.batch_size)

if __name__ == "__main__":
    main()