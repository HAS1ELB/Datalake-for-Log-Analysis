#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour générer des logs de test d'une application web.
"""

import os
import random
import time
import datetime
import argparse
from faker import Faker

# Initialisation de Faker pour générer des données réalistes
fake = Faker()

# Liste des méthodes HTTP
HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "HEAD"]

# Liste des codes de statut HTTP avec leur poids
HTTP_STATUSES = {
    200: 70,  # OK (70% de chance)
    301: 5,   # Moved Permanently (5% de chance)
    302: 5,   # Found (5% de chance)
    304: 5,   # Not Modified (5% de chance)
    400: 5,   # Bad Request (5% de chance)
    403: 3,   # Forbidden (3% de chance)
    404: 5,   # Not Found (5% de chance)
    500: 2    # Internal Server Error (2% de chance)
}

# Liste des pages populaires
POPULAR_PAGES = [
    "/",
    "/index.html",
    "/about",
    "/contact",
    "/products",
    "/services",
    "/login",
    "/register",
    "/dashboard",
    "/profile",
    "/cart",
    "/checkout",
    "/blog",
    "/api/v1/users",
    "/api/v1/products",
    "/images/logo.png",
    "/css/style.css",
    "/js/main.js"
]

# Liste des navigateurs avec leur poids
BROWSERS = {
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36": 40,
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15": 25,
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0": 20,
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36": 10,
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1": 3,
    "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36": 2,
}

def weighted_choice(choices_dict):
    """Sélectionne un élément en fonction de son poids."""
    total = sum(choices_dict.values())
    r = random.uniform(0, total)
    upto = 0
    for choice, weight in choices_dict.items():
        upto += weight
        if upto > r:
            return choice
    # Si on arrive ici, c'est qu'il y a un problème avec les poids
    return list(choices_dict.keys())[0]

def generate_ip():
    """Génère une adresse IP aléatoire."""
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

def generate_log_entry(timestamp):
    """Génère une entrée de log au format Apache Common Log Format."""
    ip = generate_ip()
    # Identifiant distant (souvent '-')
    remote_logname = "-"
    # Identifiant utilisateur (souvent '-', mais peut être un nom d'utilisateur si l'authentification est activée)
    user_id = "-"
    # Timestamp au format [jour/mois/année:heure:minute:seconde +zone]
    timestamp_str = timestamp.strftime("[%d/%b/%Y:%H:%M:%S %z]")
    
    # Méthode HTTP
    method = random.choice(HTTP_METHODS)
    
    # URL demandée (avec une chance sur 10 d'avoir une page aléatoire)
    if random.random() < 0.9:
        url = random.choice(POPULAR_PAGES)
    else:
        # Générer un chemin aléatoire
        path_depth = random.randint(0, 3)
        path_parts = [fake.word() for _ in range(path_depth)]
        url = "/" + "/".join(path_parts)
        # Ajouter une extension de fichier parfois
        if random.random() < 0.3:
            extensions = ["html", "php", "jpg", "png", "js", "css"]
            url += "." + random.choice(extensions)
    
    # Protocole HTTP
    protocol = "HTTP/1.1"
    
    # Requête complète
    request = f'"{method} {url} {protocol}"'
    
    # Code de statut HTTP
    status = weighted_choice(HTTP_STATUSES)
    
    # Taille de la réponse en octets
    # Plus élevée pour les codes 200, plus petite pour les erreurs
    if status == 200:
        size = random.randint(500, 50000)
    else:
        size = random.randint(100, 1000)
    
    # Referer (URL d'où provient la demande)
    if random.random() < 0.7:  # 70% de chance d'avoir un referer
        referer = f'"http://www.{fake.domain_name()}{random.choice(POPULAR_PAGES)}"'
    else:
        referer = '"-"'
    
    # User Agent
    user_agent = f'"{weighted_choice(BROWSERS)}"'
    
    # Format: IP - RemoteLogname UserId [Timestamp] "Request" Status Size "Referer" "UserAgent"
    return f'{ip} {remote_logname} {user_id} {timestamp_str} {request} {status} {size} {referer} {user_agent}'

def generate_logs(output_file, num_entries, start_time=None, end_time=None):
    """
    Génère un fichier de logs au format Apache Common Log Format.
    
    Args:
        output_file (str): Chemin du fichier de sortie
        num_entries (int): Nombre d'entrées à générer
        start_time (datetime): Heure de début (default: 24 heures avant maintenant)
        end_time (datetime): Heure de fin (default: maintenant)
    """
    # Définir la période par défaut si non spécifiée
    if not end_time:
        end_time = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
    if not start_time:
        start_time = end_time - datetime.timedelta(days=1)
    
    # Calculer l'intervalle de temps entre chaque entrée
    time_diff = (end_time - start_time).total_seconds()
    interval = time_diff / num_entries
    
    # Créer le répertoire de sortie si nécessaire
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    with open(output_file, 'w') as f:
        for i in range(num_entries):
            # Calculer le timestamp pour cette entrée
            # Ajouter un peu d'aléatoire pour éviter des intervalles parfaitement réguliers
            random_offset = random.uniform(-interval/2, interval/2)
            entry_time = start_time + datetime.timedelta(seconds=(i * interval + random_offset))
            
            # Générer et écrire l'entrée de log
            log_entry = generate_log_entry(entry_time)
            f.write(log_entry + '\n')
            
            # Afficher la progression
            if (i+1) % 1000 == 0 or (i+1) == num_entries:
                print(f"Généré {i+1}/{num_entries} entrées... ({(i+1)/num_entries*100:.1f}%)")

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description='Générateur de logs web pour tests')
    parser.add_argument('--output', type=str, default='./sample_logs/sample_web_logs.log',
                       help='Chemin du fichier de sortie')
    parser.add_argument('--entries', type=int, default=10000,
                       help='Nombre d\'entrées de log à générer')
    parser.add_argument('--days', type=int, default=1,
                       help='Nombre de jours à couvrir')
    
    args = parser.parse_args()
    
    # Calculer la période
    end_time = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(days=args.days)
    
    print(f"Génération de {args.entries} entrées de log couvrant {args.days} jour(s)...")
    print(f"Période: du {start_time.strftime('%Y-%m-%d %H:%M:%S')} au {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Fichier de sortie: {args.output}")
    
    generate_logs(args.output, args.entries, start_time, end_time)
    
    print(f"Génération terminée. {args.entries} entrées écrites dans {args.output}")

if __name__ == "__main__":
    main()