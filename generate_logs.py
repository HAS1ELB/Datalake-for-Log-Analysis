#!/usr/bin/env python3
"""
Script pour générer des logs d'application web synthétiques.
Ces logs simulent le format Apache Combined Log Format.
"""

import random
import time
from datetime import datetime, timedelta
import json
import os

# Configurations
NUM_LOGS = 5000
OUTPUT_FILE = "web_logs.log"

# Données synthétiques
IP_ADDRESSES = [
    "192.168.1." + str(i) for i in range(1, 254)
] + [
    "10.0.0." + str(i) for i in range(1, 100)
] + [
    f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    for _ in range(50)
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
]

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE"]

ENDPOINTS = [
    "/",
    "/home",
    "/products",
    "/products/electronics",
    "/products/clothing",
    "/about",
    "/contact",
    "/login",
    "/register",
    "/user/profile",
    "/cart",
    "/checkout",
    "/api/v1/users",
    "/api/v1/products",
    "/api/v1/orders",
    "/search",
    "/blog",
    "/blog/tech-news",
    "/blog/company-updates",
    "/static/css/main.css",
    "/static/js/app.js",
    "/static/images/logo.png"
]

HTTP_STATUS = [200, 200, 200, 200, 200, 301, 302, 304, 400, 401, 403, 404, 500]
HTTP_STATUS_WEIGHTS = [70, 70, 70, 70, 70, 5, 5, 10, 3, 3, 2, 7, 2]  # 200 étant le plus courant

REFERRERS = [
    "-",
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.facebook.com/",
    "https://www.twitter.com/",
    "https://www.instagram.com/",
    "https://www.linkedin.com/",
    "https://example.com/"
]

def random_date(start_date, end_date):
    """Génère une date aléatoire entre start_date et end_date."""
    time_delta = end_date - start_date
    random_seconds = random.randrange(int(time_delta.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)

def generate_log_entry():
    """Génère une entrée de log au format Apache Combined."""
    ip = random.choice(IP_ADDRESSES)
    timestamp = random_date(
        datetime.now() - timedelta(days=7),
        datetime.now()
    ).strftime("%d/%b/%Y:%H:%M:%S +0000")
    
    method = random.choice(HTTP_METHODS)
    endpoint = random.choice(ENDPOINTS)
    protocol = "HTTP/1.1"
    
    status = random.choices(HTTP_STATUS, weights=HTTP_STATUS_WEIGHTS, k=1)[0]
    
    # La taille de la réponse varie en fonction du statut HTTP
    if status == 200:
        size = random.randint(1024, 10485760)  # 1KB à 10MB
    elif status in [301, 302, 304]:
        size = random.randint(0, 512)  # 0 à 0.5KB
    elif status in [400, 401, 403, 404]:
        size = random.randint(512, 2048)  # 0.5KB à 2KB
    else:  # 500
        size = random.randint(512, 4096)  # 0.5KB à 4KB
    
    referrer = random.choice(REFERRERS)
    user_agent = random.choice(USER_AGENTS)
    
    log_entry = f'{ip} - - [{timestamp}] "{method} {endpoint} {protocol}" {status} {size} "{referrer}" "{user_agent}"'
    return log_entry

def generate_logs(num_logs, output_file):
    """Génère un fichier de logs contenant num_logs entrées."""
    dir_name = os.path.dirname(output_file)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

        
    with open(output_file, 'w') as f:
        for _ in range(num_logs):
            log_entry = generate_log_entry()
            f.write(log_entry + "\n")

if __name__ == "__main__":
    print(f"Génération de {NUM_LOGS} entrées de logs dans le fichier {OUTPUT_FILE}")
    generate_logs(NUM_LOGS, OUTPUT_FILE)
    print("Génération terminée!")