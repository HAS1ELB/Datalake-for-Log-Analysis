#!/bin/bash

# Script pour démarrer l'environnement et exécuter le projet
set -e

echo "=== Démarrage de l'environnement de Datalake pour l'analyse des logs ==="

# Vérifier que Docker et Docker Compose sont installés
if ! command -v docker &> /dev/null; then
    echo "Erreur: Docker n'est pas installé. Veuillez installer Docker avant de continuer."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Erreur: Docker Compose n'est pas installé. Veuillez installer Docker Compose avant de continuer."
    exit 1
fi

# Créer le fichier hadoop.env s'il n'existe pas
if [ ! -f hadoop.env ]; then
    echo "Création du fichier hadoop.env..."
    cat > hadoop.env << EOF
CORE_CONF_fs_defaultFS=hdfs://namenode:9000
CORE_CONF_hadoop_http_staticuser_user=root
CORE_CONF_hadoop_proxyuser_hue_hosts=*
CORE_CONF_hadoop_proxyuser_hue_groups=*
CORE_CONF_io_compression_codecs=org.apache.hadoop.io.compress.SnappyCodec

HDFS_CONF_dfs_webhdfs_enabled=true
HDFS_CONF_dfs_permissions_enabled=false
HDFS_CONF_dfs_namenode_datanode_registration_ip___hostname___check=false

YARN_CONF_yarn_log___aggregation___enable=true
YARN_CONF_yarn_log_server_url=http://historyserver:8188/applicationhistory/logs/
YARN_CONF_yarn_resourcemanager_recovery_enabled=true
YARN_CONF_yarn_resourcemanager_store_class=org.apache.hadoop.yarn.server.resourcemanager.recovery.FileSystemRMStateStore
YARN_CONF_yarn_resourcemanager_scheduler_class=org.apache.hadoop.yarn.server.resourcemanager.scheduler.capacity.CapacityScheduler
YARN_CONF_yarn_scheduler_capacity_root_default_maximum___allocation___mb=8192
YARN_CONF_yarn_scheduler_capacity_root_default_maximum___allocation___vcores=4
YARN_CONF_yarn_resourcemanager_fs_state___store_uri=/rmstate
YARN_CONF_yarn_resourcemanager_system___metrics___publisher_enabled=true
YARN_CONF_yarn_resourcemanager_hostname=resourcemanager
YARN_CONF_yarn_resourcemanager_address=resourcemanager:8032
YARN_CONF_yarn_resourcemanager_scheduler_address=resourcemanager:8030
YARN_CONF_yarn_resourcemanager_resource__tracker_address=resourcemanager:8031
YARN_CONF_yarn_timeline___service_enabled=true
YARN_CONF_yarn_timeline___service_generic___application___history_enabled=true
YARN_CONF_yarn_timeline___service_hostname=historyserver
YARN_CONF_mapreduce_map_output_compress=true
YARN_CONF_mapred_map_output_compress_codec=org.apache.hadoop.io.compress.SnappyCodec
YARN_CONF_yarn_nodemanager_resource_memory___mb=16384
YARN_CONF_yarn_nodemanager_resource_cpu___vcores=8
YARN_CONF_yarn_nodemanager_disk___health___checker_max___disk___utilization___per___disk___percentage=98.5
YARN_CONF_yarn_nodemanager_remote___app___log___dir=/app-logs
YARN_CONF_yarn_nodemanager_aux___services=mapreduce_shuffle

MAPRED_CONF_mapreduce_framework_name=yarn
MAPRED_CONF_mapred_child_java_opts=-Xmx4096m
MAPRED_CONF_mapreduce_map_memory_mb=4096
MAPRED_CONF_mapreduce_reduce_memory_mb=8192
MAPRED_CONF_mapreduce_map_java_opts=-Xmx3072m
MAPRED_CONF_mapreduce_reduce_java_opts=-Xmx6144m
EOF
fi

# Créer le répertoire des logs d'exemple s'il n'existe pas
mkdir -p sample_logs

# Générer des logs d'exemple si nécessaire
if [ ! -f sample_logs/sample_web_logs.log ] || [ ! -s sample_logs/sample_web_logs.log ]; then
    echo "Génération de logs d'exemple..."
    python3 generate_sample_logs.py --output sample_logs/sample_web_logs.log --entries 10000
else
    echo "Fichier de logs d'exemple existant détecté."
fi

# Démarrer les conteneurs Docker
echo "Démarrage des conteneurs Docker..."
docker-compose up -d

# Attendre que les services soient prêts
echo "Attente du démarrage complet des services..."
sleep 10

# Exécuter le script principal
echo "Exécution du traitement des logs..."
docker exec -it logs-app python3 /app/main.py --log-file /app/logs/sample_web_logs.log --run-queries

echo "=== Traitement terminé ==="
echo "Pour accéder à l'interface Web HDFS, visitez: http://localhost:9870"
echo "Pour accéder à l'interface Web Hive, vous pouvez vous connecter au conteneur: docker exec -it hive-server bash"
echo "et exécuter la commande: hive"