.PHONY: start stop restart generate-logs upload-logs analyze logs check-services

# Variables
CONTAINER_NAMENODE=namenode
CONTAINER_HIVE=hive-server

# Démarrer l'environnement Hadoop
start:
	docker-compose up -d
	@echo "Attente du démarrage des services..."
	sleep 20
	@echo "Services démarrés"

# Arrêter l'environnement Hadoop
stop:
	docker-compose down

# Redémarrer l'environnement Hadoop
restart: stop start

# Générer des logs d'application web
generate-logs:
	python3 generate_logs.py

# Créer les répertoires HDFS et uploader les logs
upload-logs: generate-logs
	docker exec -i $(CONTAINER_NAMENODE) hdfs dfs -mkdir -p /data/raw_logs
	docker cp web_logs.log $(CONTAINER_NAMENODE):/opt/web_logs.log
	docker exec -i $(CONTAINER_NAMENODE) hdfs dfs -put -f /opt/web_logs.log /data/raw_logs/

# Créer les tables Hive et charger les données
prepare-hive: upload-logs
	docker cp prepare_hive_tables.hql $(CONTAINER_HIVE):/opt/prepare_hive_tables.hql
	docker exec -i $(CONTAINER_HIVE) beeline -u jdbc:hive2://localhost:10000 -f /opt/prepare_hive_tables.hql

# Exécuter des requêtes d'analyse
analyze:
	docker cp sample_queries.hql $(CONTAINER_HIVE):/opt/sample_queries.hql
	docker exec -i $(CONTAINER_HIVE) beeline -u jdbc:hive2://localhost:10000 -f /opt/sample_queries.hql

# Afficher les dernières entrées de logs
logs:
	docker-compose logs --tail=100

# Vérifier l'état des services
check-services:
	@echo "État des conteneurs:"
	docker-compose ps
	@echo "\nVérification HDFS:"
	docker exec -i $(CONTAINER_NAMENODE) hdfs dfsadmin -report | head -20
	@echo "\nVérification Hive:"
	docker exec -i $(CONTAINER_HIVE) beeline -u jdbc:hive2://localhost:10000 -e "SHOW DATABASES;"

# Pipeline complet: démarrer, générer les logs, préparer Hive et analyser
pipeline: start generate-logs upload-logs prepare-hive analyze

# Nettoyage complet (arrêt et suppression des volumes)
clean:
	docker-compose down -v
	rm -f web_logs.log